from __future__ import annotations

from fastapi import FastAPI, WebSocket

from musicsync.api import ApiService, create_router, download_socket
from musicsync.infrastructure.downloaders import YtDlpDownloaderAdapter


def create_app(service: ApiService | None = None) -> FastAPI:
    api_service = service or ApiService(YtDlpDownloaderAdapter())
    application = FastAPI(title="MusicSync API", version="0.1.0")
    application.state.api_service = api_service
    application.include_router(create_router(api_service), prefix="/api/v1")

    @application.get("/api/v1/health", tags=["health"])
    def health() -> dict[str, str]:
        """Return a lightweight health check for local development and CI."""
        return {"status": "ok"}

    @application.websocket("/ws/downloads/{job_id}")
    async def download_progress(websocket: WebSocket, job_id: str) -> None:
        await download_socket(websocket, api_service, job_id)

    return application


app = create_app()
