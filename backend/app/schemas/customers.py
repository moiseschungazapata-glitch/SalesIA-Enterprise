"""Customer request and response schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class CustomerType(StrEnum):
    PERSON = "person"
    COMPANY = "company"


class DocumentType(StrEnum):
    DNI = "DNI"
    RUC = "RUC"


class CustomerCreate(BaseModel):
    customer_type: CustomerType
    document_type: DocumentType
    document_number: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=2, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("document_number")
    @classmethod
    def normalize_document(cls, value: str) -> str:
        return value.strip()

    @field_validator("phone", "address")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=500)
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value is not None else None

    @field_validator("phone", "address")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @model_validator(mode="after")
    def require_one_field(self) -> "CustomerUpdate":
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar")
        for field in {"name", "active"} & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"El campo {field} no acepta null")
        return self


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_type: CustomerType
    document_type: DocumentType
    document_number: str
    name: str
    phone: str | None
    email: EmailStr | None
    address: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
