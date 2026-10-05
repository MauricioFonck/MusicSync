from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from musicsync.domain.value_objects import Duration, MediaFormat, MediaPath, Quality


@dataclass(frozen=True, slots=True)
class MediaInspection:
    duration: Duration
    bitrate_kbps: int | None
    checksum: str | None


@dataclass(frozen=True, slots=True)
class ProcessingOptions:
    media_format: MediaFormat
    quality: Quality


class MediaProcessorPort(Protocol):
    def process(
        self,
        source: MediaPath,
        destination: MediaPath,
        options: ProcessingOptions,
    ) -> MediaPath: ...

    def inspect(self, path: MediaPath) -> MediaInspection: ...

    def validate(self, path: MediaPath) -> bool: ...
