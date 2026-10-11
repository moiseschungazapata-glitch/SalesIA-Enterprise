"""Request and response contracts for commercial orders."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.sales import PaymentMethod, SaleItemCreate, SaleResponse


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[SaleItemCreate] = Field(min_length=1, max_length=100)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    @model_validator(mode="after")
    def reject_duplicates(self) -> "OrderCreate":
        ids = [item.product_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Cada producto debe aparecer una sola vez")
        return self


class OrderUpdate(OrderCreate):
    pass


class OrderStatusUpdate(BaseModel):
    status: Literal["approved", "cancelled"]


class OrderConvert(BaseModel):
    payment_method: PaymentMethod


class OrderItemResponse(BaseModel):
    product_id: int
    sku: str
    product_name: str
    category_name: str
    quantity: int
    unit_price: Decimal
    gross_subtotal: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    number: str
    status: Literal["draft", "pending", "approved", "cancelled", "converted"]
    customer_id: int
    customer_name: str
    seller_id: int
    seller_name: str
    sale_id: int | None
    currency: Literal["PEN"]
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    tax_rate: Decimal
    general_discount_percent: Decimal
    total: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int


class OrderConversionResponse(BaseModel):
    order: OrderResponse
    sale: SaleResponse
