from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from musicsync.domain.value_objects import JobId, MediaPath

from .errors import PathSecurityError
from .paths import SafePathResolver


class TemporaryDirectoryManager:
    def __init__(self, root: Path) -> None:
        self.resolver = SafePathResolver(root)

    def create(self, job_id: JobId) -> MediaPath:
        # Short on purpose: Windows MAX_PATH is 260 and the device root may already be deep.
        del job_id
        relative_directory = f"job-{uuid.uuid4().hex[:12]}"
        directory = self.resolver.resolve(relative_directory)
        directory.mkdir(parents=False, exist_ok=False)
        return MediaPath(relative_directory)

    def cleanup(self, directory: MediaPath) -> None:
        path = self.resolver.resolve(directory)
        if not path.name.startswith("job-"):
            raise PathSecurityError("Only managed job directories can be cleaned")
        if path.exists():
            shutil.rmtree(path)
