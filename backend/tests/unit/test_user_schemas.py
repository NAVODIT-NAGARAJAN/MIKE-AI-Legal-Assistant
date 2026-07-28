"""
Unit Tests — User Management Schemas (Pydantic Validation)
============================================================
Tests for app/users/schemas.py.
No database or HTTP required.
"""

import pytest
from pydantic import ValidationError

from app.users.schemas import ChangePasswordRequest, UpdateProfileRequest


class TestUpdateProfileRequest:

    def test_valid_full_name_accepted(self):
        r = UpdateProfileRequest(full_name="Rahul Sharma")
        assert r.full_name == "Rahul Sharma"

    def test_full_name_is_stripped(self):
        r = UpdateProfileRequest(full_name="  Priya  ")
        assert r.full_name == "Priya"

    def test_missing_all_fields_raises(self):
        with pytest.raises(ValidationError) as exc:
            UpdateProfileRequest()
        assert "At least one field" in str(exc.value)

    def test_whitespace_only_name_raises(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(full_name="   ")

    def test_name_too_short_raises(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(full_name="A")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            UpdateProfileRequest(full_name="A" * 101)


class TestChangePasswordRequest:

    def _valid(self, **kwargs):
        defaults = dict(
            current_password="OldPass1",
            new_password="NewPass1",
            confirm_password="NewPass1",
        )
        defaults.update(kwargs)
        return ChangePasswordRequest(**defaults)

    def test_valid_payload_accepted(self):
        r = self._valid()
        assert r.new_password == "NewPass1"

    def test_mismatched_confirm_raises(self):
        with pytest.raises(ValidationError) as exc:
            self._valid(confirm_password="DifferentPass1")
        assert "do not match" in str(exc.value)

    def test_same_current_and_new_raises(self):
        with pytest.raises(ValidationError) as exc:
            self._valid(current_password="SamePass1", new_password="SamePass1", confirm_password="SamePass1")
        assert "different" in str(exc.value)

    def test_new_password_no_uppercase_raises(self):
        with pytest.raises(ValidationError) as exc:
            self._valid(new_password="newpass1", confirm_password="newpass1")
        assert "uppercase" in str(exc.value)

    def test_new_password_no_lowercase_raises(self):
        with pytest.raises(ValidationError) as exc:
            self._valid(new_password="NEWPASS1", confirm_password="NEWPASS1")
        assert "lowercase" in str(exc.value)

    def test_new_password_no_digit_raises(self):
        with pytest.raises(ValidationError) as exc:
            self._valid(new_password="NewPassword", confirm_password="NewPassword")
        assert "digit" in str(exc.value)

    def test_new_password_too_short_raises(self):
        with pytest.raises(ValidationError):
            self._valid(new_password="Np1", confirm_password="Np1")

    def test_empty_current_password_raises(self):
        with pytest.raises(ValidationError):
            self._valid(current_password="")
