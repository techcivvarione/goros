"""Domain entities for the Conversations module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.conversations.domain.enums import MessageStatus
from app.modules.llm.domain.enums import MessageRole


@dataclass(frozen=True, slots=True)
class Conversation:
    """A conversation container.

    This entity does not reference users or organizations -- those are
    deferred to later sprints.
    """

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """A single persisted message belonging to a conversation.

    Distinct from :class:`app.modules.llm.domain.entities.Message`, which is
    the LLM Gateway's transient, in-flight chat message -- this entity is
    the durable, conversation-scoped record of one turn (user or assistant),
    persisted via ``MessageRepository``.
    """

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime
    status: MessageStatus = MessageStatus.COMPLETED
    metadata: dict[str, object] = field(default_factory=dict)
