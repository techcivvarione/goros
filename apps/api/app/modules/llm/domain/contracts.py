"""Provider abstraction boundary (ports) for the LLM Gateway domain.

Every concrete provider adapter implemented in the infrastructure layer must
satisfy this contract. The domain layer depends only on this abstraction,
never on a concrete provider implementation, so the gateway can add or swap
providers without changing application logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class BaseProvider(ABC):
    """Strategy boundary implemented by every LLM provider adapter."""

    provider_type: ProviderType

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a single, non-streamed chat completion."""

    @abstractmethod
    def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Yield incremental chat completion chunks for the given request."""

    @abstractmethod
    async def list_models(self) -> tuple[ModelInfo, ...]:
        """Return the models exposed by this provider."""

    @abstractmethod
    async def health(self) -> ProviderHealth:
        """Return the provider's current health status."""

    @abstractmethod
    async def count_tokens(self, request: ChatRequest) -> TokenCount:
        """Return the token count for the given chat request."""

    @abstractmethod
    async def embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Return embedding vectors for the given input request."""
