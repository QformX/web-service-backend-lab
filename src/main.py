from __future__ import annotations

from fastapi import FastAPI

from src.api.v1.users.router import router as users_router
from src.api.v1.articles.router import router as articles_router
from src.api.v1.comments.router import router as comments_router
from src.infrastructure.db.base import Base
from src.infrastructure.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="Blog API", version="1.0.0")

    app.include_router(users_router, prefix="/api")
    app.include_router(articles_router, prefix="/api")
    app.include_router(comments_router, prefix="/api")

    # Auto-create tables for local testing (SQLite default)
    Base.metadata.create_all(bind=engine)

    return app


app = create_app()


