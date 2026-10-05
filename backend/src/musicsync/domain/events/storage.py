from __future__ import annotations

from dataclasses import dataclass, field

from musicsync.domain.events.base import DomainEvent
from musicsync.domain.value_objects import StorageDeviceId


@dataclass(frozen=True, slots=True)
class StorageConnected(DomainEvent):
    device_id: StorageDeviceId = field(default_factory=lambda: StorageDeviceId("unknown"))


@dataclass(frozen=True, slots=True)
class StorageDisconnected(DomainEvent):
    device_id: StorageDeviceId = field(default_factory=lambda: StorageDeviceId("unknown"))
