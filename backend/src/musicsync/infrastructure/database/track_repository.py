from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from musicsync.domain.entities import Track
from musicsync.domain.services import ExistingTrack, TrackNormalizationService
from musicsync.domain.value_objects import Duration, Source, SourceId, TrackId
from musicsync.infrastructure.database.models import TrackModel


class SqlAlchemyTrackRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._normalizer = TrackNormalizationService()

    def find_by_source_id(self, source: Source, source_id: SourceId) -> Track | None:
        model = self._session.scalar(
            select(TrackModel).where(
                TrackModel.source == source.value,
                TrackModel.source_id == source_id.value,
            )
        )
        return self._to_domain(model) if model else None

    def find_existing_for_duplicate_check(self, track: Track) -> ExistingTrack | None:
        models = self._session.scalars(select(TrackModel)).all()
        title = self._normalizer.normalize_title(track.title).value
        artist = self._normalizer.normalize_artist(track.artist).value
        for model in models:
            model_title = self._normalizer.normalize_title(model.title).value
            model_artist = self._normalizer.normalize_artist(model.artist).value
            if model.source_id == track.source_id.value or (
                model_title == title and model_artist == artist
            ):
                return ExistingTrack(
                    source_id=model.source_id,
                    normalized_title=model_title,
                    normalized_artist=model_artist,
                    duration=(
                        Duration(Decimal(model.duration_seconds))
                        if model.duration_seconds is not None
                        else None
                    ),
                )
        return None

    def save(self, track: Track) -> None:
        model = self._session.get(TrackModel, str(track.id))
        if model is None:
            model = TrackModel(id=str(track.id))
            self._session.add(model)
        model.source = track.source.value
        model.source_id = track.source_id.value
        model.title = track.title
        model.artist = track.artist
        model.album = track.album
        model.album_artist = track.album_artist
        model.duration_seconds = str(track.duration.seconds) if track.duration else None
        model.track_number = track.track_number
        model.disc_number = track.disc_number
        model.genre = track.genre
        model.release_date = track.release_date
        model.thumbnail_url = track.thumbnail_url
        model.original_url = track.original_url
        self._session.commit()

    @staticmethod
    def _to_domain(model: TrackModel) -> Track:
        return Track(
            id=TrackId(UUID(model.id)),
            source=Source(model.source),
            source_id=SourceId(model.source_id),
            title=model.title,
            artist=model.artist,
            album=model.album,
            album_artist=model.album_artist,
            duration=Duration(Decimal(model.duration_seconds))
            if model.duration_seconds is not None
            else None,
            track_number=model.track_number,
            disc_number=model.disc_number,
            genre=model.genre,
            release_date=model.release_date,
            thumbnail_url=model.thumbnail_url,
            original_url=model.original_url,
        )
