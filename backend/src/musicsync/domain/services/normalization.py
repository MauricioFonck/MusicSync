from __future__ import annotations

import re
import unicodedata

from musicsync.domain.value_objects import NormalizedArtist, NormalizedTitle


class TrackNormalizationService:
    """Normalize searchable metadata without changing the original track fields."""

    def normalize_title(self, title: str) -> NormalizedTitle:
        return NormalizedTitle(self._normalize(title))

    def normalize_artist(self, artist: str) -> NormalizedArtist:
        return NormalizedArtist(self._normalize(artist))

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized
