from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath

from musicsync.domain.value_objects import MediaPath

from .errors import PathSecurityError


class SafePathResolver:
    """Resolve user-derived relative paths without escaping a configured root."""

    def __init__(self, root: Path, *, max_path_length: int = 240) -> None:
        self.root = root.expanduser().resolve()
        self.max_path_length = max_path_length
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: MediaPath | str, *, allow_missing: bool = True) -> Path:
        raw_value = str(relative_path).strip()
        if not raw_value or len(raw_value) > self.max_path_length:
            raise PathSecurityError("Path is empty or exceeds the maximum length")
        if self._is_absolute(raw_value):
            raise PathSecurityError("Absolute paths are not allowed")

        normalized = raw_value.replace("\\", "/")
        parts = PurePosixPath(normalized).parts
        if any(part in {"", ".", ".."} for part in parts):
            raise PathSecurityError("Path contains unsafe traversal components")

        candidate = self.root.joinpath(*parts)
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self.root)
        except ValueError as error:
            raise PathSecurityError("Path escapes the configured root") from error

        if not allow_missing and not resolved.exists():
            raise FileNotFoundError(resolved)
        if self._contains_symlink(candidate):
            raise PathSecurityError("Symlinks are not allowed in controlled paths")
        return resolved

    @staticmethod
    def _is_absolute(value: str) -> bool:
        return (
            os.path.isabs(value)
            or PureWindowsPath(value).is_absolute()
            or bool(PureWindowsPath(value).drive)
        )

    def _contains_symlink(self, candidate: Path) -> bool:
        current = candidate
        while current != self.root:
            if current.is_symlink():
                return True
            current = current.parent
        return False
