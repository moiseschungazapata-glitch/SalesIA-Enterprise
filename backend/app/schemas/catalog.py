"""Category and product request and response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value is not None else None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @model_validator(mode="after")
    def require_one_field(self) -> "CategoryUpdate":
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar")
        for field in {"name", "active"} & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"El campo {field} no acepta null")
        return self


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    initial_stock: int = Field(default=0, ge=0)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None


class ProductUpdate(BaseModel):
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9._-]+$",
    )
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    category_id: int | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    active: bool | None = None

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value is not None else None

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @model_validator(mode="after")
    def require_one_field(self) -> "ProductUpdate":
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar")
        for field in {"sku", "name", "category_id", "unit_price", "active"} & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"El campo {field} no acepta null")
        return self


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None
    category_id: int
    category_name: str
    unit_price: Decimal
    stock: int = Field(ge=0)
    active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
