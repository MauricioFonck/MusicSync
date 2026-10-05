from __future__ import annotations

from pathlib import PurePath

from musicsync.domain.entities import Track
from musicsync.domain.services.filename import FilenameSanitizer
from musicsync.domain.value_objects import MediaFormat, MediaPath


class StoragePathService:
    def __init__(self, sanitizer: FilenameSanitizer | None = None) -> None:
        self._sanitizer = sanitizer or FilenameSanitizer()

    def build_track_path(
        self, track: Track, media_format: MediaFormat = MediaFormat.MP3
    ) -> MediaPath:
        artist = self._sanitizer.sanitize(track.artist)
        album = self._sanitizer.sanitize(track.album or "Singles")
        title = self._sanitizer.sanitize(track.title)
        prefix = f"{track.track_number:02d} - " if track.track_number is not None else ""
        filename = f"{prefix}{title}.{media_format.value}"
        path = PurePath("MUSIC") / artist / album / filename
        return MediaPath(str(path))
