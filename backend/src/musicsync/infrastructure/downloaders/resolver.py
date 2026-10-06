from __future__ import annotations

from collections.abc import Iterable, Mapping
from urllib.parse import urlparse

from musicsync.domain.entities import DownloadItem
from musicsync.domain.ports import DownloaderPort, SourceAnalysis
from musicsync.domain.value_objects import Source, TrackId

from .errors import InvalidSourceUrlError, UnknownTrackError


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


class ResolvingDownloader(DownloaderPort):
    """DownloaderPort that routes each URL to its adapter and remembers who owns each track."""

    def __init__(self, resolver: SourceResolver, adapters: Iterable[DownloaderPort]) -> None:
        self._resolver = resolver
        self._adapters = tuple(adapters)
        self._owners: dict[TrackId, DownloaderPort] = {}

    def analyze(self, url: str) -> SourceAnalysis:
        adapter = self._resolver.resolve(url)
        analysis = adapter.analyze(url)
        self._owners.update({track.id: adapter for track in analysis.tracks})
        return analysis

    def download(self, item: DownloadItem, destination: str) -> str:
        adapter = self._owners.get(item.track_id)
        if adapter is None:
            raise UnknownTrackError(f"Track {item.track_id} was not analyzed")
        return adapter.download(item, destination)

    def cancel(self, job_id: str) -> None:
        for adapter in self._adapters:
            adapter.cancel(job_id)
