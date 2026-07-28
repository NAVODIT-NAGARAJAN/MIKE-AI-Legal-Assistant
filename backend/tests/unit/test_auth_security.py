"""
Unit Tests — Security Utilities (hash_password, verify_password, JWT)
=======================================================================
Tests for app/utils/security.py.
No database or HTTP server required — pure Python unit tests.
"""

from datetime import timedelta

import pytest
from jose import JWTError

from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)


# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------

class TestHashPassword:
    """Tests for hash_password()."""

    def test_hash_returns_non_empty_string(self):
        result = hash_password("SecurePass1")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_is_bcrypt_format(self):
        """bcrypt hashes always start with $2b$."""
        result = hash_password("SecurePass1")
        assert result.startswith("$2b$") or result.startswith("$2a$")

    def test_hash_is_different_each_call(self):
        """bcrypt uses random salt — two hashes of the same password differ."""
        h1 = hash_password("SecurePass1")
        h2 = hash_password("SecurePass1")
        assert h1 != h2

    def test_hash_does_not_contain_plain_password(self):
        plain = "SecurePass1"
        result = hash_password(plain)
        assert plain not in result


class TestVerifyPassword:
    """Tests for verify_password()."""

    def test_correct_password_returns_true(self):
        plain = "SecurePass1"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("SecurePass1")
        assert verify_password("WrongPass99", hashed) is False

    def test_empty_string_does_not_match(self):
        hashed = hash_password("SecurePass1")
        assert verify_password("", hashed) is False

    def test_case_sensitive(self):
        hashed = hash_password("SecurePass1")
        assert verify_password("securepass1", hashed) is False

    def test_similar_password_does_not_match(self):
        hashed = hash_password("SecurePass1")
        assert verify_password("SecurePass12", hashed) is False


# ---------------------------------------------------------------------------
# JWT Token Creation & Decoding
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    """Tests for create_access_token()."""

    def test_returns_non_empty_string(self):
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_has_three_segments(self):
        """Valid JWT always has exactly 3 dot-separated segments."""
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
        )
        segments = token.split(".")
        assert len(segments) == 3

    def test_custom_expiry(self):
        """Token created with custom TTL should be decodable."""
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            expires_delta=timedelta(hours=2),
        )
        payload = decode_access_token(token)
        assert payload["sub"] == "123e4567-e89b-12d3-a456-426614174000"


class TestDecodeAccessToken:
    """Tests for decode_access_token()."""

    def test_valid_token_returns_correct_payload(self):
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        payload = decode_access_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["type"] == "access"

    def test_expired_token_raises_jwt_error(self):
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_tampered_token_raises_jwt_error(self):
        token = create_access_token(
            user_id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
        )
        # Corrupt the signature segment
        parts = token.split(".")
        parts[2] = parts[2][::-1]  # Reverse the signature
        tampered = ".".join(parts)

        with pytest.raises(JWTError):
            decode_access_token(tampered)

    def test_completely_invalid_token_raises_jwt_error(self):
        with pytest.raises(JWTError):
            decode_access_token("not.a.jwt")

    def test_empty_string_raises_jwt_error(self):
        with pytest.raises(JWTError):
            decode_access_token("")


# ---------------------------------------------------------------------------
# Password Strength Validation
# ---------------------------------------------------------------------------

class TestValidatePasswordStrength:
    """Tests for validate_password_strength()."""

    def test_strong_password_is_valid(self):
        is_valid, msg = validate_password_strength("SecurePass1")
        assert is_valid is True
        assert msg == ""

    def test_too_short_fails(self):
        is_valid, msg = validate_password_strength("Sh0rt")
        assert is_valid is False
        assert "8 characters" in msg

    def test_no_uppercase_fails(self):
        is_valid, msg = validate_password_strength("securepass1")
        assert is_valid is False
        assert "uppercase" in msg.lower()

    def test_no_lowercase_fails(self):
        is_valid, msg = validate_password_strength("SECUREPASS1")
        assert is_valid is False
        assert "lowercase" in msg.lower()

    def test_no_digit_fails(self):
        is_valid, msg = validate_password_strength("SecurePassWord")
        assert is_valid is False
        assert "digit" in msg.lower()

    def test_minimum_valid_password(self):
        """Exactly 8 chars, mixed case, one digit."""
        is_valid, msg = validate_password_strength("Secure1x")
        assert is_valid is True
