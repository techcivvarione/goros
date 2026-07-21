"""Core application services and platform configuration."""

from app.core.config import Settings, settings
from app.core.database import Base, DatabaseManager, create_database_manager

__all__ = [
    "Base",
    "DatabaseManager",
    "Settings",
    "create_database_manager",
    "settings",
]
