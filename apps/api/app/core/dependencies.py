"""Dependency providers used by FastAPI routers and services."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import DatabaseManager, get_db_session


@dataclass(slots=True)
class ApplicationContainer:
    """Long-lived application dependencies stored on FastAPI app state."""

    settings: Settings
    database: DatabaseManager


def get_container(request: Request) -> ApplicationContainer:
    """Return the application container stored on FastAPI app state."""

    container = getattr(request.app.state, "container", None)
    if not isinstance(container, ApplicationContainer):
        raise RuntimeError("Application container has not been initialized.")
    return container


def get_app_settings() -> Settings:
    """Return the process-wide settings instance."""

    return get_settings()


def get_database_manager(request: Request) -> DatabaseManager:
    """Return the initialized database manager from the application container."""

    return get_container(request).database


def get_db(request: Request) -> Generator[Session, None, None]:
    """Yield a database session for request-scoped database access."""

    yield from get_db_session(get_database_manager(request))
