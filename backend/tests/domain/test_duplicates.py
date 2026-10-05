from musicsync.domain.entities import Track
from musicsync.domain.services import DuplicateDetectionService, ExistingTrack
from musicsync.domain.value_objects import (
    Checksum,
    DuplicateDecision,
    Duration,
    Source,
    SourceId,
    TrackId,
)


def track() -> Track:
    return Track(
        id=TrackId.new(),
        source=Source.YOUTUBE,
        source_id=SourceId("source-1"),
        title="Song",
        artist="Artist",
        duration=Duration.from_seconds(200),
    )


def test_duplicate_by_source_id() -> None:
    existing = ExistingTrack("source-1", "song", "artist", Duration.from_seconds(200))

    assert DuplicateDetectionService().detect(track(), existing) is DuplicateDecision.DUPLICATE


def test_duplicate_by_checksum() -> None:
    checksum = Checksum("a" * 64)
    existing = ExistingTrack("other", "other", "artist", checksum=checksum)

    assert (
        DuplicateDetectionService().detect(track(), existing, checksum=checksum)
        is DuplicateDecision.DUPLICATE
    )


def test_possible_duplicate_by_metadata_and_duration() -> None:
    existing = ExistingTrack("other", "song", "artist", Duration.from_seconds(201))

    assert (
        DuplicateDetectionService().detect(track(), existing)
        is DuplicateDecision.POSSIBLE_DUPLICATE
    )


def test_unrelated_track_is_new() -> None:
    existing = ExistingTrack("other", "different", "artist", Duration.from_seconds(200))

    assert DuplicateDetectionService().detect(track(), existing) is DuplicateDecision.NEW
