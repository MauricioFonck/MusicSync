from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from musicsync.domain.entities import DownloadItem, DownloadJob, StorageDevice
from musicsync.domain.ports import DownloaderPort, SearchPort, SourceAnalysis
from musicsync.domain.value_objects import DownloadStatus, JobId, StorageDeviceId

from .schemas import (
    AnalysisResponse,
    DownloadItemResponse,
    DownloadJobResponse,
    SearchResultResponse,
    StorageDeviceResponse,
    TrackResponse,
)

DeviceProvider = Callable[[], Sequence[StorageDevice]]
JobRunner = Callable[[DownloadJob], None]

ACTIVE = {
    DownloadStatus.PENDING,
    DownloadStatus.ANALYZING,
    DownloadStatus.DOWNLOADING,
    DownloadStatus.PROCESSING,
}

RUNNABLE = {
    DownloadStatus.PENDING,
    DownloadStatus.PAUSED,
    DownloadStatus.FAILED,
    DownloadStatus.PARTIALLY_COMPLETED,
}


class ApiService:
    """Application-facing facade: live jobs in memory, executed and persisted via hooks."""

    def __init__(
        self,
        downloader: DownloaderPort,
        devices: Sequence[StorageDevice] | DeviceProvider = (),
        *,
        runner: JobRunner | None = None,
        on_change: Callable[[DownloadJob], None] | None = None,
        jobs: Iterable[DownloadJob] = (),
        searcher: SearchPort | None = None,
    ) -> None:
        self.downloader = downloader
        self._searcher = searcher
        self._lock = Lock()
        self._devices = devices if callable(devices) else (lambda: tuple(devices))
        self._runner = runner
        self._on_change = on_change or (lambda job: None)
        # ponytail: one worker runs jobs sequentially; raise max_workers if parallel syncs matter.
        self._executor = ThreadPoolExecutor(max_workers=1) if runner else None
        self.analyses: dict[str, SourceAnalysis] = {}
        self.jobs: dict[str, DownloadJob] = {str(job.id): job for job in jobs}

    @property
    def devices(self) -> tuple[StorageDevice, ...]:
        return tuple(self._devices())

    def submit(self, job: DownloadJob) -> None:
        if self._executor is not None and self._runner is not None:
            self._executor.submit(self._runner, job)

    def shutdown(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)

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

    def search(self, query: str, source: str, limit: int) -> list[SearchResultResponse]:
        if self._searcher is None:
            raise ValueError("Search is not configured")
        return [
            SearchResultResponse(
                title=hit.title,
                artist=hit.artist,
                url=hit.url,
                source=hit.source,
                duration_seconds=hit.duration_seconds,
                album=hit.album,
            )
            for hit in self._searcher.search(query, source, limit)
        ]

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
        wanted = {track.id for track in tracks}
        with self._lock:
            # Same url + device + tracks already queued or running: reuse it, never enqueue twice.
            for existing in self.jobs.values():
                if (
                    existing.status in ACTIVE
                    and existing.source_url == url
                    and str(existing.destination_device_id) == device_id
                    and {item.track_id for item in existing.items} == wanted
                ):
                    return self.to_job_response(existing)
            job = DownloadJob(JobId.new(), url, StorageDeviceId(device_id))
            job.items.extend(
                DownloadItem(f"{job.id}-{index}", job.id, track.id)
                for index, track in enumerate(tracks)
            )
            self.jobs[str(job.id)] = job
        self._on_change(job)
        self.submit(job)
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
        self._on_change(job)
        return self.to_job_response(job)

    def resume_job(self, job_id: str) -> DownloadJobResponse | None:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        if self._runner is None:
            job.start()
        elif job.status not in RUNNABLE or job.status in ACTIVE:
            raise ValueError(f"Cannot resume a job in {job.status} status")
        else:
            self.submit(job)
        return self.to_job_response(job)

    def history(self) -> list[DownloadJobResponse]:
        jobs = sorted(self.jobs.values(), key=lambda job: job.created_at, reverse=True)
        return [self.to_job_response(job) for job in jobs]

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
