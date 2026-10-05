from collections.abc import Sequence
from datetime import UTC, datetime

import pytest

from musicsync.domain.entities import StorageDevice
from musicsync.domain.value_objects import StorageDeviceId
from musicsync.infrastructure.storage import (
    InsufficientSpaceError,
    StorageMonitor,
    StorageNotAvailableError,
)


class FakeStorageAdapter:
    def __init__(self, devices: Sequence[StorageDevice] = ()) -> None:
        self.devices = tuple(devices)

    def list_devices(self) -> Sequence[StorageDevice]:
        return self.devices


def device(identifier: str = "usb-serial-1", *, free_space: int = 100) -> StorageDevice:
    return StorageDevice(
        id=StorageDeviceId(identifier),
        volume_label="Music USB",
        mount_point="/mnt/music",
        filesystem="exFAT",
        total_space=1000,
        free_space=free_space,
        last_seen=datetime.now(UTC),
    )


def test_monitor_emits_connect_disconnect_and_notifies_subscriber() -> None:
    adapter = FakeStorageAdapter([device()])
    monitor = StorageMonitor(adapter)
    received = []
    monitor.subscribe(received.append)

    connected = monitor.refresh()
    assert len(connected) == 1
    assert connected[0].device_id.value == "usb-serial-1"
    assert received == list(connected)

    adapter.devices = ()
    disconnected = monitor.refresh()
    assert len(disconnected) == 1
    assert disconnected[0].device_id.value == "usb-serial-1"
    assert not monitor.list_devices()[0].is_available


def test_monitor_requires_space_and_availability() -> None:
    adapter = FakeStorageAdapter([device(free_space=100)])
    monitor = StorageMonitor(adapter)
    monitor.refresh()

    selected = monitor.require_available(StorageDeviceId("usb-serial-1"), required_bytes=100)
    assert selected.free_space == 100
    with pytest.raises(InsufficientSpaceError):
        monitor.require_available(StorageDeviceId("usb-serial-1"), required_bytes=101)

    adapter.devices = ()
    monitor.refresh()
    with pytest.raises(StorageNotAvailableError):
        monitor.require_available(StorageDeviceId("usb-serial-1"))
