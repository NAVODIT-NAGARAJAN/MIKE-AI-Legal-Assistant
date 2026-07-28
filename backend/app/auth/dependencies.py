"""
LegalEase AI - Authentication Dependencies
============================================
FastAPI dependency functions for JWT-based authentication.

These are injected into protected route handlers via FastAPI's Depends().
They extract the Bearer token, validate it, and return the authenticated user.

Usage in a protected route:
    @router.get("/protected")
    async def protected_endpoint(
        current_user: User = Depends(get_current_active_user),
    ):
        return {"user_id": str(current_user.id)}
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repository import AuthRepository
from app.database.connection import get_db
from app.models.user import User
from app.utils.logger import get_logger
from app.utils.security import decode_access_token

log = get_logger(__name__)

# OAuth2 / Bearer token extractor — reads Authorization: Bearer <token> header
_bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description="Provide your JWT access token as: Authorization: Bearer <token>",
    auto_error=True,   # Raises 403 if header is missing (we override below)
)

# Standard 401 raised for any token validation failure
_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials. Please log in again.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: validate JWT and return the authenticated User.

    Workflow:
    1. Extract Bearer token from Authorization header.
    2. Decode and verify the JWT signature + expiry.
    3. Extract user_id from the 'sub' claim.
    4. Fetch the User record from PostgreSQL.
    5. Return the User ORM instance.

    Args:
        credentials: Injected by HTTPBearer — contains the raw token string.
        db: Injected async database session.

    Returns:
        The authenticated User ORM instance.

    Raises:
        HTTPException 401: If the token is missing, invalid, expired, or the
                           user no longer exists in the database.
    """
    token = credentials.credentials

    # Step 2 — Decode JWT
    try:
        payload = decode_access_token(token)
    except JWTError:
        # decode_access_token already logs the error type (not the token)
        raise _CREDENTIALS_EXCEPTION

    # Step 3 — Extract user_id from 'sub' claim
    user_id_str: str = payload.get("sub")
    if not user_id_str:
        log.warning("JWT 'sub' claim is missing")
        raise _CREDENTIALS_EXCEPTION

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        log.warning("JWT 'sub' claim is not a valid UUID")
        raise _CREDENTIALS_EXCEPTION

    # Step 4 — Fetch user from database
    repo = AuthRepository(db)
    user = await repo.get_user_by_id(user_id)

    if user is None:
        log.warning(f"JWT references non-existent user — id={user_id_str[:8]}...")
        raise _CREDENTIALS_EXCEPTION

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency: ensure the authenticated user's account is active.

    Extends get_current_user() with an account-status check.
    Inject this dependency in all protected routes that require an active user.

    Args:
        current_user: Injected User from get_current_user().

    Returns:
        The authenticated, active User ORM instance.

    Raises:
        HTTPException 403: If the user's account is deactivated.
    """
    if not current_user.is_active:
        log.warning(
            f"Access denied for inactive account — id={str(current_user.id)[:8]}..."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )
    return current_user
