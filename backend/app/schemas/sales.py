"""Sales request and response schemas."""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError


class PaymentMethod(StrEnum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value: object) -> object:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PydanticCustomError("invalid_quantity", "La cantidad debe ser mayor que cero")
        return value


class SaleCreate(BaseModel):
    customer_id: int = Field(gt=0)
    payment_method: PaymentMethod
    items: list[SaleItemCreate] = Field(min_length=1, max_length=100)

    @field_validator("payment_method", mode="before")
    @classmethod
    def validate_payment_method(cls, value: object) -> object:
        if value not in {method.value for method in PaymentMethod}:
            raise PydanticCustomError(
                "invalid_payment_method", "El metodo de pago no es valido"
            )
        return value

    @field_validator("items", mode="before")
    @classmethod
    def validate_items(cls, value: object) -> object:
        if isinstance(value, list) and not value:
            raise PydanticCustomError("empty_sale", "La venta debe incluir productos")
        return value

    @model_validator(mode="after")
    def reject_duplicate_products(self) -> "SaleCreate":
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Cada producto debe aparecer una sola vez")
        return self


class SalePartyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class SaleItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    product_name: str
    category_name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal
    subtotal: Decimal


class SalePaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    method: PaymentMethod
    amount: Decimal
    status: str
    paid_at: datetime


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    status: str
    created_at: datetime
    customer: SalePartyResponse
    seller: SalePartyResponse
    items: list[SaleItemResponse]
    payment: SalePaymentResponse
    currency: str
    total: Decimal


class SaleListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    status: str
    created_at: datetime
    customer: SalePartyResponse
    seller: SalePartyResponse
    items_count: int = Field(ge=1)
    payment_method: PaymentMethod
    currency: str
    total: Decimal


class SaleListResponse(BaseModel):
    items: list[SaleListItemResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
