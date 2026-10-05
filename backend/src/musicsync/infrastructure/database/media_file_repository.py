from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from musicsync.domain.entities import MediaFile
from musicsync.domain.value_objects import Checksum, Duration, MediaPath, TrackId
from musicsync.infrastructure.database.models import MediaFileModel


class SqlAlchemyMediaFileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_checksum(self, checksum: Checksum) -> bool:
        return (
            self._session.scalar(
                select(MediaFileModel.id).where(MediaFileModel.checksum == checksum.value)
            )
            is not None
        )

    def save(self, media_file: MediaFile) -> None:
        model = self._session.get(MediaFileModel, media_file.id)
        if model is None:
            model = MediaFileModel(id=media_file.id)
            self._session.add(model)
        model.track_id = str(media_file.track_id)
        model.path = str(media_file.path)
        model.filename = media_file.filename
        model.extension = media_file.extension
        model.size = media_file.size
        model.duration_seconds = str(media_file.duration.seconds)
        model.bitrate = media_file.bitrate
        model.checksum = media_file.checksum.value
        model.created_at = media_file.created_at
        self._session.commit()

    def get(self, media_file_id: str) -> MediaFile | None:
        model = self._session.get(MediaFileModel, media_file_id)
        if model is None:
            return None
        return MediaFile(
            id=model.id,
            track_id=TrackId(UUID(model.track_id)),
            path=MediaPath(model.path),
            filename=model.filename,
            extension=model.extension,
            size=model.size,
            duration=Duration(Decimal(model.duration_seconds)),
            bitrate=model.bitrate,
            checksum=Checksum(model.checksum),
            created_at=model.created_at,
        )
