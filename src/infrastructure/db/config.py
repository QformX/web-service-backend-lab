from __future__ import annotations

import os


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # Default to local Postgres; adjust as needed
        user = os.getenv("DB_USER", "app")
        password = os.getenv("DB_PASSWORD", "app")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "app")
        url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
    return url


