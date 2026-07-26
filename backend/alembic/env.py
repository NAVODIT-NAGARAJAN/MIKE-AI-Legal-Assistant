"""
LegalEase AI - Alembic Migration Environment
=============================================
Configured for async SQLAlchemy with asyncpg PostgreSQL driver.
Reads DATABASE_URL from app settings (.env file).
All models are imported so Alembic can detect table changes.
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

# Add backend root to Python path so app modules can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Load all ORM models so metadata is populated
import app.models  # noqa: F401
from app.database.connection import Base
from app.config.settings import settings

# This is the Alembic Config object
config = context.config

# Set up Python logging from alembic.ini config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use our SQLAlchemy Base metadata for autogenerate
target_metadata = Base.metadata

# Override alembic.ini sqlalchemy.url with our settings
# Convert postgresql:// to postgresql+asyncpg:// for async driver
_async_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("postgres://", "postgresql+asyncpg://")
config.set_main_option("sqlalchemy.url", _async_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL, without an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' async mode using asyncpg."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
