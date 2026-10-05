from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from musicsync.domain.entities import StorageDevice
from musicsync.domain.value_objects import StorageDeviceId
from musicsync.infrastructure.database.models import StorageDeviceModel


class SqlAlchemyStorageDeviceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, device: StorageDevice) -> None:
        model = self._session.get(StorageDeviceModel, device.id.value)
        if model is None:
            model = StorageDeviceModel(id=device.id.value)
            self._session.add(model)
        model.volume_label = device.volume_label
        model.mount_point = device.mount_point
        model.filesystem = device.filesystem
        model.total_space = device.total_space
        model.free_space = device.free_space
        model.is_available = device.is_available
        model.last_seen = device.last_seen
        self._session.commit()

    def get(self, device_id: StorageDeviceId) -> StorageDevice | None:
        model = self._session.get(StorageDeviceModel, device_id.value)
        return self._to_domain(model) if model else None

    def list_devices(self, *, available_only: bool = False) -> tuple[StorageDevice, ...]:
        statement = select(StorageDeviceModel)
        if available_only:
            statement = statement.where(StorageDeviceModel.is_available.is_(True))
        models = self._session.scalars(statement).all()
        return tuple(self._to_domain(model) for model in models)

    @staticmethod
    def _to_domain(model: StorageDeviceModel) -> StorageDevice:
        return StorageDevice(
            id=StorageDeviceId(model.id),
            volume_label=model.volume_label,
            mount_point=model.mount_point,
            filesystem=model.filesystem,
            total_space=model.total_space,
            free_space=model.free_space,
            is_available=model.is_available,
            last_seen=model.last_seen,
        )
