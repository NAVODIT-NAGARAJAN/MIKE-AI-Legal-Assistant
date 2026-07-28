"""
Unit Tests — Consumer Case Schemas
"""
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.cases.schemas import CreateCaseRequest, UpdateCaseRequest
from app.models.consumer_case import IssueCategory


def _valid_create(**kwargs):
    defaults = dict(
        title="Defective product received from seller",
        description="I received a completely damaged product that does not work at all.",
        category=IssueCategory.DEFECTIVE_PRODUCT,
        product_or_service="Samsung TV",
    )
    defaults.update(kwargs)
    return CreateCaseRequest(**defaults)


class TestCreateCaseRequest:

    def test_valid_minimal_payload(self):
        r = _valid_create()
        assert r.category == IssueCategory.DEFECTIVE_PRODUCT

    def test_title_stripped(self):
        r = _valid_create(title="  Valid Title Here  ")
        assert r.title == "Valid Title Here"

    def test_title_too_short_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(title="Hi")

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(title="A" * 256)

    def test_description_too_short_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(description="Too short")

    def test_description_too_long_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(description="A" * 5001)

    def test_blank_title_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(title="     ")

    def test_future_purchase_date_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(purchase_date=date.today() + timedelta(days=1))

    def test_past_purchase_date_valid(self):
        r = _valid_create(purchase_date=date(2024, 1, 15))
        assert r.purchase_date == date(2024, 1, 15)

    def test_optional_fields_default_to_none(self):
        r = _valid_create()
        assert r.seller_name is None
        assert r.purchase_date is None

    def test_all_categories_accepted(self):
        for cat in IssueCategory:
            r = _valid_create(category=cat)
            assert r.category == cat

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            _valid_create(category="INVALID_CATEGORY")


class TestUpdateCaseRequest:

    def test_empty_update_has_no_updates(self):
        r = UpdateCaseRequest()
        assert r.has_updates() is False

    def test_single_field_has_updates(self):
        r = UpdateCaseRequest(title="New title here!")
        assert r.has_updates() is True

    def test_title_too_short_raises(self):
        with pytest.raises(ValidationError):
            UpdateCaseRequest(title="Hi")

    def test_future_purchase_date_raises(self):
        with pytest.raises(ValidationError):
            UpdateCaseRequest(purchase_date=date.today() + timedelta(days=1))

    def test_all_none_fields(self):
        r = UpdateCaseRequest(title=None, description=None)
        assert r.has_updates() is False
