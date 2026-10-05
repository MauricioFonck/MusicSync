from __future__ import annotations

import os
from pathlib import Path

from musicsync.domain.value_objects import MediaPath

from .errors import DestinationExistsError, PathSecurityError
from .paths import SafePathResolver


class AtomicFileStore:
    def __init__(self, destination_root: Path, temporary_root: Path) -> None:
        self.destination = SafePathResolver(destination_root)
        self.temporary = SafePathResolver(temporary_root)

    def move(self, source: MediaPath, destination: MediaPath | str) -> MediaPath:
        source_path = self.temporary.resolve(source, allow_missing=False)
        if not source_path.is_file():
            raise PathSecurityError("Atomic source must be a regular file")
        destination_path = self.destination.resolve(destination)
        if destination_path.exists():
            raise DestinationExistsError(f"Destination already exists: {destination_path}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source_path, destination_path)
        return MediaPath(str(destination_path.relative_to(self.destination.root)))
