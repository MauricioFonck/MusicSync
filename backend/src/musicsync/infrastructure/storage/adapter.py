from __future__ import annotations

import os
import shutil
import string
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from musicsync.domain.entities import StorageDevice
from musicsync.domain.ports import StorageDevicePort
from musicsync.domain.value_objects import StorageDeviceId

MountMetadata = tuple[str, str]
MetadataReader = Callable[[Path], MountMetadata]


class LocalStorageDeviceAdapter(StorageDevicePort):
    """Discover mounted removable-like paths without using drive letters as identity."""

    def __init__(
        self,
        *,
        mount_points: Iterable[Path] | None = None,
        scan_roots: Iterable[Path] | None = None,
        metadata_reader: MetadataReader | None = None,
    ) -> None:
        self._mount_points = (
            tuple(path for path in mount_points) if mount_points is not None else None
        )
        self._scan_roots = (
            tuple(scan_roots) if scan_roots is not None else self._default_scan_roots()
        )
        self._metadata_reader = metadata_reader or self._default_metadata

    def list_devices(self) -> Sequence[StorageDevice]:
        devices: list[StorageDevice] = []
        seen: set[str] = set()
        for mount_point in self._candidate_mount_points():
            try:
                if not mount_point.is_dir():
                    continue
                identifier = self._stable_identifier(mount_point)
                if identifier in seen:
                    continue
                total_space, free_space = self._capacity(mount_point)
                filesystem, volume_label = self._metadata_reader(mount_point)
                devices.append(
                    StorageDevice(
                        id=StorageDeviceId(identifier),
                        volume_label=volume_label or mount_point.name or identifier,
                        mount_point=str(mount_point.resolve()),
                        filesystem=filesystem or "UNKNOWN",
                        total_space=total_space,
                        free_space=free_space,
                        is_available=True,
                        last_seen=datetime.now(UTC),
                    )
                )
                seen.add(identifier)
            except OSError:
                continue
        return tuple(devices)

    def subscribe(self, callback: Callable[[StorageDevice], None]) -> Callable[[], None]:
        """The monitor owns event subscriptions; the adapter itself is polling-only."""
        del callback
        return lambda: None

    def _candidate_mount_points(self) -> Iterable[Path]:
        if self._mount_points is not None:
            return self._mount_points
        candidates: list[Path] = []
        for root in self._scan_roots:
            if not root.is_dir():
                continue
            try:
                candidates.extend(child for child in root.iterdir() if child.is_dir())
            except OSError:
                continue
        return candidates

    @staticmethod
    def _capacity(path: Path) -> tuple[int, int]:
        usage = shutil.disk_usage(path)
        return usage.total, usage.free

    @staticmethod
    def _stable_identifier(path: Path) -> str:
        stat_result = path.stat()
        platform_prefix = "windows" if os.name == "nt" else "posix"
        return f"{platform_prefix}:volume:{stat_result.st_dev}"

    @staticmethod
    def _default_scan_roots() -> tuple[Path, ...]:
        if os.name == "nt":
            return tuple(Path(f"{letter}:\\") for letter in string.ascii_uppercase)
        user = os.environ.get("USER", "")
        roots = [Path("/media"), Path("/mnt")]
        if user:
            roots.append(Path("/run/media") / user)
        return tuple(roots)

    @staticmethod
    def _default_metadata(path: Path) -> MountMetadata:
        filesystem = "NTFS" if os.name == "nt" else "UNKNOWN"
        return filesystem, path.name


class WindowsStorageDeviceAdapter(LocalStorageDeviceAdapter):
    """Named adapter for the Windows target; identity still comes from volume metadata."""

    def __init__(self, *, metadata_reader: MetadataReader | None = None) -> None:
        super().__init__(
            mount_points=(Path(f"{letter}:\\") for letter in string.ascii_uppercase),
            metadata_reader=metadata_reader,
        )
