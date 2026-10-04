"""Contracts for persistent commercial and statistical reports."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

ReportType = Literal["sales", "products", "customers", "sellers", "statistical"]
ReportStatus = Literal["pending", "completed", "failed"]
ColumnFormat = Literal["text", "date", "datetime", "integer", "money", "decimal", "status"]


class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    title: str | None = Field(default=None, min_length=3, max_length=180)
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "ReportGenerateRequest":
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial")
        return self


class ReportColumn(BaseModel):
    key: str
    label: str
    format: ColumnFormat = "text"


class ReportContent(BaseModel):
    columns: list[ReportColumn]
    rows: list[dict[str, Any]]
    summary: dict[str, Any]


class ReportResponse(BaseModel):
    id: int
    report_type: ReportType
    title: str
    parameters: dict[str, Any]
    status: ReportStatus
    row_count: int = Field(ge=0)
    created_at: datetime
    generated_at: datetime | None


class ReportDetailResponse(ReportResponse):
    content: ReportContent


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
