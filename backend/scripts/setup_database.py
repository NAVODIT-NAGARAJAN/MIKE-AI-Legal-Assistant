"""
LegalEase AI - Database Setup Script
======================================
Creates the PostgreSQL database, user, and all tables.
Run once during initial setup: python scripts/setup_database.py

REQUIREMENTS:
- PostgreSQL running on localhost:5432
- A superuser account (postgres) to create the database/user

Usage:
    python scripts/setup_database.py

Environment:
    Reads from backend/.env
"""

import asyncio
import sys
from pathlib import Path

# Add backend root to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.config.settings import settings
from app.database.connection import Base, engine
from app.utils.logger import get_logger, setup_logging

# Must import all models so they register with Base.metadata
import app.models  # noqa: F401

setup_logging()
log = get_logger(__name__)

DB_NAME = "legalease_db"
DB_USER = "legalease_user"


def create_database_and_user(admin_password: str) -> None:
    """
    Connect as the postgres superuser and:
    1. Create the 'legalease_user' role (if not exists)
    2. Create the 'legalease_db' database (if not exists)
    3. Grant all privileges
    """
    log.info("Connecting to PostgreSQL as superuser...")

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="postgres",
        user="postgres",
        password=admin_password,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Read desired app DB password from .env
    from urllib.parse import urlparse
    parsed = urlparse(settings.database_url)
    app_db_password = parsed.password

    # Create app user if not exists
    cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
    if cursor.fetchone() is None:
        cursor.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{app_db_password}'")
        log.info(f"Created PostgreSQL user: {DB_USER}")
    else:
        log.info(f"PostgreSQL user '{DB_USER}' already exists")

    # Create app database if not exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if cursor.fetchone() is None:
        cursor.execute(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER}")
        log.info(f"Created database: {DB_NAME}")
    else:
        log.info(f"Database '{DB_NAME}' already exists")

    # Grant all privileges
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
    log.info(f"Granted privileges on '{DB_NAME}' to '{DB_USER}'")

    cursor.close()
    conn.close()


async def create_tables() -> None:
    """
    Create all SQLAlchemy ORM tables in PostgreSQL.
    Equivalent to: CREATE TABLE IF NOT EXISTS ...
    """
    log.info("Creating application tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("All tables created successfully")


async def verify_tables() -> None:
    """List all created tables for verification."""
    from sqlalchemy import inspect, text
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        )
        tables = [row[0] for row in result]
    log.info(f"Tables in database: {tables}")


async def main(admin_password: str) -> None:
    log.info("=" * 60)
    log.info("LegalEase AI - Database Setup")
    log.info("=" * 60)

    # Step 1: Create DB and user (requires superuser)
    create_database_and_user(admin_password)

    # Step 2: Create all application tables
    await create_tables()

    # Step 3: Verify
    await verify_tables()

    log.info("Database setup complete!")
    log.info(f"Connection URL: {settings.database_url.split('@')[1]}")


if __name__ == "__main__":
    import getpass
    print("LegalEase AI - Database Setup")
    print("=" * 40)
    pg_admin_pass = getpass.getpass("Enter PostgreSQL superuser (postgres) password: ")
    asyncio.run(main(pg_admin_pass))
