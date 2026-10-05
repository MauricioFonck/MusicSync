from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from pathlib import PurePath


@dataclass(frozen=True, slots=True)
class NormalizedTitle:
    value: str

    def __post_init__(self) -> None:
        value = " ".join(self.value.split()).casefold()
        if not value:
            raise ValueError("NormalizedTitle cannot be empty")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedArtist:
    value: str

    def __post_init__(self) -> None:
        value = " ".join(self.value.split()).casefold()
        if not value:
            raise ValueError("NormalizedArtist cannot be empty")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Duration:
    seconds: Decimal

    def __post_init__(self) -> None:
        value = Decimal(str(self.seconds))
        if value < 0:
            raise ValueError("Duration cannot be negative")
        object.__setattr__(self, "seconds", value)

    @classmethod
    def from_seconds(cls, seconds: int | float | Decimal) -> Duration:
        return cls(Decimal(str(seconds)))

    def differs_from(self, other: Duration, tolerance_seconds: Decimal = Decimal("2")) -> bool:
        return abs(self.seconds - other.seconds) > tolerance_seconds


@dataclass(frozen=True, slots=True)
class MediaPath:
    value: str

    def __post_init__(self) -> None:
        value = self.value.strip()
        if not value or PurePath(value).name in {"", ".", ".."}:
            raise ValueError("MediaPath must contain a valid path")
        object.__setattr__(self, "value", value)

    def __str__(self) -> str:
        return self.value


class MediaFormat(StrEnum):
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"


@dataclass(frozen=True, slots=True)
class Quality:
    bitrate_kbps: int

    def __post_init__(self) -> None:
        if self.bitrate_kbps <= 0:
            raise ValueError("Quality bitrate must be positive")
