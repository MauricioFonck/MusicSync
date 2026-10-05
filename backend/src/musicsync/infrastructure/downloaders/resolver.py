from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlparse

from musicsync.domain.ports import DownloaderPort
from musicsync.domain.value_objects import Source

from .errors import InvalidSourceUrlError


class SourceResolver:
    """Select a downloader without leaking source routing into HTTP controllers."""

    def __init__(self, adapters: Mapping[Source, DownloaderPort]) -> None:
        self._adapters = dict(adapters)

    def resolve(self, url: str) -> DownloaderPort:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InvalidSourceUrlError("Source URL must be an absolute HTTP(S) URL")
        host = (parsed.hostname or "").lower()
        source = (
            Source.SPOTIFY
            if host in {"spotify.com", "www.spotify.com", "open.spotify.com"}
            else Source.YOUTUBE_MUSIC
            if host == "music.youtube.com"
            else Source.YOUTUBE
            if host in {"youtube.com", "www.youtube.com", "youtu.be"}
            else Source.OTHER
        )
        adapter = self._adapters.get(source) or self._adapters.get(Source.OTHER)
        if adapter is None:
            raise InvalidSourceUrlError(f"No downloader configured for source {source}")
        return adapter
