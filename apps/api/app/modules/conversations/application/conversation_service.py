"""Application service for conversation management.

Sprint 4 scope only: create, list, get, and soft-delete conversations, plus
simple (non-AI) title generation. Message persistence, history, and any AI
involvement in title generation are deferred to later sprints.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.conversations.domain.entities import Conversation
from app.modules.conversations.infrastructure.repository import ConversationRepository

DEFAULT_CONVERSATION_TITLE = "New Conversation"
MAX_TITLE_LENGTH = 60


class ConversationService:
    """Application-facing entry point for conversation management."""

    def __init__(self, repository: ConversationRepository) -> None:
        """Initialize the service with the injected repository."""

        self._repository = repository

    def create(self, title: str | None = None) -> Conversation:
        """Create a new conversation, generating a title if none is given."""

        now = datetime.now(UTC)
        conversation = Conversation(
            id=uuid4(),
            title=self.generate_title(title),
            created_at=now,
            updated_at=now,
            is_deleted=False,
            metadata={},
        )
        return self._repository.add(conversation)

    def list(self) -> tuple[Conversation, ...]:
        """Return all non-deleted conversations."""

        return self._repository.list_active()

    def get(self, conversation_id: UUID) -> Conversation:
        """Return a single non-deleted conversation.

        Raises :class:`ConversationNotFoundError
        <app.modules.conversations.domain.exceptions.ConversationNotFoundError>`
        if it does not exist or has been soft-deleted.
        """

        return self._repository.get_active(conversation_id)

    def exists(self, conversation_id: UUID) -> bool:
        """Return whether a non-deleted conversation exists for this id."""

        return self._repository.exists_active(conversation_id)

    def delete(self, conversation_id: UUID) -> Conversation:
        """Soft-delete a conversation and return its updated state.

        Raises :class:`ConversationNotFoundError
        <app.modules.conversations.domain.exceptions.ConversationNotFoundError>`
        if it does not exist or has already been soft-deleted.
        """

        return self._repository.soft_delete(conversation_id)

    @staticmethod
    def generate_title(source: str | None) -> str:
        """Generate a conversation title from a source string.

        This is a simple, non-AI title generator: it collapses whitespace
        and truncates to approximately :data:`MAX_TITLE_LENGTH` characters on
        a word boundary where possible. Falls back to a stable default title
        when no usable source is given. AI-assisted title generation is
        deferred to a later sprint.
        """

        if source is None:
            return DEFAULT_CONVERSATION_TITLE

        cleaned = " ".join(source.split())
        if not cleaned:
            return DEFAULT_CONVERSATION_TITLE

        if len(cleaned) <= MAX_TITLE_LENGTH:
            return cleaned

        truncated = cleaned[:MAX_TITLE_LENGTH]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated.rstrip() + "..."
