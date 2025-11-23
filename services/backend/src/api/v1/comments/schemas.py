from __future__ import annotations

from pydantic import BaseModel


class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: int
    body: str

    class Config:
        from_attributes = True


