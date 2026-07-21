"""Ollama provider adapter for the LLM Gateway.

Implements chat, streaming chat, model listing, health checking, and
best-effort token counting against a local (or configured) Ollama server
using the official ``ollama`` Python package. ``embeddings()`` remains a
``NotImplementedError`` placeholder; it is out of scope for this sprint.
"""

from __future__ import annotations

import time
from collections.abc import AsyncIterator

import httpx
import ollama

from app.core.config import Settings
from app.core.logging import get_logger
from app.modules.llm.domain.entities import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    Message,
    ModelInfo,
    ProviderHealth,
    StreamChunk,
    TokenCount,
    TokenUsage,
)
from app.modules.llm.domain.enums import MessageRole, ProviderType
from app.modules.llm.domain.exceptions import ProviderRequestError
from app.modules.llm.infrastructure.providers.base import ProviderBase

logger = get_logger(__name__)

# Ollama has no standalone tokenizer endpoint. When an exact prompt token
# count cannot be obtained from the server, this is the fallback estimate of
# characters per token, a widely used rough approximation for English text.
_APPROXIMATE_CHARS_PER_TOKEN = 4

_ROLE_BY_VALUE = {role.value: role for role in MessageRole}


def _parse_role(role: str) -> MessageRole:
    """Map an Ollama message role string onto the domain ``MessageRole``.

    Falls back to ``MessageRole.ASSISTANT`` for any role value Ollama
    returns that this domain model does not recognize, since chat
    completions are always authored by the assistant.
    """

    return _ROLE_BY_VALUE.get(role, MessageRole.ASSISTANT)


def _build_ollama_messages(request: ChatRequest) -> list[dict[str, str]]:
    """Convert a chat request's messages into Ollama's message format.

    ``system_prompt`` is prepended as a leading system-role message.
    Ollama has no equivalent of the domain ``Message.name`` field except
    for tool-role messages (``tool_name``); ``name`` is otherwise dropped.
    """

    messages: list[dict[str, str]] = []
    if request.system_prompt:
        messages.append(
            {"role": MessageRole.SYSTEM.value, "content": request.system_prompt}
        )

    for message in request.messages:
        payload: dict[str, str] = {
            "role": message.role.value,
            "content": message.content,
        }
        if message.role is MessageRole.TOOL and message.name:
            payload["tool_name"] = message.name
        messages.append(payload)

    return messages


def _build_options(request: ChatRequest) -> dict[str, object]:
    """Translate the well-known ``ChatRequest`` sampling fields into Ollama options."""

    options: dict[str, object] = {}
    if request.temperature is not None:
        options["temperature"] = request.temperature
    if request.max_tokens is not None:
        options["num_predict"] = request.max_tokens
    if request.top_p is not None:
        options["top_p"] = request.top_p
    if request.frequency_penalty is not None:
        options["frequency_penalty"] = request.frequency_penalty
    if request.presence_penalty is not None:
        options["presence_penalty"] = request.presence_penalty
    if request.stop_sequences:
        options["stop"] = list(request.stop_sequences)
    if request.seed is not None:
        options["seed"] = request.seed
    return options


def _extract_usage(response: ollama.ChatResponse) -> TokenUsage | None:
    """Build a ``TokenUsage`` from an Ollama chat response, if it reported any."""

    prompt_tokens = response.prompt_eval_count
    completion_tokens = response.eval_count
    if prompt_tokens is None and completion_tokens is None:
        return None

    prompt = prompt_tokens or 0
    completion = completion_tokens or 0
    return TokenUsage(
        prompt_tokens=prompt,
        completion_tokens=completion,
        total_tokens=prompt + completion,
    )


def _flatten_prompt(request: ChatRequest) -> str:
    """Concatenate a chat request's system prompt and messages into one string."""

    parts: list[str] = []
    if request.system_prompt:
        parts.append(request.system_prompt)
    parts.extend(message.content for message in request.messages)
    return "\n".join(parts)


class OllamaProvider(ProviderBase):
    """Adapter for a local (or remote) Ollama server."""

    provider_type = ProviderType.OLLAMA

    def __init__(self, settings: Settings) -> None:
        """Initialize the provider with an Ollama client for the configured host."""

        super().__init__(settings)
        host = str(settings.ollama_url) if settings.ollama_url else None
        self._client = ollama.AsyncClient(host=host)

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a single chat completion from Ollama."""

        messages = _build_ollama_messages(request)
        options = _build_options(request)

        try:
            response = await self._client.chat(
                model=request.model,
                messages=messages,
                options=options or None,
                stream=False,
            )
        except ollama.ResponseError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc
        except ConnectionError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc

        message = Message(
            role=_parse_role(response.message.role),
            content=response.message.content or "",
        )
        return ChatResponse(
            provider=self.provider_type,
            model=response.model or request.model,
            message=message,
            usage=_extract_usage(response),
            finish_reason=response.done_reason,
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        """Yield incremental chat completion chunks from Ollama.

        Ollama's streaming protocol yields one JSON object per generation
        step, where ``message.content`` is the incremental delta since the
        previous chunk (not the cumulative text), and the final object
        carries ``done=True`` plus completion metadata (``done_reason``,
        ``prompt_eval_count``, ``eval_count``). This method accumulates
        those deltas itself so each yielded :class:`StreamChunk.content` is
        the full text generated so far, alongside ``delta`` for just the
        new increment.

        Unlike :meth:`chat`, a connection failure here is not wrapped into a
        plain :class:`ConnectionError` by the ``ollama`` SDK (that wrapping
        only happens on its non-streaming request path), so ``httpx``
        connection errors are caught directly.
        """

        messages = _build_ollama_messages(request)
        options = _build_options(request)

        try:
            response_stream = await self._client.chat(
                model=request.model,
                messages=messages,
                options=options or None,
                stream=True,
            )
        except ollama.ResponseError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc
        except (ConnectionError, httpx.ConnectError) as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc

        accumulated_content = ""
        try:
            async for chunk in response_stream:
                delta = chunk.message.content or ""
                accumulated_content += delta
                yield StreamChunk(
                    content=accumulated_content,
                    delta=delta,
                    finish_reason=chunk.done_reason if chunk.done else None,
                    usage=_extract_usage(chunk) if chunk.done else None,
                )
        except ollama.ResponseError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc
        except httpx.ConnectError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc

    async def list_models(self) -> tuple[ModelInfo, ...]:
        """Return the models installed on the local Ollama server."""

        try:
            response = await self._client.list()
        except ollama.ResponseError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc
        except ConnectionError as exc:
            raise ProviderRequestError(self.provider_type, str(exc)) from exc

        models: list[ModelInfo] = []
        for entry in response.models:
            name = entry.model or ""
            models.append(
                ModelInfo(
                    provider=self.provider_type,
                    name=name,
                    display_name=name,
                    # The /api/tags listing does not report context length;
                    # obtaining it would require an additional show() call
                    # per model, which is intentionally skipped here.
                    context_window=None,
                    supports_streaming=True,
                )
            )
        return tuple(models)

    async def health(self) -> ProviderHealth:
        """Verify the Ollama server is reachable and return its health status."""

        started_at = time.perf_counter()
        try:
            response = await self._client.list()
        except (ollama.ResponseError, ConnectionError) as exc:
            latency_ms = (time.perf_counter() - started_at) * 1000
            logger.warning("ollama_health_check_failed", error=str(exc))
            return ProviderHealth(
                provider=self.provider_type,
                healthy=False,
                latency_ms=latency_ms,
                available_models=(),
                error_message=str(exc),
            )
        except Exception as exc:
            # Broad on purpose: a health probe that raises on an unexpected
            # failure mode is worse than one that reports itself unhealthy.
            latency_ms = (time.perf_counter() - started_at) * 1000
            logger.warning("ollama_health_check_unexpected_error", error=str(exc))
            return ProviderHealth(
                provider=self.provider_type,
                healthy=False,
                latency_ms=latency_ms,
                available_models=(),
                error_message=str(exc),
            )

        latency_ms = (time.perf_counter() - started_at) * 1000
        available_models = tuple(
            entry.model for entry in response.models if entry.model
        )
        return ProviderHealth(
            provider=self.provider_type,
            healthy=True,
            latency_ms=latency_ms,
            available_models=available_models,
            error_message=None,
        )

    async def count_tokens(self, request: ChatRequest) -> TokenCount:
        """Return the token count for the given chat request.

        Attempts to obtain an exact prompt token count from Ollama with a
        zero-generation prompt evaluation (``num_predict=0``), which asks
        the model to evaluate the prompt without generating any completion
        tokens. Ollama does not expose a standalone tokenizer endpoint, so
        if that call is unavailable or fails, this falls back to a rough
        character-based approximation (~4 characters per token for English
        text). The approximation is inexact and may be significantly off
        for other languages, code, or models with different tokenizers.
        """

        prompt_text = _flatten_prompt(request)

        try:
            response = await self._client.generate(
                model=request.model,
                prompt=prompt_text,
                options={"num_predict": 0},
                stream=False,
            )
        except (ollama.ResponseError, ConnectionError) as exc:
            logger.debug("ollama_exact_token_count_unavailable", error=str(exc))
        else:
            if response.prompt_eval_count is not None:
                return TokenCount(
                    provider=self.provider_type,
                    model=request.model,
                    total_tokens=response.prompt_eval_count,
                )
            logger.debug("ollama_exact_token_count_missing_in_response")

        approximate_tokens = max(1, len(prompt_text) // _APPROXIMATE_CHARS_PER_TOKEN)
        return TokenCount(
            provider=self.provider_type,
            model=request.model,
            total_tokens=approximate_tokens,
        )

    async def embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Return embedding vectors for the given input request."""

        raise NotImplementedError("Ollama embeddings are not yet implemented.")
