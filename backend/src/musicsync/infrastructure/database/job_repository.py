from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from musicsync.domain.entities import DownloadItem, DownloadJob
from musicsync.domain.value_objects import (
    Checksum,
    DownloadStatus,
    JobId,
    MediaPath,
    StorageDeviceId,
    TrackId,
)
from musicsync.infrastructure.database.models import DownloadItemModel, DownloadJobModel


class SqlAlchemyDownloadJobRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, job_id: JobId) -> DownloadJob | None:
        model = self._session.get(DownloadJobModel, str(job_id))
        if model is None:
            return None
        item_models = self._session.scalars(
            select(DownloadItemModel).where(DownloadItemModel.job_id == model.id)
        ).all()
        return DownloadJob(
            id=JobId(UUID(model.id)),
            source_url=model.source_url,
            destination_device_id=StorageDeviceId(model.destination_device_id),
            items=[self._item_to_domain(item) for item in item_models],
            status=DownloadStatus(model.status),
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

    def save(self, job: DownloadJob) -> None:
        model = self._session.get(DownloadJobModel, str(job.id))
        if model is None:
            model = DownloadJobModel(id=str(job.id))
            self._session.add(model)
        model.source_url = job.source_url
        model.destination_device_id = job.destination_device_id.value
        model.status = job.status.value
        model.created_at = job.created_at
        model.started_at = job.started_at
        model.completed_at = job.completed_at
        self._session.execute(delete(DownloadItemModel).where(DownloadItemModel.job_id == model.id))
        for item in job.items:
            self._session.add(
                DownloadItemModel(
                    id=item.id,
                    job_id=model.id,
                    track_id=str(item.track_id),
                    status=item.status.value,
                    progress=item.progress,
                    error=item.error,
                    output_path=str(item.output_path) if item.output_path else None,
                    checksum=item.checksum.value if item.checksum else None,
                )
            )
        self._session.commit()

    @staticmethod
    def _item_to_domain(model: DownloadItemModel) -> DownloadItem:
        return DownloadItem(
            id=model.id,
            job_id=JobId(UUID(model.job_id)),
            track_id=TrackId(UUID(model.track_id)),
            status=DownloadStatus(model.status),
            progress=model.progress,
            error=model.error,
            output_path=MediaPath(model.output_path) if model.output_path else None,
            checksum=Checksum(model.checksum) if model.checksum else None,
        )
