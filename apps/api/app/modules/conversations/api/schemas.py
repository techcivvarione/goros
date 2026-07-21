"""Pydantic schemas for the Conversations module."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.conversations.domain.enums import MessageStatus
from app.modules.llm.domain.enums import MessageRole


class ConversationsModuleSchema(BaseModel):
    """Base schema namespace for the Conversations module."""

    module: Literal["conversations"] = Field(
        default="conversations",
        description="Stable module identifier.",
    )


class ConversationCreateRequest(BaseModel):
    """Request payload for creating a conversation."""

    title: str | None = Field(
        default=None,
        description=(
            "Optional conversation title. If omitted, a title is generated "
            "automatically."
        ),
    )


class ConversationResponseData(BaseModel):
    """Response payload data describing a single conversation."""

    id: UUID = Field(description="Unique conversation identifier.")
    title: str = Field(description="Conversation title.")
    created_at: datetime = Field(description="Timestamp the conversation was created.")
    updated_at: datetime = Field(
        description="Timestamp the conversation was last updated."
    )
    is_deleted: bool = Field(
        description="Whether the conversation has been soft-deleted."
    )
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Arbitrary conversation metadata.",
    )


class MessageResponseData(BaseModel):
    """Response payload data describing a single conversation message."""

    id: UUID = Field(description="Unique message identifier.")
    conversation_id: UUID = Field(
        description="Identifier of the conversation this message belongs to."
    )
    role: MessageRole = Field(description="Author role of the message.")
    content: str = Field(description="Message content.")
    status: MessageStatus = Field(description="Lifecycle status of the message.")
    created_at: datetime = Field(description="Timestamp the message was created.")
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Arbitrary message metadata.",
    )
