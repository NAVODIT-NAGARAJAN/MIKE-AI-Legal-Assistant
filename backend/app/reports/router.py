"""
LegalEase AI - Reports API Router
====================================
Endpoints for report generation and retrieval.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_agent.repository import ConversationRepository
from app.auth.dependencies import get_current_active_user
from app.database.connection import get_db
from app.models.user import User
from app.reports.repository import ReportRepository
from app.reports.schemas import ReportResponseSchema
from app.reports.service import ReportService
from app.schemas.response import SuccessResponse
from app.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    report_repo = ReportRepository(db)
    conv_repo = ConversationRepository(db)
    return ReportService(report_repo, conv_repo)


@router.post(
    "/generate/{conversation_id}",
    response_model=SuccessResponse[ReportResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Generate a report from a completed conversation",
)
async def generate_report(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: ReportService = Depends(get_report_service),
) -> SuccessResponse[ReportResponseSchema]:
    """Uses AI to extract structured report data from the conversation and saves it."""
    try:
        report = await service.generate_report_from_conversation(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
        return SuccessResponse(
            message="Report generated successfully.",
            data=ReportResponseSchema.model_validate(report),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        log.error(f"Failed to generate report: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/{case_id}",
    response_model=SuccessResponse[ReportResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get report by Case ID",
)
async def get_report(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: ReportService = Depends(get_report_service),
) -> SuccessResponse[ReportResponseSchema]:
    """Retrieve the generated report for a specific case."""
    try:
        report = await service.get_report(
            case_id=case_id,
            user_id=current_user.id,
        )
        return SuccessResponse(
            message="Report retrieved successfully.",
            data=ReportResponseSchema.model_validate(report),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/{case_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download PDF report",
)
async def download_report_pdf(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    service: ReportService = Depends(get_report_service),
) -> Response:
    """Generate and download the report as a PDF document."""
    try:
        pdf_bytes = await service.generate_pdf(
            case_id=case_id,
            user_id=current_user.id,
        )
        headers = {
            "Content-Disposition": f'attachment; filename="legalease_report_{case_id}.pdf"'
        }
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        log.error(f"Failed to generate PDF: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate PDF.")