"""Repository for persisting and retrieving conversations."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.conversations.domain.entities import Conversation
from app.modules.conversations.domain.exceptions import ConversationNotFoundError
from app.modules.conversations.infrastructure.models import ConversationModel


def _to_entity(model: ConversationModel) -> Conversation:
    """Translate a persistence model into its domain entity."""

    return Conversation(
        id=model.id,
        title=model.title,
        created_at=model.created_at,
        updated_at=model.updated_at,
        is_deleted=model.is_deleted,
        metadata=dict(model.metadata_),
    )


class ConversationRepository:
    """SQLAlchemy-backed persistence for the Conversation entity.

    Owns translation between :class:`ConversationModel` (the ORM row) and
    :class:`Conversation` (the domain entity); callers outside this module
    only ever see the domain entity.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a request-scoped session."""

        self._session = session

    def add(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation and return the stored entity."""

        model = ConversationModel(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            is_deleted=conversation.is_deleted,
            metadata_=dict(conversation.metadata),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)

    def list_active(self) -> tuple[Conversation, ...]:
        """Return all non-deleted conversations, newest first."""

        statement = (
            select(ConversationModel)
            .where(ConversationModel.is_deleted.is_(False))
            .order_by(ConversationModel.created_at.desc())
        )
        models = self._session.execute(statement).scalars().all()
        return tuple(_to_entity(model) for model in models)

    def get_active(self, conversation_id: UUID) -> Conversation:
        """Return a single non-deleted conversation.

        Raises :class:`ConversationNotFoundError` if it does not exist or
        has been soft-deleted.
        """

        model = self._session.get(ConversationModel, conversation_id)
        if model is None or model.is_deleted:
            raise ConversationNotFoundError(conversation_id)
        return _to_entity(model)

    def exists_active(self, conversation_id: UUID) -> bool:
        """Return whether a non-deleted conversation exists for this id."""

        model = self._session.get(ConversationModel, conversation_id)
        return model is not None and not model.is_deleted

    def soft_delete(self, conversation_id: UUID) -> Conversation:
        """Mark a conversation as deleted without removing its row.

        Raises :class:`ConversationNotFoundError` if it does not exist or
        has already been soft-deleted.
        """

        model = self._session.get(ConversationModel, conversation_id)
        if model is None or model.is_deleted:
            raise ConversationNotFoundError(conversation_id)
        model.is_deleted = True
        model.updated_at = datetime.now(UTC)
        self._session.commit()
        self._session.refresh(model)
        return _to_entity(model)
