from datetime import UTC, datetime

from sqlalchemy.orm import Session

from musicsync.domain.entities import StorageDevice
from musicsync.domain.value_objects import StorageDeviceId
from musicsync.infrastructure.database import SqlAlchemyStorageDeviceRepository


def test_storage_device_round_trip_and_available_filter(session: Session) -> None:
    repository = SqlAlchemyStorageDeviceRepository(session)
    device = StorageDevice(
        id=StorageDeviceId("windows:volume:123"),
        volume_label="Music USB",
        mount_point="E:\\",
        filesystem="exFAT",
        total_space=10_000,
        free_space=8_000,
        is_available=True,
        last_seen=datetime.now(UTC),
    )

    repository.save(device)
    loaded = repository.get(device.id)

    assert loaded is not None
    assert loaded.id == device.id
    assert loaded.free_space == 8_000
    assert len(repository.list_devices(available_only=True)) == 1

    device.is_available = False
    repository.save(device)
    assert repository.list_devices(available_only=True) == ()
