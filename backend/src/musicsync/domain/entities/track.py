from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from musicsync.domain.value_objects import (
    Duration,
    Source,
    SourceId,
    TrackId,
)


@dataclass(slots=True)
class Track:
    id: TrackId
    source: Source
    source_id: SourceId
    title: str
    artist: str
    album: str | None = None
    album_artist: str | None = None
    duration: Duration | None = None
    track_number: int | None = None
    disc_number: int | None = None
    genre: str | None = None
    release_date: date | None = None
    thumbnail_url: str | None = None
    original_url: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Track title cannot be empty")
        if not self.artist.strip():
            raise ValueError("Track artist cannot be empty")
        if self.track_number is not None and self.track_number < 1:
            raise ValueError("Track number must be positive")
        if self.disc_number is not None and self.disc_number < 1:
            raise ValueError("Disc number must be positive")
