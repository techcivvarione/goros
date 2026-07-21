"""Gemini provider adapter placeholder for the LLM Gateway.

Sprint 2.1 implements architecture only: no Gemini SDK or HTTP client is
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


class GeminiProvider(ProviderBase):
    """Placeholder adapter for the Gemini provider."""

    provider_type = ProviderType.GEMINI

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a single chat completion from Gemini."""

        raise NotImplementedError("Gemini chat completions are not yet implemented.")

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Yield incremental chat completion chunks from Gemini."""

        raise NotImplementedError("Gemini streaming is not yet implemented.")
        yield  # pragma: no cover - unreachable; marks this as an async generator

    async def list_models(self) -> tuple[ModelInfo, ...]:
        """Return the models exposed by the Gemini provider."""

        raise NotImplementedError("Gemini model listing is not yet implemented.")

    async def health(self) -> ProviderHealth:
        """Return whether the Gemini provider is reachable."""

        raise NotImplementedError("Gemini health checks are not yet implemented.")

    async def count_tokens(self, request: ChatRequest) -> TokenCount:
        """Return the token count for the given chat request."""

        raise NotImplementedError("Gemini token counting is not yet implemented.")

    async def embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Return embedding vectors for the given input request."""

        raise NotImplementedError("Gemini embeddings are not yet implemented.")
