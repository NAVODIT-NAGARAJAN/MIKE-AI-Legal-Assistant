"""
LegalEase AI - User Management Schemas
========================================
Pydantic request and response models for the User Management module.

Schemas:
    UserProfileResponse  — Full user profile (safe, no password_hash)
    UpdateProfileRequest — PATCH /users/profile — updatable fields only
    ChangePasswordRequest— POST /users/change-password — current + new password
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class UserProfileResponse(BaseModel):
    """
    Full user profile returned by GET /api/v1/users/profile.
    Never contains password_hash or any internal field.
    """

    id: uuid.UUID = Field(..., description="User's unique identifier (UUID).")
    full_name: str = Field(..., description="User's full name.")
    email: str = Field(..., description="User's registered email address.")
    is_active: bool = Field(..., description="Whether the account is currently active.")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last profile update timestamp (UTC).")

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class UpdateProfileRequest(BaseModel):
    """
    Request body for PUT /api/v1/users/profile.

    At least one field must be provided.
    Email changes are not permitted — email is the account identifier.
    """

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Rahul Sharma"],
        description="New full name (2–100 characters). Optional.",
    )

    @field_validator("full_name")
    @classmethod
    def full_name_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        """Reject whitespace-only names if provided."""
        if v is not None and not v.strip():
            raise ValueError("Full name must not be blank or whitespace only.")
        return v.strip() if v is not None else None

    @model_validator(mode="after")
    def at_least_one_field_required(self) -> "UpdateProfileRequest":
        """Ensure at least one field is present."""
        if self.full_name is None:
            raise ValueError(
                "At least one field must be provided for a profile update."
            )
        return self

    model_config = {"str_strip_whitespace": True}


class ChangePasswordRequest(BaseModel):
    """
    Request body for POST /api/v1/users/change-password.

    Rules:
    - current_password must match the stored hash.
    - new_password must meet strength requirements.
    - new_password must differ from current_password.
    """

    current_password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="The user's current account password.",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["NewSecurePass1"],
        description=(
            "New password: 8–128 characters. "
            "Must contain at least one uppercase letter, one lowercase letter, "
            "and one digit."
        ),
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Must exactly match new_password.",
    )

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        """Enforce password complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("New password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("New password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("New password must contain at least one digit.")
        return v

    @model_validator(mode="after")
    def passwords_must_match_and_differ(self) -> "ChangePasswordRequest":
        """Confirm passwords match and new differs from current."""
        if self.new_password != self.confirm_password:
            raise ValueError("new_password and confirm_password do not match.")
        if self.current_password == self.new_password:
            raise ValueError(
                "New password must be different from the current password."
            )
        return self
