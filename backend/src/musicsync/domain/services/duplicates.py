from __future__ import annotations

from dataclasses import dataclass

from musicsync.domain.entities import Track
from musicsync.domain.value_objects import Checksum, DuplicateDecision, Duration


@dataclass(frozen=True, slots=True)
class ExistingTrack:
    source_id: str
    normalized_title: str
    normalized_artist: str
    duration: Duration | None = None
    checksum: Checksum | None = None


class DuplicateDetectionService:
    def detect(
        self,
        track: Track,
        existing: ExistingTrack | None,
        *,
        checksum: Checksum | None = None,
    ) -> DuplicateDecision:
        if existing is None:
            return DuplicateDecision.NEW
        if existing.source_id == track.source_id.value:
            return DuplicateDecision.DUPLICATE
        if checksum is not None and existing.checksum == checksum:
            return DuplicateDecision.DUPLICATE

        same_metadata = (
            existing.normalized_title == " ".join(track.title.split()).casefold()
            and existing.normalized_artist == " ".join(track.artist.split()).casefold()
        )
        if same_metadata and self._durations_match(track.duration, existing.duration):
            return DuplicateDecision.POSSIBLE_DUPLICATE
        return DuplicateDecision.NEW

    @staticmethod
    def _durations_match(left: Duration | None, right: Duration | None) -> bool:
        if left is None or right is None:
            return False
        return not left.differs_from(right)
