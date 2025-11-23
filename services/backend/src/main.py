from __future__ import annotations

from fastapi import FastAPI

from src.api.v1.articles.router import router as articles_router
from src.api.v1.comments.router import router as comments_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blog Backend API",
        version="1.0.0",
        description="API для статей и комментариев (без пользователей)",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": "backend-api"}

    app.include_router(articles_router, prefix="/api")
    app.include_router(comments_router, prefix="/api")

    return app


app = create_app()
