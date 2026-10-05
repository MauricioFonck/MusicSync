from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from musicsync.domain.value_objects import StorageDeviceId


@dataclass(slots=True)
class StorageDevice:
    id: StorageDeviceId
    volume_label: str
    mount_point: str
    filesystem: str
    total_space: int
    free_space: int
    is_available: bool = True
    last_seen: datetime | None = None

    def __post_init__(self) -> None:
        if not self.volume_label.strip():
            raise ValueError("Storage device volume label cannot be empty")
        if not self.mount_point.strip():
            raise ValueError("Storage device mount point cannot be empty")
        if self.total_space < 0 or self.free_space < 0:
            raise ValueError("Storage capacity cannot be negative")
        if self.free_space > self.total_space:
            raise ValueError("Free space cannot exceed total space")

    def can_fit(self, required_bytes: int) -> bool:
        if required_bytes < 0:
            raise ValueError("Required bytes cannot be negative")
        return self.is_available and self.free_space >= required_bytes
