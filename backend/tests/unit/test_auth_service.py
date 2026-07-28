"""
Unit Tests — Authentication Service (Business Logic)
======================================================
Tests for app/auth/service.py.

The database session is replaced with a mock so these are pure
unit tests — no real database I/O occurs.

Approach:
- Use unittest.mock.AsyncMock to simulate AuthRepository methods.
- Patch the repository inside the service under test.
- Verify that the service produces the correct output or raises the
  correct HTTPException for every code path.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.auth.schemas import LoginRequest, RegisterRequest
from app.auth.service import AuthService
from app.models.user import User
from app.utils.security import hash_password


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(
    email: str = "rahul@example.com",
    full_name: str = "Rahul Sharma",
    password: str = "SecurePass1",
    is_active: bool = True,
) -> User:
    """Build a fake User ORM object for use in mock returns."""
    user = User()
    user.id = uuid.uuid4()
    user.full_name = full_name
    user.email = email
    user.password_hash = hash_password(password)
    user.is_active = is_active
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


def _make_mock_db() -> AsyncMock:
    """Build a mock AsyncSession that satisfies commit/refresh calls."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


# ---------------------------------------------------------------------------
# Tests — register_user
# ---------------------------------------------------------------------------

class TestAuthServiceRegister:
    """Unit tests for AuthService.register_user()."""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Happy path: new email, valid password → user created."""
        mock_db = _make_mock_db()
        fake_user = _make_user()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=None)
            repo_instance.create_user = AsyncMock(return_value=fake_user)
            repo_instance.log_auth_event = AsyncMock()
            mock_db.refresh = AsyncMock()

            service = AuthService(mock_db)
            result = await service.register_user(
                RegisterRequest(
                    full_name="Rahul Sharma",
                    email="rahul@example.com",
                    password="SecurePass1",
                )
            )

        assert result.email == fake_user.email
        assert result.full_name == fake_user.full_name
        assert not hasattr(result, "password_hash")  # Never expose hash

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises_409(self):
        """Existing email → HTTPException 409 Conflict."""
        mock_db = _make_mock_db()
        existing_user = _make_user()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=existing_user)

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.register_user(
                    RegisterRequest(
                        full_name="Another User",
                        email="rahul@example.com",
                        password="SecurePass1",
                    )
                )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_register_integrity_error_raises_409(self):
        """Race condition IntegrityError → HTTPException 409."""
        mock_db = _make_mock_db()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=None)
            repo_instance.create_user = AsyncMock(
                side_effect=IntegrityError("dup", None, None)
            )

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.register_user(
                    RegisterRequest(
                        full_name="Rahul Sharma",
                        email="rahul@example.com",
                        password="SecurePass1",
                    )
                )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_register_unexpected_error_raises_500(self):
        """Unexpected DB error → HTTPException 500."""
        mock_db = _make_mock_db()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=None)
            repo_instance.create_user = AsyncMock(
                side_effect=Exception("DB unavailable")
            )

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.register_user(
                    RegisterRequest(
                        full_name="Rahul Sharma",
                        email="rahul@example.com",
                        password="SecurePass1",
                    )
                )

        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# Tests — login_user
# ---------------------------------------------------------------------------

class TestAuthServiceLogin:
    """Unit tests for AuthService.login_user()."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Correct credentials → TokenResponse with access_token."""
        mock_db = _make_mock_db()
        fake_user = _make_user(password="SecurePass1")

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=fake_user)
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            result = await service.login_user(
                LoginRequest(email="rahul@example.com", password="SecurePass1")
            )

        assert result.access_token
        assert result.token_type == "bearer"
        assert result.expires_in > 0
        assert result.user.email == fake_user.email

    @pytest.mark.asyncio
    async def test_login_unknown_email_raises_401(self):
        """Non-existent email → HTTPException 401."""
        mock_db = _make_mock_db()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=None)
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.login_user(
                    LoginRequest(email="unknown@example.com", password="SecurePass1")
                )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises_401(self):
        """Correct email, wrong password → HTTPException 401."""
        mock_db = _make_mock_db()
        fake_user = _make_user(password="SecurePass1")

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=fake_user)
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.login_user(
                    LoginRequest(email="rahul@example.com", password="WrongPass99")
                )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_account_raises_401(self):
        """Correct credentials but inactive account → HTTPException 401."""
        mock_db = _make_mock_db()
        inactive_user = _make_user(password="SecurePass1", is_active=False)

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=inactive_user)
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_info:
                await service.login_user(
                    LoginRequest(email="rahul@example.com", password="SecurePass1")
                )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_error_message_is_generic(self):
        """Both wrong email and wrong password return the SAME 401 message (no enumeration)."""
        mock_db = _make_mock_db()

        # Wrong email
        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=None)
            repo_instance.log_auth_event = AsyncMock()
            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_email:
                await service.login_user(
                    LoginRequest(email="nobody@example.com", password="SecurePass1")
                )

        # Wrong password
        fake_user = _make_user(password="SecurePass1")
        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_user_by_email = AsyncMock(return_value=fake_user)
            repo_instance.log_auth_event = AsyncMock()
            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc_pw:
                await service.login_user(
                    LoginRequest(email="rahul@example.com", password="WrongPass99")
                )

        # Same error message prevents user enumeration
        assert exc_email.value.detail == exc_pw.value.detail


# ---------------------------------------------------------------------------
# Tests — logout_user
# ---------------------------------------------------------------------------

class TestAuthServiceLogout:
    """Unit tests for AuthService.logout_user()."""

    @pytest.mark.asyncio
    async def test_logout_logs_event(self):
        """Logout should call log_auth_event with USER_LOGOUT."""
        mock_db = _make_mock_db()
        user_id = uuid.uuid4()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            await service.logout_user(user_id=user_id)

            repo_instance.log_auth_event.assert_called_once_with(
                event_type="USER_LOGOUT",
                user_id=user_id,
                details={},
            )

    @pytest.mark.asyncio
    async def test_logout_commits_transaction(self):
        """Logout should commit the session."""
        mock_db = _make_mock_db()
        user_id = uuid.uuid4()

        with patch("app.auth.service.AuthRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.log_auth_event = AsyncMock()

            service = AuthService(mock_db)
            await service.logout_user(user_id=user_id)

            mock_db.commit.assert_called_once()
