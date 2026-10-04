"""Allow deterministic insight generation analyses.

Revision ID: 20261004_0002
Revises: 20261002_0001
Create Date: 2026-10-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20261004_0002"
down_revision: str | None = "20261002_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CONSTRAINT_NAME = "ck_statistical_analyses_analysis_type_allowed"


def upgrade() -> None:
    op.drop_constraint(op.f(CONSTRAINT_NAME), "statistical_analyses", type_="check")
    op.create_check_constraint(
        "analysis_type_allowed",
        "statistical_analyses",
        "analysis_type IN ('mean', 'median', 'comparison', 'frequency', "
        "'random_variable', 'bayes', 'insight')",
    )


def downgrade() -> None:
    op.drop_constraint(op.f(CONSTRAINT_NAME), "statistical_analyses", type_="check")
    op.create_check_constraint(
        "analysis_type_allowed",
        "statistical_analyses",
        "analysis_type IN ('mean', 'median', 'comparison', 'frequency', "
        "'random_variable', 'bayes')",
    )
