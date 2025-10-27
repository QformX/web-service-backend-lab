from __future__ import annotations
import os


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Provide a PostgreSQL URL, e.g. "
            "postgresql+psycopg://user:password@host:5432/dbname"
        )
    return url


