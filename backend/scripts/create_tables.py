"""
LegalEase AI - Create Database Tables
Run: python scripts/create_tables.py
Creates all SQLAlchemy ORM tables in the existing PostgreSQL database.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

async def main():
    # Must import models before create_all so they register with Base
    import app.models  # noqa: F401
    from app.database.connection import Base, engine
    from sqlalchemy import text

    print("=" * 50)
    print("LegalEase AI - Creating Database Tables")
    print("=" * 50)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")

    # List created tables
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        )
        tables = [row[0] for row in result]

    print(f"\nTables in 'legalease_ai' database ({len(tables)} total):")
    for t in tables:
        print(f"  [OK] {t}")

    await engine.dispose()
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    asyncio.run(main())
