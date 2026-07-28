"""
Unit Tests — Consumer Case Service (Business Logic)
"""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.cases.schemas import CreateCaseRequest, UpdateCaseRequest
from app.cases.service import CaseService
from app.models.consumer_case import CaseStatus, ConsumerCase, IssueCategory
from app.models.user import User


def _make_user() -> User:
    u = User()
    u.id = uuid.uuid4()
    u.full_name = "Rahul Sharma"
    u.email = "rahul@example.com"
    u.password_hash = "hashed"
    u.is_active = True
    u.created_at = datetime.now(timezone.utc)
    u.updated_at = datetime.now(timezone.utc)
    return u


def _make_case(user_id: uuid.UUID, status: CaseStatus = CaseStatus.OPEN) -> ConsumerCase:
    c = ConsumerCase()
    c.id = uuid.uuid4()
    c.user_id = user_id
    c.title = "Defective product received from seller"
    c.description = "I received a completely damaged product that does not work."
    c.category = IssueCategory.DEFECTIVE_PRODUCT
    c.product_or_service = "Samsung TV"
    c.seller_name = None
    c.purchase_date = None
    c.status = status
    c.created_at = datetime.now(timezone.utc)
    c.updated_at = datetime.now(timezone.utc)
    return c


def _mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    return db


class TestCreateCase:

    @pytest.mark.asyncio
    async def test_create_case_success(self):
        user = _make_user()
        case = _make_case(user.id)
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create = AsyncMock(return_value=case)

            svc = CaseService(db)
            result = await svc.create_case(
                user=user,
                payload=CreateCaseRequest(
                    title="Defective product received from seller",
                    description="I received a completely damaged product that does not work.",
                    category=IssueCategory.DEFECTIVE_PRODUCT,
                    product_or_service="Samsung TV",
                ),
            )

        assert result.category == IssueCategory.DEFECTIVE_PRODUCT
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_case_db_error_raises_500(self):
        user = _make_user()
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.create = AsyncMock(side_effect=Exception("DB down"))

            svc = CaseService(db)
            with pytest.raises(HTTPException) as exc:
                await svc.create_case(
                    user=user,
                    payload=CreateCaseRequest(
                        title="Defective product received from seller",
                        description="I received a completely damaged product that does not work.",
                        category=IssueCategory.DEFECTIVE_PRODUCT,
                        product_or_service="Samsung TV",
                    ),
                )
        assert exc.value.status_code == 500


class TestGetCase:

    @pytest.mark.asyncio
    async def test_get_case_found(self):
        user = _make_user()
        case = _make_case(user.id)
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=case)

            result = await CaseService(db).get_case(user, case.id)
        assert result.id == case.id

    @pytest.mark.asyncio
    async def test_get_case_not_found_raises_404(self):
        user = _make_user()
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc:
                await CaseService(db).get_case(user, uuid.uuid4())
        assert exc.value.status_code == 404


class TestUpdateCase:

    @pytest.mark.asyncio
    async def test_update_title_success(self):
        user = _make_user()
        case = _make_case(user.id, CaseStatus.OPEN)
        updated = _make_case(user.id)
        updated.title = "Updated title here!"
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=case)
            repo.update = AsyncMock(return_value=updated)

            result = await CaseService(db).update_case(
                user, case.id, UpdateCaseRequest(title="Updated title here!")
            )
        assert result.title == "Updated title here!"

    @pytest.mark.asyncio
    async def test_update_closed_case_raises_422(self):
        user = _make_user()
        case = _make_case(user.id, CaseStatus.CLOSED)
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=case)

            with pytest.raises(HTTPException) as exc:
                await CaseService(db).update_case(
                    user, case.id, UpdateCaseRequest(title="New title attempt here")
                )
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_update_no_fields_raises_400(self):
        user = _make_user()
        db = _mock_db()

        with pytest.raises(HTTPException) as exc:
            await CaseService(db).update_case(
                user, uuid.uuid4(), UpdateCaseRequest()
            )
        assert exc.value.status_code == 400


class TestDeleteCase:

    @pytest.mark.asyncio
    async def test_delete_open_case_success(self):
        user = _make_user()
        case = _make_case(user.id, CaseStatus.OPEN)
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=case)
            repo.delete = AsyncMock()

            await CaseService(db).delete_case(user, case.id)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_report_generated_case_raises_422(self):
        user = _make_user()
        case = _make_case(user.id, CaseStatus.REPORT_GENERATED)
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=case)

            with pytest.raises(HTTPException) as exc:
                await CaseService(db).delete_case(user, case.id)
        assert exc.value.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_not_found_raises_404(self):
        user = _make_user()
        db = _mock_db()

        with patch("app.cases.service.CaseRepository") as MockRepo:
            repo = MockRepo.return_value
            repo.get_by_id_and_user = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc:
                await CaseService(db).delete_case(user, uuid.uuid4())
        assert exc.value.status_code == 404
