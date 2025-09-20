from __future__ import annotations

import os


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # Default to local SQLite for easy local testing
        url = "sqlite:///./app.db"
    return url


