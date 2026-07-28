"""
Integration Tests — Authentication API Endpoints
==================================================
Tests for POST /api/v1/auth/register, /login, /logout.

These tests use the real FastAPI application with a real async
database session (SQLite in-memory via conftest.py fixtures).

Each test runs in an isolated database transaction that is
rolled back after the test completes.
"""

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------

class TestRegisterEndpoint:
    """Integration tests for POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success_returns_201(self, app_client: AsyncClient):
        """Valid registration payload → 201 Created with user data."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Rahul Sharma",
                "email": "rahul.test@example.com",
                "password": "SecurePass1",
            },
        )
        assert response.status_code == 201

        body = response.json()
        assert body["success"] is True
        assert "Registration successful" in body["message"]
        assert body["data"]["email"] == "rahul.test@example.com"
        assert body["data"]["full_name"] == "Rahul Sharma"
        assert "password_hash" not in body["data"]
        assert "password" not in body["data"]
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_409(self, app_client: AsyncClient):
        """Registering the same email twice → 409 Conflict."""
        payload = {
            "full_name": "Priya Singh",
            "email": "priya.test@example.com",
            "password": "SecurePass1",
        }

        # First registration — should succeed
        r1 = await app_client.post("/api/v1/auth/register", json=payload)
        assert r1.status_code == 201

        # Second registration with same email — should conflict
        r2 = await app_client.post("/api/v1/auth/register", json=payload)
        assert r2.status_code == 409
        assert r2.json()["success"] is False

    @pytest.mark.asyncio
    async def test_register_missing_full_name_returns_422(self, app_client: AsyncClient):
        """Missing required full_name field → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 422
        body = response.json()
        assert body["success"] is False

    @pytest.mark.asyncio
    async def test_register_invalid_email_returns_422(self, app_client: AsyncClient):
        """Invalid email format → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Test User",
                "email": "not-an-email",
                "password": "SecurePass1",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password_no_uppercase_returns_422(
        self, app_client: AsyncClient
    ):
        """Password without uppercase → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Test User",
                "email": "weak@example.com",
                "password": "weakpass1",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password_returns_422(self, app_client: AsyncClient):
        """Password < 8 chars → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Test User",
                "email": "short@example.com",
                "password": "Sh0rt",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_body_returns_422(self, app_client: AsyncClient):
        """Empty request body → 422 Unprocessable Entity."""
        response = await app_client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_response_never_contains_password(
        self, app_client: AsyncClient
    ):
        """Ensure password fields are never in the response body."""
        response = await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Secure User",
                "email": "secure.nopass@example.com",
                "password": "SecurePass1",
            },
        )
        raw_text = response.text
        assert "password_hash" not in raw_text
        assert "SecurePass1" not in raw_text


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------

class TestLoginEndpoint:
    """Integration tests for POST /api/v1/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success_returns_200_with_token(self, app_client: AsyncClient):
        """Valid credentials after registration → 200 with JWT token."""
        # First register
        await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Login User",
                "email": "loginuser@example.com",
                "password": "SecurePass1",
            },
        )

        # Then login
        response = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "loginuser@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 200

        body = response.json()
        assert body["success"] is True
        assert "Login successful" in body["message"]
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"
        assert body["data"]["expires_in"] > 0
        assert body["data"]["user"]["email"] == "loginuser@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password_returns_401(self, app_client: AsyncClient):
        """Correct email, wrong password → 401 Unauthorized."""
        # Register user
        await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Password Test",
                "email": "pwtest@example.com",
                "password": "SecurePass1",
            },
        )

        response = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "pwtest@example.com", "password": "WrongPass99"},
        )
        assert response.status_code == 401
        assert response.json()["success"] is False

    @pytest.mark.asyncio
    async def test_login_unknown_email_returns_401(self, app_client: AsyncClient):
        """Email not in database → 401 Unauthorized."""
        response = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "SecurePass1"},
        )
        assert response.status_code == 401
        assert response.json()["success"] is False

    @pytest.mark.asyncio
    async def test_login_error_messages_are_identical(self, app_client: AsyncClient):
        """Wrong email and wrong password return the SAME error (anti-enumeration)."""
        # Register
        await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Enum Test",
                "email": "enumtest@example.com",
                "password": "SecurePass1",
            },
        )

        r_bad_email = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@example.com", "password": "SecurePass1"},
        )
        r_bad_pass = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "enumtest@example.com", "password": "WrongPass99"},
        )

        assert r_bad_email.json()["message"] == r_bad_pass.json()["message"]

    @pytest.mark.asyncio
    async def test_login_missing_email_returns_422(self, app_client: AsyncClient):
        """Missing email → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/login",
            json={"password": "SecurePass1"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_password_returns_422(self, app_client: AsyncClient):
        """Missing password → 422 Unprocessable Entity."""
        response = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_response_has_no_password_fields(self, app_client: AsyncClient):
        """Ensure password fields never appear in login response."""
        await app_client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Secure Login",
                "email": "securelg@example.com",
                "password": "SecurePass1",
            },
        )
        response = await app_client.post(
            "/api/v1/auth/login",
            json={"email": "securelg@example.com", "password": "SecurePass1"},
        )
        raw_text = response.text
        assert "password_hash" not in raw_text
        assert "SecurePass1" not in raw_text


# ---------------------------------------------------------------------------
# POST /api/v1/auth/logout
# ---------------------------------------------------------------------------

class TestLogoutEndpoint:
    """Integration tests for POST /api/v1/auth/logout."""

    async def _register_and_login(self, client: AsyncClient, email: str) -> str:
        """Helper: register a user and return their JWT access token."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Logout Test User",
                "email": email,
                "password": "SecurePass1",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "SecurePass1"},
        )
        return login_resp.json()["data"]["access_token"]

    @pytest.mark.asyncio
    async def test_logout_with_valid_token_returns_200(self, app_client: AsyncClient):
        """Valid JWT → 200 OK with confirmation message."""
        token = await self._register_and_login(
            app_client, "logout.valid@example.com"
        )
        response = await app_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "logged out" in body["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_without_token_returns_403_or_401(
        self, app_client: AsyncClient
    ):
        """No Authorization header → 401 or 403 (FastAPI HTTPBearer default)."""
        response = await app_client.post("/api/v1/auth/logout")
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token_returns_401(
        self, app_client: AsyncClient
    ):
        """Invalid JWT → 401 Unauthorized."""
        response = await app_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer this.is.invalid"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_malformed_bearer_returns_401_or_403(
        self, app_client: AsyncClient
    ):
        """Malformed Authorization header → 401 or 403."""
        response = await app_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "NotBearer some_token"},
        )
        assert response.status_code in (401, 403)
