"""Record approximate anonymous visits before authentication.

Revision ID: 20261011_0007
Revises: 20261004_0006
Create Date: 2026-10-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0007"
down_revision: str | None = "20261004_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "anonymous_visits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.String(300)),
        sa.Column("latitude", sa.Numeric(9, 6)),
        sa.Column("longitude", sa.Numeric(9, 6)),
        sa.Column("city", sa.String(100)),
        sa.Column("region", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("country_code", sa.String(2)),
        sa.Column("isp", sa.String(160)),
        sa.Column("location_timezone", sa.String(64)),
        sa.Column("visit_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_anonymous_visits_company_created",
        "anonymous_visits",
        ["company_id", "created_at"],
    )
    op.create_index(
        "ix_anonymous_visits_company_ip",
        "anonymous_visits",
        ["company_id", "ip_address"],
    )


def downgrade() -> None:
    op.drop_index("ix_anonymous_visits_company_ip", table_name="anonymous_visits")
    op.drop_index("ix_anonymous_visits_company_created", table_name="anonymous_visits")
    op.drop_table("anonymous_visits")
