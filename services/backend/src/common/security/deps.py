from __future__ import annotations

from typing import Optional
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.common.security.jwt import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class User:
    """
    DTO for User extracted from JWT token.
    This is NOT a database model.
    """
    id: int
    email: str
    username: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    subject = payload.get("sub")
    user_id = payload.get("id")
    username = payload.get("username")

    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload: missing sub")
    
    # If ID is missing (legacy tokens), we can't proceed for Backend operations requiring ID
    if user_id is None:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload: missing id")

    return User(id=int(user_id), email=subject, username=username)
