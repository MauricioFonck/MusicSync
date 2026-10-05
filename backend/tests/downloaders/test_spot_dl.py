from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from musicsync.domain.entities import DownloadItem
from musicsync.domain.value_objects import JobId
from musicsync.infrastructure.downloaders import InvalidSourceUrlError, SpotDlDownloaderAdapter


def test_spotdl_analyzes_spotify_metadata_without_leaking_cli_objects() -> None:
    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        assert command[:2] == ["spotdl", "metadata"]
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps({"id": "spotify-1", "title": "Song", "artist": "Artist"}),
            "",
        )

    analysis = SpotDlDownloaderAdapter(runner=runner).analyze(
        "https://open.spotify.com/track/1"
    )

    assert len(analysis.tracks) == 1
    assert analysis.tracks[0].artist == "Artist"
    assert analysis.tracks[0].source.value == "SPOTIFY"


def test_spotdl_rejects_non_spotify_urls() -> None:
    with pytest.raises(InvalidSourceUrlError):
        SpotDlDownloaderAdapter().analyze("https://www.youtube.com/watch?v=1")


def test_spotdl_download_uses_safe_argument_list(tmp_path: Path) -> None:
    output = tmp_path / "track [safe].mp3"
    commands: list[list[str]] = []

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if command[1] == "metadata":
            return subprocess.CompletedProcess(
                command,
                0,
                json.dumps({"id": "spotify-1", "title": "Song", "artist": "Artist"}),
                "",
            )
        Path(command[command.index("--output") + 1]).write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    adapter = SpotDlDownloaderAdapter(runner=runner)
    track = adapter.analyze("https://open.spotify.com/track/1").tracks[0]
    item = DownloadItem("item-1", JobId.new(), track.id)

    assert adapter.download(item, str(output)) == str(output)
    assert commands[-1][-1] == str(output)
