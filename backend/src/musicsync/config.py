from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from musicsync.domain.value_objects import MediaFormat


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./data/musicsync.db"
    default_format: MediaFormat = MediaFormat.MP3
    default_quality: int = Field(default=192, ge=32, le=320)
    # Explicit mount points (comma-separated env var); empty means auto-discovery.
    storage_mount_points: list[Path] = Field(default_factory=list)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:4200"])
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    yt_dlp_binary: str = "yt-dlp"
    spotdl_binary: str = "spotdl"
