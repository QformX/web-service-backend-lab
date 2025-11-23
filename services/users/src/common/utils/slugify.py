from __future__ import annotations

import re
import unicodedata


_pattern = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = _pattern.sub("-", value).strip("-")
    return value


