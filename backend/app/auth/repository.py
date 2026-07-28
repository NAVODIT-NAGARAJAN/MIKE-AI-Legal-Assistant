"""
LegalEase AI - Authentication Repository
==========================================
Data access layer for all authentication-related database operations.

Responsibilities:
    - Fetch users by email or ID (async)
    - Create new user records
    - Log authentication events to ActivityLog table

Rules:
    - No business logic here — only SQL operations.
    - Passwords (even hashes) are passed in from the service layer.
    - Never raise HTTP exceptions; raise domain-level exceptions instead.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application_models import ActivityLog
from app.models.user import User
from app.utils.logger import get_logger

log = get_logger(__name__)


class AuthRepository:
    """
    Repository for authentication-related database operations.

    All methods are async and expect an injected AsyncSession.
    The session lifecycle (commit/rollback) is managed by the caller.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Read Operations
    # ------------------------------------------------------------------

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Fetch a user record by their email address.

        Args:
            email: The email address to search for (case-sensitive match).

        Returns:
            The User ORM instance if found, None otherwise.

        Raises:
            SQLAlchemyError: On unexpected database failure.
        """
        try:
            result = await self._db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            log.error(f"DB error fetching user by email: {type(exc).__name__}")
            raise

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetch a user record by their UUID.

        Args:
            user_id: The user's UUID primary key.

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

    async def create_user(
        self,
        full_name: str,
        email: str,
        password_hash: str,
    ) -> User:
        """
        Persist a new User record in the database.

        The caller must commit the session after this call.
        Uses flush() to obtain the generated UUID before commit.

        Args:
            full_name: The user's full name.
            email: The user's email address (unique constraint enforced by DB).
            password_hash: A bcrypt hash of the user's password.

        Returns:
            The newly created User ORM instance (with id populated).

        Raises:
            IntegrityError: If the email address is already registered.
            SQLAlchemyError: On unexpected database failure.
        """
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            is_active=True,
        )
        try:
            self._db.add(user)
            await self._db.flush()   # Assigns UUID without committing transaction
            await self._db.refresh(user)  # Reload server-generated defaults
            log.info(f"User created — id={str(user.id)[:8]}...")
            return user
        except IntegrityError as exc:
            # Email uniqueness violation — let service layer handle the HTTP response
            log.warning(f"Duplicate email detected during user creation: {type(exc).__name__}")
            raise
        except SQLAlchemyError as exc:
            log.error(f"DB error creating user: {type(exc).__name__}")
            raise

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    async def log_auth_event(
        self,
        event_type: str,
        user_id: Optional[uuid.UUID] = None,
        details: Optional[dict] = None,
    ) -> None:
        """
        Append an authentication event to the ActivityLog table.

        SECURITY: Never log passwords, tokens, or API keys in details.

        Args:
            event_type: A constant string such as 'USER_REGISTERED', 'USER_LOGIN',
                        'USER_LOGOUT', 'LOGIN_FAILED'.
            user_id: The UUID of the affected user (None if user is unknown).
            details: Optional dict with safe event metadata (no secrets).
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
            # Log failures must not crash the main authentication flow
            log.error(f"Failed to write activity log [{event_type}]: {type(exc).__name__}")
