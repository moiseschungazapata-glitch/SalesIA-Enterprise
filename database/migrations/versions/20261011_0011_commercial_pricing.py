"""Add configurable taxes and discounts.

Revision ID: 20261011_0011
Revises: 20261011_0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0011"
down_revision: str | None = "20261011_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="18.00"),
    )
    op.add_column(
        "companies",
        sa.Column(
            "prices_include_tax", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
    )
    op.add_column(
        "companies",
        sa.Column(
            "max_discount_percent",
            sa.Numeric(5, 2),
            nullable=False,
            server_default="30.00",
        ),
    )
    op.create_check_constraint(
        "tax_rate_range", "companies", "tax_rate >= 0 AND tax_rate <= 100"
    )
    op.create_check_constraint(
        "max_discount_percent_range",
        "companies",
        "max_discount_percent >= 0 AND max_discount_percent <= 100",
    )

    for table in ("sales", "orders"):
        op.add_column(
            table,
            sa.Column(
                "subtotal", sa.Numeric(14, 2), nullable=False, server_default="0"
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "discount_total", sa.Numeric(14, 2), nullable=False, server_default="0"
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "tax_total", sa.Numeric(14, 2), nullable=False, server_default="0"
            ),
        )
        op.add_column(
            table,
            sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="0"),
        )
        op.add_column(
            table,
            sa.Column(
                "general_discount_percent",
                sa.Numeric(5, 2),
                nullable=False,
                server_default="0",
            ),
        )
        op.execute(sa.text(f"UPDATE {table} SET subtotal = total"))
        op.create_check_constraint(
            "subtotal_non_negative", table, "subtotal >= 0"
        )
        op.create_check_constraint(
            "discount_non_negative", table, "discount_total >= 0"
        )
        op.create_check_constraint(
            "tax_non_negative", table, "tax_total >= 0"
        )

    op.drop_constraint(
        "subtotal_matches", "sale_details", type_="check"
    )
    for table in ("sale_details", "order_details"):
        op.add_column(
            table,
            sa.Column(
                "gross_subtotal", sa.Numeric(14, 2), nullable=False, server_default="0"
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "discount_percent", sa.Numeric(5, 2), nullable=False, server_default="0"
            ),
        )
        op.add_column(
            table,
            sa.Column(
                "discount_amount", sa.Numeric(14, 2), nullable=False, server_default="0"
            ),
        )
        op.execute(sa.text(f"UPDATE {table} SET gross_subtotal = subtotal"))
        op.create_check_constraint(
            "gross_subtotal_positive", table, "gross_subtotal > 0"
        )
        op.create_check_constraint(
            "discount_range",
            table,
            "discount_percent >= 0 AND discount_percent <= 100",
        )
        op.create_check_constraint(
            "discount_amount_non_negative", table, "discount_amount >= 0"
        )


def downgrade() -> None:
    for table in ("order_details", "sale_details"):
        op.drop_constraint(
            "discount_amount_non_negative", table, type_="check"
        )
        op.drop_constraint("discount_range", table, type_="check")
        op.drop_constraint("gross_subtotal_positive", table, type_="check")
        op.drop_column(table, "discount_amount")
        op.drop_column(table, "discount_percent")
        op.drop_column(table, "gross_subtotal")
    op.create_check_constraint(
        "subtotal_matches",
        "sale_details",
        "subtotal = round(unit_price * quantity, 2)",
    )
    for table in ("orders", "sales"):
        op.drop_constraint("tax_non_negative", table, type_="check")
        op.drop_constraint("discount_non_negative", table, type_="check")
        op.drop_constraint("subtotal_non_negative", table, type_="check")
        for column in (
            "general_discount_percent",
            "tax_rate",
            "tax_total",
            "discount_total",
            "subtotal",
        ):
            op.drop_column(table, column)
    op.drop_constraint(
        "max_discount_percent_range", "companies", type_="check"
    )
    op.drop_constraint("tax_rate_range", "companies", type_="check")
    op.drop_column("companies", "max_discount_percent")
    op.drop_column("companies", "prices_include_tax")
    op.drop_column("companies", "tax_rate")
