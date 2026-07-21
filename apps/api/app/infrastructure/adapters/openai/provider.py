"""OpenAI adapter configuration boundary."""

from __future__ import annotations

from app.core.config import Settings
from app.infrastructure.adapters.base import (
    AdapterConfiguration,
    ConfigurableAdapter,
    normalize_endpoint,
)


class OpenAIAdapter(ConfigurableAdapter):
    """Read-only adapter exposing normalized OpenAI connectivity settings."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the adapter with application settings."""

        self._settings = settings

    def configuration(self) -> AdapterConfiguration:
        """Return the configured OpenAI endpoint metadata."""

        return AdapterConfiguration(
            name="openai",
            endpoint=normalize_endpoint(self._settings.openai_base_url),
        )
