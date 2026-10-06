from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from musicsync.domain.entities import DownloadItem
from musicsync.domain.value_objects import JobId
from musicsync.infrastructure.downloaders import InvalidSourceUrlError, SpotDlDownloaderAdapter

SONG = {
    "song_id": "spotify-1",
    "name": "Song",
    "artist": "Artist",
    "album_name": "Album",
    "duration": 180,
    "track_number": 2,
    "date": "2020-05-01",
    "url": "https://open.spotify.com/track/1",
}


def fake_runner(commands: list[list[str]]) -> Any:
    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        if command[1] == "save":
            Path(command[command.index("--save-file") + 1]).write_text(json.dumps([SONG]))
        else:
            template = command[command.index("--output") + 1]
            Path(template.replace("{output-ext}", "mp3")).write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 0, "", "")

    return runner


def test_spotdl_analyzes_spotify_metadata_without_leaking_cli_objects() -> None:
    commands: list[list[str]] = []
    analysis = SpotDlDownloaderAdapter(runner=fake_runner(commands)).analyze(
        "https://open.spotify.com/track/1"
    )

    assert commands[0][:2] == ["spotdl", "save"]
    track = analysis.tracks[0]
    assert (track.artist, track.album, track.track_number) == ("Artist", "Album", 2)
    assert track.source.value == "SPOTIFY"
    assert track.release_date is not None and track.release_date.year == 2020


def test_spotdl_rejects_non_spotify_urls() -> None:
    with pytest.raises(InvalidSourceUrlError):
        SpotDlDownloaderAdapter().analyze("https://www.youtube.com/watch?v=1")


def test_spotdl_download_uses_safe_argument_list(tmp_path: Path) -> None:
    commands: list[list[str]] = []
    adapter = SpotDlDownloaderAdapter(runner=fake_runner(commands))
    track = adapter.analyze("https://open.spotify.com/track/1").tracks[0]
    item = DownloadItem("item-1", JobId.new(), track.id)

    produced = adapter.download(item, str(tmp_path / "track [safe].source"))

    assert produced == str(tmp_path / "track [safe].mp3")
    assert commands[-1][:3] == ["spotdl", "download", SONG["url"]]
