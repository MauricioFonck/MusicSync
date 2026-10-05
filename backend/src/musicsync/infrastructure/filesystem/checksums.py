from __future__ import annotations

import hashlib
from pathlib import Path

from musicsync.domain.value_objects import Checksum, MediaPath


class Sha256ChecksumService:
    def __init__(self, *, chunk_size: int = 1024 * 1024) -> None:
        if chunk_size <= 0:
            raise ValueError("Checksum chunk size must be positive")
        self.chunk_size = chunk_size

    def calculate(self, path: MediaPath | Path) -> Checksum:
        digest = hashlib.sha256()
        resolved_path = Path(str(path)) if isinstance(path, MediaPath) else path
        with resolved_path.open("rb") as source:
            for chunk in iter(lambda: source.read(self.chunk_size), b""):
                digest.update(chunk)
        return Checksum(digest.hexdigest())
