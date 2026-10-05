from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from musicsync.domain.entities import DownloadItem, Track


@dataclass(frozen=True, slots=True)
class SourceAnalysis:
    source: str
    tracks: tuple[Track, ...]


class DownloaderPort(Protocol):
    def analyze(self, url: str) -> SourceAnalysis: ...

    def download(self, item: DownloadItem, destination: str) -> str: ...

    def cancel(self, job_id: str) -> None: ...
