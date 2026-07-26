"""
LegalEase AI - Database Connection & Session Management
=======================================================
Provides async SQLAlchemy engine and session factory.
Uses asyncpg driver for async PostgreSQL operations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings

# ---- Engine ----------------------------------------------------------------
# Convert postgresql:// to postgresql+asyncpg:// for async driver
_async_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace(
    "postgres://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    _async_url,
    echo=settings.database_echo,
    pool_pre_ping=True,       # Detect stale connections before use
    pool_size=10,
    max_overflow=20,
)

# ---- Session Factory -------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Keep attributes accessible after commit
    autocommit=False,
    autoflush=False,
)


# ---- Declarative Base ------------------------------------------------------
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    All models must inherit from this class.
    """
    pass


# ---- Dependency ------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.
    Automatically commits on success and rolls back on failure.
    Always closes the session on exit.

    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---- Context Manager (for non-dependency use) --------------------------------
@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    Use this in scripts or background tasks (not FastAPI routes).

    Usage:
        async with get_db_context() as db:
            result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---- Health Check -----------------------------------------------------------
async def check_database_connection() -> bool:
    """
    Verify that the database is reachable.
    Used in the health check endpoint.
    Returns True if connected, False otherwise.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
