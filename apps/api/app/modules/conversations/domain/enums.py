"""Enumerations for the Conversations domain model."""

from __future__ import annotations

from enum import StrEnum


class MessageStatus(StrEnum):
    """Lifecycle status of a persisted conversation message.

    Every message defaults to ``COMPLETED`` (its content was saved in full,
    in one write). Streaming responses instead create the assistant message
    as ``GENERATING``, update its content as chunks arrive, and finish as
    either ``COMPLETED`` or ``FAILED`` -- a failed message is never deleted,
    only marked as such, so partial output remains visible in history.
    """

    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
