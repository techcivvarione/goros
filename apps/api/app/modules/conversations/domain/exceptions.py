"""Domain-level exceptions for the Conversations module."""

from __future__ import annotations

from uuid import UUID


class ConversationError(Exception):
    """Base class for all Conversations domain errors."""


class ConversationNotFoundError(ConversationError):
    """Raised when a requested conversation does not exist or is deleted."""

    def __init__(self, conversation_id: UUID) -> None:
        """Initialize the error with the unresolved conversation id."""

        self.conversation_id = conversation_id
        super().__init__(f"Conversation '{conversation_id}' was not found.")


class MessageNotFoundError(ConversationError):
    """Raised when a requested message does not exist.

    In practice this guards an internal invariant: callers only ever update
    a message id they just created in the same request, so this should not
    occur in normal operation.
    """

    def __init__(self, message_id: UUID) -> None:
        """Initialize the error with the unresolved message id."""

        self.message_id = message_id
        super().__init__(f"Message '{message_id}' was not found.")
