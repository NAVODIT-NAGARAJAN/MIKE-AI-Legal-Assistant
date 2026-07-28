"""
LegalEase AI - Consumer Case Router
=======================================
FastAPI route handlers for Consumer Case Management.

All endpoints are protected (JWT required).
Users can only access their own cases.

Endpoints:
    POST   /api/v1/cases              — Create a new case
    GET    /api/v1/cases              — List all cases for the current user
    GET    /api/v1/cases/{case_id}    — Get a specific case
    PUT    /api/v1/cases/{case_id}    — Update a case
    DELETE /api/v1/cases/{case_id}    — Delete a case
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.cases.schemas import (
    CaseListItem,
    CaseResponse,
    CreateCaseRequest,
    UpdateCaseRequest,
)
from app.cases.service import CaseService
from app.database.connection import get_db
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /cases — Create
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=SuccessResponse[CaseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new consumer case",
    responses={
        201: {"description": "Case created successfully."},
        401: {"description": "Unauthorized."},
        422: {"description": "Validation error."},
        500: {"description": "Internal server error."},
    },
)
async def create_case(
    payload: CreateCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[CaseResponse]:
    """
    Create a new consumer case.

    - **title**: Short issue description (5–255 chars).
    - **description**: Detailed description (20–5000 chars).
    - **category**: One of the 8 supported issue categories.
    - **product_or_service**: Name of the product or service involved.
    - **seller_name**: Optional seller name.
    - **purchase_date**: Optional ISO date of purchase (cannot be future).

    Requires: `Authorization: Bearer <token>` header.
    """
    service = CaseService(db)
    case = await service.create_case(user=current_user, payload=payload)
    return SuccessResponse(message="Case created successfully.", data=case)


# ---------------------------------------------------------------------------
# GET /cases — List
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List all cases for the current user",
    responses={
        200: {"description": "Cases retrieved successfully."},
        401: {"description": "Unauthorized."},
    },
)
async def list_cases(
    skip: int = Query(default=0, ge=0, description="Pagination offset."),
    limit: int = Query(default=20, ge=1, le=100, description="Max results (1–100)."),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[dict[str, Any]]:
    """
    List all consumer cases for the authenticated user.

    - Results ordered by creation date (newest first).
    - Supports pagination via `skip` and `limit` query parameters.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = CaseService(db)
    result = await service.list_cases(user=current_user, skip=skip, limit=limit)
    return SuccessResponse(message="Cases retrieved successfully.", data=result)


# ---------------------------------------------------------------------------
# GET /cases/{case_id} — Single
# ---------------------------------------------------------------------------

@router.get(
    "/{case_id}",
    response_model=SuccessResponse[CaseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get a specific consumer case",
    responses={
        200: {"description": "Case retrieved successfully."},
        401: {"description": "Unauthorized."},
        404: {"description": "Case not found."},
    },
)
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[CaseResponse]:
    """
    Retrieve a specific consumer case by ID.

    Only accessible by the case owner.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = CaseService(db)
    case = await service.get_case(user=current_user, case_id=case_id)
    return SuccessResponse(message="Case retrieved successfully.", data=case)


# ---------------------------------------------------------------------------
# PUT /cases/{case_id} — Update
# ---------------------------------------------------------------------------

@router.put(
    "/{case_id}",
    response_model=SuccessResponse[CaseResponse],
    status_code=status.HTTP_200_OK,
    summary="Update a consumer case",
    responses={
        200: {"description": "Case updated successfully."},
        400: {"description": "No fields provided."},
        401: {"description": "Unauthorized."},
        404: {"description": "Case not found."},
        422: {"description": "Closed cases cannot be modified."},
    },
)
async def update_case(
    case_id: uuid.UUID,
    payload: UpdateCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[CaseResponse]:
    """
    Update mutable fields of a consumer case.

    - Category and status cannot be changed via this endpoint.
    - Closed cases cannot be modified.
    - Only the case owner can update.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = CaseService(db)
    case = await service.update_case(user=current_user, case_id=case_id, payload=payload)
    return SuccessResponse(message="Case updated successfully.", data=case)


# ---------------------------------------------------------------------------
# DELETE /cases/{case_id} — Delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{case_id}",
    response_model=SuccessResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete a consumer case",
    responses={
        200: {"description": "Case deleted successfully."},
        401: {"description": "Unauthorized."},
        404: {"description": "Case not found."},
        422: {"description": "Cannot delete a case with a generated report."},
    },
)
async def delete_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[None]:
    """
    Delete a consumer case.

    - Cases with a generated report cannot be deleted.
    - Only the case owner can delete.

    Requires: `Authorization: Bearer <token>` header.
    """
    service = CaseService(db)
    await service.delete_case(user=current_user, case_id=case_id)
    return SuccessResponse(message="Case deleted successfully.", data=None)