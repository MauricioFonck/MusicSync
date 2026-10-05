import pytest

from musicsync.domain.entities import Track
from musicsync.domain.services import (
    DownloadPolicy,
    FilenameSanitizer,
    StoragePathService,
    TrackNormalizationService,
)
from musicsync.domain.value_objects import Source, SourceId, TrackId


def make_track(**changes: object) -> Track:
    values: dict[str, object] = {
        "id": TrackId.new(),
        "source": Source.YOUTUBE,
        "source_id": SourceId("video-123"),
        "title": "Track: One?",
        "artist": "The Artist",
    }
    values.update(changes)
    return Track(**values)  # type: ignore[arg-type]


def test_track_normalization_collapses_whitespace_and_case() -> None:
    service = TrackNormalizationService()

    assert service.normalize_title("  Mi  Canción  ").value == "mi canción"
    assert service.normalize_artist(" ARTISTA ").value == "artista"


def test_filename_sanitizer_handles_windows_rules() -> None:
    sanitizer = FilenameSanitizer()

    assert sanitizer.sanitize("CON") == "_CON"
    assert sanitizer.sanitize("track:one?.mp3") == "track_one_.mp3"
    assert sanitizer.sanitize("...") == "untitled"


def test_storage_path_is_safe_and_structured() -> None:
    path = StoragePathService().build_track_path(make_track(album="Album/../Other"))

    assert str(path) == "MUSIC/The Artist/Album_.._Other/Track_ One_.mp3"
    assert ".." not in str(path).split("/")


def test_download_policy_rejects_non_http_urls_and_unauthorized_content() -> None:
    policy = DownloadPolicy()

    policy.validate_source_url("https://example.com/video")
    with pytest.raises(ValueError):
        policy.validate_source_url("file:///tmp/video")

    with pytest.raises(PermissionError):
        policy.validate_authorized_operation(False)
