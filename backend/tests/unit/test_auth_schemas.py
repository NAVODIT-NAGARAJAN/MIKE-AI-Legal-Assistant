"""
Unit Tests — Authentication Schemas (Pydantic Validation)
===========================================================
Tests for app/auth/schemas.py.
Validates that request bodies are correctly accepted or rejected
before reaching the service layer.
No database or HTTP server required.
"""

import pytest
from pydantic import ValidationError

from app.auth.schemas import LoginRequest, RegisterRequest


# ---------------------------------------------------------------------------
# RegisterRequest
# ---------------------------------------------------------------------------

class TestRegisterRequest:
    """Tests for RegisterRequest Pydantic schema."""

    # --- Happy path ---

    def test_valid_payload_is_accepted(self):
        payload = RegisterRequest(
            full_name="Rahul Sharma",
            email="rahul@example.com",
            password="SecurePass1",
        )
        assert payload.full_name == "Rahul Sharma"
        assert payload.email == "rahul@example.com"
        assert payload.password == "SecurePass1"

    def test_full_name_is_stripped(self):
        payload = RegisterRequest(
            full_name="  Rahul Sharma  ",
            email="rahul@example.com",
            password="SecurePass1",
        )
        assert payload.full_name == "Rahul Sharma"

    # --- Missing fields ---

    def test_missing_full_name_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(email="rahul@example.com", password="SecurePass1")
        assert "full_name" in str(exc_info.value)

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(full_name="Rahul Sharma", password="SecurePass1")
        assert "email" in str(exc_info.value)

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(full_name="Rahul Sharma", email="rahul@example.com")
        assert "password" in str(exc_info.value)

    # --- Email validation ---

    def test_invalid_email_format_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                full_name="Rahul Sharma",
                email="not-an-email",
                password="SecurePass1",
            )

    def test_email_without_domain_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                full_name="Rahul Sharma",
                email="rahul@",
                password="SecurePass1",
            )

    # --- Password validation ---

    def test_short_password_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                full_name="Rahul Sharma",
                email="rahul@example.com",
                password="Sh0rt",
            )
        errors = str(exc_info.value)
        assert "password" in errors

    def test_password_without_uppercase_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                full_name="Rahul Sharma",
                email="rahul@example.com",
                password="securepass1",
            )
        assert "uppercase" in str(exc_info.value).lower()

    def test_password_without_lowercase_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                full_name="Rahul Sharma",
                email="rahul@example.com",
                password="SECUREPASS1",
            )
        assert "lowercase" in str(exc_info.value).lower()

    def test_password_without_digit_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                full_name="Rahul Sharma",
                email="rahul@example.com",
                password="SecurePassword",
            )
        assert "digit" in str(exc_info.value).lower()

    # --- full_name validation ---

    def test_whitespace_only_name_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                full_name="   ",
                email="rahul@example.com",
                password="SecurePass1",
            )

    def test_name_too_short_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                full_name="R",
                email="rahul@example.com",
                password="SecurePass1",
            )

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                full_name="R" * 101,
                email="rahul@example.com",
                password="SecurePass1",
            )


# ---------------------------------------------------------------------------
# LoginRequest
# ---------------------------------------------------------------------------

class TestLoginRequest:
    """Tests for LoginRequest Pydantic schema."""

    def test_valid_payload_is_accepted(self):
        payload = LoginRequest(
            email="rahul@example.com",
            password="SecurePass1",
        )
        assert payload.email == "rahul@example.com"
        assert payload.password == "SecurePass1"

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(password="SecurePass1")
        assert "email" in str(exc_info.value)

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="rahul@example.com")
        assert "password" in str(exc_info.value)

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="invalid", password="SecurePass1")

    def test_empty_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="rahul@example.com", password="")
