from __future__ import annotations

import re


class FilenameSanitizer:
    _INVALID_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    _RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    def sanitize(self, value: str, fallback: str = "untitled") -> str:
        sanitized = self._INVALID_CHARACTERS.sub("_", value).strip().rstrip(".")
        sanitized = re.sub(r"\s+", " ", sanitized)
        if not sanitized:
            sanitized = fallback
        if sanitized.upper().split(".", 1)[0] in self._RESERVED_NAMES:
            sanitized = f"_{sanitized}"
        return sanitized
