from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from musicsync.domain.entities.download_item import DownloadItem
from musicsync.domain.value_objects import DownloadStatus, JobId, StorageDeviceId


@dataclass(slots=True)
class DownloadJob:
    id: JobId
    source_url: str
    destination_device_id: StorageDeviceId
    items: list[DownloadItem] = field(default_factory=list)
    status: DownloadStatus = DownloadStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.source_url.strip():
            raise ValueError("Download job source URL cannot be empty")

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def completed_items(self) -> int:
        return sum(item.status is DownloadStatus.COMPLETED for item in self.items)

    @property
    def failed_items(self) -> int:
        return sum(item.status is DownloadStatus.FAILED for item in self.items)

    @property
    def skipped_items(self) -> int:
        return sum(item.status is DownloadStatus.CANCELLED for item in self.items)

    def start(self) -> None:
        if self.status not in {DownloadStatus.PENDING, DownloadStatus.PAUSED}:
            raise ValueError(f"Cannot start a job in {self.status} status")
        self.status = DownloadStatus.DOWNLOADING
        self.started_at = self.started_at or datetime.now(UTC)

    def pause(self) -> None:
        if self.status not in {
            DownloadStatus.ANALYZING,
            DownloadStatus.DOWNLOADING,
            DownloadStatus.PROCESSING,
        }:
            raise ValueError(f"Cannot pause a job in {self.status} status")
        self.status = DownloadStatus.PAUSED

    def cancel(self) -> None:
        if self.status in {DownloadStatus.COMPLETED, DownloadStatus.CANCELLED}:
            raise ValueError(f"Cannot cancel a job in {self.status} status")
        self.status = DownloadStatus.CANCELLED
        self.completed_at = datetime.now(UTC)

    def finish(self) -> None:
        if not self.items:
            raise ValueError("Cannot finish a job without items")
        if self.failed_items == 0 and self.completed_items == self.total_items:
            self.status = DownloadStatus.COMPLETED
        elif self.completed_items > 0:
            self.status = DownloadStatus.PARTIALLY_COMPLETED
        else:
            self.status = DownloadStatus.FAILED
        self.completed_at = datetime.now(UTC)
