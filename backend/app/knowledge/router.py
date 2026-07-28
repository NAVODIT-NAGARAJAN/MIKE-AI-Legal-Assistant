"""
LegalEase AI - Knowledge Base Router
=======================================
API endpoints for knowledge base search and status.

Endpoints:
    POST /api/v1/knowledge/search  — Semantic search over legal documents
    GET  /api/v1/knowledge/status  — Knowledge base status (chunk count, etc.)

Search requires JWT authentication.
Status is public (useful for health checks).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_active_user
from app.knowledge.schemas import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeStatusResponse,
    RetrievalResultSchema,
)
from app.knowledge.service import KnowledgeBaseService
from app.models.user import User
from app.schemas.response import SuccessResponse
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.post(
    "/search",
    response_model=SuccessResponse[KnowledgeSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search the legal knowledge base",
    description=(
        "Perform semantic search against the Indian consumer rights knowledge base. "
        "Returns the most relevant legal text chunks for the given query. "
        "Requires JWT authentication."
    ),
    responses={
        200: {"description": "Search results returned successfully."},
        400: {"description": "Invalid query or empty knowledge base."},
        401: {"description": "Unauthorized."},
    },
)
async def search_knowledge(
    payload: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_active_user),
) -> SuccessResponse[KnowledgeSearchResponse]:
    """
    Semantic search over the legal knowledge base.

    - **query**: Natural language question (3–500 chars).
    - **top_k**: Number of results to return (1–10, default 5).
    - **source_type**: Optional filter — 'act', 'rules', or 'guidance'.
    """
    service = KnowledgeBaseService()
    try:
        results = service.retrieve(
            query=payload.query,
            top_k=payload.top_k,
            source_type_filter=payload.source_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    response = KnowledgeSearchResponse(
        query=payload.query,
        results=[RetrievalResultSchema(**r.to_dict()) for r in results],
        total_results=len(results),
    )
    return SuccessResponse(
        message=f"Found {len(results)} relevant legal sections.",
        data=response,
    )


@router.get(
    "/status",
    response_model=SuccessResponse[KnowledgeStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Knowledge base status",
    description="Returns the current state of the ChromaDB knowledge base.",
)
async def knowledge_status() -> SuccessResponse[KnowledgeStatusResponse]:
    """Return knowledge base status — total chunks and readiness."""
    service = KnowledgeBaseService()
    status_data = service.get_status()

    response = KnowledgeStatusResponse(
        status=status_data.get("status", "unknown"),
        total_chunks=status_data.get("total_chunks", 0),
        collection_name=status_data.get("collection_name", ""),
    )
    return SuccessResponse(
        message="Knowledge base status retrieved.",
        data=response,
    )