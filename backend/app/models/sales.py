"""Sales header, immutable line snapshots and payments."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Sale(TimestampMixin, Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("status IN ('confirmed')", name="status_allowed"),
        CheckConstraint("currency = 'PEN'", name="currency_pen"),
        CheckConstraint("total > 0", name="total_positive"),
        UniqueConstraint("company_id", "number", name="uq_sales_company_number"),
        UniqueConstraint(
            "company_id",
            "idempotency_key",
            name="uq_sales_company_idempotency_key",
        ),
        Index("ix_sales_company_created_at", "company_id", "created_at"),
        Index("ix_sales_company_customer", "company_id", "customer_id"),
        Index("ix_sales_company_seller", "company_id", "seller_id"),
        Index("ix_sales_company_status", "company_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(30), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PEN")
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SaleDetail(Base):
    __tablename__ = "sale_details"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price > 0", name="unit_price_positive"),
        CheckConstraint("subtotal = round(unit_price * quantity, 2)", name="subtotal_matches"),
        UniqueConstraint("sale_id", "product_id"),
        Index("ix_sale_details_product", "product_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    sku_snapshot: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name_snapshot: Mapped[str] = mapped_column(String(180), nullable=False)
    category_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("method IN ('cash', 'card', 'bank_transfer')", name="method_allowed"),
        CheckConstraint("status = 'completed'", name="status_completed"),
        CheckConstraint("amount > 0", name="amount_positive"),
        Index("ix_payments_paid_at", "paid_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    reference: Mapped[str | None] = mapped_column(String(120))
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
