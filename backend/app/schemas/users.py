"""User-management schemas."""

from datetime import datetime
from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


class RoleCode(StrEnum):
    ADMINISTRATOR = "administrator"
    SELLER = "seller"
    MANAGER = "manager"


def _validate_password(value: SecretStr | None) -> SecretStr | None:
    if value is None:
        return None
    length = len(value.get_secret_value())
    if length < 12 or length > 128:
        raise ValueError("La contraseña debe tener entre 12 y 128 caracteres")
    return value


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: SecretStr
    role: RoleCode

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        validated = _validate_password(value)
        assert validated is not None
        return validated


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    email: EmailStr | None = None
    role: RoleCode | None = None
    active: bool | None = None
    new_password: SecretStr | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value is not None else None

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value: SecretStr | None) -> SecretStr | None:
        return _validate_password(value)

    @model_validator(mode="after")
    def require_one_field(self) -> "UserUpdate":
        if not self.model_fields_set:
            raise ValueError("Debe enviar al menos un campo para actualizar")
        non_nullable_fields = {"name", "email", "role", "active", "new_password"}
        invalid_nulls = [
            field
            for field in non_nullable_fields & self.model_fields_set
            if getattr(self, field) is None
        ]
        if invalid_nulls:
            raise ValueError(f"Estos campos no aceptan null: {', '.join(sorted(invalid_nulls))}")
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: RoleCode
    active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
