from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from musicsync.domain.value_objects import MediaFormat


class Settings(BaseSettings):
    # Root .env (next to .env.example) first, then backend/.env overrides it.
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

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
    # Optional: free app keys from developer.spotify.com make Spotify search fast with many hits.
    spotify_client_id: str = ""
    spotify_client_secret: SecretStr = SecretStr("")
