"""Gemini adapter configuration boundary."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.adapters.base import (
    AdapterConfiguration,
    ConfigurableAdapter,
    normalize_endpoint,
)


class GeminiAdapter(ConfigurableAdapter):
    """Read-only adapter exposing normalized Gemini connectivity settings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the adapter with application settings."""

        self._settings = settings

    def configuration(self) -> AdapterConfiguration:
        """Return the configured Gemini endpoint metadata."""

        return AdapterConfiguration(
            name="gemini",
            endpoint=normalize_endpoint(self._settings.gemini_base_url),
        )
