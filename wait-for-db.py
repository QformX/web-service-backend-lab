#!/usr/bin/env python3
"""Wait for database to be ready before starting the application."""

import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from src.infrastructure.db.config import get_database_url


def wait_for_db(max_retries: int = 30, delay: int = 2) -> bool:
    """Wait for database to be ready.
    
    Args:
        max_retries: Maximum number of connection attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if database is ready, False otherwise
    """
    database_url = get_database_url()
    print(f"Waiting for database at {database_url}...")
    
    engine = create_engine(database_url)
    
    for attempt in range(1, max_retries + 1):
        try:
            # Try to connect to the database
            with engine.connect() as conn:
                print(f"✓ Database is ready! (attempt {attempt}/{max_retries})")
                return True
        except OperationalError as e:
            print(f"✗ Database not ready (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                print(f"✗ Failed to connect to database after {max_retries} attempts")
                return False
    
    return False


if __name__ == "__main__":
    success = wait_for_db()
    sys.exit(0 if success else 1)

