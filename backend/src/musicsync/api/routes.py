from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from .schemas import (
    AnalysisResponse,
    AnalyzeRequest,
    CreateDownloadRequest,
    DownloadJobResponse,
    ErrorResponse,
    SearchResultResponse,
    StorageDeviceResponse,
)
from .service import ApiService


def create_router(service: ApiService | Callable[[], ApiService]) -> APIRouter:
    """Build routes; a callable defers service construction until the first request."""
    get = service if callable(service) else lambda: service
    router = APIRouter()

    @router.post("/downloads/analyze", response_model=AnalysisResponse)
    def analyze(request: AnalyzeRequest) -> AnalysisResponse:
        try:
            return get().analyze(request.url)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorResponse(code="INVALID_URL", message=str(exc)).model_dump(),
            ) from exc

    @router.get("/search", response_model=list[SearchResultResponse])
    def search(q: str, source: str = "youtube", limit: int = 5) -> list[SearchResultResponse]:
        try:
            return get().search(q, source, limit)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorResponse(code="VALIDATION_FAILED", message=str(exc)).model_dump(),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=ErrorResponse(code="SEARCH_FAILED", message=str(exc)).model_dump(),
            ) from exc

    @router.post("/downloads", response_model=DownloadJobResponse, status_code=201)
    def create_download(request: CreateDownloadRequest) -> DownloadJobResponse:
        try:
            return get().create_job(request.url, request.destination_device_id, request.track_ids)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorResponse(code="VALIDATION_FAILED", message=str(exc)).model_dump(),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=ErrorResponse(code="DOWNLOAD_FAILED", message=str(exc)).model_dump(),
            ) from exc

    @router.get("/downloads/history", response_model=list[DownloadJobResponse])
    def history() -> list[DownloadJobResponse]:
        return get().history()

    @router.get("/downloads/{job_id}", response_model=DownloadJobResponse)
    def get_download(job_id: str) -> DownloadJobResponse:
        job = get().get_job(job_id)
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.post("/downloads/{job_id}/cancel", response_model=DownloadJobResponse)
    def cancel_download(job_id: str) -> DownloadJobResponse:
        try:
            job = get().cancel_job(job_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.post("/downloads/{job_id}/resume", response_model=DownloadJobResponse)
    def resume_download(job_id: str) -> DownloadJobResponse:
        try:
            job = get().resume_job(job_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.get("/storage/devices", response_model=list[StorageDeviceResponse])
    def storage_devices() -> list[StorageDeviceResponse]:
        return [get().to_device_response(device) for device in get().devices]

    @router.get("/storage/devices/{device_id}", response_model=StorageDeviceResponse)
    def storage_device(device_id: str) -> StorageDeviceResponse:
        for device in get().devices:
            if str(device.id) == device_id:
                return get().to_device_response(device)
        raise _not_found("STORAGE_NOT_AVAILABLE", "Storage device was not found")

    return router


def _not_found(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorResponse(code=code, message=message).model_dump(),
    )


TERMINAL_EVENTS = {
    "COMPLETED": "download.completed",
    "PARTIALLY_COMPLETED": "download.completed",
    "FAILED": "download.failed",
    "CANCELLED": "download.failed",
}


async def download_socket(
    websocket: WebSocket, service: ApiService, job_id: str, *, interval: float = 0.5
) -> None:
    await websocket.accept()
    try:
        job = service.get_job(job_id)
        if job is None:
            await websocket.send_json(
                {"event": "download.failed", "job_id": job_id, "reason": "JOB_NOT_FOUND"}
            )
            await websocket.close()
            return
        last: dict[str, Any] | None = None
        while job is not None:
            event = {
                "event": "download.progress",
                "job_id": job.id,
                "progress": _job_progress(job),
                "status": job.status,
                "job": job.model_dump(),
            }
            if event != last:
                await websocket.send_json(event)
                last = event
            if job.status in TERMINAL_EVENTS:
                await websocket.send_json(
                    {"event": TERMINAL_EVENTS[job.status], "job_id": job.id, "status": job.status}
                )
                await websocket.close()
                return
            # Waiting on receive doubles as the poll delay and notices client disconnects.
            with suppress(TimeoutError):
                await asyncio.wait_for(websocket.receive_text(), timeout=interval)
            job = service.get_job(job_id)
    except WebSocketDisconnect:
        return


def _job_progress(job: DownloadJobResponse) -> int:
    if not job.items:
        return 0
    return round(sum(item.progress for item in job.items) / len(job.items))
