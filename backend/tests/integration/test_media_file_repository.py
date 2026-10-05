from sqlalchemy.orm import Session

from musicsync.domain.entities import MediaFile
from musicsync.domain.value_objects import Checksum, Duration, MediaPath, TrackId
from musicsync.infrastructure.database.media_file_repository import SqlAlchemyMediaFileRepository


def make_media_file() -> MediaFile:
    return MediaFile(
        id="media-1",
        track_id=TrackId.new(),
        path=MediaPath("MUSIC/Artist/Album/song.mp3"),
        filename="song.mp3",
        extension="mp3",
        size=2048,
        duration=Duration.from_seconds(180),
        bitrate=192,
        checksum=Checksum("d" * 64),
    )


def test_media_file_round_trip_and_checksum_lookup(session: Session) -> None:
    repository = SqlAlchemyMediaFileRepository(session)
    media_file = make_media_file()

    repository.save(media_file)

    assert repository.find_by_checksum(media_file.checksum)
    loaded = repository.get(media_file.id)
    assert loaded is not None
    assert loaded.track_id == media_file.track_id
    assert loaded.path == media_file.path
    assert loaded.size == media_file.size
