"""Schemas for statistics, random variables and probability endpoints."""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class StatisticalVariableType(StrEnum):
    QUALITATIVE = "qualitative"
    QUANTITATIVE_DISCRETE = "quantitative_discrete"
    QUANTITATIVE_CONTINUOUS = "quantitative_continuous"


class RandomVariableType(StrEnum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


class NumericSeriesRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    variable_name: str = Field(
        default="value", min_length=2, max_length=100, pattern=r"^[a-z][a-z0-9_]*$"
    )
    variable_label: str = Field(default="Valor observado", min_length=2, max_length=160)
    variable_type: Literal[
        StatisticalVariableType.QUANTITATIVE_DISCRETE,
        StatisticalVariableType.QUANTITATIVE_CONTINUOUS,
    ] = StatisticalVariableType.QUANTITATIVE_CONTINUOUS
    unit: str | None = Field(default=None, max_length=40)
    values: list[Decimal] = Field(min_length=1, max_length=1000)

    @field_validator("values")
    @classmethod
    def validate_values(cls, values: list[Decimal]) -> list[Decimal]:
        if any(not value.is_finite() for value in values):
            raise ValueError("Todos los valores deben ser numeros finitos")
        if any(abs(value) > Decimal("1000000000000") for value in values):
            raise ValueError("Los valores exceden el limite permitido")
        return values


class SalesComparisonRequest(BaseModel):
    metric: Literal["sale_total", "items_per_sale"] = "sale_total"
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_period(self) -> "SalesComparisonRequest":
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("La fecha final no puede ser anterior a la fecha inicial")
        return self


class EventProbabilityRequest(BaseModel):
    event_name: str = Field(min_length=2, max_length=160)
    favorable_cases: int = Field(ge=0, le=1000000)
    total_observations: int = Field(gt=0, le=1000000)

    @model_validator(mode="after")
    def validate_cases(self) -> "EventProbabilityRequest":
        if self.favorable_cases > self.total_observations:
            raise ValueError("Los casos favorables no pueden superar el total")
        return self


class BayesRequest(BaseModel):
    event_a: str = Field(min_length=2, max_length=200)
    event_b: str = Field(min_length=2, max_length=200)
    probability_a: Decimal = Field(ge=0, le=1)
    probability_b_given_a: Decimal = Field(ge=0, le=1)
    probability_b: Decimal = Field(gt=0, le=1)

    @field_validator("probability_a", "probability_b_given_a", "probability_b")
    @classmethod
    def validate_probability(cls, value: Decimal) -> Decimal:
        if not value.is_finite():
            raise ValueError("La probabilidad debe ser un numero finito")
        return value


class RandomVariableRequest(NumericSeriesRequest):
    random_variable_type: RandomVariableType = RandomVariableType.CONTINUOUS


class VariableDefinitionResponse(BaseModel):
    name: str
    label: str
    variable_type: StatisticalVariableType
    data_type: Literal["integer", "decimal", "text", "boolean", "datetime"]
    unit: str | None = None
    description: str


class AnalysisResultResponse(BaseModel):
    metric: str
    numeric_value: Decimal | None = None
    text_value: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AnalysisExecutionResponse(BaseModel):
    analysis_id: int
    dataset_id: int
    dataset_name: str
    analysis_type: Literal[
        "mean", "median", "comparison", "frequency", "random_variable", "bayes", "insight"
    ]
    variable_name: str | None = None
    variable_label: str | None = None
    variable_type: StatisticalVariableType | None = None
    observation_count: int = Field(ge=0)
    results: list[AnalysisResultResponse]
    created_at: datetime
    completed_at: datetime | None


class AnalysisHistoryItemResponse(AnalysisExecutionResponse):
    status: Literal["pending", "completed", "failed"]
    parameters: dict[str, Any] = Field(default_factory=dict)


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisHistoryItemResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
