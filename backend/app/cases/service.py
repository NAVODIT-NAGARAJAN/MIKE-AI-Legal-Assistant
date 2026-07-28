"""
LegalEase AI - Consumer Case Service
=======================================
Business logic layer for Consumer Case Management.

Authorization model:
    - Users can ONLY access/modify their own cases.
    - Ownership is enforced via scoped repository queries (user_id filter).
    - No admin bypass in this module.

Raises HTTPException — never raw SQLAlchemy errors to the caller.
"""

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.repository import CaseRepository
from app.cases.schemas import (
    CaseListItem,
    CaseResponse,
    CreateCaseRequest,
    UpdateCaseRequest,
)
from app.models.consumer_case import CaseStatus, ConsumerCase
from app.models.user import User
from app.utils.logger import get_logger

log = get_logger(__name__)


class CaseService:
    """
    Business logic for consumer case lifecycle.
    All methods accept the authenticated User from the JWT dependency.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = CaseRepository(db)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create_case(
        self, user: User, payload: CreateCaseRequest
    ) -> CaseResponse:
        """
        Create a new consumer case owned by the authenticated user.

        Args:
            user: Authenticated user from JWT dependency.
            payload: Validated CreateCaseRequest.

        Returns:
            CaseResponse with the persisted case data.

        Raises:
            HTTPException 500: On unexpected database failure.
        """
        log.info(f"Creating case for user={str(user.id)[:8]}... category={payload.category}")

        case = ConsumerCase(
            user_id=user.id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            product_or_service=payload.product_or_service,
            seller_name=payload.seller_name,
            purchase_date=payload.purchase_date,
            status=CaseStatus.OPEN,
        )

        try:
            created = await self._repo.create(case)
            await self._db.commit()
            await self._db.refresh(created)
        except Exception as exc:
            log.error(f"Failed to create case: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create case. Please try again.",
            )

        return CaseResponse.model_validate(created)

    # ------------------------------------------------------------------
    # Read — single
    # ------------------------------------------------------------------

    async def get_case(self, user: User, case_id: uuid.UUID) -> CaseResponse:
        """
        Retrieve a single case by ID, scoped to the authenticated user.

        Raises:
            HTTPException 404: If case not found or belongs to a different user.
        """
        case = await self._repo.get_by_id_and_user(case_id, user.id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found.",
            )
        return CaseResponse.model_validate(case)

    # ------------------------------------------------------------------
    # Read — list
    # ------------------------------------------------------------------

    async def list_cases(
        self,
        user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> dict:
        """
        List all cases for the authenticated user with pagination.

        Returns:
            Dict with 'items' (list of CaseListItem), 'total', 'skip', 'limit'.
        """
        cases = await self._repo.list_by_user(user.id, skip=skip, limit=limit)
        total = await self._repo.count_by_user(user.id)
        return {
            "items": [CaseListItem.model_validate(c) for c in cases],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update_case(
        self,
        user: User,
        case_id: uuid.UUID,
        payload: UpdateCaseRequest,
    ) -> CaseResponse:
        """
        Update mutable fields of an existing case.

        Authorization: case must belong to the authenticated user.

        Raises:
            HTTPException 404: Case not found or not owned by user.
            HTTPException 400: No update fields provided.
            HTTPException 422: Case is closed and cannot be modified.
            HTTPException 500: Unexpected DB failure.
        """
        if not payload.has_updates():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for an update.",
            )

        case = await self._repo.get_by_id_and_user(case_id, user.id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found.",
            )

        if case.status == CaseStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Closed cases cannot be modified.",
            )

        # Apply partial update
        if payload.title is not None:
            case.title = payload.title
        if payload.description is not None:
            case.description = payload.description
        if payload.product_or_service is not None:
            case.product_or_service = payload.product_or_service
        if payload.seller_name is not None:
            case.seller_name = payload.seller_name
        if payload.purchase_date is not None:
            case.purchase_date = payload.purchase_date

        try:
            updated = await self._repo.update(case)
            await self._db.commit()
            await self._db.refresh(updated)
        except Exception as exc:
            log.error(f"Failed to update case {case_id}: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update case. Please try again.",
            )

        return CaseResponse.model_validate(updated)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_case(self, user: User, case_id: uuid.UUID) -> None:
        """
        Delete a consumer case owned by the authenticated user.

        Raises:
            HTTPException 404: Case not found or not owned by user.
            HTTPException 422: Cannot delete a case with REPORT_GENERATED status.
            HTTPException 500: Unexpected DB failure.
        """
        case = await self._repo.get_by_id_and_user(case_id, user.id)
        if case is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found.",
            )

        if case.status == CaseStatus.REPORT_GENERATED:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cases with a generated report cannot be deleted.",
            )

        try:
            await self._repo.delete(case)
            await self._db.commit()
        except Exception as exc:
            log.error(f"Failed to delete case {case_id}: {type(exc).__name__}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete case. Please try again.",
            )
