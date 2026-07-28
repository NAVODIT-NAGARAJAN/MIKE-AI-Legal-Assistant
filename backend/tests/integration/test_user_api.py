"""
Integration Tests — User Management API Endpoints
===================================================
Tests for GET /api/v1/users/profile, PUT /api/v1/users/profile,
and POST /api/v1/users/change-password.

Uses the real FastAPI app with a SQLite test database (via conftest.py).
"""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _register_and_login(client: AsyncClient, email: str, password: str = "SecurePass1") -> dict:
    """Register a user and return {token, user_id}."""
    await client.post(
        "/api/v1/auth/register",
        json={"full_name": "Test User", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    data = resp.json()["data"]
    return {"token": data["access_token"], "user_id": str(data["user"]["id"])}


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /api/v1/users/profile
# ---------------------------------------------------------------------------

class TestGetProfile:

    @pytest.mark.asyncio
    async def test_get_profile_returns_200(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "getprofile@example.com")
        resp = await app_client.get("/api/v1/users/profile", headers=_auth(info["token"]))

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["email"] == "getprofile@example.com"
        assert "password_hash" not in body["data"]
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    @pytest.mark.asyncio
    async def test_get_profile_without_token_returns_403_or_401(self, app_client: AsyncClient):
        resp = await app_client.get("/api/v1/users/profile")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_profile_with_invalid_token_returns_401(self, app_client: AsyncClient):
        resp = await app_client.get(
            "/api/v1/users/profile",
            headers=_auth("invalid.token.here"),
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /api/v1/users/profile
# ---------------------------------------------------------------------------

class TestUpdateProfile:

    @pytest.mark.asyncio
    async def test_update_full_name_returns_200(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "updateprofile@example.com")
        resp = await app_client.put(
            "/api/v1/users/profile",
            headers=_auth(info["token"]),
            json={"full_name": "Updated Name"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["full_name"] == "Updated Name"
        assert body["data"]["email"] == "updateprofile@example.com"

    @pytest.mark.asyncio
    async def test_update_profile_reflects_in_get(self, app_client: AsyncClient):
        """Updating profile should be visible in subsequent GET."""
        info = await _register_and_login(app_client, "reflectupdate@example.com")
        await app_client.put(
            "/api/v1/users/profile",
            headers=_auth(info["token"]),
            json={"full_name": "Reflected Name"},
        )
        get_resp = await app_client.get("/api/v1/users/profile", headers=_auth(info["token"]))
        assert get_resp.json()["data"]["full_name"] == "Reflected Name"

    @pytest.mark.asyncio
    async def test_update_empty_body_returns_422(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "emptyupdate@example.com")
        resp = await app_client.put(
            "/api/v1/users/profile",
            headers=_auth(info["token"]),
            json={},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_profile_without_token_returns_403_or_401(self, app_client: AsyncClient):
        resp = await app_client.put("/api/v1/users/profile", json={"full_name": "Name"})
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_update_name_too_short_returns_422(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "shortname@example.com")
        resp = await app_client.put(
            "/api/v1/users/profile",
            headers=_auth(info["token"]),
            json={"full_name": "A"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_response_never_contains_password_hash(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "nopwhash@example.com")
        resp = await app_client.put(
            "/api/v1/users/profile",
            headers=_auth(info["token"]),
            json={"full_name": "Safe User"},
        )
        assert "password_hash" not in resp.text


# ---------------------------------------------------------------------------
# POST /api/v1/users/change-password
# ---------------------------------------------------------------------------

class TestChangePassword:

    @pytest.mark.asyncio
    async def test_change_password_success_returns_200(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "changepw@example.com", "OldPass1")
        resp = await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "OldPass1",
                "new_password": "NewPass2",
                "confirm_password": "NewPass2",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    @pytest.mark.asyncio
    async def test_changed_password_works_for_login(self, app_client: AsyncClient):
        """After changing password, old password must fail and new must succeed."""
        email = "newpwlogin@example.com"
        info = await _register_and_login(app_client, email, "OldPass1")
        await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "OldPass1",
                "new_password": "NewPass2",
                "confirm_password": "NewPass2",
            },
        )
        # New password must work
        new_login = await app_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "NewPass2"},
        )
        assert new_login.status_code == 200

        # Old password must fail
        old_login = await app_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "OldPass1"},
        )
        assert old_login.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_current_password_returns_400(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "wrongpw@example.com", "OldPass1")
        resp = await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "WrongPass9",
                "new_password": "NewPass2",
                "confirm_password": "NewPass2",
            },
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False

    @pytest.mark.asyncio
    async def test_mismatched_confirm_returns_422(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "mismatch@example.com", "OldPass1")
        resp = await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "OldPass1",
                "new_password": "NewPass2",
                "confirm_password": "Different3",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_same_password_returns_422(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "samepw@example.com", "OldPass1")
        resp = await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "OldPass1",
                "new_password": "OldPass1",
                "confirm_password": "OldPass1",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_without_token_returns_403_or_401(self, app_client: AsyncClient):
        resp = await app_client.post(
            "/api/v1/users/change-password",
            json={
                "current_password": "OldPass1",
                "new_password": "NewPass2",
                "confirm_password": "NewPass2",
            },
        )
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_weak_new_password_returns_422(self, app_client: AsyncClient):
        info = await _register_and_login(app_client, "weaknew@example.com", "OldPass1")
        resp = await app_client.post(
            "/api/v1/users/change-password",
            headers=_auth(info["token"]),
            json={
                "current_password": "OldPass1",
                "new_password": "weakpassword",
                "confirm_password": "weakpassword",
            },
        )
        assert resp.status_code == 422
