"""Store approximate IP locations for authenticated sessions.

Revision ID: 20261004_0005
Revises: 20261004_0004
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261004_0005"
down_revision: str | None = "20261004_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("auth_sessions", sa.Column("latitude", sa.Numeric(9, 6)))
    op.add_column("auth_sessions", sa.Column("longitude", sa.Numeric(9, 6)))
    op.add_column("auth_sessions", sa.Column("city", sa.String(100)))
    op.add_column("auth_sessions", sa.Column("region", sa.String(100)))
    op.add_column("auth_sessions", sa.Column("country", sa.String(100)))
    op.add_column("auth_sessions", sa.Column("country_code", sa.String(2)))
    op.add_column("auth_sessions", sa.Column("isp", sa.String(160)))
    op.add_column("auth_sessions", sa.Column("location_timezone", sa.String(64)))
    op.add_column("auth_sessions", sa.Column("location_source", sa.String(40)))
    op.add_column("auth_sessions", sa.Column("located_at", sa.DateTime(timezone=True)))
    op.create_index(
        "ix_auth_sessions_company_location",
        "auth_sessions",
        ["company_id", "located_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_company_location", table_name="auth_sessions")
    for column in (
        "located_at",
        "location_source",
        "location_timezone",
        "isp",
        "country_code",
        "country",
        "region",
        "city",
        "longitude",
        "latitude",
    ):
        op.drop_column("auth_sessions", column)
