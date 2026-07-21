"""Domain entities for the LLM Gateway."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.llm.domain.enums import (
    MessageRole,
    ModelAlias,
    ModelCapability,
    ProviderType,
)


@dataclass(frozen=True, slots=True)
class Message:
    """A single conversational message exchanged with an LLM provider."""

    role: MessageRole
    content: str
    name: str | None = None


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """A normalized request to generate a chat completion."""

    provider: ProviderType
    model: str
    messages: tuple[Message, ...]
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
    system_prompt: str | None = None
    tools: tuple[dict[str, object], ...] | None = None
    response_format: dict[str, object] | None = None
    stop_sequences: tuple[str, ...] | None = None
    seed: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Token accounting for a completed chat request."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class ChatResponse:
    """A normalized chat completion response from an LLM provider."""

    provider: ProviderType
    model: str
    message: Message
    usage: TokenUsage | None = None
    finish_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ModelInfo:
    """Describes a model made available by a provider."""

    provider: ProviderType
    name: str
    display_name: str
    context_window: int | None = None
    supports_streaming: bool = False


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    """Provider-agnostic identity and capability metadata for an LLM provider.

    Describes what a provider integration supports at a glance, independent
    of any specific model, so callers can introspect capabilities before
    issuing a request.
    """

    provider: ProviderType
    display_name: str
    description: str
    website: str | None = None
    supports_chat: bool = False
    supports_streaming: bool = False
    supports_tools: bool = False
    supports_embeddings: bool = False
    supports_vision: bool = False
    supports_json_mode: bool = False
    supports_function_calling: bool = False
    supports_image_generation: bool = False
    supports_audio: bool = False
    default_model: str | None = None


@dataclass(frozen=True, slots=True)
class StreamChunk:
    """A single incremental chunk emitted while streaming a chat completion."""

    content: str
    delta: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Health check result for a single LLM provider."""

    provider: ProviderType
    healthy: bool
    latency_ms: float | None = None
    available_models: tuple[str, ...] = ()
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class TokenCount:
    """Strongly typed token count result for a chat request."""

    provider: ProviderType
    model: str
    total_tokens: int


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    """A normalized request to generate embeddings for one or more inputs."""

    provider: ProviderType
    model: str
    input: tuple[str, ...]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    """A single embedding vector result for one input item."""

    index: int
    vector: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class EmbeddingResponse:
    """A normalized embeddings response returned by a provider."""

    provider: ProviderType
    model: str
    data: tuple[EmbeddingVector, ...]
    usage: TokenUsage | None = None


@dataclass(frozen=True, slots=True)
class ModelDefinition:
    """Concrete provider/model binding for a logical model alias.

    Produced by the model registry and consumed by the model resolver to
    translate a role like ``ModelAlias.CHAT_FAST`` into the provider and
    model that should actually handle the request.
    """

    alias: ModelAlias
    provider: ProviderType
    model: str
    capabilities: tuple[ModelCapability, ...] = ()
