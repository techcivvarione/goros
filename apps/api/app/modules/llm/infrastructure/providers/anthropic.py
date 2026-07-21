"""Anthropic provider adapter placeholder for the LLM Gateway.

Sprint 2.1 implements architecture only: no Anthropic SDK or HTTP client is
imported, and every method raises ``NotImplementedError``. Real request
handling is added in a later sprint.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.modules.llm.domain.entities import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ModelInfo,
    ProviderHealth,
    StreamChunk,
    TokenCount,
)
from app.modules.llm.domain.enums import ProviderType
from app.modules.llm.infrastructure.providers.base import ProviderBase


class AnthropicProvider(ProviderBase):
    """Placeholder adapter for the Anthropic provider."""

    provider_type = ProviderType.ANTHROPIC

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a single chat completion from Anthropic."""

        raise NotImplementedError("Anthropic chat completions are not yet implemented.")

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Yield incremental chat completion chunks from Anthropic."""

        raise NotImplementedError("Anthropic streaming is not yet implemented.")
        yield  # pragma: no cover - unreachable; marks this as an async generator

    async def list_models(self) -> tuple[ModelInfo, ...]:
        """Return the models exposed by the Anthropic provider."""

        raise NotImplementedError("Anthropic model listing is not yet implemented.")

    async def health(self) -> ProviderHealth:
        """Return whether the Anthropic provider is reachable."""

        raise NotImplementedError("Anthropic health checks are not yet implemented.")

    async def count_tokens(self, request: ChatRequest) -> TokenCount:
        """Return the token count for the given chat request."""

        raise NotImplementedError("Anthropic token counting is not yet implemented.")

    async def embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Return embedding vectors for the given input request."""

        raise NotImplementedError("Anthropic embeddings are not yet implemented.")
