from __future__ import annotations


class DownloadError(RuntimeError):
    """Base error for source analysis and downloads."""


class InvalidSourceUrlError(DownloadError):
    """Raised when a source URL is not an allowed HTTP(S) URL."""


class DownloaderToolError(DownloadError):
    """Raised when the external downloader is unavailable or fails."""


class UnknownTrackError(DownloadError):
    """Raised when an item was not produced by the adapter analysis."""
