"""
LegalEase AI - Authentication Schemas
=======================================
Pydantic models for all authentication request payloads and response bodies.
All inputs are strictly validated. Passwords are never returned in responses.

Schemas:
    RegisterRequest  — POST /auth/register body
    LoginRequest     — POST /auth/login body
    UserResponse     — Safe user representation (no password_hash)
    TokenResponse    — JWT token + user info returned on login
    LogoutResponse   — Confirmation on logout
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """
    Request body for POST /api/v1/auth/register.

    Validation rules:
    - full_name: 2–100 characters, must not be blank.
    - email: must be a valid email address.
    - password: minimum 8 chars, must include upper, lower, and digit.
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Rahul Sharma"],
        description="Consumer's full name (2–100 characters).",
    )
    email: EmailStr = Field(
        ...,
        examples=["rahul@example.com"],
        description="Valid email address. Must be unique across all users.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass1"],
        description=(
            "Password: 8–128 characters. "
            "Must contain at least one uppercase letter, one lowercase letter, "
            "and one digit."
        ),
    )

    @field_validator("full_name")
    @classmethod
    def full_name_must_not_be_blank(cls, v: str) -> str:
        """Reject whitespace-only names."""
        if not v.strip():
            raise ValueError("Full name must not be blank or whitespace only.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_must_meet_strength_requirements(cls, v: str) -> str:
        """
        Enforce password complexity rules:
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v

    model_config = {"str_strip_whitespace": True}


class LoginRequest(BaseModel):
    """
    Request body for POST /api/v1/auth/login.
    """

    email: EmailStr = Field(
        ...,
        examples=["rahul@example.com"],
        description="Registered email address.",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        examples=["SecurePass1"],
        description="Account password.",
    )

    model_config = {"str_strip_whitespace": True}


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Safe user representation included in API responses.
    The password_hash field is NEVER included.
    """

    id: uuid.UUID = Field(..., description="User's unique identifier (UUID).")
    full_name: str = Field(..., description="User's full name.")
    email: str = Field(..., description="User's email address.")
    is_active: bool = Field(..., description="Whether the account is active.")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC).")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Response body for POST /api/v1/auth/login.
    Contains the JWT access token and authenticated user info.
    """

    access_token: str = Field(
        ...,
        description="Signed JWT access token. Include in Authorization header as: Bearer <token>.",
    )
    token_type: str = Field(
        default="bearer",
        description="Token type. Always 'bearer'.",
    )
    expires_in: int = Field(
        ...,
        description="Token TTL in seconds.",
    )
    user: UserResponse = Field(
        ...,
        description="Authenticated user's profile.",
    )


class LogoutResponse(BaseModel):
    """
    Response body for POST /api/v1/auth/logout.
    """

    message: str = Field(
        default="Logout successful. Please discard your access token.",
        description="Confirmation message.",
    )
