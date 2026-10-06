from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from musicsync.api import ApiService, create_router, download_socket
from musicsync.application import SyncPipeline
from musicsync.config import Settings
from musicsync.domain.entities import DownloadJob, MediaFile, StorageDevice, Track
from musicsync.domain.ports import ProcessingOptions
from musicsync.domain.value_objects import DownloadStatus, Quality, Source
from musicsync.infrastructure import FfmpegMediaProcessor
from musicsync.infrastructure.database import (
    SqlAlchemyDownloadJobRepository,
    SqlAlchemyMediaFileRepository,
    SqlAlchemyTrackRepository,
)
from musicsync.infrastructure.database.session import (
    create_database_engine,
    create_schema,
    create_session_factory,
)
from musicsync.infrastructure.downloaders import (
    ResolvingDownloader,
    SourceResolver,
    SpotDlDownloaderAdapter,
    YtDlpDownloaderAdapter,
)
from musicsync.infrastructure.filesystem import LocalFilesystemService
from musicsync.infrastructure.storage import LocalStorageDeviceAdapter, StorageMonitor

INTERRUPTED = {DownloadStatus.ANALYZING, DownloadStatus.DOWNLOADING, DownloadStatus.PROCESSING}


def build_service(settings: Settings) -> ApiService:
    """Compose the real adapters: SQLite, USB discovery, yt-dlp/spotDL and FFmpeg."""
    if settings.database_url.startswith("sqlite:///"):
        Path(settings.database_url.removeprefix("sqlite:///")).parent.mkdir(
            parents=True, exist_ok=True
        )
    engine = create_database_engine(settings.database_url)
    create_schema(engine)
    sessions = create_session_factory(engine)

    yt_dlp = YtDlpDownloaderAdapter(binary=settings.yt_dlp_binary)
    spotdl = SpotDlDownloaderAdapter(binary=settings.spotdl_binary)
    downloader = ResolvingDownloader(
        SourceResolver({Source.SPOTIFY: spotdl, Source.OTHER: yt_dlp}), (yt_dlp, spotdl)
    )
    monitor = StorageMonitor(
        LocalStorageDeviceAdapter(mount_points=settings.storage_mount_points or None)
    )

    def devices() -> tuple[StorageDevice, ...]:
        monitor.refresh()
        return tuple(device for device in monitor.list_devices() if device.is_available)

    def save(job: DownloadJob) -> None:
        with sessions() as session:
            SqlAlchemyDownloadJobRepository(session).save(job)

    def record(track: Track, media_file: MediaFile) -> None:
        with sessions() as session:
            SqlAlchemyTrackRepository(session).save(track)
            SqlAlchemyMediaFileRepository(session).save(media_file)

    pipeline = SyncPipeline(
        downloader,
        FfmpegMediaProcessor(
            ffmpeg_binary=settings.ffmpeg_binary, ffprobe_binary=settings.ffprobe_binary
        ),
        LocalFilesystemService,
        ProcessingOptions(settings.default_format, Quality(settings.default_quality)),
        on_change=save,
        record=record,
    )

    def run(job: DownloadJob) -> None:
        device = next((d for d in devices() if d.id == job.destination_device_id), None)
        pipeline.run(job, device)

    with sessions() as session:
        jobs = SqlAlchemyDownloadJobRepository(session).list_all()
    for job in jobs:
        if job.status in INTERRUPTED:  # the process died mid-job: make it resumable
            job.pause()
            save(job)
    service = ApiService(downloader, devices, runner=run, on_change=save, jobs=jobs)
    for job in jobs:
        if job.status is DownloadStatus.PENDING:
            service.submit(job)
    return service


def create_app(service: ApiService | None = None, settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    state: dict[str, ApiService] = {}
    if service is not None:
        state["service"] = service

    def current() -> ApiService:
        if "service" not in state:
            state["service"] = build_service(settings)
        return state["service"]

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        current()
        yield
        state["service"].shutdown()

    application = FastAPI(title="MusicSync API", version="0.1.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(create_router(current), prefix="/api/v1")

    @application.get("/api/v1/health", tags=["health"])
    def health() -> dict[str, str]:
        """Return a lightweight health check for local development and CI."""
        return {"status": "ok"}

    @application.websocket("/ws/downloads/{job_id}")
    async def download_progress(websocket: WebSocket, job_id: str) -> None:
        await download_socket(websocket, current(), job_id)

    return application


app = create_app()
