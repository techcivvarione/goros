"""Enumerations for the LLM Gateway domain model."""

from __future__ import annotations

from enum import StrEnum


class ProviderType(StrEnum):
    """Identifies a supported LLM provider backend."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class MessageRole(StrEnum):
    """Identifies the author role of a chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ModelAlias(StrEnum):
    """Logical model role requested by application code, independent of provider.

    Applications request a role such as ``CHAT_FAST`` instead of naming a
    specific provider and model. The concrete provider/model binding for
    each alias is configured separately and resolved at runtime through the
    ModelResolver, so applications never need to know provider names.
    """

    CHAT_FAST = "chat_fast"
    CHAT_PREMIUM = "chat_premium"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDINGS = "embeddings"


class ModelCapability(StrEnum):
    """A discrete capability a model or model role may support."""

    CHAT = "chat"
    STREAMING = "streaming"
    TOOLS = "tools"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    JSON_MODE = "json_mode"
    FUNCTION_CALLING = "function_calling"
    IMAGE_GENERATION = "image_generation"
    AUDIO = "audio"
    REASONING = "reasoning"
