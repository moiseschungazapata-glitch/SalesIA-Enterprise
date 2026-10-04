"""Request and response contracts for deterministic business insights."""

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

InsightCategory = Literal["sales", "products", "sellers", "customers", "statistics"]
InsightSeverity = Literal["info", "warning", "critical"]


class InsightGenerationRequest(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    branch: Literal["main"] = "main"
    seller_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_period(self) -> "InsightGenerationRequest":
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial")
        return self


class InsightResponse(BaseModel):
    id: int
    analysis_id: int
    dataset_id: int
    dataset_name: str
    title: str
    description: str
    category: InsightCategory
    rule_code: str
    severity: InsightSeverity
    evidence: dict[str, Any]
    active: bool
    period_start: date | None
    period_end: date | None
    generated_at: datetime


class InsightGenerationResponse(BaseModel):
    analysis_id: int
    dataset_id: int
    generated_count: int = Field(ge=0)
    items: list[InsightResponse]


class InsightListResponse(BaseModel):
    items: list[InsightResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
