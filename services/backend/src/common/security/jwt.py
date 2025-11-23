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


def create_access_token(subject: str, expires_minutes: int | None = None, extra: Dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire_delta = timedelta(minutes=expires_minutes or int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MIN", "30")))
    payload: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + expire_delta).timestamp())}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, _get_secret(), algorithm=_get_algorithm())
    return token


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, _get_secret(), algorithms=[_get_algorithm()])


