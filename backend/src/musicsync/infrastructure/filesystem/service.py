from __future__ import annotations

from pathlib import Path

from musicsync.domain.value_objects import Checksum, JobId, MediaPath

from .atomic import AtomicFileStore
from .checksums import Sha256ChecksumService
from .temporary import TemporaryDirectoryManager


class LocalFilesystemService:
    def __init__(self, storage_root: Path, temporary_root: Path) -> None:
        self.temporary = TemporaryDirectoryManager(temporary_root)
        self.atomic = AtomicFileStore(storage_root, temporary_root)
        self.checksums = Sha256ChecksumService()

    def create_temp_directory(self, job_id: JobId) -> MediaPath:
        return self.temporary.create(job_id)

    def checksum(self, path: MediaPath) -> Checksum:
        resolved = self.temporary.resolver.resolve(path, allow_missing=False)
        return self.checksums.calculate(resolved)

    def atomic_move(self, source: MediaPath, destination: MediaPath) -> MediaPath:
        return self.atomic.move(source, destination)

    def cleanup_temp_directory(self, directory: MediaPath) -> None:
        self.temporary.cleanup(directory)
