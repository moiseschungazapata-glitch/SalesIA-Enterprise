"""Persistence structures reserved for the statistical phases."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

JSON_DOCUMENT = JSON().with_variant(JSONB, "postgresql")


class Dataset(Base):
    __tablename__ = "datasets"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('sales_snapshot', 'manual', 'upload')", name="source_type_allowed"
        ),
        CheckConstraint(
            "period_end IS NULL OR period_start IS NULL OR period_end >= period_start",
            name="period_valid",
        ),
        Index("ix_datasets_company_created", "company_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    filters: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    period_start: Mapped[date | None] = mapped_column(Date)
    period_end: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class DatasetVariable(Base):
    __tablename__ = "dataset_variables"
    __table_args__ = (
        CheckConstraint(
            "variable_type IN ('qualitative', 'quantitative_discrete', 'quantitative_continuous')",
            name="variable_type_allowed",
        ),
        CheckConstraint(
            "data_type IN ('integer', 'decimal', 'text', 'boolean', 'datetime')",
            name="data_type_allowed",
        ),
        UniqueConstraint("dataset_id", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    variable_type: Mapped[str] = mapped_column(String(40), nullable=False)
    data_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_field: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str | None] = mapped_column(String(40))


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint(
            "(value_numeric IS NOT NULL AND value_text IS NULL) OR "
            "(value_numeric IS NULL AND value_text IS NOT NULL)",
            name="single_value_type",
        ),
        Index("ix_observations_dataset_variable", "dataset_id", "variable_id"),
        Index("ix_observations_observed_at", "observed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    variable_id: Mapped[int] = mapped_column(
        ForeignKey("dataset_variables.id", ondelete="CASCADE"), nullable=False
    )
    source_record_id: Mapped[str | None] = mapped_column(String(80))
    ordinal: Mapped[int] = mapped_column(nullable=False)
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    value_text: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StatisticalAnalysis(Base):
    __tablename__ = "statistical_analyses"
    __table_args__ = (
        CheckConstraint(
            "analysis_type IN ('mean', 'median', 'comparison', 'frequency', "
            "'random_variable', 'bayes')",
            name="analysis_type_allowed",
        ),
        CheckConstraint("status IN ('pending', 'completed', 'failed')", name="status_allowed"),
        Index("ix_statistical_analyses_company_created", "company_id", "created_at"),
        Index("ix_statistical_analyses_dataset", "dataset_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=False
    )
    requested_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    analysis_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    parameters: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StatisticalResult(Base):
    __tablename__ = "statistical_results"
    __table_args__ = (
        CheckConstraint(
            "numeric_value IS NOT NULL OR text_value IS NOT NULL OR details <> '{}'",
            name="result_has_value",
        ),
        UniqueConstraint("analysis_id", "variable_id", "metric"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("statistical_analyses.id", ondelete="CASCADE"), nullable=False
    )
    variable_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataset_variables.id", ondelete="SET NULL")
    )
    metric: Mapped[str] = mapped_column(String(60), nullable=False)
    numeric_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    text_value: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )


class BayesAnalysis(Base):
    __tablename__ = "bayes_analyses"
    __table_args__ = (
        CheckConstraint("probability_a BETWEEN 0 AND 1", name="probability_a_range"),
        CheckConstraint(
            "probability_b_given_a BETWEEN 0 AND 1", name="probability_b_given_a_range"
        ),
        CheckConstraint("probability_b > 0 AND probability_b <= 1", name="probability_b_range"),
        CheckConstraint("posterior BETWEEN 0 AND 1", name="posterior_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("statistical_analyses.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    event_a: Mapped[str] = mapped_column(String(200), nullable=False)
    event_b: Mapped[str] = mapped_column(String(200), nullable=False)
    probability_a: Mapped[Decimal] = mapped_column(Numeric(8, 7), nullable=False)
    probability_b_given_a: Mapped[Decimal] = mapped_column(Numeric(8, 7), nullable=False)
    probability_b: Mapped[Decimal] = mapped_column(Numeric(8, 7), nullable=False)
    posterior: Mapped[Decimal] = mapped_column(Numeric(8, 7), nullable=False)


class RandomVariable(TimestampMixin, Base):
    __tablename__ = "random_variables"
    __table_args__ = (
        CheckConstraint("variable_type IN ('discrete', 'continuous')", name="type_allowed"),
        UniqueConstraint("dataset_id", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    variable_type: Mapped[str] = mapped_column(String(20), nullable=False)
    distribution: Mapped[dict] = mapped_column(JSON_DOCUMENT, nullable=False)
    expected_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    variance: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))


class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = (
        CheckConstraint("severity IN ('info', 'warning', 'critical')", name="severity_allowed"),
        Index("ix_insights_company_generated", "company_id", "generated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey("statistical_analyses.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    evidence: Mapped[dict] = mapped_column(
        JSON_DOCUMENT, nullable=False, server_default=text("'{}'")
    )
    active: Mapped[bool] = mapped_column(nullable=False, default=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
