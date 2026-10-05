from __future__ import annotations

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from .schemas import (
    AnalysisResponse,
    AnalyzeRequest,
    CreateDownloadRequest,
    DownloadJobResponse,
    ErrorResponse,
    StorageDeviceResponse,
)
from .service import ApiService


def create_router(service: ApiService) -> APIRouter:
    router = APIRouter()

    @router.post("/downloads/analyze", response_model=AnalysisResponse)
    def analyze(request: AnalyzeRequest) -> AnalysisResponse:
        try:
            return service.analyze(request.url)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorResponse(code="INVALID_URL", message=str(exc)).model_dump(),
            ) from exc

    @router.post("/downloads", response_model=DownloadJobResponse, status_code=201)
    def create_download(request: CreateDownloadRequest) -> DownloadJobResponse:
        try:
            return service.create_job(request.url, request.destination_device_id, request.track_ids)
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
        return service.history()

    @router.get("/downloads/{job_id}", response_model=DownloadJobResponse)
    def get_download(job_id: str) -> DownloadJobResponse:
        job = service.get_job(job_id)
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.post("/downloads/{job_id}/cancel", response_model=DownloadJobResponse)
    def cancel_download(job_id: str) -> DownloadJobResponse:
        try:
            job = service.cancel_job(job_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.post("/downloads/{job_id}/resume", response_model=DownloadJobResponse)
    def resume_download(job_id: str) -> DownloadJobResponse:
        try:
            job = service.resume_job(job_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        if job is None:
            raise _not_found("JOB_NOT_FOUND", "Download job was not found")
        return job

    @router.get("/storage/devices", response_model=list[StorageDeviceResponse])
    def storage_devices() -> list[StorageDeviceResponse]:
        return [service.to_device_response(device) for device in service.devices]

    @router.get("/storage/devices/{device_id}", response_model=StorageDeviceResponse)
    def storage_device(device_id: str) -> StorageDeviceResponse:
        for device in service.devices:
            if str(device.id) == device_id:
                return service.to_device_response(device)
        raise _not_found("STORAGE_NOT_AVAILABLE", "Storage device was not found")

    return router


def _not_found(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=ErrorResponse(code=code, message=message).model_dump(),
    )


async def download_socket(websocket: WebSocket, service: ApiService, job_id: str) -> None:
    await websocket.accept()
    try:
        job = service.get_job(job_id)
        if job is None:
            await websocket.send_json(
                {"event": "download.failed", "job_id": job_id, "reason": "JOB_NOT_FOUND"}
            )
            return
        await websocket.send_json(
            {
                "event": "download.progress",
                "job_id": job.id,
                "progress": _job_progress(job),
                "status": job.status,
            }
        )
        await websocket.receive_text()
    except WebSocketDisconnect:
        return


def _job_progress(job: DownloadJobResponse) -> int:
    if not job.items:
        return 0
    return round(sum(item.progress for item in job.items) / len(job.items))
