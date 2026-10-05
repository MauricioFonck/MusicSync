from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class DownloadPolicy:
    allowed_schemes: frozenset[str] = frozenset({"http", "https"})

    def validate_source_url(self, source_url: str) -> None:
        parsed = urlparse(source_url.strip())
        if parsed.scheme.lower() not in self.allowed_schemes or not parsed.netloc:
            raise ValueError("Source URL must be an absolute HTTP or HTTPS URL")

    def validate_authorized_operation(self, authorized: bool) -> None:
        if not authorized:
            raise PermissionError(
                "The operation requires content the user is authorized to download"
            )
