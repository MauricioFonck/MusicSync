from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from musicsync.domain.entities import DownloadItem
from musicsync.domain.value_objects import JobId, Source
from musicsync.infrastructure.downloaders import (
    DownloaderToolError,
    InvalidSourceUrlError,
    SourceResolver,
    YtDlpDownloaderAdapter,
)


def test_analyze_normalizes_single_track_metadata() -> None:
    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        assert command[-1] == "https://www.youtube.com/watch?v=abc"
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "id": "abc",
                    "title": "Song",
                    "uploader": "Artist",
                    "duration": 123.5,
                    "upload_date": "20240131",
                    "webpage_url": "https://www.youtube.com/watch?v=abc",
                }
            ),
            "",
        )

    analysis = YtDlpDownloaderAdapter(runner=runner).analyze("https://www.youtube.com/watch?v=abc")

    assert len(analysis.tracks) == 1
    track = analysis.tracks[0]
    assert track.source is Source.YOUTUBE
    assert str(track.source_id) == "abc"
    assert track.artist == "Artist"
    assert track.release_date is not None
    assert track.release_date.isoformat() == "2024-01-31"


def test_download_uses_analyzed_track_and_reports_progress(tmp_path: Path) -> None:
    commands: list[list[str]] = []
    progress: list[int] = []
    output = tmp_path / "song.mp3"

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if "--output" in command:
            Path(command[command.index("--output") + 1]).write_bytes(b"audio")
            return subprocess.CompletedProcess(command, 0, "", "")
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps({"id": "abc", "title": "Song", "uploader": "Artist"}),
            "",
        )

    adapter = YtDlpDownloaderAdapter(
        runner=runner,
        progress_callback=lambda _item, value: progress.append(value),
    )
    track = adapter.analyze("https://youtu.be/abc").tracks[0]
    item = DownloadItem("item-1", JobId.new(), track.id)

    result = adapter.download(item, str(output))

    assert result == str(output)
    assert output.read_bytes() == b"audio"
    assert progress == [0, 100]
    assert commands[0][-1] == "https://youtu.be/abc"


def test_invalid_urls_and_failed_downloads_are_controlled(tmp_path: Path) -> None:
    with pytest.raises(InvalidSourceUrlError):
        YtDlpDownloaderAdapter().analyze("file:///tmp/audio")

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "network failure")

    adapter = YtDlpDownloaderAdapter(runner=runner)
    with pytest.raises(DownloaderToolError, match="network failure"):
        adapter.analyze("https://example.com/audio")


def test_source_resolver_prefers_spotify_and_falls_back_to_other() -> None:
    youtube = object()
    spotify = object()
    other = object()
    resolver = SourceResolver(
        {Source.YOUTUBE: youtube, Source.SPOTIFY: spotify, Source.OTHER: other}  # type: ignore[dict-item]
    )

    assert resolver.resolve("https://open.spotify.com/track/1") is spotify
    assert resolver.resolve("https://example.com/audio") is other
