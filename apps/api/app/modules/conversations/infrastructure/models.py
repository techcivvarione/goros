"""SQLAlchemy ORM models for the Conversations module."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.modules.conversations.domain.enums import MessageStatus


def _utcnow() -> datetime:
    """Return the current UTC timestamp for column defaults."""

    return datetime.now(UTC)


class ConversationModel(Base):
    """Persistence model for a conversation.

    No ``user_id`` or ``organization_id`` -- those are deferred to later
    sprints. Related messages live in :class:`MessageModel`, referencing
    this table's ``id`` by foreign key.
    """

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    # Named `metadata_` on the Python side because `metadata` is reserved on
    # declarative model classes (it holds the table's `MetaData` collection);
    # the underlying column is still named `metadata`.
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )


class MessageModel(Base):
    """Persistence model for a single message within a conversation.

    A plain foreign key to ``conversations.id`` -- no ORM ``relationship()``
    is declared since this codebase queries through explicit repositories
    rather than ORM relationship navigation.
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        default=MessageStatus.COMPLETED.value,
        server_default=MessageStatus.COMPLETED.value,
        nullable=False,
    )
    # Named `metadata_` for the same reason as `ConversationModel.metadata_`.
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
