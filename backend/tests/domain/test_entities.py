import pytest

from musicsync.domain.entities import DownloadItem, DownloadJob, Track
from musicsync.domain.value_objects import (
    Checksum,
    DownloadStatus,
    JobId,
    MediaPath,
    Source,
    SourceId,
    StorageDeviceId,
    TrackId,
)


def test_download_item_progress_is_monotonic_and_completion_is_explicit() -> None:
    item = DownloadItem("item-1", JobId.new(), TrackId.new())
    item.update_progress(40)
    with pytest.raises(ValueError):
        item.update_progress(20)

    item.mark_completed(MediaPath("MUSIC/Artist/Album/song.mp3"), Checksum("b" * 64))

    assert item.status is DownloadStatus.COMPLETED
    assert item.progress == 100


def test_download_job_transitions_and_counters() -> None:
    job = DownloadJob(JobId.new(), "https://example.com/list", StorageDeviceId("device-1"))
    item = DownloadItem("item-1", job.id, TrackId.new())
    job.items.append(item)

    job.start()
    assert job.status is DownloadStatus.DOWNLOADING
    item.mark_failed("network error")
    job.finish()

    assert job.status is DownloadStatus.FAILED
    assert job.failed_items == 1
    assert job.completed_at is not None


def test_track_rejects_empty_metadata() -> None:
    with pytest.raises(ValueError):
        Track(TrackId.new(), Source.YOUTUBE, SourceId("id"), "", "Artist")
