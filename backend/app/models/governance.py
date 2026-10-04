"""Reports and append-only audit records."""

from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

JSON_DOCUMENT = JSON().with_variant(JSONB, "postgresql")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint(
            "report_type IN ('sales', 'products', 'customers', 'sellers', 'statistical')",
            name="report_type_allowed",
        ),
        CheckConstraint("status IN ('pending', 'completed', 'failed')", name="status_allowed"),
        Index("ix_reports_company_created", "company_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    requested_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    parameters: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    file_path: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    content: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_company_created", "company_id", "created_at"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(80))
    changes: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    request_id: Mapped[str | None] = mapped_column(String(80))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
