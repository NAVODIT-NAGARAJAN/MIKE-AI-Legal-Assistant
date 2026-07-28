"""
LegalEase AI - User Management Package
========================================
Exports the public interface of the users module.
"""

from app.users.schemas import (
    ChangePasswordRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)

__all__ = [
    "UserProfileResponse",
    "UpdateProfileRequest",
    "ChangePasswordRequest",
]
