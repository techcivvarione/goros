"""Ollama adapter configuration boundary."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.adapters.base import (
    AdapterConfiguration,
    ConfigurableAdapter,
    normalize_endpoint,
)


class OllamaAdapter(ConfigurableAdapter):
    """Read-only adapter exposing normalized Ollama connectivity settings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the adapter with application settings."""

        self._settings = settings

    def configuration(self) -> AdapterConfiguration:
        """Return the configured Ollama endpoint metadata."""

        return AdapterConfiguration(
            name="ollama",
            endpoint=normalize_endpoint(self._settings.ollama_base_url),
        )
