from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from musicsync import mcp_server
from musicsync.api import ApiService
from musicsync.domain.entities import Track
from musicsync.domain.ports import SearchHit, SourceAnalysis
from musicsync.domain.value_objects import Source, SourceId, TrackId
from musicsync.infrastructure.downloaders import MusicSearch
from musicsync.main import create_app

URL = "https://example.com/list"


class FakeDownloader:
    def __init__(self) -> None:
        self.track = Track(TrackId.new(), Source.OTHER, SourceId("s-1"), "Song", "Artist")

    def analyze(self, url: str) -> SourceAnalysis:
        return SourceAnalysis(url, (self.track,))

    def download(self, item: object, destination: str) -> str:
        return destination

    def cancel(self, job_id: str) -> None:
        del job_id


class FakeSearcher:
    def search(self, query: str, source: str, limit: int) -> list[SearchHit]:
        if source == "bad":
            raise ValueError("Search source must be 'youtube' or 'spotify'")
        return [SearchHit(query, "Someone", "https://youtu.be/x", source)][:limit]


def test_same_active_job_is_returned_instead_of_queued_twice() -> None:
    queued: list[object] = []
    service = ApiService(FakeDownloader(), runner=queued.append)

    first = service.create_job(URL, "usb-1", None)
    second = service.create_job(URL, "usb-1", None)

    assert first.id == second.id
    assert len(service.jobs) == 1
    assert service.create_job(URL, "usb-2", None).id != first.id
    service.shutdown()


def test_search_endpoint_returns_hits_and_validates_source() -> None:
    api = TestClient(create_app(ApiService(FakeDownloader(), searcher=FakeSearcher())))

    hits = api.get("/api/v1/search", params={"q": "Artist - Song", "source": "spotify"})
    assert hits.json()[0]["url"] == "https://youtu.be/x"
    assert api.get("/api/v1/search", params={"q": "x", "source": "bad"}).status_code == 422


def test_music_search_parses_youtube_and_spotify_cli_output() -> None:
    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        if command[0] == "yt-dlp":
            assert command[-1] == "ytsearch2:daft punk"
            entries = [{"id": "abc", "title": "One More Time", "channel": "Daft Punk"}]
            return subprocess.CompletedProcess(command, 0, json.dumps({"entries": entries}), "")
        song = {"name": "Song", "artist": "Artist", "url": "https://open.spotify.com/track/1"}
        Path(command[command.index("--save-file") + 1]).write_text(json.dumps([song]))
        return subprocess.CompletedProcess(command, 0, "", "")

    search = MusicSearch(runner=runner)

    youtube = search.search("daft punk", "youtube", 2)
    assert youtube[0].url == "https://www.youtube.com/watch?v=abc"
    assert search.search("Artist - Song", "spotify", 5)[0].source == "spotify"
    with pytest.raises(ValueError):
        search.search("x", "other", 1)


def test_mcp_lists_tools_and_forwards_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, Any]] = []

    def fake_api(method: str, path: str, body: Any = None, timeout: int = 300) -> Any:
        calls.append((method, path, body))
        if path == "/storage/devices":
            return [{"id": "dev-1", "volume_label": "USB", "mount_point": "E:\\"}]
        if path.startswith("/search"):
            return [{"url": "https://youtu.be/x", "title": "T"}]
        return {"id": "job-1", "status": "PENDING"}

    monkeypatch.setattr(mcp_server, "call_api", fake_api)

    listed = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert listed is not None
    names = {tool["name"] for tool in listed["result"]["tools"]}
    assert {"search_music", "queue_songs", "start_sync", "job_status"} <= names
    assert mcp_server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None

    reply = mcp_server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "queue_songs", "arguments": {"queries": ["A - B"]}},
        }
    )
    assert reply is not None and "isError" not in reply["result"]
    started = json.loads(reply["result"]["content"][0]["text"])[0]
    assert started["job_id"] == "job-1"
    assert (
        "POST",
        "/downloads",
        {"url": "https://youtu.be/x", "destination_device_id": "dev-1", "track_ids": None},
    ) in calls


def test_mcp_reports_unknown_tool_as_error() -> None:
    reply = mcp_server.handle(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "nope"}}
    )
    assert reply is not None and reply["result"]["isError"] is True
