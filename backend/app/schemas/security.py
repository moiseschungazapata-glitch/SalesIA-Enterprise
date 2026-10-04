"""Schemas for revocable sessions and audit history."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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
