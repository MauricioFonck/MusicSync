class FilesystemError(Exception):
    """Base error for safe filesystem operations."""


class PathSecurityError(FilesystemError, ValueError):
    """Raised when a path is absolute, traverses a root, or uses a symlink."""


class DestinationExistsError(FilesystemError, FileExistsError):
    """Raised instead of silently creating duplicate filename variants."""
