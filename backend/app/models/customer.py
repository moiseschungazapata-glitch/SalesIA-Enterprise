"""Customer persistence model."""

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        CheckConstraint("customer_type IN ('person', 'company')", name="customer_type_allowed"),
        CheckConstraint("document_type IN ('DNI', 'RUC')", name="document_type_allowed"),
        CheckConstraint(
            "(customer_type = 'person' AND document_type = 'DNI' "
            "AND document_number ~ '^[0-9]{8}$') OR "
            "(customer_type = 'company' AND document_type = 'RUC' "
            "AND document_number ~ '^[0-9]{11}$')",
            name="document_matches_customer_type",
        ).ddl_if(dialect="postgresql"),
        UniqueConstraint("company_id", "document_number"),
        Index("ix_customers_company_active", "company_id", "active"),
        Index("ix_customers_company_name", "company_id", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    document_type: Mapped[str] = mapped_column(String(10), nullable=False)
    document_number: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(254))
    address: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
