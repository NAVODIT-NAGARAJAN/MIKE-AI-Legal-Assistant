"""
LegalEase AI - User Management Router
=======================================
FastAPI route handlers for the User Management module.

All endpoints are protected — they require a valid JWT access token.
Authorization is enforced per-request: users can only access and
modify their own profile (enforced via the get_current_active_user dependency).

Endpoints:
    GET  /api/v1/users/profile         — Retrieve authenticated user's profile
    PUT  /api/v1/users/profile         — Update authenticated user's profile
    POST /api/v1/users/change-password — Change authenticated user's password
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.users.schemas import (
    ChangePasswordRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from app.users.service import UserService
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /profile
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=SuccessResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description=(
        "Retrieve the authenticated user's full profile. "
        "Requires a valid JWT access token in the Authorization header."
    ),
    responses={
        200: {"description": "User profile retrieved successfully."},
        401: {"description": "Invalid or missing JWT token."},
        403: {"description": "Account is inactive."},
    },
)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[UserProfileResponse]:
    """
    Get the current authenticated user's profile.

    Requires: `Authorization: Bearer <token>` header.
    """
    # No DB call needed — user is already loaded by the dependency
    profile = UserProfileResponse.model_validate(current_user)
    return SuccessResponse(
        message="Profile retrieved successfully.",
        data=profile,
    )


# ---------------------------------------------------------------------------
# PUT /profile
# ---------------------------------------------------------------------------

@router.put(
    "/profile",
    response_model=SuccessResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description=(
        "Update the authenticated user's profile information. "
        "Currently supports updating full_name. "
        "Email changes are not permitted. "
        "Requires a valid JWT access token."
    ),
    responses={
        200: {"description": "Profile updated successfully."},
        400: {"description": "No fields provided for update."},
        401: {"description": "Invalid or missing JWT token."},
        403: {"description": "Account is inactive."},
        422: {"description": "Validation error — check request body."},
    },
)
async def update_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[UserProfileResponse]:
    """
    Update the current authenticated user's profile.

    - **full_name**: New full name (2–100 characters).

    Requires: `Authorization: Bearer <token>` header.
    """
    service = UserService(db)
    updated = await service.update_profile(user=current_user, payload=payload)
    return SuccessResponse(
        message="Profile updated successfully.",
        data=updated,
    )


# ---------------------------------------------------------------------------
# POST /change-password
# ---------------------------------------------------------------------------

@router.post(
    "/change-password",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Change current user password",
    description=(
        "Change the authenticated user's password. "
        "Requires the current password for verification. "
        "The new password must meet strength requirements and "
        "differ from the current password. "
        "Requires a valid JWT access token."
    ),
    responses={
        200: {"description": "Password changed successfully."},
        400: {"description": "Current password is incorrect or new password matches current."},
        401: {"description": "Invalid or missing JWT token."},
        403: {"description": "Account is inactive."},
        422: {"description": "Validation error — check request body."},
    },
)
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    """
    Change the current authenticated user's password.

    - **current_password**: The user's existing password.
    - **new_password**: Must be 8+ chars with upper, lower, and digit.
    - **confirm_password**: Must match new_password exactly.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = UserService(db)
    await service.change_password(user=current_user, payload=payload)
    return SuccessResponse(
        message="Password changed successfully. Please log in again with your new password.",
        data=None,
    )