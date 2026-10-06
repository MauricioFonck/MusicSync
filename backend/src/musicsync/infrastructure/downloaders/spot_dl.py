from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from musicsync.domain.entities import DownloadItem
from musicsync.domain.ports import SourceAnalysis

from .errors import DownloaderToolError, InvalidSourceUrlError, UnknownTrackError
from .yt_dlp import CommandRunner, YtDlpDownloaderAdapter

SPOTIFY_HOSTS = {"spotify.com", "www.spotify.com", "open.spotify.com"}


class SpotDlDownloaderAdapter(YtDlpDownloaderAdapter):
    """Normalize spotDL 4.x CLI output behind the shared downloader port."""

    def __init__(self, *, binary: str = "spotdl", runner: CommandRunner | None = None) -> None:
        super().__init__(binary=binary, runner=runner)

    def analyze(self, url: str) -> SourceAnalysis:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in SPOTIFY_HOSTS:
            raise InvalidSourceUrlError("spotDL requires an absolute Spotify URL")
        songs = self.save(url)
        tracks = self._tracks_from_payload(
            {"entries": [self._entry(song) for song in songs]}, url
        )
        if not tracks:
            raise DownloaderToolError("spotDL returned no tracks")
        self._tracks.update({track.id: track for track in tracks})
        return SourceAnalysis(source=url, tracks=tuple(tracks))

    def save(self, target: str) -> list[dict[str, Any]]:
        """Resolve a Spotify URL or free-text query to spotDL song records."""
        with tempfile.TemporaryDirectory(prefix="musicsync-spotdl-") as directory:
            save_file = Path(directory) / "analysis.spotdl"
            result = self._run([self._binary, "save", target, "--save-file", str(save_file)])
            if result.returncode != 0:
                detail = (result.stderr or "").strip() or "unknown spotDL error"
                raise DownloaderToolError(f"spotDL analysis failed: {detail}")
            try:
                songs = json.loads(save_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise DownloaderToolError("spotDL returned invalid song data") from exc
        if not isinstance(songs, list):
            raise DownloaderToolError("spotDL returned invalid song data")
        return [song for song in songs if isinstance(song, dict)]

    def download(self, item: DownloadItem, destination: str) -> str:
        if str(item.job_id) in self._cancelled_jobs:
            raise DownloaderToolError(f"Download job {item.job_id} was cancelled")
        track = self._tracks.get(item.track_id)
        if track is None or not track.original_url:
            raise UnknownTrackError(f"Track {item.track_id} was not analyzed by this adapter")
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        # spotDL always appends its own extension, so give it the template it expects.
        template = str(output.parent / f"{output.stem}.{{output-ext}}")
        result = self._run([self._binary, "download", track.original_url, "--output", template])
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown spotDL error"
            raise DownloaderToolError(f"spotDL download failed: {detail}")
        produced = [
            path
            for path in output.parent.iterdir()
            if path.stem == output.stem and path.is_file() and path.stat().st_size > 0
        ]
        if not produced:
            raise DownloaderToolError("spotDL completed without producing an output file")
        return str(produced[0])

    @staticmethod
    def _entry(song: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": song.get("song_id"),
            "title": song.get("name"),
            "artist": song.get("artist"),
            "album": song.get("album_name"),
            "album_artist": song.get("album_artist"),
            "duration": song.get("duration"),
            "track_number": song.get("track_number"),
            "disc_number": song.get("disc_number"),
            "genre": (song.get("genres") or [None])[0],
            "upload_date": str(song.get("date") or "").replace("-", ""),
            "thumbnail": song.get("cover_url"),
            "webpage_url": song.get("url"),
        }
