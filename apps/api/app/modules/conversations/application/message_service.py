"""Application service for conversation message persistence.

Create, update, and list messages for a conversation. This service does not
validate that the conversation exists -- callers (for example the AI chat
endpoints) are responsible for validating the conversation via
``ConversationService`` before creating or listing its messages.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.conversations.domain.entities import ConversationMessage
from app.modules.conversations.domain.enums import MessageStatus
from app.modules.conversations.infrastructure.message_repository import (
    MessageRepository,
)
from app.modules.llm.domain.enums import MessageRole


class MessageService:
    """Application-facing entry point for conversation message persistence."""

    def __init__(self, repository: MessageRepository) -> None:
        """Initialize the service with the injected repository."""

        self._repository = repository

    def create(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        metadata: dict[str, object] | None = None,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> ConversationMessage:
        """Persist a single message for a conversation.

        Defaults to ``MessageStatus.COMPLETED``, matching non-streamed
        message creation (the content is saved in full, in one write). The
        streaming chat flow instead passes ``MessageStatus.GENERATING`` when
        creating the placeholder assistant message.
        """

        message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.now(UTC),
            status=status,
            metadata=metadata or {},
        )
        return self._repository.add(message)

    def update_content_and_status(
        self,
        message_id: UUID,
        *,
        content: str,
        status: MessageStatus,
    ) -> ConversationMessage:
        """Update a message's content and status.

        Used by the streaming chat flow to update the assistant message as
        chunks arrive, and to record its final ``completed``/``failed``
        status once generation ends. The message is never deleted, even on
        failure.
        """

        return self._repository.update_content_and_status(
            message_id, content=content, status=status
        )

    def list_by_conversation(
        self, conversation_id: UUID
    ) -> tuple[ConversationMessage, ...]:
        """Return all messages for a conversation, ordered oldest first."""

        return self._repository.list_by_conversation(conversation_id)
