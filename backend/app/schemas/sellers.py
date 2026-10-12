"""Seller profile and performance contracts."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class SellerProfileUpdate(BaseModel):
    employee_code: str = Field(min_length=2, max_length=30)
    phone: str | None = Field(default=None, max_length=30)
    document_number: str | None = Field(default=None, max_length=30)
    hire_date: date | None = None
    zone: str | None = Field(default=None, max_length=120)
    monthly_target: Decimal = Field(default=Decimal("0"), ge=0)
    commission_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    employment_status: Literal["active", "leave", "terminated"] = "active"


class SellerResponse(BaseModel):
    user_id: int
    employee_id: int | None
    employee_code: str | None
    name: str
    email: str
    phone: str | None
    document_number: str | None
    hire_date: date | None
    zone: str | None
    monthly_target: Decimal
    commission_percent: Decimal
    employment_status: Literal["active", "leave", "terminated"]
    active: bool
    sales_count: int
    sales_total: Decimal
    commission_estimate: Decimal
    target_progress_percent: Decimal
    created_at: datetime


class SellerListResponse(BaseModel):
    items: list[SellerResponse]
    total: int
