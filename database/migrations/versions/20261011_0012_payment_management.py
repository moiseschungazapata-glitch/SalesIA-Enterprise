"""Add complete payment management.

Revision ID: 20261011_0012
Revises: 20261011_0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0012"
down_revision: str | None = "20261011_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column(
            "payment_status", sa.String(20), nullable=False, server_default="paid"
        ),
    )
    op.add_column(
        "sales",
        sa.Column("paid_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
    )
    op.execute(sa.text("UPDATE sales SET paid_amount = total, payment_status = 'paid'"))
    op.create_check_constraint(
        "payment_status_allowed",
        "sales",
        "payment_status IN ('pending', 'partial', 'paid', 'refunded')",
    )
    op.create_check_constraint(
        "paid_amount_range", "sales", "paid_amount >= 0 AND paid_amount <= total"
    )

    op.drop_constraint("status_completed", "payments", type_="check")
    op.drop_constraint("uq_payments_sale_id", "payments", type_="unique")
    op.create_check_constraint(
        "status_allowed", "payments", "status IN ('completed', 'cancelled', 'refunded')"
    )
    op.add_column(
        "payments", sa.Column("registered_by_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "payments", sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "payments", sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_foreign_key(
        "fk_payments_registered_by_id_users",
        "payments",
        "users",
        ["registered_by_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_payments_sale_id", "payments", ["sale_id"])


def downgrade() -> None:
    op.drop_index("ix_payments_sale_id", table_name="payments")
    op.drop_constraint(
        "fk_payments_registered_by_id_users", "payments", type_="foreignkey"
    )
    op.drop_column("payments", "refunded_at")
    op.drop_column("payments", "cancelled_at")
    op.drop_column("payments", "registered_by_id")
    op.drop_constraint("status_allowed", "payments", type_="check")
    op.create_unique_constraint("uq_payments_sale_id", "payments", ["sale_id"])
    op.create_check_constraint("status_completed", "payments", "status = 'completed'")
    op.drop_constraint("paid_amount_range", "sales", type_="check")
    op.drop_constraint("payment_status_allowed", "sales", type_="check")
    op.drop_column("sales", "paid_amount")
    op.drop_column("sales", "payment_status")
