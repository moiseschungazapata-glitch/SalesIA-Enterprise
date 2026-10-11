"""Add commercial orders and order details.

Revision ID: 20261011_0010
Revises: 20261011_0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0010"
down_revision: str | None = "20261011_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("seller_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="RESTRICT"), unique=True),
        sa.Column("number", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="PEN"),
        sa.Column("total", sa.Numeric(14, 2), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("cancelled_at", sa.DateTime(timezone=True)),
        sa.Column("converted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('draft', 'pending', 'approved', 'cancelled', 'converted')", name="ck_orders_status_allowed"),
        sa.CheckConstraint("total > 0", name="ck_orders_total_positive"),
    )
    op.create_index("ix_orders_company_created", "orders", ["company_id", "created_at"])
    op.create_index("ix_orders_company_status", "orders", ["company_id", "status"])
    op.create_table(
        "order_details",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False),
        sa.Column("sku_snapshot", sa.String(50), nullable=False),
        sa.Column("product_name_snapshot", sa.String(180), nullable=False),
        sa.Column("category_name_snapshot", sa.String(120), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_order_details_quantity_positive"),
        sa.CheckConstraint("unit_price > 0", name="ck_order_details_unit_price_positive"),
    )
    op.create_index("ix_order_details_order", "order_details", ["order_id"])
    op.execute(sa.text('ALTER TABLE "orders" ENABLE ROW LEVEL SECURITY'))
    op.execute(sa.text('ALTER TABLE "order_details" ENABLE ROW LEVEL SECURITY'))


def downgrade() -> None:
    op.drop_table("order_details")
    op.drop_table("orders")
