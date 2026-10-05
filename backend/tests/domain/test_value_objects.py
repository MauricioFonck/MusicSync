from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from musicsync.domain.value_objects import (
    Checksum,
    Duration,
    MediaPath,
    NormalizedTitle,
    Quality,
)


def test_checksum_normalizes_valid_sha256() -> None:
    checksum = Checksum("A" * 64)

    assert checksum.value == "a" * 64


def test_checksum_rejects_invalid_digest() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        Checksum("invalid")


def test_duration_rejects_negative_values_and_compares_tolerance() -> None:
    with pytest.raises(ValueError):
        Duration.from_seconds(-1)

    assert not Duration.from_seconds(180).differs_from(Duration(Decimal("181.5")))
    assert Duration.from_seconds(180).differs_from(Duration(Decimal("183")))


def test_value_objects_are_immutable() -> None:
    title = NormalizedTitle("  My Song  ")

    assert title.value == "my song"
    with pytest.raises(FrozenInstanceError):
        title.value = "changed"  # type: ignore[misc]


def test_quality_and_path_require_valid_values() -> None:
    with pytest.raises(ValueError):
        Quality(0)
    with pytest.raises(ValueError):
        MediaPath("")
