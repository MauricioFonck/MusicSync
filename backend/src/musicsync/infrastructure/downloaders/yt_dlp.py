from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import NAMESPACE_URL, uuid5

from musicsync.domain.entities import DownloadItem, Track
from musicsync.domain.ports import DownloaderPort, SourceAnalysis
from musicsync.domain.value_objects import Duration, Source, SourceId, TrackId

from .errors import (
    DownloaderToolError,
    InvalidSourceUrlError,
    UnknownTrackError,
)

ProgressCallback = Callable[[DownloadItem, int], None]
CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class YtDlpDownloaderAdapter(DownloaderPort):
    """Thin subprocess wrapper that exposes normalized domain objects."""

    def __init__(
        self,
        *,
        binary: str = "yt-dlp",
        runner: CommandRunner | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        self._binary = binary
        self._runner = runner or subprocess.run
        self._progress_callback = progress_callback
        self._tracks: dict[TrackId, Track] = {}
        self._cancelled_jobs: set[str] = set()

    def analyze(self, url: str) -> SourceAnalysis:
        self._validate_url(url)
        command = [
            self._binary,
            "--dump-single-json",
            "--skip-download",
            "--no-warnings",
            url,
        ]
        result = self._run(command)
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown yt-dlp error"
            raise DownloaderToolError(f"yt-dlp analysis failed: {detail}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise DownloaderToolError("yt-dlp returned invalid JSON") from exc
        tracks = self._tracks_from_payload(payload, url)
        if not tracks:
            raise DownloaderToolError("yt-dlp returned no downloadable tracks")
        self._tracks.update({track.id: track for track in tracks})
        return SourceAnalysis(source=url, tracks=tuple(tracks))

    def download(self, item: DownloadItem, destination: str) -> str:
        if str(item.job_id) in self._cancelled_jobs:
            raise DownloaderToolError(f"Download job {item.job_id} was cancelled")
        track = self._tracks.get(item.track_id)
        if track is None or not track.original_url:
            raise UnknownTrackError(f"Track {item.track_id} was not analyzed by this adapter")
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self._binary,
            "--no-warnings",
            "--no-playlist",
            "--no-part",
            "--format",
            "bestaudio/best",
            "--output",
            str(output),
            track.original_url,
        ]
        if self._progress_callback is not None:
            self._progress_callback(item, 0)
        result = self._run(command)
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown yt-dlp error"
            raise DownloaderToolError(f"yt-dlp download failed: {detail}")
        if not output.is_file() or output.stat().st_size == 0:
            raise DownloaderToolError("yt-dlp completed without producing an output file")
        if self._progress_callback is not None:
            self._progress_callback(item, 100)
        return str(output)

    def cancel(self, job_id: str) -> None:
        self._cancelled_jobs.add(job_id)

    def _run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            result = self._runner(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=3600,
            )
        except FileNotFoundError as exc:
            raise DownloaderToolError(f"Downloader tool is not available: {self._binary}") from exc
        except subprocess.TimeoutExpired as exc:
            raise DownloaderToolError("yt-dlp timed out after 3600 seconds") from exc
        except OSError as exc:
            raise DownloaderToolError(f"Could not execute downloader: {self._binary}") from exc
        return result

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InvalidSourceUrlError("Source URL must be an absolute HTTP(S) URL")

    @classmethod
    def _tracks_from_payload(cls, payload: dict[str, Any], source_url: str) -> list[Track]:
        entries = payload.get("entries") or [payload]
        source = cls._source_for_url(source_url)
        tracks: list[Track] = []
        for entry in entries:
            if not isinstance(entry, dict) or not entry.get("id") or not entry.get("title"):
                continue
            duration = entry.get("duration")
            tracks.append(
                Track(
                    # Stable per source item so re-analysis (resume, restart) matches job items.
                    id=TrackId(uuid5(NAMESPACE_URL, f"{source}:{entry['id']}")),
                    source=source,
                    source_id=SourceId(str(entry["id"])),
                    title=str(entry["title"]),
                    artist=str(entry.get("artist") or entry.get("uploader") or "Unknown artist"),
                    album=entry.get("album"),
                    album_artist=entry.get("album_artist"),
                    duration=Duration.from_seconds(duration) if duration is not None else None,
                    track_number=cls._positive_int(entry.get("track_number")),
                    disc_number=cls._positive_int(entry.get("disc_number")),
                    genre=entry.get("genre"),
                    release_date=cls._release_date(entry.get("upload_date")),
                    thumbnail_url=entry.get("thumbnail"),
                    original_url=str(
                        entry.get("webpage_url") or entry.get("original_url") or source_url
                    ),
                )
            )
        return tracks

    @staticmethod
    def _source_for_url(url: str) -> Source:
        host = (urlparse(url).hostname or "").lower()
        if host in {"youtube.com", "www.youtube.com", "youtu.be", "music.youtube.com"}:
            return Source.YOUTUBE_MUSIC if host == "music.youtube.com" else Source.YOUTUBE
        if host in {"spotify.com", "www.spotify.com", "open.spotify.com"}:
            return Source.SPOTIFY
        return Source.OTHER

    @staticmethod
    def _positive_int(value: Any) -> int | None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return None
        return parsed if parsed > 0 else None

    @staticmethod
    def _release_date(value: Any) -> date | None:
        if not value:
            return None
        try:
            return datetime.strptime(str(value)[:8], "%Y%m%d").date()
        except ValueError:
            return None
