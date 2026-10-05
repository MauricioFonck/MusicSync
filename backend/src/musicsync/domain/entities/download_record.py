from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from musicsync.domain.value_objects import DownloadStatus, JobId, TrackId


@dataclass(frozen=True, slots=True)
class DownloadRecord:
    id: str
    job_id: JobId
    track_id: TrackId
    status: DownloadStatus
    message: str | None = None
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("DownloadRecord id cannot be empty")
