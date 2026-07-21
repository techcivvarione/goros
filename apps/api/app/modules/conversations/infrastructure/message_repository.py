"""Repository for persisting and retrieving conversation messages."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.conversations.domain.entities import ConversationMessage
from app.modules.conversations.domain.enums import MessageStatus
from app.modules.conversations.domain.exceptions import MessageNotFoundError
from app.modules.conversations.infrastructure.models import MessageModel
from app.modules.llm.domain.enums import MessageRole


def _to_entity(model: MessageModel) -> ConversationMessage:
    """Translate a persistence model into its domain entity."""

    return ConversationMessage(
        id=model.id,
        conversation_id=model.conversation_id,
        role=MessageRole(model.role),
        content=model.content,
        created_at=model.created_at,
        status=MessageStatus(model.status),
        metadata=dict(model.metadata_),
    )


class MessageRepository:
    """SQLAlchemy-backed persistence for the ConversationMessage entity.

    Owns translation between :class:`MessageModel` (the ORM row) and
    :class:`ConversationMessage` (the domain entity); callers outside this
    module only ever see the domain entity.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a request-scoped session."""

        self._session = session

    def add(self, message: ConversationMessage) -> ConversationMessage:
        """Persist a new message and return the stored entity."""

        model = MessageModel(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role.value,
            content=message.content,
            status=message.status.value,
            metadata_=dict(message.metadata),
            created_at=message.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)

    def update_content_and_status(
        self,
        message_id: UUID,
        *,
        content: str,
        status: MessageStatus,
    ) -> ConversationMessage:
        """Update a message's content and status, returning the stored entity.

        Used by the streaming chat flow to update the assistant message as
        chunks arrive and to record its final ``completed``/``failed``
        status. Raises :class:`MessageNotFoundError` if the message does not
        exist, which should not happen in practice -- callers only ever
        update a message id they just created in the same request.
        """

        model = self._session.get(MessageModel, message_id)
        if model is None:
            raise MessageNotFoundError(message_id)
        model.content = content
        model.status = status.value
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)

    def list_by_conversation(
        self, conversation_id: UUID
    ) -> tuple[ConversationMessage, ...]:
        """Return all messages for a conversation, ordered oldest first."""

        statement = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())
        )
        models = self._session.execute(statement).scalars().all()
        return tuple(_to_entity(model) for model in models)
