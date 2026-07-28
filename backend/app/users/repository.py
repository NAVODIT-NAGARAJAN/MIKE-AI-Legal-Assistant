"""
LegalEase AI - User Repository
================================
Data access layer for all user management database operations.

Responsibilities:
    - Fetch users by ID (for profile retrieval)
    - Update user profile fields
    - Update user password hash
    - Log user management events to ActivityLog table

Rules:
    - No business logic — only database operations.
    - Delegates session lifecycle to the service / FastAPI dependency.
    - Never raises HTTP exceptions — only domain-level exceptions.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application_models import ActivityLog
from app.models.user import User
from app.utils.logger import get_logger

log = get_logger(__name__)


class UserRepository:
    """
    Repository for user profile and password management.

    All methods are async and require an injected AsyncSession.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Read Operations
    # ------------------------------------------------------------------

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetch a user by their UUID primary key.

        Args:
            user_id: The user's UUID.

        Returns:
            The User ORM instance if found, None otherwise.

        Raises:
            SQLAlchemyError: On unexpected database failure.
        """
        try:
            result = await self._db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            log.error(f"DB error fetching user by id: {type(exc).__name__}")
            raise

    # ------------------------------------------------------------------
    # Write Operations
    # ------------------------------------------------------------------

    async def update_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
    ) -> User:
        """
        Update mutable profile fields on an existing User instance.

        Only applies non-None values — callers may pass partial updates.
        Uses flush() to reflect changes without committing the transaction.

        Args:
            user: The authenticated User ORM instance to modify.
            full_name: New full name (optional).

        Returns:
            The updated User ORM instance.

        Raises:
            SQLAlchemyError: On unexpected database failure.
        """
        try:
            if full_name is not None:
                user.full_name = full_name

            self._db.add(user)
            await self._db.flush()
            await self._db.refresh(user)

            log.info(f"Profile updated — id={str(user.id)[:8]}...")
            return user
        except SQLAlchemyError as exc:
            log.error(f"DB error updating user profile: {type(exc).__name__}")
            raise

    async def update_password(self, user: User, new_password_hash: str) -> None:
        """
        Replace the stored password hash on a User record.

        Args:
            user: The authenticated User ORM instance.
            new_password_hash: The new bcrypt hash to store.

        Raises:
            SQLAlchemyError: On unexpected database failure.
        """
        try:
            user.password_hash = new_password_hash
            self._db.add(user)
            await self._db.flush()

            log.info(f"Password updated — id={str(user.id)[:8]}...")
        except SQLAlchemyError as exc:
            log.error(f"DB error updating password: {type(exc).__name__}")
            raise

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    async def log_user_event(
        self,
        event_type: str,
        user_id: uuid.UUID,
        details: Optional[dict] = None,
    ) -> None:
        """
        Append a user management event to the ActivityLog table.

        SECURITY: Never log passwords or password hashes in details.

        Args:
            event_type: Constant string such as 'PROFILE_UPDATED', 'PASSWORD_CHANGED'.
            user_id: The UUID of the affected user.
            details: Safe event metadata dict (no secrets).
        """
        try:
            log_entry = ActivityLog(
                user_id=user_id,
                event_type=event_type,
                details=details or {},
            )
            self._db.add(log_entry)
            await self._db.flush()
        except SQLAlchemyError as exc:
            log.error(f"Failed to write user activity log [{event_type}]: {type(exc).__name__}")
