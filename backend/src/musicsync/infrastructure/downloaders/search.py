from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from musicsync.domain.ports import SearchHit

from .errors import DownloaderToolError
from .spot_dl import SpotDlDownloaderAdapter
from .spotify_api import SpotifyWebSearch
from .yt_dlp import CommandRunner

MAX_RESULTS = 20
CACHE_TTL_SECONDS = 600
CACHE_MAX_ENTRIES = 256

# (query, limit) -> raw yt-dlp flat entries
YoutubeSearch = Callable[[str, int], list[dict[str, Any]]]


def _yt_dlp_search(query: str, limit: int) -> list[dict[str, Any]]:
    """In-process yt-dlp: skips the ~1-2 s interpreter start of a subprocess per search."""
    import yt_dlp

    options = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
    except yt_dlp.utils.DownloadError as exc:
        raise DownloaderToolError(f"YouTube search failed: {exc}") from exc
    entries = (info or {}).get("entries") or []
    return [entry for entry in entries if isinstance(entry, dict)]


class MusicSearch:
    """Find source URLs from free text.

    YouTube: in-process yt-dlp. Spotify: official Web API when credentials are configured
    (fast, many results), otherwise spotDL (slow, best match only). Results are cached briefly.
    """

    def __init__(
        self,
        *,
        spotdl_binary: str = "spotdl",
        runner: CommandRunner | None = None,
        youtube: YoutubeSearch = _yt_dlp_search,
        spotify_api: SpotifyWebSearch | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._youtube_search = youtube
        self._spotify_api = spotify_api
        self._spotdl = SpotDlDownloaderAdapter(binary=spotdl_binary, runner=runner)
        self._clock = clock
        # ponytail: plain dict, oldest-first eviction; swap for a real cache if it gets hot.
        self._cache: dict[tuple[str, str, int], tuple[float, list[SearchHit]]] = {}

    @property
    def spotify_api_enabled(self) -> bool:
        return self._spotify_api is not None

    def search(self, query: str, source: str, limit: int) -> list[SearchHit]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty")
        if source not in {"youtube", "spotify"}:
            raise ValueError("Search source must be 'youtube' or 'spotify'")
        limit = max(1, min(limit, MAX_RESULTS))
        key = (source, query.casefold(), limit)
        cached = self._cache.get(key)
        if cached is not None and cached[0] > self._clock():
            return list(cached[1])
        hits = self._youtube(query, limit) if source == "youtube" else self._spotify(query, limit)
        if len(self._cache) >= CACHE_MAX_ENTRIES:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = (self._clock() + CACHE_TTL_SECONDS, hits)
        return list(hits)

    def _youtube(self, query: str, limit: int) -> list[SearchHit]:
        return [
            SearchHit(
                title=str(entry["title"]),
                artist=str(entry.get("channel") or entry.get("uploader") or "Unknown artist"),
                url=f"https://www.youtube.com/watch?v={entry['id']}",
                source="youtube",
                duration_seconds=entry.get("duration"),
                thumbnail_url=f"https://i.ytimg.com/vi/{entry['id']}/mqdefault.jpg",
            )
            for entry in self._youtube_search(query, limit)
            if entry.get("id") and entry.get("title")
        ]

    def _spotify(self, query: str, limit: int) -> list[SearchHit]:
        if self._spotify_api is not None:
            return self._spotify_api.search(query, limit)
        return [
            SearchHit(
                title=str(song.get("name", "")),
                artist=str(song.get("artist", "")),
                url=str(song["url"]),
                source="spotify",
                duration_seconds=song.get("duration"),
                album=song.get("album_name"),
                thumbnail_url=song.get("cover_url"),
            )
            for song in self._spotdl.save(query)[:limit]
            if song.get("url") and song.get("name")
        ]
