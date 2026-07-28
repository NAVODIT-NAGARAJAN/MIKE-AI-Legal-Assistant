"""
LegalEase AI - User Management Service
========================================
Business logic layer for all user management operations.

Responsibilities:
    - Get current user profile (read-through from ORM instance)
    - Update user profile fields
    - Change user password (verify current → hash new → persist)

Rules:
    - Business logic only — no SQL queries (delegates to UserRepository).
    - Raises HTTPException with appropriate status codes.
    - Passwords are NEVER logged.
    - Authorization is enforced by the router via JWT dependency —
      this service always operates on the authenticated user's own data.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.users.repository import UserRepository
from app.users.schemas import (
    ChangePasswordRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from app.utils.logger import get_logger
from app.utils.security import hash_password, verify_password

log = get_logger(__name__)

# Event type constants for activity_logs table
_EVENT_PROFILE_UPDATED = "PROFILE_UPDATED"
_EVENT_PASSWORD_CHANGED = "PASSWORD_CHANGED"


class UserService:
    """
    Service layer for user management business logic.

    Each method represents a complete use-case.
    Accepts the authenticated User ORM instance from the JWT dependency.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._repo = UserRepository(db)
        self._db = db

    # ------------------------------------------------------------------
    # Get Profile
    # ------------------------------------------------------------------

    def get_profile(self, user: User) -> UserProfileResponse:
        """
        Return the authenticated user's profile.

        No database call needed — the User ORM instance is already
        loaded by the JWT dependency (get_current_active_user).

        Args:
            user: The authenticated User ORM instance.

        Returns:
            UserProfileResponse with safe user data.
        """
        return UserProfileResponse.model_validate(user)

    # ------------------------------------------------------------------
    # Update Profile
    # ------------------------------------------------------------------

    async def update_profile(
        self,
        user: User,
        payload: UpdateProfileRequest,
    ) -> UserProfileResponse:
        """
        Update the authenticated user's profile.

        Workflow:
        1. Apply updates to the User record via repository.
        2. Log PROFILE_UPDATED event.
        3. Commit and return updated profile.

        Args:
            user: The authenticated User ORM instance.
            payload: Validated UpdateProfileRequest.

        Returns:
            UserProfileResponse with the updated data.

        Raises:
            HTTPException 500: On unexpected persistence failure.
        """
        log.info(f"Profile update initiated — id={str(user.id)[:8]}...")

        try:
            updated_user = await self._repo.update_profile(
                user=user,
                full_name=payload.full_name,
            )
        except Exception as exc:
            log.error(f"Unexpected error during profile update: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile. Please try again later.",
            )

        # Audit log
        await self._repo.log_user_event(
            event_type=_EVENT_PROFILE_UPDATED,
            user_id=user.id,
            details={
                "updated_fields": [
                    k for k, v in payload.model_dump().items() if v is not None
                ]
            },
        )

        await self._db.commit()
        await self._db.refresh(updated_user)

        log.info(f"Profile updated successfully — id={str(user.id)[:8]}...")
        return UserProfileResponse.model_validate(updated_user)

    # ------------------------------------------------------------------
    # Change Password
    # ------------------------------------------------------------------

    async def change_password(
        self,
        user: User,
        payload: ChangePasswordRequest,
    ) -> None:
        """
        Change the authenticated user's password.

        Workflow:
        1. Verify current password against stored hash.
        2. Hash the new password with bcrypt.
        3. Persist the new hash.
        4. Log PASSWORD_CHANGED event.
        5. Commit transaction.

        Args:
            user: The authenticated User ORM instance.
            payload: Validated ChangePasswordRequest.

        Raises:
            HTTPException 400: If current_password is incorrect.
            HTTPException 500: On unexpected persistence failure.
        """
        log.info(f"Password change initiated — id={str(user.id)[:8]}...")

        # Step 1 — Verify current password
        if not verify_password(payload.current_password, user.password_hash):
            log.warning(
                f"Password change rejected: incorrect current password — id={str(user.id)[:8]}..."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )

        # Step 2 — Hash the new password
        new_hash = hash_password(payload.new_password)

        # Step 3 — Persist
        try:
            await self._repo.update_password(user=user, new_password_hash=new_hash)
        except Exception as exc:
            log.error(f"Unexpected error during password change: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password. Please try again later.",
            )

        # Step 4 — Audit log
        await self._repo.log_user_event(
            event_type=_EVENT_PASSWORD_CHANGED,
            user_id=user.id,
            details={},  # Never log any password data
        )

        await self._db.commit()

        log.info(f"Password changed successfully — id={str(user.id)[:8]}...")
