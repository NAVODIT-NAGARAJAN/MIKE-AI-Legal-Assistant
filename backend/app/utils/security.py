"""
LegalEase AI - Security Utilities
===================================
Password hashing and JWT token creation/verification.
Uses passlib[bcrypt] for password hashing.
Uses python-jose for JWT operations.
NEVER logs passwords, tokens, or API keys.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

# ---- Password Hashing -------------------------------------------------------
# bcrypt with cost factor 12 (secure default for 2024+)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    The resulting hash is safe to store in the database.

    Args:
        plain_password: The user's plain text password.

    Returns:
        A bcrypt hash string.
    """
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a stored bcrypt hash.

    Args:
        plain_password: The password provided during login.
        hashed_password: The bcrypt hash stored in the database.

    Returns:
        True if the password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ---- JWT Token Management ---------------------------------------------------

def create_access_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        user_id: The user's UUID as a string.
        email: The user's email address.
        expires_delta: Custom token TTL. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        A signed JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": user_id,           # Subject: user UUID
        "email": email,           # User email for convenience
        "iat": now,               # Issued at
        "exp": expire,            # Expiry
        "type": "access",         # Token type
    }

    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    log.debug(f"Access token created for user_id={user_id[:8]}...")
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT string from the Authorization header.

    Returns:
        The decoded payload dict containing 'sub' (user_id) and 'email'.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        # Validate required fields
        if payload.get("sub") is None:
            raise JWTError("Token missing subject claim")

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    except JWTError as e:
        # Do NOT log the token value — only log the error type
        log.warning(f"JWT verification failed: {type(e).__name__}")
        raise


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.

    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit

    Returns:
        (is_valid: bool, error_message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."

    return True, ""
