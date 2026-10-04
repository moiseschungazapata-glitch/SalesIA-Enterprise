"""Add device accuracy to authenticated session locations.

Revision ID: 20261004_0006
Revises: 20261004_0005
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261004_0006"
down_revision: str | None = "20261004_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_sessions",
        sa.Column("location_accuracy_m", sa.Numeric(10, 2)),
    )


def downgrade() -> None:
    op.drop_column("auth_sessions", "location_accuracy_m")
