"""Pydantic schemas for the AI module."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.llm.domain.enums import ModelAlias, ProviderType


class AIModuleSchema(BaseModel):
    """Base schema namespace for the AI module."""

    module: Literal["ai"] = Field(
        default="ai",
        description="Stable module identifier.",
    )


class ChatRequestSchema(BaseModel):
    """Request payload for the AI chat endpoint."""

    message: str = Field(description="The user's message to send to the model.")
    model_alias: ModelAlias = Field(
        default=ModelAlias.CHAT_FAST,
        description="Logical model role to route the request to.",
    )
    temperature: float | None = Field(
        default=None,
        description="Sampling temperature override, if supported by the provider.",
    )
    system_prompt: str | None = Field(
        default=None,
        description="Optional system prompt to prepend to the conversation.",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description=(
            "Optional id of an existing conversation to associate this chat "
            "with. If omitted, chat behavior is unchanged. If supplied, the "
            "conversation must exist. Sprint 4 does not yet persist messages "
            "against it -- that is deferred to a later sprint."
        ),
    )


class ChatStreamRequestSchema(BaseModel):
    """Request payload for the AI chat streaming endpoint.

    Unlike :class:`ChatRequestSchema`, ``conversation_id`` is required: this
    endpoint's entire purpose is to stream tokens while updating a
    conversation's assistant message in real time, so there is no
    "unchanged without one" fallback the way there is for ``POST /chat``.
    """

    message: str = Field(description="The user's message to send to the model.")
    model_alias: ModelAlias = Field(
        default=ModelAlias.CHAT_FAST,
        description="Logical model role to route the request to.",
    )
    temperature: float | None = Field(
        default=None,
        description="Sampling temperature override, if supported by the provider.",
    )
    system_prompt: str | None = Field(
        default=None,
        description="Optional system prompt to prepend to the conversation.",
    )
    conversation_id: UUID = Field(
        description=(
            "Id of an existing conversation to stream this chat into. The "
            "user's message and the streamed assistant reply are both "
            "persisted against it."
        ),
    )


class ChatUsageSchema(BaseModel):
    """Token usage for a chat completion, if the provider reported it."""

    prompt_tokens: int = Field(description="Tokens consumed by the prompt.")
    completion_tokens: int = Field(description="Tokens consumed by the completion.")
    total_tokens: int = Field(description="Total tokens consumed by the request.")


class ChatResponseData(BaseModel):
    """Response payload data for the AI chat endpoint."""

    response: str = Field(description="The model's reply text.")
    provider: ProviderType = Field(description="Provider that handled the request.")
    model: str = Field(description="Concrete model name that handled the request.")
    usage: ChatUsageSchema | None = Field(
        default=None,
        description="Token usage, if the provider reported it.",
    )
    finish_reason: str | None = Field(
        default=None,
        description="Reason the model stopped generating, if reported.",
    )
