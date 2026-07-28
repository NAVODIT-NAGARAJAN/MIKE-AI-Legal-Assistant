"""
LegalEase AI - Consumer Case Schemas
======================================
Pydantic request/response models for the Consumer Case Management module.

All timestamps are UTC. Passwords are never included.
Authorization: only the owning user can access their own cases.
"""

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.consumer_case import CaseStatus, IssueCategory


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class CaseResponse(BaseModel):
    """Full consumer case representation returned by the API."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    category: IssueCategory
    product_or_service: str
    seller_name: Optional[str] = None
    purchase_date: Optional[date] = None
    status: CaseStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseListItem(BaseModel):
    """Lightweight case representation for list endpoints."""

    id: uuid.UUID
    title: str
    category: IssueCategory
    status: CaseStatus
    product_or_service: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class CreateCaseRequest(BaseModel):
    """
    Request body for POST /api/v1/cases.
    Creates a new consumer case for the authenticated user.
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        examples=["Defective smartphone received from Amazon"],
        description="Short, descriptive title of the issue (5–255 chars).",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=5000,
        examples=["I received a damaged smartphone on 2024-01-15..."],
        description="Detailed description of the consumer issue (20–5000 chars).",
    )
    category: IssueCategory = Field(
        ...,
        description="Issue category from the supported list.",
    )
    product_or_service: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the product or service involved.",
    )
    seller_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Name of the seller or service provider (optional).",
    )
    purchase_date: Optional[date] = Field(
        default=None,
        description="Date of purchase or service (optional, ISO 8601 format).",
    )

    @field_validator("title", "product_or_service")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be blank.")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description must not be blank.")
        return v.strip()

    @field_validator("purchase_date")
    @classmethod
    def purchase_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Purchase date cannot be in the future.")
        return v

    model_config = {"str_strip_whitespace": True}


class UpdateCaseRequest(BaseModel):
    """
    Request body for PUT /api/v1/cases/{case_id}.
    Partial update — only provided fields are changed.
    Status transitions are handled separately via PATCH /status.
    """

    title: Optional[str] = Field(
        default=None, min_length=5, max_length=255,
        description="Updated title (optional).",
    )
    description: Optional[str] = Field(
        default=None, min_length=20, max_length=5000,
        description="Updated description (optional).",
    )
    product_or_service: Optional[str] = Field(
        default=None, min_length=2, max_length=255,
        description="Updated product or service name (optional).",
    )
    seller_name: Optional[str] = Field(
        default=None, max_length=255,
        description="Updated seller name (optional).",
    )
    purchase_date: Optional[date] = Field(
        default=None,
        description="Updated purchase date (optional).",
    )

    @field_validator("purchase_date")
    @classmethod
    def purchase_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Purchase date cannot be in the future.")
        return v

    def has_updates(self) -> bool:
        """Return True if at least one field has a non-None value."""
        return any(v is not None for v in self.model_dump().values())
