import os
from pathlib import Path

from musicsync.infrastructure.storage import LocalStorageDeviceAdapter


def test_adapter_discovers_mount_metadata_and_stable_volume_identity(tmp_path: Path) -> None:
    mount = tmp_path / "USB Music"
    mount.mkdir()
    adapter = LocalStorageDeviceAdapter(
        mount_points=[mount],
        metadata_reader=lambda path: ("exFAT", "MUSIC_USB"),
    )

    devices = adapter.list_devices()

    assert len(devices) == 1
    device = devices[0]
    assert device.id.value.startswith("windows:volume:" if os.name == "nt" else "posix:volume:")
    assert device.volume_label == "MUSIC_USB"
    assert device.filesystem == "exFAT"
    assert device.mount_point == str(mount.resolve())
    assert device.total_space > 0
    assert device.free_space > 0
