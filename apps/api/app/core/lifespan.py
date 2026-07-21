"""Application lifespan management for process-wide resource initialization."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import create_database_manager
from app.core.dependencies import ApplicationContainer
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down process-wide application resources."""

    settings = get_settings()
    configure_logging(settings)
    database = create_database_manager(settings)

    try:
        database.initialize()
    except Exception:
        logger.exception("application_startup_failed", module="platform")
        raise

    app.state.container = ApplicationContainer(settings=settings, database=database)
    logger.info("application_startup_completed", module="platform")

    try:
        yield
    finally:
        logger.info("application_shutdown_started", module="platform")
        try:
            database.dispose()
        except Exception:
            logger.exception("application_shutdown_failed", module="platform")
            raise
        logger.info("application_shutdown_completed", module="platform")
