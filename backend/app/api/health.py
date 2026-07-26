"""
LegalEase AI - Health Check API
================================
Public endpoint — no authentication required.
Returns status of server, database, and AI service.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database.connection import check_database_connection
from app.schemas.response import success_response
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.get("/health", summary="Health Check", response_description="Service health status")
async def health_check() -> JSONResponse:
    """
    Verify that the server and its dependencies are operational.

    Returns:
        - server: Always "ok" if this endpoint responds
        - database: "ok" or "unavailable"
        - ai_service: "configured" or "not_configured"
    """
    from app.config.settings import settings

    # Check database
    db_status = "ok" if await check_database_connection() else "unavailable"

    # Check Gemini key presence (not validity — avoid API calls in health check)
    ai_status = (
        "configured"
        if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here"
        else "not_configured"
    )

    health_data = {
        "server": "ok",
        "database": db_status,
        "ai_service": ai_status,
        "version": settings.app_version,
        "environment": settings.app_env,
    }

    status_code = 200 if db_status == "ok" else 503
    message = "All systems operational" if db_status == "ok" else "Database unavailable"

    log.info(f"Health check: db={db_status}, ai={ai_status}")

    return JSONResponse(
        status_code=status_code,
        content=success_response(message=message, data=health_data),
    )
