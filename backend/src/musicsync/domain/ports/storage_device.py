from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from musicsync.domain.entities import StorageDevice


class StorageDevicePort(Protocol):
    def list_devices(self) -> Sequence[StorageDevice]: ...

    def subscribe(self, callback: Callable[[StorageDevice], None]) -> Callable[[], None]: ...
