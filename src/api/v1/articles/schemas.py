from __future__ import annotations

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    title: str
    description: str
    body: str
    tagList: list[str] | None = Field(default=None)


class ArticleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    body: str | None = None
    tagList: list[str] | None = None


class ArticleOut(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tagList: list[str] = []

    class Config:
        from_attributes = True


