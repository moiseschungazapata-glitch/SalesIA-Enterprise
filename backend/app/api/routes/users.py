"""Administrator-only user management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.users import (
    RoleCode,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.identity import UserRecord, UserService
from app.services.security import SessionService, record_audit

router = APIRouter(prefix="/users", tags=["users"])

AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


def _response(user: UserRecord) -> UserResponse:
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=UserListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_users(
    current_user: AdminUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    active: bool | None = None,
    role: RoleCode | None = None,
) -> UserListResponse:
    users, total = UserService(session, current_user.company_id).list(
        page=page,
        page_size=page_size,
        search=search,
        active=active,
        role=role.value if role else None,
    )
    return UserListResponse(
        items=[_response(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def create_user(
    payload: UserCreate,
    request: Request,
    current_user: AdminUser,
    session: DatabaseSession,
) -> UserResponse:
    user = UserService(session, current_user.company_id).create(payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        request=request,
        changes={"role": user.role, "active": user.active},
    )
    session.commit()
    return _response(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_user(
    user_id: int,
    current_user: AdminUser,
    session: DatabaseSession,
) -> UserResponse:
    return _response(UserService(session, current_user.company_id).get(user_id))


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    current_user: AdminUser,
    session: DatabaseSession,
) -> UserResponse:
    user = UserService(session, current_user.company_id).update(user_id, payload)
    sensitive_change = any(
        field in payload.model_fields_set
        for field in {"email", "role", "active", "new_password"}
    )
    if sensitive_change:
        SessionService(session, current_user.company_id, user_id).revoke_all(
            "user_security_change"
        )
    changes = {
        "fields": sorted(payload.model_fields_set - {"new_password"}),
        "password_changed": "new_password" in payload.model_fields_set,
        "sessions_revoked": sensitive_change,
    }
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="user.update",
        entity_type="user",
        entity_id=user_id,
        request=request,
        changes=changes,
    )
    session.commit()
    return _response(user)
