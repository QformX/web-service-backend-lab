from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET", "change_me")
    return secret


def _get_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, _get_secret(), algorithms=[_get_algorithm()])


