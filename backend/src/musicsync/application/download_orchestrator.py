from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from musicsync.domain.entities import DownloadJob
from musicsync.domain.ports import DownloaderPort
from musicsync.domain.value_objects import DownloadStatus, MediaPath

DestinationBuilder = Callable[[int], str]


class DownloadOrchestrator:
    """Coordinate source analysis and item downloads without controller logic."""

    def run(
        self,
        job: DownloadJob,
        downloader: DownloaderPort,
        destination_for: DestinationBuilder,
    ) -> DownloadJob:
        job.start()
        analysis = downloader.analyze(job.source_url)
        tracks_by_id = {track.id: track for track in analysis.tracks}
        for index, item in enumerate(job.items):
            if job.status is DownloadStatus.CANCELLED:
                break
            track = tracks_by_id.get(item.track_id)
            if track is None:
                item.mark_failed(f"Track {item.track_id} was not found in source analysis")
                continue
            item.status = DownloadStatus.DOWNLOADING
            try:
                output = downloader.download(item, str(Path(destination_for(index))))
            except Exception as exc:  # adapter errors are isolated to the item
                item.mark_failed(str(exc))
                continue
            item.output_path = MediaPath(output)
            item.update_progress(100)
            item.status = DownloadStatus.COMPLETED
        if job.status is not DownloadStatus.CANCELLED:
            job.finish()
        return job
