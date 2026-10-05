from sqlalchemy.orm import Session

from musicsync.domain.entities import DownloadItem, DownloadJob
from musicsync.domain.value_objects import DownloadStatus, JobId, StorageDeviceId, TrackId
from musicsync.infrastructure.database.job_repository import SqlAlchemyDownloadJobRepository


def test_download_job_round_trip_includes_items(session: Session) -> None:
    repository = SqlAlchemyDownloadJobRepository(session)
    job = DownloadJob(JobId.new(), "https://example.com/playlist", StorageDeviceId("usb-1"))
    job.items.append(DownloadItem("item-1", job.id, TrackId.new()))
    job.start()

    repository.save(job)
    loaded = repository.get(job.id)

    assert loaded is not None
    assert loaded.status is DownloadStatus.DOWNLOADING
    assert len(loaded.items) == 1
    assert loaded.items[0].id == "item-1"
    assert loaded.items[0].job_id == job.id
