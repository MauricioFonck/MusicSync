from __future__ import annotations

from typing import Protocol

from musicsync.domain.entities import DownloadJob, Track
from musicsync.domain.services import ExistingTrack
from musicsync.domain.value_objects import Checksum, JobId, Source, SourceId


class TrackRepository(Protocol):
    def find_by_source_id(self, source: Source, source_id: SourceId) -> Track | None: ...

    def find_existing_for_duplicate_check(self, track: Track) -> ExistingTrack | None: ...

    def save(self, track: Track) -> None: ...


class MediaFileRepository(Protocol):
    def find_by_checksum(self, checksum: Checksum) -> bool: ...


class DownloadJobRepository(Protocol):
    def get(self, job_id: JobId) -> DownloadJob | None: ...

    def save(self, job: DownloadJob) -> None: ...
