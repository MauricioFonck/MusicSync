from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)


class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    title: str
    artist: str
    album: str | None = None
    duration_seconds: float | None = None
    release_date: date | None = None
    original_url: str | None = None


class AnalysisResponse(BaseModel):
    source: str
    tracks: list[TrackResponse]


class SearchResultResponse(BaseModel):
    title: str
    artist: str
    url: str
    source: str
    duration_seconds: float | None = None
    album: str | None = None
    thumbnail_url: str | None = None


class CreateDownloadRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    destination_device_id: str = Field(min_length=1, max_length=255)
    track_ids: list[str] | None = None


class DownloadItemResponse(BaseModel):
    id: str
    track_id: str
    status: str
    progress: int
    error: str | None = None
    output_path: str | None = None


class DownloadJobResponse(BaseModel):
    id: str
    source_url: str
    destination_device_id: str
    status: str
    total_items: int
    completed_items: int
    failed_items: int
    items: list[DownloadItemResponse]


class StorageDeviceResponse(BaseModel):
    id: str
    volume_label: str
    mount_point: str
    filesystem: str
    total_space: int
    free_space: int
    is_available: bool
