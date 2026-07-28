"""
LegalEase AI - Authentication Package
=======================================
Exports the public interface of the auth module.
"""

from app.auth.dependencies import get_current_active_user, get_current_user
from app.auth.schemas import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

__all__ = [
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    # Schemas
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "LogoutResponse",
]
