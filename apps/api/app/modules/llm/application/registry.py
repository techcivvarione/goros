"""Provider registry for the LLM Gateway.

Implements the Registry pattern: a simple in-memory lookup of provider
adapters keyed by :class:`ProviderType`, used to resolve which concrete
provider instance should handle a given request.
"""

from __future__ import annotations

from app.modules.llm.domain.contracts import BaseProvider
from app.modules.llm.domain.enums import ProviderType
from app.modules.llm.domain.exceptions import ProviderNotRegisteredError


class ProviderRegistry:
    """In-memory registry mapping provider types to provider instances."""

    def __init__(self) -> None:
        """Initialize an empty provider registry."""

        self._providers: dict[ProviderType, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register a provider instance under its declared provider type."""

        self._providers[provider.provider_type] = provider

    def get(self, provider_type: ProviderType) -> BaseProvider:
        """Return the registered provider for the given provider type."""

        try:
            return self._providers[provider_type]
        except KeyError as exc:
            raise ProviderNotRegisteredError(provider_type) from exc

    def is_registered(self, provider_type: ProviderType) -> bool:
        """Return whether a provider has been registered for the given type."""

        return provider_type in self._providers

    def list_registered(self) -> tuple[ProviderType, ...]:
        """Return the provider types currently registered."""

        return tuple(self._providers.keys())
