from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.infrastructure.db.config import get_database_url


database_url: str = get_database_url()
async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(async_database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)


@asynccontextmanager
async def get_async_session() -> AsyncIterator[AsyncSession]:
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


