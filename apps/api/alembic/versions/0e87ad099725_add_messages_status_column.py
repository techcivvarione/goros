"""add messages status column

Revision ID: 0e87ad099725
Revises: 7a3cf4e6fa54
Create Date: 2026-07-21

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0e87ad099725"
down_revision: str | None = "7a3cf4e6fa54"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Apply the migration."""

    op.add_column(
        "messages",
        sa.Column(
            "status",
            sa.String(length=16),
            nullable=False,
            server_default="completed",
        ),
    )


def downgrade() -> None:
    """Revert the migration."""

    op.drop_column("messages", "status")
