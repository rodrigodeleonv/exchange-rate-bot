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
def get_engine(database_url: str | None = None) -> AsyncEngine:
    """Get async database engine."""
    return create_async_engine(
        database_url or get_config().database.url,
        echo=get_config().database.echo,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Get async session maker.

    Sessionmaker gets the cached engine. It must be previously called `get_engine()`.
    """
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)


class DatabaseManager:
    """Database manager class to handle async SQLAlchemy operations."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def initialize(self) -> None:
        """Initialize async database engine and session maker."""

        if self._engine is not None:
            logger.warning("Database already initialized; skipping.")
            return

        # Create async engine and cache it
        self._engine = get_engine(get_config().database.url)

        # Create session maker and cache it
        self._session_maker = get_sessionmaker()

        logger.info("Database initialized")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """Get async database session context manager."""
        if not self._session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database engine."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
        self._session_maker = None

        # Clear cached functions
        get_sessionmaker.cache_clear()
        get_engine.cache_clear()
        logger.info("Database engine closed")


@lru_cache(maxsize=1)
def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return DatabaseManager()


@asynccontextmanager
async def get_session(database_url: str | None = None) -> AsyncGenerator[AsyncSession]:
    """Get async database session using the global manager."""
    get_db_manager().initialize()
    async with get_db_manager().get_session() as session:
        yield session


async def close_database() -> None:
    """Close database connection."""
    await get_db_manager().close()
    logger.info("Database connection closed")
