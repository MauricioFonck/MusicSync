from __future__ import annotations

import json
from typing import Any

from musicsync.domain.ports import SearchHit

from .errors import DownloaderToolError
from .spot_dl import SpotDlDownloaderAdapter
from .yt_dlp import CommandRunner, YtDlpDownloaderAdapter

MAX_RESULTS = 20


class MusicSearch:
    """Find source URLs from free text: YouTube via yt-dlp, Spotify via spotDL."""

    def __init__(
        self,
        *,
        yt_dlp_binary: str = "yt-dlp",
        spotdl_binary: str = "spotdl",
        runner: CommandRunner | None = None,
    ) -> None:
        self._yt = YtDlpDownloaderAdapter(binary=yt_dlp_binary, runner=runner)
        self._spotify = SpotDlDownloaderAdapter(binary=spotdl_binary, runner=runner)

    def search(self, query: str, source: str, limit: int) -> list[SearchHit]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty")
        limit = max(1, min(limit, MAX_RESULTS))
        if source == "youtube":
            return self._youtube(query, limit)
        if source == "spotify":
            return self._spotify_hits(query, limit)
        raise ValueError("Search source must be 'youtube' or 'spotify'")

    def _youtube(self, query: str, limit: int) -> list[SearchHit]:
        result = self._yt._run(
            [
                self._yt._binary,
                "--dump-single-json",
                "--flat-playlist",
                "--no-warnings",
                f"ytsearch{limit}:{query}",
            ]
        )
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown yt-dlp error"
            raise DownloaderToolError(f"YouTube search failed: {detail}")
        try:
            entries: list[dict[str, Any]] = json.loads(result.stdout).get("entries") or []
        except json.JSONDecodeError as exc:
            raise DownloaderToolError("yt-dlp returned invalid JSON") from exc
        return [
            SearchHit(
                title=str(entry["title"]),
                artist=str(entry.get("channel") or entry.get("uploader") or "Unknown artist"),
                url=f"https://www.youtube.com/watch?v={entry['id']}",
                source="youtube",
                duration_seconds=entry.get("duration"),
                thumbnail_url=f"https://i.ytimg.com/vi/{entry['id']}/mqdefault.jpg",
            )
            for entry in entries
            if entry.get("id") and entry.get("title")
        ]

    def _spotify_hits(self, query: str, limit: int) -> list[SearchHit]:
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
            for song in self._spotify.save(query)[:limit]
            if song.get("url") and song.get("name")
        ]
