"""
LegalEase AI - Authentication Router
======================================
FastAPI route handlers for the Authentication module.

Public endpoints (no JWT required):
    POST /api/v1/auth/register  — Create a new user account
    POST /api/v1/auth/login     — Authenticate and receive JWT

Protected endpoints (JWT required):
    POST /api/v1/auth/logout    — Record logout; client discards token

All routes follow the standard response format from api.md:
    Success: { "success": true, "message": "...", "data": {...} }
    Error:   { "success": false, "message": "...", "errors": [...] }
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.schemas import LoginRequest, LogoutResponse, RegisterRequest, TokenResponse, UserResponse
from app.auth.service import AuthService
from app.database.connection import get_db
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Create a new LegalEase AI user account. "
        "Requires a unique email address and a strong password. "
        "This is a public endpoint — no authentication required."
    ),
    responses={
        201: {"description": "User registered successfully."},
        409: {"description": "Email address is already registered."},
        422: {"description": "Validation error — check request body."},
    },
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[UserResponse]:
    """
    Register a new consumer account.

    - **full_name**: 2–100 characters.
    - **email**: Must be unique and a valid email format.
    - **password**: Minimum 8 characters with at least one uppercase,
      one lowercase, and one digit.
    """
    service = AuthService(db)
    user = await service.register_user(payload)
    return SuccessResponse(
        message="Registration successful. Welcome to LegalEase AI.",
        data=user,
    )


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login and receive a JWT access token",
    description=(
        "Authenticate with email and password. "
        "Returns a signed JWT access token on success. "
        "Include the token in subsequent requests as: Authorization: Bearer <token>. "
        "This is a public endpoint — no authentication required."
    ),
    responses={
        200: {"description": "Login successful — token returned."},
        401: {"description": "Invalid credentials."},
        422: {"description": "Validation error — check request body."},
    },
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TokenResponse]:
    """
    Authenticate and receive a JWT access token.

    - **email**: The registered email address.
    - **password**: The account password.
    """
    service = AuthService(db)
    token_response = await service.login_user(payload)
    return SuccessResponse(
        message="Login successful.",
        data=token_response,
    )


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------

@router.post(
    "/logout",
    response_model=SuccessResponse[LogoutResponse],
    status_code=status.HTTP_200_OK,
    summary="Logout and invalidate session",
    description=(
        "Record a logout event for the authenticated user. "
        "JWT tokens are stateless — the client is responsible for discarding the token. "
        "Requires a valid JWT in the Authorization header."
    ),
    responses={
        200: {"description": "Logout recorded successfully."},
        401: {"description": "Invalid or missing JWT token."},
        403: {"description": "Account is inactive."},
    },
)
async def logout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[LogoutResponse]:
    """
    Logout the currently authenticated user.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = AuthService(db)
    await service.logout_user(user_id=current_user.id)
    return SuccessResponse(
        message="You have been logged out successfully.",
        data=LogoutResponse(),
    )