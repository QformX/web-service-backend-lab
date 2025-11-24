from __future__ import annotations

from fastapi import FastAPI

from src.api.v1.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Users API",
        version="1.0.0",
        description="API для управления пользователями и аутентификацией",
        docs_url="/docs",
        openapi_url="/openapi.json",
        root_path="/api/users"
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "service": "users-api"}

    app.include_router(users_router, prefix="/api")

    return app


app = create_app()
