"""Create the complete SalesIA PostgreSQL schema.

Revision ID: 20261002_0001
Revises: None
Create Date: 2026-10-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20261002_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )


def _build_schema() -> sa.MetaData:
    metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)

    sa.Table(
        "companies",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("legal_name", sa.String(200)),
        sa.Column("tax_id", sa.String(20), unique=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), server_default="PEN", nullable=False),
        sa.Column("timezone", sa.String(50), server_default="America/Lima", nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
    )

    sa.Table(
        "roles",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
    )

    users = sa.Table(
        "users",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        *_timestamps(),
    )
    sa.Index(
        "uq_users_company_email_ci", users.c.company_id, sa.func.lower(users.c.email), unique=True
    )
    sa.Index("ix_users_company_active", users.c.company_id, users.c.active)

    sa.Table(
        "employees",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), unique=True
        ),
        sa.Column("employee_code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254)),
        sa.Column("phone", sa.String(30)),
        sa.Column("position", sa.String(100)),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("company_id", "employee_code"),
        sa.Index("ix_employees_company_active", "company_id", "active"),
    )

    sa.Table(
        "customers",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("customer_type", sa.String(20), nullable=False),
        sa.Column("document_type", sa.String(10), nullable=False),
        sa.Column("document_number", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(30)),
        sa.Column("email", sa.String(254)),
        sa.Column("address", sa.Text()),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("customer_type IN ('person', 'company')", name="customer_type_allowed"),
        sa.CheckConstraint("document_type IN ('DNI', 'RUC')", name="document_type_allowed"),
        sa.CheckConstraint(
            "(customer_type = 'person' AND document_type = 'DNI' "
            "AND document_number ~ '^[0-9]{8}$') OR "
            "(customer_type = 'company' AND document_type = 'RUC' "
            "AND document_number ~ '^[0-9]{11}$')",
            name="document_matches_customer_type",
        ),
        sa.UniqueConstraint("company_id", "document_number"),
        sa.Index("ix_customers_company_active", "company_id", "active"),
        sa.Index("ix_customers_company_name", "company_id", "name"),
    )

    categories = sa.Table(
        "categories",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
    )
    sa.Index(
        "uq_categories_company_name_ci",
        categories.c.company_id,
        sa.func.lower(categories.c.name),
        unique=True,
    )
    sa.Index("ix_categories_company_active", categories.c.company_id, categories.c.active)

    sa.Table(
        "products",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(50), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("unit_price > 0", name="unit_price_positive"),
        sa.UniqueConstraint("company_id", "sku"),
        sa.Index("ix_products_company_category", "company_id", "category_id"),
        sa.Index("ix_products_company_active", "company_id", "active"),
        sa.Index("ix_products_company_name", "company_id", "name"),
    )

    sa.Table(
        "inventory",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("quantity >= 0", name="quantity_non_negative"),
        sa.Index("ix_inventory_company_quantity", "company_id", "quantity"),
    )

    sa.Table(
        "sales",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("number", sa.String(30), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), server_default="confirmed", nullable=False),
        sa.Column("currency", sa.String(3), server_default="PEN", nullable=False),
        sa.Column("total", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "confirmed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        *_timestamps(),
        sa.CheckConstraint("status IN ('confirmed')", name="status_allowed"),
        sa.CheckConstraint("currency = 'PEN'", name="currency_pen"),
        sa.CheckConstraint("total > 0", name="total_positive"),
        sa.UniqueConstraint("company_id", "number", name="uq_sales_company_number"),
        sa.UniqueConstraint(
            "company_id",
            "idempotency_key",
            name="uq_sales_company_idempotency_key",
        ),
        sa.Index("ix_sales_company_created_at", "company_id", "created_at"),
        sa.Index("ix_sales_company_customer", "company_id", "customer_id"),
        sa.Index("ix_sales_company_seller", "company_id", "seller_id"),
        sa.Index("ix_sales_company_status", "company_id", "status"),
    )

    sa.Table(
        "sale_details",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False),
        sa.Column("sku_snapshot", sa.String(50), nullable=False),
        sa.Column("product_name_snapshot", sa.String(180), nullable=False),
        sa.Column("category_name_snapshot", sa.String(120), nullable=False),
        sa.CheckConstraint("quantity > 0", name="quantity_positive"),
        sa.CheckConstraint("unit_price > 0", name="unit_price_positive"),
        sa.CheckConstraint("subtotal = round(unit_price * quantity, 2)", name="subtotal_matches"),
        sa.UniqueConstraint("sale_id", "product_id"),
        sa.Index("ix_sale_details_product", "product_id"),
    )

    sa.Table(
        "payments",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "sale_id",
            sa.Integer(),
            sa.ForeignKey("sales.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("method", sa.String(30), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(20), server_default="completed", nullable=False),
        sa.Column("reference", sa.String(120)),
        sa.Column(
            "paid_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("method IN ('cash', 'card', 'bank_transfer')", name="method_allowed"),
        sa.CheckConstraint("status = 'completed'", name="status_completed"),
        sa.CheckConstraint("amount > 0", name="amount_positive"),
        sa.Index("ix_payments_paid_at", "paid_at"),
    )

    sa.Table(
        "inventory_movements",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
        ),
        sa.Column("sale_id", sa.Integer(), sa.ForeignKey("sales.id", ondelete="RESTRICT")),
        sa.Column("movement_type", sa.String(30), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("stock_before", sa.Integer(), nullable=False),
        sa.Column("stock_after", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "movement_type IN ('initial', 'entry', 'adjustment_in', 'adjustment_out', 'sale')",
            name="movement_type_allowed",
        ),
        sa.CheckConstraint("quantity > 0", name="quantity_positive"),
        sa.CheckConstraint("stock_before >= 0", name="stock_before_non_negative"),
        sa.CheckConstraint("stock_after >= 0", name="stock_after_non_negative"),
        sa.CheckConstraint(
            "(movement_type = 'sale' AND sale_id IS NOT NULL) OR "
            "(movement_type <> 'sale' AND sale_id IS NULL)",
            name="sale_reference_matches_type",
        ),
        sa.Index("ix_inventory_movements_company_created", "company_id", "created_at"),
        sa.Index("ix_inventory_movements_product_created", "product_id", "created_at"),
        sa.Index("ix_inventory_movements_sale", "sale_id"),
    )

    sa.Table(
        "datasets",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column(
            "filters", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.Column("period_start", sa.Date()),
        sa.Column("period_end", sa.Date()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "source_type IN ('sales_snapshot', 'manual', 'upload')", name="source_type_allowed"
        ),
        sa.CheckConstraint(
            "period_end IS NULL OR period_start IS NULL OR period_end >= period_start",
            name="period_valid",
        ),
        sa.Index("ix_datasets_company_created", "company_id", "created_at"),
    )

    sa.Table(
        "dataset_variables",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("variable_type", sa.String(40), nullable=False),
        sa.Column("data_type", sa.String(20), nullable=False),
        sa.Column("source_field", sa.String(120)),
        sa.Column("unit", sa.String(40)),
        sa.CheckConstraint(
            "variable_type IN ('qualitative', 'quantitative_discrete', 'quantitative_continuous')",
            name="variable_type_allowed",
        ),
        sa.CheckConstraint(
            "data_type IN ('integer', 'decimal', 'text', 'boolean', 'datetime')",
            name="data_type_allowed",
        ),
        sa.UniqueConstraint("dataset_id", "name"),
    )

    sa.Table(
        "observations",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variable_id",
            sa.Integer(),
            sa.ForeignKey("dataset_variables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_record_id", sa.String(80)),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("value_numeric", sa.Numeric(20, 6)),
        sa.Column("value_text", sa.Text()),
        sa.Column("observed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "(value_numeric IS NOT NULL AND value_text IS NULL) OR "
            "(value_numeric IS NULL AND value_text IS NOT NULL)",
            name="single_value_type",
        ),
        sa.Index("ix_observations_dataset_variable", "dataset_id", "variable_id"),
        sa.Index("ix_observations_observed_at", "observed_at"),
    )

    sa.Table(
        "statistical_analyses",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("datasets.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "requested_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("analysis_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column(
            "parameters", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.Column("error_message", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "analysis_type IN ('mean', 'median', 'comparison', 'frequency', "
            "'random_variable', 'bayes')",
            name="analysis_type_allowed",
        ),
        sa.CheckConstraint("status IN ('pending', 'completed', 'failed')", name="status_allowed"),
        sa.Index("ix_statistical_analyses_company_created", "company_id", "created_at"),
        sa.Index("ix_statistical_analyses_dataset", "dataset_id"),
    )

    sa.Table(
        "statistical_results",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("statistical_analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "variable_id", sa.Integer(), sa.ForeignKey("dataset_variables.id", ondelete="SET NULL")
        ),
        sa.Column("metric", sa.String(60), nullable=False),
        sa.Column("numeric_value", sa.Numeric(20, 6)),
        sa.Column("text_value", sa.Text()),
        sa.Column(
            "details", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.CheckConstraint(
            "numeric_value IS NOT NULL OR text_value IS NOT NULL OR details <> '{}'::jsonb",
            name="result_has_value",
        ),
        sa.UniqueConstraint("analysis_id", "variable_id", "metric"),
    )

    sa.Table(
        "bayes_analyses",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("statistical_analyses.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("event_a", sa.String(200), nullable=False),
        sa.Column("event_b", sa.String(200), nullable=False),
        sa.Column("probability_a", sa.Numeric(8, 7), nullable=False),
        sa.Column("probability_b_given_a", sa.Numeric(8, 7), nullable=False),
        sa.Column("probability_b", sa.Numeric(8, 7), nullable=False),
        sa.Column("posterior", sa.Numeric(8, 7), nullable=False),
        sa.CheckConstraint("probability_a BETWEEN 0 AND 1", name="probability_a_range"),
        sa.CheckConstraint(
            "probability_b_given_a BETWEEN 0 AND 1", name="probability_b_given_a_range"
        ),
        sa.CheckConstraint("probability_b > 0 AND probability_b <= 1", name="probability_b_range"),
        sa.CheckConstraint("posterior BETWEEN 0 AND 1", name="posterior_range"),
    )

    sa.Table(
        "random_variables",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "dataset_id",
            sa.Integer(),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("variable_type", sa.String(20), nullable=False),
        sa.Column("distribution", postgresql.JSONB(), nullable=False),
        sa.Column("expected_value", sa.Numeric(20, 6)),
        sa.Column("variance", sa.Numeric(20, 6)),
        *_timestamps(),
        sa.CheckConstraint("variable_type IN ('discrete', 'continuous')", name="type_allowed"),
        sa.UniqueConstraint("dataset_id", "name"),
    )

    sa.Table(
        "insights",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("statistical_analyses.id", ondelete="SET NULL"),
        ),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(20), server_default="info", nullable=False),
        sa.Column(
            "evidence", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("severity IN ('info', 'warning', 'critical')", name="severity_allowed"),
        sa.Index("ix_insights_company_generated", "company_id", "generated_at"),
    )

    sa.Table(
        "reports",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "requested_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("report_type", sa.String(30), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column(
            "parameters", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("file_path", sa.Text()),
        sa.Column("error_message", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("generated_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "report_type IN ('sales', 'products', 'customers', 'sellers', 'statistical')",
            name="report_type_allowed",
        ),
        sa.CheckConstraint("status IN ('pending', 'completed', 'failed')", name="status_allowed"),
        sa.Index("ix_reports_company_created", "company_id", "created_at"),
    )

    sa.Table(
        "audit_logs",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.String(80)),
        sa.Column(
            "changes", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False
        ),
        sa.Column("request_id", sa.String(80)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Index("ix_audit_logs_company_created", "company_id", "created_at"),
        sa.Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        sa.Index("ix_audit_logs_user", "user_id"),
    )

    return metadata


def upgrade() -> None:
    schema = _build_schema()
    schema.create_all(bind=op.get_bind(), checkfirst=False)

    # Supabase exposes the public schema through its Data API. With RLS enabled
    # and no public policies, anon/authenticated clients cannot bypass FastAPI.
    for table_name in schema.tables:
        op.execute(sa.text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY'))


def downgrade() -> None:
    _build_schema().drop_all(bind=op.get_bind(), checkfirst=False)
