from __future__ import annotations

from collections.abc import Sequence

from musicsync.domain.entities import DownloadItem, DownloadJob, StorageDevice
from musicsync.domain.ports import DownloaderPort, SourceAnalysis
from musicsync.domain.value_objects import JobId, StorageDeviceId

from .schemas import (
    AnalysisResponse,
    DownloadItemResponse,
    DownloadJobResponse,
    StorageDeviceResponse,
    TrackResponse,
)


class ApiService:
    """Application-facing in-memory facade, replaceable by persistent use cases."""

    def __init__(self, downloader: DownloaderPort, devices: Sequence[StorageDevice] = ()) -> None:
        self.downloader = downloader
        self.devices = tuple(devices)
        self.analyses: dict[str, SourceAnalysis] = {}
        self.jobs: dict[str, DownloadJob] = {}

    def analyze(self, url: str) -> AnalysisResponse:
        analysis = self.downloader.analyze(url)
        self.analyses[url] = analysis
        return AnalysisResponse(
            source=analysis.source,
            tracks=[
                TrackResponse(
                    id=str(track.id),
                    source_id=str(track.source_id),
                    title=track.title,
                    artist=track.artist,
                    album=track.album,
                    duration_seconds=float(track.duration.seconds) if track.duration else None,
                    release_date=track.release_date,
                    original_url=track.original_url,
                )
                for track in analysis.tracks
            ],
        )

    def create_job(
        self, url: str, device_id: str, track_ids: list[str] | None
    ) -> DownloadJobResponse:
        analysis = self.analyses.get(url) or self.downloader.analyze(url)
        self.analyses[url] = analysis
        selected = set(track_ids) if track_ids is not None else None
        tracks = [
            track for track in analysis.tracks if selected is None or str(track.id) in selected
        ]
        if not tracks:
            raise ValueError("No tracks selected for download")
        job = DownloadJob(JobId.new(), url, StorageDeviceId(device_id))
        job.items.extend(
            DownloadItem(f"{job.id}-{index}", job.id, track.id)
            for index, track in enumerate(tracks)
        )
        self.jobs[str(job.id)] = job
        return self.to_job_response(job)

    def get_job(self, job_id: str) -> DownloadJobResponse | None:
        job = self.jobs.get(job_id)
        return self.to_job_response(job) if job else None

    def cancel_job(self, job_id: str) -> DownloadJobResponse | None:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        job.cancel()
        self.downloader.cancel(job_id)
        return self.to_job_response(job)

    def resume_job(self, job_id: str) -> DownloadJobResponse | None:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        job.start()
        return self.to_job_response(job)

    def history(self) -> list[DownloadJobResponse]:
        return [self.to_job_response(job) for job in self.jobs.values()]

    @staticmethod
    def to_job_response(job: DownloadJob) -> DownloadJobResponse:
        return DownloadJobResponse(
            id=str(job.id),
            source_url=job.source_url,
            destination_device_id=str(job.destination_device_id),
            status=job.status.value,
            total_items=job.total_items,
            completed_items=job.completed_items,
            failed_items=job.failed_items,
            items=[
                DownloadItemResponse(
                    id=item.id,
                    track_id=str(item.track_id),
                    status=item.status.value,
                    progress=item.progress,
                    error=item.error,
                    output_path=str(item.output_path) if item.output_path else None,
                )
                for item in job.items
            ],
        )

    @staticmethod
    def to_device_response(device: StorageDevice) -> StorageDeviceResponse:
        return StorageDeviceResponse(
            id=str(device.id),
            volume_label=device.volume_label,
            mount_point=device.mount_point,
            filesystem=device.filesystem,
            total_space=device.total_space,
            free_space=device.free_space,
            is_available=device.is_available,
        )
