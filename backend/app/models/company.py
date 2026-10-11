"""Company model used as the tenant boundary of business data."""

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(200))
    tax_id: Mapped[str | None] = mapped_column(String(20), unique=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="PEN")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="America/Lima")
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("18.00")
    )
    prices_include_tax: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("30.00")
    )

    __table_args__ = (
        CheckConstraint("tax_rate >= 0 AND tax_rate <= 100", name="tax_rate_range"),
        CheckConstraint(
            "max_discount_percent >= 0 AND max_discount_percent <= 100",
            name="max_discount_percent_range",
        ),
    )
