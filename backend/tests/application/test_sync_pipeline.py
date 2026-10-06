from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path

from musicsync.application import SyncPipeline
from musicsync.config import Settings
from musicsync.domain.entities import DownloadItem, DownloadJob, MediaFile, StorageDevice, Track
from musicsync.domain.ports import MediaInspection, ProcessingOptions, SourceAnalysis
from musicsync.domain.value_objects import (
    DownloadStatus,
    Duration,
    JobId,
    MediaFormat,
    MediaPath,
    Quality,
    Source,
    SourceId,
    StorageDeviceId,
    TrackId,
)
from musicsync.infrastructure.database import SqlAlchemyDownloadJobRepository
from musicsync.infrastructure.database.session import (
    create_database_engine,
    create_schema,
    create_session_factory,
)
from musicsync.infrastructure.downloaders import ResolvingDownloader, SourceResolver
from musicsync.infrastructure.filesystem import LocalFilesystemService
from musicsync.main import build_service

URL = "https://example.com/list"


class FakeDownloader:
    def __init__(self) -> None:
        self.track = Track(
            TrackId.new(), Source.OTHER, SourceId("s-1"), "Song", "Artist", album="Album"
        )
        self.downloads = 0

    def analyze(self, url: str) -> SourceAnalysis:
        return SourceAnalysis(url, (self.track,))

    def download(self, item: DownloadItem, destination: str) -> str:
        self.downloads += 1
        Path(destination).write_bytes(b"raw audio")
        return destination

    def cancel(self, job_id: str) -> None:
        del job_id


class FakeMedia:
    def __init__(self) -> None:
        self.options: ProcessingOptions | None = None

    def process(
        self, source: MediaPath, destination: MediaPath, options: ProcessingOptions
    ) -> MediaPath:
        self.options = options
        shutil.copyfile(source.value, destination.value)
        return destination

    def inspect(self, path: MediaPath) -> MediaInspection:
        del path
        return MediaInspection(Duration(Decimal(120)), 192, None)

    def validate(self, path: MediaPath) -> bool:
        del path
        return True


def device(root: Path) -> StorageDevice:
    return StorageDevice(StorageDeviceId("usb-1"), "USB", str(root), "FAT32", 10**9, 10**9)


def new_job(downloader: FakeDownloader) -> DownloadJob:
    job = DownloadJob(JobId.new(), URL, StorageDeviceId("usb-1"))
    job.items.append(DownloadItem(f"{job.id}-0", job.id, downloader.track.id))
    return job


def pipeline(
    downloader: FakeDownloader, media: FakeMedia, recorded: list[MediaFile]
) -> SyncPipeline:
    return SyncPipeline(
        downloader,
        media,
        LocalFilesystemService,
        ProcessingOptions(MediaFormat.MP3, Quality(192)),
        record=lambda track, media_file: recorded.append(media_file),
    )


def test_pipeline_places_tagged_file_on_device_and_skips_duplicates(tmp_path: Path) -> None:
    downloader, media, recorded = FakeDownloader(), FakeMedia(), []
    sync = pipeline(downloader, media, recorded)

    job = sync.run(new_job(downloader), device(tmp_path))

    assert job.status is DownloadStatus.COMPLETED
    item = job.items[0]
    assert item.output_path == MediaPath("MUSIC/Artist/Album/Song.mp3")
    assert (tmp_path / "MUSIC/Artist/Album/Song.mp3").read_bytes() == b"raw audio"
    assert item.checksum is not None and recorded[0].checksum == item.checksum
    assert media.options is not None and ("title", "Song") in media.options.metadata
    assert list((tmp_path / ".musicsync-tmp").iterdir()) == []

    again = sync.run(new_job(downloader), device(tmp_path))
    assert again.status is DownloadStatus.COMPLETED
    assert downloader.downloads == 1


def test_pipeline_fails_job_when_device_is_missing() -> None:
    downloader = FakeDownloader()
    job = pipeline(downloader, FakeMedia(), []).run(new_job(downloader), None)

    assert job.status is DownloadStatus.FAILED
    assert job.items[0].error == "Storage device is not available"


def test_resolving_downloader_routes_download_to_analyzing_adapter(tmp_path: Path) -> None:
    youtube, other = FakeDownloader(), FakeDownloader()
    resolving = ResolvingDownloader(
        SourceResolver({Source.YOUTUBE: youtube, Source.OTHER: other}), (youtube, other)
    )
    track = resolving.analyze("https://youtu.be/abc").tracks[0]

    resolving.download(DownloadItem("i", JobId.new(), track.id), str(tmp_path / "out"))

    assert (youtube.downloads, other.downloads) == (1, 0)


def test_restart_pauses_interrupted_jobs(tmp_path: Path) -> None:
    url = f"sqlite:///{(tmp_path / 'db.sqlite').as_posix()}"
    sessions = create_session_factory(create_database_engine(url))
    create_schema(sessions.kw["bind"])
    job = DownloadJob(JobId.new(), URL, StorageDeviceId("usb-1"), status=DownloadStatus.DOWNLOADING)
    job.items.append(DownloadItem(f"{job.id}-0", job.id, TrackId.new()))
    with sessions() as session:
        SqlAlchemyDownloadJobRepository(session).save(job)

    service = build_service(Settings(database_url=url, storage_mount_points=[tmp_path]))

    restored = service.get_job(str(job.id))
    assert restored is not None and restored.status == "PAUSED"
    assert [d.mount_point for d in service.devices] == [str(tmp_path.resolve())]
    service.shutdown()
