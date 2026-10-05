from __future__ import annotations

from dataclasses import dataclass

from musicsync.domain.value_objects import Checksum, DownloadStatus, JobId, MediaPath, TrackId


@dataclass(slots=True)
class DownloadItem:
    id: str
    job_id: JobId
    track_id: TrackId
    status: DownloadStatus = DownloadStatus.PENDING
    progress: int = 0
    error: str | None = None
    output_path: MediaPath | None = None
    checksum: Checksum | None = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("DownloadItem id cannot be empty")
        self._validate_progress(self.progress)

    def update_progress(self, progress: int) -> None:
        self._validate_progress(progress)
        if progress < self.progress:
            raise ValueError("Download item progress cannot move backwards")
        self.progress = progress

    def mark_completed(self, output_path: MediaPath, checksum: Checksum) -> None:
        self.output_path = output_path
        self.checksum = checksum
        self.progress = 100
        self.status = DownloadStatus.COMPLETED
        self.error = None

    def mark_failed(self, error: str) -> None:
        if not error.strip():
            raise ValueError("Failure error cannot be empty")
        self.status = DownloadStatus.FAILED
        self.error = error

    @staticmethod
    def _validate_progress(progress: int) -> None:
        if not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 and 100")
