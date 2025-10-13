#!/usr/bin/env python3

import os
import sys
import time
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError

from src.infrastructure.db.config import get_database_url


async def wait_for_db(max_retries: int = 30, delay: int = 2) -> bool:
    database_url = get_database_url()
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    print(f"Waiting for database at {database_url}...")
    
    engine = create_async_engine(async_database_url)
    
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                print(f"✓ Database is ready! (attempt {attempt}/{max_retries})")
                return True
        except OperationalError as e:
            print(f"✗ Database not ready (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
            else:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                return False
    
    return False


if __name__ == "__main__":
    success = asyncio.run(wait_for_db())
    sys.exit(0 if success else 1)

