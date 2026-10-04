"""Session control and administrator audit endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.security import (
    AuditLogListResponse,
    AuditLogResponse,
    SessionActionResponse,
    SessionListResponse,
    SessionResponse,
)
from app.services.security import AuditService, SessionService, record_audit

router = APIRouter(prefix="/security", tags=["security"])
AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(current_user: CurrentUser, session: DatabaseSession) -> SessionListResponse:
    items = SessionService(session, current_user.company_id, current_user.id).list()
    return SessionListResponse(
        items=[
            SessionResponse.model_validate(item).model_copy(
                update={"current": item.id == current_user.session_id}
            )
            for item in items
        ]
    )


@router.post(
    "/sessions/{session_id}/revoke",
    response_model=SessionActionResponse,
    responses={404: {"model": ErrorResponse}},
)
def revoke_session(
    session_id: int,
    request: Request,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> SessionActionResponse:
    revoked = SessionService(session, current_user.company_id, current_user.id).revoke(
        session_id
    )
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="session.revoke",
        entity_type="session",
        entity_id=session_id,
        request=request,
        changes={"current_session": session_id == current_user.session_id},
    )
    session.commit()
    return SessionActionResponse(revoked=revoked)


@router.post("/sessions/revoke-others", response_model=SessionActionResponse)
def revoke_other_sessions(
    request: Request,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> SessionActionResponse:
    if current_user.session_id is None:
        return SessionActionResponse(revoked=0)
    revoked = SessionService(session, current_user.company_id, current_user.id).revoke_others(
        current_user.session_id
    )
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="session.revoke_others",
        entity_type="session",
        entity_id=current_user.session_id,
        request=request,
        changes={"revoked_count": revoked},
    )
    session.commit()
    return SessionActionResponse(revoked=revoked)


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    responses={403: {"model": ErrorResponse}},
)
def list_audit_logs(
    current_user: AdminUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    action: Annotated[str | None, Query(max_length=80)] = None,
    user_id: Annotated[int | None, Query(gt=0)] = None,
) -> AuditLogListResponse:
    rows, total = AuditService(session, current_user.company_id).list(
        page=page, page_size=page_size, action=action, user_id=user_id
    )
    return AuditLogListResponse(
        items=[
            AuditLogResponse(
                id=entry.id,
                user_id=entry.user_id,
                user_name=user_name,
                action=entry.action,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                changes=entry.changes,
                request_id=entry.request_id,
                ip_address=entry.ip_address,
                created_at=entry.created_at,
            )
            for entry, user_name in rows
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
