from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from musicsync.domain.entities import DownloadItem
from musicsync.domain.ports import SourceAnalysis

from .errors import DownloaderToolError, InvalidSourceUrlError, UnknownTrackError
from .yt_dlp import CommandRunner, YtDlpDownloaderAdapter


class SpotDlDownloaderAdapter(YtDlpDownloaderAdapter):
    """Normalize spotDL CLI output behind the shared downloader port."""

    def __init__(self, *, binary: str = "spotdl", runner: CommandRunner | None = None) -> None:
        super().__init__(binary=binary, runner=runner)

    def analyze(self, url: str) -> SourceAnalysis:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
            "spotify.com",
            "www.spotify.com",
            "open.spotify.com",
        }:
            raise InvalidSourceUrlError("spotDL requires an absolute Spotify URL")
        result = self._run([self._binary, "metadata", url, "--format", "json"])
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown spotDL error"
            raise DownloaderToolError(f"spotDL analysis failed: {detail}")
        try:
            payload: dict[str, Any] = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise DownloaderToolError("spotDL returned invalid JSON") from exc
        tracks = self._tracks_from_payload(payload, url)
        if not tracks:
            raise DownloaderToolError("spotDL returned no tracks")
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
        result = self._run(
            [self._binary, "download", track.original_url, "--output", str(output)]
        )
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown spotDL error"
            raise DownloaderToolError(f"spotDL download failed: {detail}")
        if not output.is_file() or output.stat().st_size == 0:
            raise DownloaderToolError("spotDL completed without producing an output file")
        return str(output)
