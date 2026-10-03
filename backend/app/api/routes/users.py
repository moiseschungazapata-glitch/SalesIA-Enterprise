"""Administrator-only user management routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
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
    current_user: AdminUser,
    session: DatabaseSession,
) -> UserResponse:
    user = UserService(session, current_user.company_id).create(payload)
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
    current_user: AdminUser,
    session: DatabaseSession,
) -> UserResponse:
    user = UserService(session, current_user.company_id).update(user_id, payload)
    session.commit()
    return _response(user)
