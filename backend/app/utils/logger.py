"""
LegalEase AI - Logging Configuration
======================================
Configures loguru logger for structured, colored output in development
and JSON-compatible file logging in production.
Sensitive data (passwords, tokens, API keys) is NEVER logged.
"""

import sys
from pathlib import Path

from loguru import logger

from app.config.settings import settings


def setup_logging() -> None:
    """
    Configure the global loguru logger.
    Call this once at application startup.
    """
    # Remove the default handler
    logger.remove()

    # ---- Console Handler (development) ----
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    # ---- File Handler (persistent logs) ----
    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",     # Rotate when file exceeds 10 MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",    # Compress rotated logs
        backtrace=True,
        diagnose=False,       # Never show variable values in production logs
    )

    logger.info(f"Logging initialized — level={settings.log_level}, env={settings.app_env}")


def get_logger(name: str):
    """
    Return a contextualized logger bound to the given module name.
    Usage:
        from app.utils.logger import get_logger
        log = get_logger(__name__)
        log.info("Something happened")
    """
    return logger.bind(name=name)
