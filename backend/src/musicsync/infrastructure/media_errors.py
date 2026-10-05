from __future__ import annotations


class MediaProcessingError(RuntimeError):
    """Base error for FFmpeg and FFprobe operations."""


class MediaToolNotFoundError(MediaProcessingError):
    """Raised when FFmpeg or FFprobe is not installed or cannot be executed."""


class MediaProbeError(MediaProcessingError):
    """Raised when FFprobe cannot inspect a media file."""


class MediaValidationError(MediaProcessingError):
    """Raised when a media file is missing or has no usable audio stream."""


class MediaConversionError(MediaProcessingError):
    """Raised when FFmpeg cannot produce the requested output."""
