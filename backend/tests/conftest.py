"""
LegalEase AI - pytest Configuration & Shared Fixtures
=======================================================

Test Strategy
-------------
Unit tests (tests/unit/):
    Mock the database. No real DB session needed.

Integration tests (tests/integration/):
    Use a real async SQLite database (no PostgreSQL required).
    Each test gets a fresh app instance with a clean DB state.
    Tables are truncated between tests via a teardown step.

Database URL
------------
SQLite async is used for integration tests so they run without a
live PostgreSQL instance. Set TEST_DATABASE_URL env var to use
a different database.
"""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Test database setup — SQLite in-memory file (per session)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test_legalease.db",
)

_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
)

_TestSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Session-scoped: create all tables once at the start of the test session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables():
    """
    Create all database tables once before any test runs.
    Drops them after the full session ends.
    """
    from app.database.connection import Base
    import app.models  # noqa: F401 — registers all ORM models with Base

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Clean up test database file
    await _test_engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped: clean all table rows between tests
# ---------------------------------------------------------------------------

async def _truncate_all_tables():
    """Delete all rows from all tables without dropping them."""
    table_names = [
        "activity_logs",
        "reports",
        "evidence_checklists",
        "roadmaps",
        "conversations",
        "consumer_cases",
        "users",
    ]
    async with _test_engine.begin() as conn:
        # SQLite does not support TRUNCATE — use DELETE instead
        for table in table_names:
            await conn.execute(text(f"DELETE FROM {table}"))


@pytest_asyncio.fixture(autouse=True)
async def clean_db_between_tests():
    """
    Automatically truncate all rows after every test.
    This provides test isolation without rollback complexity.
    """
    yield
    await _truncate_all_tables()


# ---------------------------------------------------------------------------
# Unit test DB session fixture (for tests that need a real DB session)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session for unit tests that need one.
    The session is properly committed and closed after each test.
    """
    async with _TestSessionLocal() as session:
        yield session
        await session.commit()


# ---------------------------------------------------------------------------
# Integration test HTTP client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def app_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTPX client for integration tests.

    Uses the real FastAPI application but overrides the database
    dependency to use the test SQLite engine instead of PostgreSQL.
    This allows integration tests to run without a live PostgreSQL server.
    """
    from app import create_app
    from app.database.connection import get_db

    test_app = create_app()

    # Override get_db to use test engine
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with _TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    test_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://testserver",
    ) as client:
        yield client

    test_app.dependency_overrides.clear()
