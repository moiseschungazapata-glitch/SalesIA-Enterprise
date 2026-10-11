"""Track active location permission and recent presence.

Revision ID: 20261011_0009
Revises: 20261011_0008
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0009"
down_revision: str | None = "20261011_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_sessions",
        sa.Column("location_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "anonymous_visits",
        sa.Column("location_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("anonymous_visits", "location_active")
    op.drop_column("auth_sessions", "location_active")
