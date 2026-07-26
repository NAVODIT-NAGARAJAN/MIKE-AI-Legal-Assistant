"""
LegalEase AI - Standard API Response Models
=============================================
Enforces consistent response shapes for all API endpoints.
Every response follows the structure defined in api.md.

Success:  { "success": true, "message": "...", "data": {...} }
Error:    { "success": false, "message": "...", "errors": [...] }
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response wrapper.
    Used by all endpoints that return data.
    """
    success: bool = True
    message: str
    data: Optional[T] = None

    model_config = {"arbitrary_types_allowed": True}


class ErrorDetail(BaseModel):
    """Single validation or domain error detail."""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """
    Standard error response wrapper.
    Used by exception handlers and validation failures.
    """
    success: bool = False
    message: str
    errors: List[ErrorDetail] = []


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated response wrapper for list endpoints.
    """
    success: bool = True
    message: str
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


def success_response(
    message: str,
    data: Any = None,
) -> dict:
    """
    Helper to build a success response dict.
    Use as: return success_response("User created", data=user_dict)
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    errors: Optional[List[dict]] = None,
) -> dict:
    """
    Helper to build an error response dict.
    Use as: return error_response("Validation failed", errors=[...])
    """
    return {
        "success": False,
        "message": message,
        "errors": errors or [],
    }
