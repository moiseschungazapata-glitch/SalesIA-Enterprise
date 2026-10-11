"""Allow precise, permission-based locations for anonymous visits.

Revision ID: 20261011_0008
Revises: 20261011_0007
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0008"
down_revision: str | None = "20261011_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "anonymous_visits",
        sa.Column(
            "location_source",
            sa.String(40),
            nullable=False,
            server_default="public_ip",
        ),
    )
    op.add_column(
        "anonymous_visits",
        sa.Column("location_accuracy_m", sa.Numeric(10, 2)),
    )


def downgrade() -> None:
    op.drop_column("anonymous_visits", "location_accuracy_m")
    op.drop_column("anonymous_visits", "location_source")
