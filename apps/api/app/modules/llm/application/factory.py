"""Provider factory for the LLM Gateway.

Implements the Factory pattern: encapsulates the knowledge of which
concrete infrastructure provider class backs each :class:`ProviderType`, so
callers can create provider instances without depending on their
constructors directly.
"""

from __future__ import annotations

from collections.abc import Callable

from app.core.config import Settings
from app.modules.llm.domain.contracts import BaseProvider
from app.modules.llm.domain.enums import ProviderType
from app.modules.llm.domain.exceptions import ProviderNotRegisteredError
from app.modules.llm.infrastructure.providers.anthropic import AnthropicProvider
from app.modules.llm.infrastructure.providers.gemini import GeminiProvider
from app.modules.llm.infrastructure.providers.ollama import OllamaProvider
from app.modules.llm.infrastructure.providers.openai import OpenAIProvider

ProviderBuilder = Callable[[Settings], BaseProvider]

_PROVIDER_BUILDERS: dict[ProviderType, ProviderBuilder] = {
    ProviderType.OLLAMA: OllamaProvider,
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.ANTHROPIC: AnthropicProvider,
    ProviderType.GEMINI: GeminiProvider,
}


class ProviderFactory:
    """Builds concrete provider adapter instances for a given provider type."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the factory with application settings."""

        self._settings = settings

    def create(self, provider_type: ProviderType) -> BaseProvider:
        """Construct a new provider adapter instance for the given type."""

        try:
            builder = _PROVIDER_BUILDERS[provider_type]
        except KeyError as exc:
            raise ProviderNotRegisteredError(provider_type) from exc
        return builder(self._settings)
