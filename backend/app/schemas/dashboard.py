"""Response contracts for the phase 10 executive analytics dashboard."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class DashboardPeriod(BaseModel):
    date_from: date
    date_to: date
    granularity: Literal["day", "week", "month"]


class DashboardKpis(BaseModel):
    sales_total: Decimal = Field(ge=0)
    transactions: int = Field(ge=0)
    active_customers: int = Field(ge=0)
    units_sold: int = Field(ge=0)
    ticket_average: Decimal = Field(ge=0)
    sales_mean: Decimal = Field(ge=0)
    sales_median: Decimal = Field(ge=0)


class DashboardPeriodPoint(BaseModel):
    period: date
    revenue: Decimal = Field(ge=0)
    transactions: int = Field(ge=0)


class DashboardBreakdownPoint(BaseModel):
    id: int
    label: str
    revenue: Decimal = Field(ge=0)
    transactions: int = Field(ge=0)
    units: int = Field(ge=0)
    share: Decimal = Field(ge=0, le=100)


class DashboardDistributionPoint(BaseModel):
    label: str
    frequency: int = Field(ge=0)
    percentage: Decimal = Field(ge=0, le=100)


class DashboardIntegerOption(BaseModel):
    id: int
    label: str


class DashboardBranchOption(BaseModel):
    id: Literal["main"]
    label: str


class DashboardFilterOptions(BaseModel):
    branches: list[DashboardBranchOption]
    sellers: list[DashboardIntegerOption]
    categories: list[DashboardIntegerOption]


class DashboardAppliedFilters(BaseModel):
    branch: Literal["main"]
    seller_id: int | None = None
    category_id: int | None = None


class DashboardSummaryResponse(BaseModel):
    generated_at: datetime
    currency: Literal["PEN"]
    period: DashboardPeriod
    applied_filters: DashboardAppliedFilters
    filter_options: DashboardFilterOptions
    kpis: DashboardKpis
    sales_by_period: list[DashboardPeriodPoint]
    sales_by_product: list[DashboardBreakdownPoint]
    sales_by_seller: list[DashboardBreakdownPoint]
    ticket_distribution: list[DashboardDistributionPoint]
