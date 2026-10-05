from __future__ import annotations

from typing import Protocol

from musicsync.domain.value_objects import Checksum, JobId, MediaPath


class FileSystemPort(Protocol):
    def create_temp_directory(self, job_id: JobId) -> MediaPath: ...

    def checksum(self, path: MediaPath) -> Checksum: ...

    def atomic_move(self, source: MediaPath, destination: MediaPath) -> MediaPath: ...
