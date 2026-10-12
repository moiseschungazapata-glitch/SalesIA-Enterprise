"""Payment management contracts."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.sales import PaymentMethod


class PaymentCreate(BaseModel):
    sale_id: int = Field(gt=0)
    method: PaymentMethod
    amount: Decimal = Field(gt=0)
    reference: str | None = Field(default=None, max_length=120)


class PaymentAction(BaseModel):
    reason: str = Field(min_length=3, max_length=250)


class PaymentResponse(BaseModel):
    id: int
    sale_id: int
    sale_number: str
    customer_name: str
    method: PaymentMethod
    amount: Decimal
    status: Literal["completed", "cancelled", "refunded"]
    reference: str | None
    paid_at: datetime
    sale_total: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    payment_status: Literal["pending", "partial", "paid", "refunded"]


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int
