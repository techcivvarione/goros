"""LLM Gateway manager coordinating provider resolution and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import replace

from app.modules.llm.application.factory import ProviderFactory
from app.modules.llm.application.model_resolver import ModelResolver
from app.modules.llm.application.registry import ProviderRegistry
from app.modules.llm.domain.contracts import BaseProvider
from app.modules.llm.domain.entities import (
    ChatRequest,
    ChatResponse,
    ModelInfo,
    ProviderHealth,
    StreamChunk,
)
from app.modules.llm.domain.enums import ModelAlias, ProviderType
from app.modules.llm.domain.exceptions import ModelResolverNotConfiguredError


class LLMManager:
    """Coordinates chat, streaming, model discovery, and health checks.

    The manager holds no provider-specific logic itself. Every operation is
    delegated to the provider resolved for the request, following the
    Strategy pattern. Provider instances are created on first use through
    the injected :class:`ProviderFactory` and cached in the injected
    :class:`ProviderRegistry` for subsequent calls.

    Callers may identify the target model either explicitly (a
    :class:`ProviderType` and model name, as before) or with a logical
    :class:`ModelAlias` such as ``ModelAlias.CHAT_FAST``. When an alias is
    given, it is resolved through the injected :class:`ModelResolver`, and
    the resolved provider/model take precedence over whatever was set
    explicitly -- so applications built against aliases never need to know
    provider names. Omitting the alias preserves the exact prior behavior.
    """

    def __init__(
        self,
        factory: ProviderFactory,
        registry: ProviderRegistry,
        model_resolver: ModelResolver | None = None,
    ) -> None:
        """Initialize the manager with a factory, registry, and optional resolver."""

        self._factory = factory
        self._registry = registry
        self._model_resolver = model_resolver

    def _resolve(self, provider_type: ProviderType) -> BaseProvider:
        """Return the provider for the given type, creating it on first use."""

        if not self._registry.is_registered(provider_type):
            self._registry.register(self._factory.create(provider_type))
        return self._registry.get(provider_type)

    def _require_model_resolver(self) -> ModelResolver:
        """Return the configured model resolver, or raise if none was provided."""

        if self._model_resolver is None:
            raise ModelResolverNotConfiguredError
        return self._model_resolver

    def _apply_alias(
        self,
        request: ChatRequest,
        alias: ModelAlias | None,
    ) -> ChatRequest:
        """Return a copy of the request with provider/model resolved from an alias.

        Returns ``request`` unchanged when no alias is given, which
        preserves the existing explicit provider/model behavior exactly.
        """

        if alias is None:
            return request
        definition = self._require_model_resolver().resolve(alias)
        return replace(request, provider=definition.provider, model=definition.model)

    def _resolve_provider_type(
        self,
        provider_type: ProviderType | None,
        alias: ModelAlias | None,
    ) -> ProviderType:
        """Resolve the effective provider type from an explicit type or an alias."""

        if alias is not None:
            return self._require_model_resolver().resolve(alias).provider
        if provider_type is not None:
            return provider_type
        raise ValueError("Either provider_type or alias must be provided.")

    async def chat(
        self,
        request: ChatRequest,
        *,
        alias: ModelAlias | None = None,
    ) -> ChatResponse:
        """Delegate a chat completion request to the resolved provider.

        If ``alias`` is given, the request's provider/model are resolved
        through the injected :class:`ModelResolver` and take precedence
        over whatever was set on ``request``.
        """

        effective_request = self._apply_alias(request, alias)
        provider = self._resolve(effective_request.provider)
        return await provider.chat(effective_request)

    async def stream(
        self,
        request: ChatRequest,
        *,
        alias: ModelAlias | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Delegate a streaming chat completion request to the resolved provider."""

        effective_request = self._apply_alias(request, alias)
        provider = self._resolve(effective_request.provider)
        async for chunk in provider.stream(effective_request):
            yield chunk

    async def list_models(
        self,
        provider_type: ProviderType | None = None,
        *,
        alias: ModelAlias | None = None,
    ) -> tuple[ModelInfo, ...]:
        """Delegate model discovery to the resolved provider."""

        resolved_type = self._resolve_provider_type(provider_type, alias)
        provider = self._resolve(resolved_type)
        return await provider.list_models()

    async def health(
        self,
        provider_type: ProviderType | None = None,
        *,
        alias: ModelAlias | None = None,
    ) -> ProviderHealth:
        """Delegate a health check to the resolved provider."""

        resolved_type = self._resolve_provider_type(provider_type, alias)
        provider = self._resolve(resolved_type)
        return await provider.health()
