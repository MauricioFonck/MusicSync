from __future__ import annotations

from collections.abc import Callable, Sequence
from threading import RLock

from musicsync.domain.entities import StorageDevice
from musicsync.domain.events import DomainEvent, StorageConnected, StorageDisconnected
from musicsync.domain.ports import StorageDevicePort
from musicsync.domain.value_objects import StorageDeviceId

from .errors import InsufficientSpaceError, StorageNotAvailableError

StorageEventCallback = Callable[[DomainEvent], None]


class StorageMonitor:
    """Poll an adapter and emit a deterministic delta of storage events."""

    def __init__(self, adapter: StorageDevicePort) -> None:
        self._adapter = adapter
        self._devices: dict[str, StorageDevice] = {}
        self._subscribers: list[StorageEventCallback] = []
        self._lock = RLock()

    def refresh(self) -> tuple[DomainEvent, ...]:
        discovered = {device.id.value: device for device in self._adapter.list_devices()}
        with self._lock:
            previous_ids = set(self._devices)
            current_ids = set(discovered)
            events: list[DomainEvent] = []
            for device_id in sorted(current_ids - previous_ids):
                events.append(StorageConnected(device_id=StorageDeviceId(device_id)))
            for device_id in sorted(previous_ids - current_ids):
                self._devices[device_id].is_available = False
                events.append(StorageDisconnected(device_id=StorageDeviceId(device_id)))
            self._devices.update(discovered)
            for event in events:
                for callback in tuple(self._subscribers):
                    callback(event)
            return tuple(events)

    def list_devices(self) -> Sequence[StorageDevice]:
        with self._lock:
            return tuple(self._devices.values())

    def subscribe(self, callback: StorageEventCallback) -> Callable[[], None]:
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._subscribers:
                    self._subscribers.remove(callback)

        return unsubscribe

    def require_available(
        self,
        device_id: StorageDeviceId,
        *,
        required_bytes: int = 0,
    ) -> StorageDevice:
        with self._lock:
            device = self._devices.get(device_id.value)
            if device is None or not device.is_available:
                raise StorageNotAvailableError(f"Storage device is unavailable: {device_id}")
            if required_bytes < 0:
                raise ValueError("Required bytes cannot be negative")
            if device.free_space < required_bytes:
                raise InsufficientSpaceError(
                    f"Storage device has {device.free_space} free bytes; {required_bytes} required"
                )
            return device
