from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from musicsync.domain.entities import DownloadItem, DownloadJob
from musicsync.domain.ports import DownloaderPort
from musicsync.domain.value_objects import DownloadStatus, MediaPath

from .reliability import RetryPolicy

DestinationBuilder = Callable[[int], str]


class DownloadOrchestrator:
    """Coordinate source analysis and item downloads without controller logic."""

    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self.retry_policy = retry_policy or RetryPolicy()

    def run(
        self,
        job: DownloadJob,
        downloader: DownloaderPort,
        destination_for: DestinationBuilder,
    ) -> DownloadJob:
        if job.status is DownloadStatus.COMPLETED:
            return job
        resumable = {
            DownloadStatus.PAUSED,
            DownloadStatus.FAILED,
            DownloadStatus.PARTIALLY_COMPLETED,
        }
        if job.status in resumable:
            job.resume()
        else:
            job.start()
        analysis = downloader.analyze(job.source_url)
        tracks_by_id = {track.id: track for track in analysis.tracks}
        for index, item in enumerate(job.items):
            if job.status is DownloadStatus.CANCELLED:
                break
            if item.status is DownloadStatus.COMPLETED:
                continue
            track = tracks_by_id.get(item.track_id)
            if track is None:
                item.mark_failed(f"Track {item.track_id} was not found in source analysis")
                continue
            output = self._download_with_retries(item, downloader, destination_for(index))
            if output is None:
                continue
            item.output_path = MediaPath(output)
            item.update_progress(100)
            item.status = DownloadStatus.COMPLETED
        if job.status is not DownloadStatus.CANCELLED:
            job.finish()
        return job

    def _download_with_retries(
        self, item: DownloadItem, downloader: DownloaderPort, destination: str
    ) -> str | None:
        last_error = "Download failed"
        for _attempt in range(self.retry_policy.max_attempts):
            try:
                item.status = DownloadStatus.DOWNLOADING
                return downloader.download(item, str(Path(destination)))
            except Exception as exc:  # adapter errors are isolated to the item
                last_error = str(exc) or last_error
        item.mark_failed(last_error)
        return None
