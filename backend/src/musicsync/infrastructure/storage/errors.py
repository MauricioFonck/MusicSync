class StorageError(Exception):
    """Base error for storage device operations."""


class StorageNotAvailableError(StorageError):
    """Raised when a selected storage device is disconnected or unavailable."""


class InsufficientSpaceError(StorageError):
    """Raised before a write when the device lacks enough free space."""
