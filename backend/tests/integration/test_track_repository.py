from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from musicsync.domain.entities import Track
from musicsync.domain.value_objects import Duration, Source, SourceId, TrackId
from musicsync.infrastructure.database import models
from musicsync.infrastructure.database.track_repository import SqlAlchemyTrackRepository


def make_track(source_id: str = "video-1") -> Track:
    return Track(
        id=TrackId.new(),
        source=Source.YOUTUBE,
        source_id=SourceId(source_id),
        title="Song",
        artist="Artist",
        album="Album",
        duration=Duration.from_seconds(180),
        track_number=1,
        release_date=date(2024, 1, 1),
    )


def test_track_round_trip_preserves_domain_values(session: Session) -> None:
    repository = SqlAlchemyTrackRepository(session)
    track = make_track()

    repository.save(track)
    loaded = repository.find_by_source_id(track.source, track.source_id)

    assert loaded is not None
    assert loaded.id == track.id
    assert loaded.title == track.title
    assert loaded.duration == track.duration
    assert loaded.release_date == track.release_date


def test_track_source_and_source_id_are_unique(session: Session) -> None:
    repository = SqlAlchemyTrackRepository(session)
    repository.save(make_track("same-source"))
    duplicate = make_track("same-source")

    with pytest.raises(IntegrityError):
        repository.save(duplicate)

    session.rollback()
    assert session.query(models.TrackModel).count() == 1


def test_existing_track_is_available_for_duplicate_detection(session: Session) -> None:
    repository = SqlAlchemyTrackRepository(session)
    track = make_track()
    repository.save(track)

    existing = repository.find_existing_for_duplicate_check(make_track("other-source"))

    assert existing is not None
    assert existing.normalized_title == "song"
    assert existing.normalized_artist == "artist"
    assert existing.duration == Duration.from_seconds(180)
