from datetime import UTC, datetime

import pytest

from musicsync.domain.entities import DownloadRecord, MediaFile, Playlist
from musicsync.domain.value_objects import (
    Checksum,
    DownloadStatus,
    Duration,
    JobId,
    MediaPath,
    Source,
    SourceId,
    TrackId,
)


def test_playlist_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        Playlist("playlist-1", Source.YOUTUBE, SourceId("playlist"), "", "https://example.com")


def test_media_file_validates_size_and_preserves_checksum() -> None:
    media_file = MediaFile(
        id="media-1",
        track_id=TrackId.new(),
        path=MediaPath("MUSIC/Artist/Album/song.mp3"),
        filename="song.mp3",
        extension="mp3",
        size=1024,
        duration=Duration.from_seconds(180),
        bitrate=192,
        checksum=Checksum("c" * 64),
        created_at=datetime.now(UTC),
    )

    assert media_file.checksum.value == "c" * 64
    with pytest.raises(ValueError):
        MediaFile(
            id="media-2",
            track_id=TrackId.new(),
            path=media_file.path,
            filename="song.mp3",
            extension="mp3",
            size=-1,
            duration=media_file.duration,
            bitrate=192,
            checksum=media_file.checksum,
        )


def test_download_record_is_immutable() -> None:
    record = DownloadRecord("record-1", JobId.new(), TrackId.new(), DownloadStatus.COMPLETED)

    assert record.status is DownloadStatus.COMPLETED
    with pytest.raises(AttributeError):
        record.status = DownloadStatus.FAILED  # type: ignore[misc]
