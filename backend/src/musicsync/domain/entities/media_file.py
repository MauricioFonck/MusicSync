from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from musicsync.domain.value_objects import Checksum, Duration, MediaPath, TrackId


@dataclass(frozen=True, slots=True)
class MediaFile:
    id: str
    track_id: TrackId
    path: MediaPath
    filename: str
    extension: str
    size: int
    duration: Duration
    bitrate: int | None
    checksum: Checksum
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("MediaFile id cannot be empty")
        if not self.filename.strip():
            raise ValueError("MediaFile filename cannot be empty")
        if not self.extension.strip():
            raise ValueError("MediaFile extension cannot be empty")
        if self.size < 0:
            raise ValueError("MediaFile size cannot be negative")
        if self.bitrate is not None and self.bitrate <= 0:
            raise ValueError("MediaFile bitrate must be positive")
