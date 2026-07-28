"""
Unit Tests — User Service (Business Logic)
===========================================
Tests for app/users/service.py with mocked repository.
No database or HTTP required.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.users.schemas import ChangePasswordRequest, UpdateProfileRequest, UserProfileResponse
from app.users.service import UserService
from app.models.user import User
from app.utils.security import hash_password


def _make_user(password: str = "SecurePass1") -> User:
    u = User()
    u.id = uuid.uuid4()
    u.full_name = "Rahul Sharma"
    u.email = "rahul@example.com"
    u.password_hash = hash_password(password)
    u.is_active = True
    u.created_at = datetime.now(timezone.utc)
    u.updated_at = datetime.now(timezone.utc)
    return u


def _make_mock_db() -> AsyncMock:
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


class TestGetProfile:

    def test_returns_profile_response(self):
        user = _make_user()
        mock_db = _make_mock_db()
        service = UserService(mock_db)
        result = service.get_profile(user)
        assert isinstance(result, UserProfileResponse)
        assert result.email == user.email
        assert result.full_name == user.full_name
        assert not hasattr(result, "password_hash")

    def test_profile_contains_id(self):
        user = _make_user()
        mock_db = _make_mock_db()
        result = UserService(mock_db).get_profile(user)
        assert result.id == user.id


class TestUpdateProfile:

    @pytest.mark.asyncio
    async def test_update_full_name_success(self):
        user = _make_user()
        mock_db = _make_mock_db()
        updated_user = _make_user()
        updated_user.id = user.id
        updated_user.full_name = "New Name"

        with patch("app.users.service.UserRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_profile = AsyncMock(return_value=updated_user)
            repo.log_user_event = AsyncMock()
            mock_db.refresh = AsyncMock()

            service = UserService(mock_db)
            result = await service.update_profile(
                user=user,
                payload=UpdateProfileRequest(full_name="New Name"),
            )

        assert result.full_name == "New Name"
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_error_raises_500(self):
        user = _make_user()
        mock_db = _make_mock_db()

        with patch("app.users.service.UserRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_profile = AsyncMock(side_effect=Exception("DB down"))

            service = UserService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.update_profile(
                    user=user,
                    payload=UpdateProfileRequest(full_name="New Name"),
                )
        assert exc.value.status_code == 500


class TestChangePassword:

    @pytest.mark.asyncio
    async def test_correct_current_password_succeeds(self):
        user = _make_user(password="OldPass1")
        mock_db = _make_mock_db()

        with patch("app.users.service.UserRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_password = AsyncMock()
            repo.log_user_event = AsyncMock()

            service = UserService(mock_db)
            await service.change_password(
                user=user,
                payload=ChangePasswordRequest(
                    current_password="OldPass1",
                    new_password="NewPass1",
                    confirm_password="NewPass1",
                ),
            )

        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_wrong_current_password_raises_400(self):
        user = _make_user(password="OldPass1")
        mock_db = _make_mock_db()

        with patch("app.users.service.UserRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_password = AsyncMock()

            service = UserService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.change_password(
                    user=user,
                    payload=ChangePasswordRequest(
                        current_password="WrongPass1",
                        new_password="NewPass1",
                        confirm_password="NewPass1",
                    ),
                )
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_db_error_during_password_update_raises_500(self):
        user = _make_user(password="OldPass1")
        mock_db = _make_mock_db()

        with patch("app.users.service.UserRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.update_password = AsyncMock(side_effect=Exception("DB error"))

            service = UserService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.change_password(
                    user=user,
                    payload=ChangePasswordRequest(
                        current_password="OldPass1",
                        new_password="NewPass1",
                        confirm_password="NewPass1",
                    ),
                )
        assert exc.value.status_code == 500
