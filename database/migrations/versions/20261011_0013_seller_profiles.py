"""Activate seller employee profiles.

Revision ID: 20261011_0013
Revises: 20261011_0012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0013"
down_revision: str | None = "20261011_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "employees", sa.Column("document_number", sa.String(30), nullable=True)
    )
    op.add_column("employees", sa.Column("hire_date", sa.Date(), nullable=True))
    op.add_column("employees", sa.Column("zone", sa.String(120), nullable=True))
    op.add_column(
        "employees",
        sa.Column(
            "monthly_target", sa.Numeric(14, 2), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "employees",
        sa.Column(
            "commission_percent", sa.Numeric(5, 2), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "employees",
        sa.Column(
            "employment_status", sa.String(20), nullable=False, server_default="active"
        ),
    )
    op.create_check_constraint(
        "monthly_target_non_negative", "employees", "monthly_target >= 0"
    )
    op.create_check_constraint(
        "commission_percent_range",
        "employees",
        "commission_percent >= 0 AND commission_percent <= 100",
    )
    op.create_check_constraint(
        "employment_status_allowed",
        "employees",
        "employment_status IN ('active', 'leave', 'terminated')",
    )
    op.execute(
        sa.text("""
        INSERT INTO employees (
            company_id, user_id, employee_code, name, email, position, active,
            monthly_target, commission_percent, employment_status, created_at, updated_at
        )
        SELECT u.company_id, u.id, 'VEN-' || LPAD(u.id::text, 6, '0'),
               u.name, u.email, 'Vendedor', u.active, 0, 0,
               CASE WHEN u.active THEN 'active' ELSE 'terminated' END, NOW(), NOW()
        FROM users u
        JOIN roles r ON r.id = u.role_id
        LEFT JOIN employees e ON e.user_id = u.id
        WHERE r.code = 'seller' AND e.id IS NULL
    """)
    )


def downgrade() -> None:
    op.drop_constraint("employment_status_allowed", "employees", type_="check")
    op.drop_constraint("commission_percent_range", "employees", type_="check")
    op.drop_constraint("monthly_target_non_negative", "employees", type_="check")
    op.drop_column("employees", "employment_status")
    op.drop_column("employees", "commission_percent")
    op.drop_column("employees", "monthly_target")
    op.drop_column("employees", "zone")
    op.drop_column("employees", "hire_date")
    op.drop_column("employees", "document_number")
