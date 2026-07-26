"""
LegalEase AI - Global Exception Handlers
=========================================
Registers FastAPI exception handlers for consistent error responses.
Prevents internal server details from leaking to clients.
All errors follow the standard ErrorResponse format.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.response import error_response
from app.utils.logger import get_logger

log = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI app.
    Call this during application startup (in create_app()).
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle explicit HTTPExceptions raised in route handlers."""
        log.warning(
            f"HTTP {exc.status_code} | {request.method} {request.url.path} | {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=str(exc.detail),
                errors=[],
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors from request body/query params."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            errors.append({"field": field, "message": error.get("msg", "Validation error")})

        log.warning(
            f"Validation error | {request.method} {request.url.path} | {len(errors)} error(s)"
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                message="Request validation failed. Please check your input.",
                errors=errors,
            ),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic ValidationError from response model serialization."""
        log.error(f"Pydantic serialization error | {request.url.path} | {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                message="An internal error occurred while processing your request."
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for any unhandled exceptions.
        Logs the full traceback but returns a generic error message to the client.
        This prevents internal implementation details from being exposed.
        """
        log.exception(
            f"Unhandled exception | {request.method} {request.url.path} | {type(exc).__name__}: {exc}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                message="An unexpected error occurred. Please try again later."
            ),
        )
