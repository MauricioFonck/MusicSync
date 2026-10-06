from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

from musicsync.domain.ports import SearchHit

from .errors import DownloaderToolError

TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

# (request, timeout) -> (status, parsed JSON body)
HttpCall = Callable[[urllib.request.Request, float], tuple[int, Any]]


def _http(request: urllib.request.Request, timeout: float) -> tuple[int, Any]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.load(exc)
        except (json.JSONDecodeError, ValueError):
            return exc.code, {}
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DownloaderToolError(f"Spotify API is unreachable: {exc}") from exc


class SpotifyWebSearch:
    """Spotify Web API track search with the app (client credentials) flow: fast, many results."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        http: HttpCall = _http,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not client_id or not client_secret:
            raise ValueError("Spotify client id and secret are required")
        self._basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        self._http = http
        self._clock = clock
        self._token = ""
        self._expires_at = 0.0

    def search(self, query: str, limit: int) -> list[SearchHit]:
        status, body = self._search(query, limit)
        if status == 401:  # token revoked or expired early: refresh once
            self._token = ""
            status, body = self._search(query, limit)
        if status == 400 and limit > 10:  # some app tiers cap the page size at 10
            status, body = self._search(query, 10)
        if status != 200:
            message = (body.get("error") or {}).get("message") if isinstance(body, dict) else None
            raise DownloaderToolError(f"Spotify search failed ({status}): {message or 'error'}")
        items = ((body.get("tracks") or {}).get("items")) or []
        return [self._hit(item) for item in items if item and item.get("external_urls")]

    def _search(self, query: str, limit: int) -> tuple[int, Any]:
        params = urllib.parse.urlencode({"q": query, "type": "track", "limit": limit})
        request = urllib.request.Request(
            f"{SEARCH_URL}?{params}", headers={"Authorization": f"Bearer {self._access_token()}"}
        )
        return self._http(request, 10)

    def _access_token(self) -> str:
        if self._token and self._clock() < self._expires_at:
            return self._token
        request = urllib.request.Request(
            TOKEN_URL,
            data=b"grant_type=client_credentials",
            headers={
                "Authorization": f"Basic {self._basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        status, body = self._http(request, 10)
        if status != 200 or not isinstance(body, dict) or not body.get("access_token"):
            raise DownloaderToolError(
                f"Spotify rejected the client credentials ({status}); "
                "check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET"
            )
        self._token = str(body["access_token"])
        self._expires_at = self._clock() + float(body.get("expires_in", 3600)) - 60
        return self._token

    @staticmethod
    def _hit(item: dict[str, Any]) -> SearchHit:
        album = item.get("album") or {}
        images = album.get("images") or []
        image = images[1] if len(images) > 1 else (images[0] if images else {})
        duration_ms = item.get("duration_ms")
        return SearchHit(
            title=str(item.get("name", "")),
            artist=", ".join(a["name"] for a in item.get("artists") or [] if a.get("name")),
            url=str(item["external_urls"]["spotify"]),
            source="spotify",
            duration_seconds=duration_ms / 1000 if duration_ms else None,
            album=album.get("name"),
            thumbnail_url=image.get("url"),
        )
