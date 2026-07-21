"""Qdrant adapter configuration boundary."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.adapters.base import (
    AdapterConfiguration,
    ConfigurableAdapter,
    normalize_endpoint,
)


class QdrantAdapter(ConfigurableAdapter):
    """Read-only adapter exposing normalized Qdrant connectivity settings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the adapter with application settings."""

        self._settings = settings

    def configuration(self) -> AdapterConfiguration:
        """Return the configured Qdrant endpoint metadata."""

        return AdapterConfiguration(
            name="qdrant",
            endpoint=normalize_endpoint(self._settings.qdrant_url),
        )
