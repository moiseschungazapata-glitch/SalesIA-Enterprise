"""Schemas for revocable sessions and audit history."""

from datetime import datetime
from ipaddress import ip_address
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    expires_at: datetime
    last_seen_at: datetime
    revoked_at: datetime | None
    current: bool = False


class SessionLocationUpdate(BaseModel):
    ip_address: str = Field(min_length=3, max_length=45)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    isp: str | None = Field(default=None, max_length=160)
    timezone: str | None = Field(default=None, max_length=64)

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, value: str) -> str:
        return str(ip_address(value))

    @field_validator("city", "region", "country", "isp", "timezone", mode="before")
    @classmethod
    def clean_optional_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) and value.strip() else None


class AccessLocationResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_seen_at: datetime
    revoked_at: datetime | None
    current: bool = False
    latitude: float | None
    longitude: float | None
    city: str | None
    region: str | None
    country: str | None
    country_code: str | None
    isp: str | None
    timezone: str | None
    location_source: str | None
    located_at: datetime | None


class AccessLocationListResponse(BaseModel):
    items: list[AccessLocationResponse]


class SessionListResponse(BaseModel):
    items: list[SessionResponse]


class SessionActionResponse(BaseModel):
    revoked: int = Field(ge=0)


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    user_name: str | None
    action: str
    entity_type: str
    entity_id: str | None
    changes: dict[str, Any]
    request_id: str | None
    ip_address: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
