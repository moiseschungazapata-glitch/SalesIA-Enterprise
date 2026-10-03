"""Inventory request and response schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core import PydanticCustomError


class ManualMovementType(StrEnum):
    INITIAL = "initial"
    ENTRY = "entry"
    ADJUSTMENT_IN = "adjustment_in"
    ADJUSTMENT_OUT = "adjustment_out"


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    sku: str
    product_name: str
    category_name: str
    stock: int = Field(ge=0)
    active: bool
    updated_at: datetime


class InventoryListResponse(BaseModel):
    items: list[InventoryItemResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class InventoryMovementCreate(BaseModel):
    product_id: int = Field(gt=0)
    movement_type: ManualMovementType
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value: object) -> object:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PydanticCustomError("invalid_quantity", "La cantidad debe ser mayor que cero")
        return value

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        return " ".join(value.split())


class InventoryMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    sku: str
    product_name: str
    movement_type: str
    quantity: int = Field(gt=0)
    stock_before: int = Field(ge=0)
    stock_after: int = Field(ge=0)
    reason: str
    user_id: int
    user_name: str
    sale_id: int | None
    sale_number: str | None
    created_at: datetime


class InventoryMovementListResponse(BaseModel):
    items: list[InventoryMovementResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
