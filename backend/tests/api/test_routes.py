from __future__ import annotations

from fastapi.testclient import TestClient

from musicsync.api import ApiService
from musicsync.domain.entities import Track
from musicsync.domain.ports import SourceAnalysis
from musicsync.domain.value_objects import Duration, Source, SourceId, TrackId
from musicsync.main import create_app


class FakeDownloader:
    def __init__(self) -> None:
        self.track = Track(
            TrackId.new(),
            Source.OTHER,
            SourceId("source-1"),
            "Song",
            "Artist",
            duration=Duration.from_seconds(120),
            original_url="https://example.com/song",
        )

    def analyze(self, url: str) -> SourceAnalysis:
        return SourceAnalysis(url, (self.track,))

    def download(self, item: object, destination: str) -> str:
        del item
        return destination

    def cancel(self, job_id: str) -> None:
        del job_id


def client() -> TestClient:
    downloader = FakeDownloader()
    return TestClient(create_app(ApiService(downloader)))


def test_health_analysis_and_job_endpoints_return_dtos() -> None:
    api = client()

    assert api.get("/api/v1/health").json() == {"status": "ok"}
    analysis = api.post("/api/v1/downloads/analyze", json={"url": "https://example.com/list"})
    assert analysis.status_code == 200
    track = analysis.json()["tracks"][0]

    created = api.post(
        "/api/v1/downloads",
        json={
            "url": "https://example.com/list",
            "destination_device_id": "usb-1",
            "track_ids": [track["id"]],
        },
    )
    assert created.status_code == 201
    job_id = created.json()["id"]
    assert api.get(f"/api/v1/downloads/{job_id}").json()["total_items"] == 1
    assert api.post(f"/api/v1/downloads/{job_id}/cancel").json()["status"] == "CANCELLED"


def test_missing_job_uses_documented_error_shape() -> None:
    response = client().get("/api/v1/downloads/missing")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "JOB_NOT_FOUND"


def test_websocket_returns_progress_event_for_known_job() -> None:
    api = client()
    analysis = api.post("/api/v1/downloads/analyze", json={"url": "https://example.com/list"}).json()
    created = api.post(
        "/api/v1/downloads",
        json={
            "url": "https://example.com/list",
            "destination_device_id": "usb-1",
            "track_ids": [analysis["tracks"][0]["id"]],
        },
    ).json()

    with api.websocket_connect(f"/ws/downloads/{created['id']}") as websocket:
        event = websocket.receive_json()

    assert event["event"] == "download.progress"
    assert event["job_id"] == created["id"]
