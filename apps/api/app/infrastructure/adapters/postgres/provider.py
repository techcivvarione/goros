"""Postgres adapter configuration boundary."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.adapters.base import (
    AdapterConfiguration,
    ConfigurableAdapter,
    normalize_endpoint,
)


class PostgresAdapter(ConfigurableAdapter):
    """Read-only adapter exposing normalized Postgres connectivity settings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the adapter with application settings."""

        self._settings = settings

    def configuration(self) -> AdapterConfiguration:
        """Return the configured Postgres endpoint metadata."""

        return AdapterConfiguration(
            name="postgres",
            endpoint=normalize_endpoint(self._settings.postgres_dsn),
        )
