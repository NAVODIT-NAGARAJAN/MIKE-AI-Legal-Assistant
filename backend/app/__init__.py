"""
LegalEase AI - FastAPI Application Factory
===========================================
Creates and configures the FastAPI application instance.
Registers middleware, exception handlers, and API routers.
Follows the Application Factory pattern for testability.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.middleware.exception_handlers import register_exception_handlers
from app.utils.logger import get_logger, setup_logging

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Code before 'yield' runs on startup.
    Code after 'yield' runs on shutdown.
    """
    # ---- Startup ----
    log.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")

    # Verify database connectivity
    from app.database.connection import check_database_connection
    db_ok = await check_database_connection()
    if not db_ok:
        log.error("Database connection failed — check DATABASE_URL in .env")
    else:
        log.info("Database connection: OK")

    log.info("Application startup complete")
    yield

    # ---- Shutdown ----
    log.info("Application shutdown initiated")


def create_app() -> FastAPI:
    """
    Application factory.
    Creates, configures and returns the FastAPI instance.
    """
    # ---- Configure Logging ----
    setup_logging()

    # ---- Create FastAPI App ----
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "LegalEase AI — Agentic AI Consumer Rights Assistant for Indian Consumers. "
            "Powered by LangGraph + Gemini API + ChromaDB RAG."
        ),
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # ---- CORS Middleware ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Exception Handlers ----
    register_exception_handlers(app)

    # ---- API Routers ----
    # Routers are registered here as modules are completed.
    # Import inside function to prevent circular import issues.
    _register_routers(app)

    return app


def _register_routers(app: FastAPI) -> None:
    """Register all API routers under the /api/v1 prefix."""
    from app.api.health import router as health_router

    # Health check (public, no auth)
    app.include_router(health_router, prefix=settings.api_v1_prefix, tags=["Health"])

    # Authentication (public endpoints)
    from app.auth.router import router as auth_router
    app.include_router(auth_router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])

    # User management (protected)
    from app.users.router import router as users_router
    app.include_router(users_router, prefix=f"{settings.api_v1_prefix}/users", tags=["Users"])

    # Consumer cases (protected)
    from app.cases.router import router as cases_router
    app.include_router(cases_router, prefix=f"{settings.api_v1_prefix}/cases", tags=["Consumer Cases"])

    # Knowledge base search (protected)
    from app.knowledge.router import router as knowledge_router
    app.include_router(knowledge_router, prefix=f"{settings.api_v1_prefix}/knowledge", tags=["Knowledge Base"])

    # AI Agent conversations (protected)
    from app.ai_agent.router import router as agent_router
    app.include_router(agent_router, prefix=f"{settings.api_v1_prefix}/agent", tags=["AI Agent"])

    # Resolution roadmaps (protected)
    from app.roadmap.router import router as roadmap_router
    app.include_router(roadmap_router, prefix=f"{settings.api_v1_prefix}/roadmap", tags=["Roadmap"])

    # Evidence checklists (protected)
    from app.evidence.router import router as evidence_router
    app.include_router(evidence_router, prefix=f"{settings.api_v1_prefix}/evidence", tags=["Evidence"])

    # Consumer guidance reports (protected)
    from app.reports.router import router as reports_router
    app.include_router(reports_router, prefix=f"{settings.api_v1_prefix}/report", tags=["Reports"])

    # Document Intelligence (protected)
    from app.document_intelligence.router import (
        router as document_intelligence_router,
    )
    app.include_router(
        document_intelligence_router,
        prefix=f"{settings.api_v1_prefix}",
        tags=["Document Intelligence"],
    )
# ---------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------
app = create_app()
    
    