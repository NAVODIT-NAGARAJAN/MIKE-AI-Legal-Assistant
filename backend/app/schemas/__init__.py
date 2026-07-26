"""
LegalEase AI - Schemas Package
================================
Exports all Pydantic request/response schemas.
"""

from app.schemas.response import (
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
    PaginatedResponse,
    success_response,
    error_response,
)

__all__ = [
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "PaginatedResponse",
    "success_response",
    "error_response",
]
