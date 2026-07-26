"""
LegalEase AI - Application Entry Point
=======================================
Runs the FastAPI application via uvicorn.
Use: python main.py OR uvicorn main:app --reload
"""

import uvicorn

from app import create_app
from app.config.settings import settings

# Create the application instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
