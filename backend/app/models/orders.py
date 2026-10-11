"""Commercial orders that can be converted atomically into sales."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'pending', 'approved', 'cancelled', 'converted')",
            name="status_allowed",
        ),
        CheckConstraint("total > 0", name="total_positive"),
        Index("ix_orders_company_created", "company_id", "created_at"),
        Index("ix_orders_company_status", "company_id", "status"),
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
    sale_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales.id", ondelete="RESTRICT"), unique=True
    )
    number: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PEN")
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OrderDetail(Base):
    __tablename__ = "order_details"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price > 0", name="unit_price_positive"),
        Index("ix_order_details_order", "order_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
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
