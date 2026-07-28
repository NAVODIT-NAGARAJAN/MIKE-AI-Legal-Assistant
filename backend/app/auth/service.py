"""
LegalEase AI - Authentication Service
=======================================
Business logic layer for all authentication operations.

Responsibilities:
    - Orchestrate user registration (duplicate check, hashing, persist, log)
    - Orchestrate user login (lookup, verify, token generation, log)
    - Handle logout (stateless — JWT is discarded client-side; log event)

Rules:
    - Business logic only — no SQL queries (delegates to AuthRepository).
    - Raises HTTPException with appropriate status codes for API consumers.
    - Follows Single Responsibility Principle.
    - Passwords are NEVER logged.
"""

import uuid
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.config.settings import settings
from app.utils.logger import get_logger
from app.utils.security import create_access_token, hash_password, verify_password

log = get_logger(__name__)

# Event type constants — used in activity_logs table
_EVENT_REGISTERED = "USER_REGISTERED"
_EVENT_LOGIN = "USER_LOGIN"
_EVENT_LOGIN_FAILED = "LOGIN_FAILED"
_EVENT_LOGOUT = "USER_LOGOUT"


class AuthService:
    """
    Service layer for authentication business logic.

    Each method represents a complete use-case with:
    - Input validation (beyond schema-level)
    - Error handling
    - Delegation to repository
    - Audit logging
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = AuthRepository(db)
        self._db = db

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------

    async def register_user(self, payload: RegisterRequest) -> UserResponse:
        """
        Register a new user account.

        Workflow:
        1. Check for duplicate email.
        2. Hash the password with bcrypt.
        3. Persist the user record.
        4. Log USER_REGISTERED event.
        5. Return safe UserResponse (no password_hash).

        Args:
            payload: Validated RegisterRequest from the route handler.

        Returns:
            UserResponse with the new user's public data.

        Raises:
            HTTPException 409: If the email address is already registered.
            HTTPException 500: On unexpected persistence failure.
        """
        log.info(f"Registration attempt for email=[REDACTED] (length={len(payload.email)})")

        # Step 1 — Duplicate email check
        existing = await self._repo.get_user_by_email(payload.email)
        if existing is not None:
            log.warning("Registration rejected: email already registered")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )

        # Step 2 — Hash the password (bcrypt via passlib)
        password_hash = hash_password(payload.password)

        # Step 3 — Persist user
        try:
            user = await self._repo.create_user(
                full_name=payload.full_name,
                email=payload.email,
                password_hash=password_hash,
            )
        except IntegrityError:
            # Race condition: two concurrent registrations with the same email
            log.warning("Registration race condition: IntegrityError on email unique constraint")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists.",
            )
        except Exception as exc:
            log.error(f"Unexpected error persisting new user: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account. Please try again later.",
            )

        # Step 4 — Audit log
        await self._repo.log_auth_event(
            event_type=_EVENT_REGISTERED,
            user_id=user.id,
            details={"email_domain": payload.email.split("@")[-1]},
        )

        # Step 5 — Commit the transaction (repository only flushes)
        await self._db.commit()
        await self._db.refresh(user)

        log.info(f"User registered successfully — id={str(user.id)[:8]}...")
        return UserResponse.model_validate(user)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    async def login_user(self, payload: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return a signed JWT access token.

        Workflow:
        1. Fetch user by email.
        2. Verify the password against the stored bcrypt hash.
        3. Check that the account is active.
        4. Generate a signed JWT access token.
        5. Log USER_LOGIN event.
        6. Return TokenResponse with token + user profile.

        Args:
            payload: Validated LoginRequest from the route handler.

        Returns:
            TokenResponse with access_token, token_type, expires_in, and user.

        Raises:
            HTTPException 401: If credentials are invalid or account is inactive.
        """
        log.info("Login attempt received")

        # Use a generic error message for ALL auth failures
        # to prevent user-enumeration attacks.
        generic_401 = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Step 1 — Lookup user
        user = await self._repo.get_user_by_email(payload.email)
        if user is None:
            await self._repo.log_auth_event(
                event_type=_EVENT_LOGIN_FAILED,
                details={"reason": "email_not_found"},
            )
            await self._db.commit()
            raise generic_401

        # Step 2 — Verify password
        if not verify_password(payload.password, user.password_hash):
            await self._repo.log_auth_event(
                event_type=_EVENT_LOGIN_FAILED,
                user_id=user.id,
                details={"reason": "wrong_password"},
            )
            await self._db.commit()
            raise generic_401

        # Step 3 — Account status check
        if not user.is_active:
            log.warning(f"Login rejected for inactive account — id={str(user.id)[:8]}...")
            await self._repo.log_auth_event(
                event_type=_EVENT_LOGIN_FAILED,
                user_id=user.id,
                details={"reason": "account_inactive"},
            )
            await self._db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your account has been deactivated. Please contact support.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Step 4 — Generate JWT
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            expires_delta=expires_delta,
        )

        # Step 5 — Audit log
        await self._repo.log_auth_event(
            event_type=_EVENT_LOGIN,
            user_id=user.id,
            details={"email_domain": user.email.split("@")[-1]},
        )
        await self._db.commit()

        log.info(f"User logged in successfully — id={str(user.id)[:8]}...")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user),
        )

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    async def logout_user(self, user_id: uuid.UUID) -> None:
        """
        Record a logout event for the authenticated user.

        JWT is stateless — the actual token invalidation is handled
        client-side (the frontend discards the token). This method
        only records the logout event in the audit log.

        Args:
            user_id: The UUID of the currently authenticated user.
        """
        await self._repo.log_auth_event(
            event_type=_EVENT_LOGOUT,
            user_id=user_id,
            details={},
        )
        await self._db.commit()
        log.info(f"User logged out — id={str(user_id)[:8]}...")
