"""
LegalEase AI - Consumer Case Repository
==========================================
Data access layer for ConsumerCase CRUD operations.

Rules:
    - No business logic — only database operations.
    - All methods are async.
    - session lifecycle managed by service / FastAPI dependency.
    - Never raises HTTP exceptions.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consumer_case import CaseStatus, ConsumerCase
from app.utils.logger import get_logger

log = get_logger(__name__)


class CaseRepository:
    """Async repository for ConsumerCase database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, case_id: uuid.UUID) -> Optional[ConsumerCase]:
        """Fetch a single case by its UUID. Returns None if not found."""
        try:
            result = await self._db.execute(
                select(ConsumerCase).where(ConsumerCase.id == case_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            log.error(f"DB error fetching case {case_id}: {type(exc).__name__}")
            raise

    async def get_by_id_and_user(
        self, case_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ConsumerCase]:
        """
        Fetch a case by ID scoped to a specific user.
        Returns None if case doesn't exist OR belongs to a different user.
        This enforces row-level ownership at the query layer.
        """
        try:
            result = await self._db.execute(
                select(ConsumerCase).where(
                    ConsumerCase.id == case_id,
                    ConsumerCase.user_id == user_id,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            log.error(f"DB error fetching case {case_id} for user: {type(exc).__name__}")
            raise

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ConsumerCase]:
        """
        List all cases belonging to a user, ordered by creation date descending.

        Args:
            user_id: Owner's UUID.
            skip: Pagination offset.
            limit: Max records to return (capped at 100).
        """
        limit = min(limit, 100)  # Hard cap
        try:
            result = await self._db.execute(
                select(ConsumerCase)
                .where(ConsumerCase.user_id == user_id)
                .order_by(ConsumerCase.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            log.error(f"DB error listing cases for user: {type(exc).__name__}")
            raise

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Return total number of cases for a user (used for pagination)."""
        from sqlalchemy import func
        try:
            result = await self._db.execute(
                select(func.count()).where(ConsumerCase.user_id == user_id)
            )
            return result.scalar_one()
        except SQLAlchemyError as exc:
            log.error(f"DB error counting cases: {type(exc).__name__}")
            raise

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, case: ConsumerCase) -> ConsumerCase:
        """Persist a new ConsumerCase record. Flushes without committing."""
        try:
            self._db.add(case)
            await self._db.flush()
            await self._db.refresh(case)
            log.info(f"Case created — id={str(case.id)[:8]}... user={str(case.user_id)[:8]}...")
            return case
        except SQLAlchemyError as exc:
            log.error(f"DB error creating case: {type(exc).__name__}")
            raise

    async def update(self, case: ConsumerCase) -> ConsumerCase:
        """Flush changes to an already-modified ConsumerCase instance."""
        try:
            self._db.add(case)
            await self._db.flush()
            await self._db.refresh(case)
            log.info(f"Case updated — id={str(case.id)[:8]}...")
            return case
        except SQLAlchemyError as exc:
            log.error(f"DB error updating case: {type(exc).__name__}")
            raise

    async def delete(self, case: ConsumerCase) -> None:
        """Soft-delete is not implemented — hard delete with CASCADE."""
        try:
            await self._db.delete(case)
            await self._db.flush()
            log.info(f"Case deleted — id={str(case.id)[:8]}...")
        except SQLAlchemyError as exc:
            log.error(f"DB error deleting case: {type(exc).__name__}")
            raise
