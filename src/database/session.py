"""Database session management for async SQLAlchemy."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_config

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Get cached async database engine."""
    return create_async_engine(
        get_config().database.url,
        echo=get_config().database.echo,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Get cached async session maker."""
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    """Get async database session context manager.

    Automatically handles commit/rollback and session lifecycle.
    """
    session_maker = get_sessionmaker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_database() -> None:
    """Close database engine and clear caches."""
    engine = get_engine()
    await engine.dispose()
    get_sessionmaker.cache_clear()
    get_engine.cache_clear()
    logger.info("Database connection closed")
