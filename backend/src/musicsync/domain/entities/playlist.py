from __future__ import annotations

from dataclasses import dataclass, field

from musicsync.domain.entities.track import Track
from musicsync.domain.value_objects import Source, SourceId


@dataclass(slots=True)
class Playlist:
    id: str
    source: Source
    source_id: SourceId
    title: str
    original_url: str
    owner: str | None = None
    items: list[Track] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Playlist id cannot be empty")
        if not self.title.strip():
            raise ValueError("Playlist title cannot be empty")
        if not self.original_url.strip():
            raise ValueError("Playlist original URL cannot be empty")
