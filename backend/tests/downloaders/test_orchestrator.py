from __future__ import annotations

from pathlib import Path

from musicsync.application import DownloadOrchestrator
from musicsync.domain.entities import DownloadItem, DownloadJob, Track
from musicsync.domain.ports import SourceAnalysis
from musicsync.domain.value_objects import JobId, Source, SourceId, StorageDeviceId, TrackId


class FakeDownloader:
    def __init__(self, tracks: tuple[Track, ...]) -> None:
        self.analysis = SourceAnalysis("https://example.com/list", tracks)
        self.downloaded: list[str] = []

    def analyze(self, url: str) -> SourceAnalysis:
        assert url == self.analysis.source
        return self.analysis

    def download(self, item: DownloadItem, destination: str) -> str:
        self.downloaded.append(str(item.track_id))
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        Path(destination).write_bytes(b"audio")
        return destination

    def cancel(self, job_id: str) -> None:
        del job_id


def test_orchestrator_analyzes_downloads_and_finishes_job(tmp_path: Path) -> None:
    track = Track(TrackId.new(), Source.OTHER, SourceId("source-1"), "Title", "Artist")
    downloader = FakeDownloader((track,))
    job = DownloadJob(JobId.new(), downloader.analysis.source, StorageDeviceId("usb-1"))
    job.items.append(DownloadItem("item-1", job.id, track.id))

    result = DownloadOrchestrator().run(
        job, downloader, lambda index: str(tmp_path / f"track-{index}.audio")
    )

    assert result.completed_items == 1
    assert result.status.value == "COMPLETED"
    assert result.items[0].progress == 100
    assert result.items[0].output_path is not None


def test_orchestrator_retries_transient_errors_and_skips_completed_items(tmp_path: Path) -> None:
    track = Track(TrackId.new(), Source.OTHER, SourceId("source-2"), "Retry", "Artist")
    downloader = FakeDownloader((track,))
    attempts = 0

    def flaky_download(item: DownloadItem, destination: str) -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary failure")
        return destination

    downloader.download = flaky_download  # type: ignore[method-assign]
    job = DownloadJob(JobId.new(), downloader.analysis.source, StorageDeviceId("usb-1"))
    job.items.append(DownloadItem("item-2", job.id, track.id))

    result = DownloadOrchestrator().run(
        job, downloader, lambda index: str(tmp_path / f"retry-{index}.audio")
    )

    assert attempts == 3
    assert result.completed_items == 1
    resumed = DownloadOrchestrator().run(
        result, downloader, lambda index: str(tmp_path / f"retry-{index}.audio")
    )
    assert attempts == 3
    assert resumed.completed_items == 1
