"""Authenticated product category routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.schemas.catalog import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.schemas.common import ErrorResponse
from app.services.catalog import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=CategoryListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_categories(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    active: bool | None = None,
) -> CategoryListResponse:
    items, total = CategoryService(session, current_user.company_id).list(
        page=page,
        page_size=page_size,
        search=search,
        active=active,
    )
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def create_category(
    payload: CategoryCreate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> CategoryResponse:
    category = CategoryService(session, current_user.company_id).create(payload)
    session.commit()
    return CategoryResponse.model_validate(category)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> CategoryResponse:
    category = CategoryService(session, current_user.company_id).update(category_id, payload)
    session.commit()
    return CategoryResponse.model_validate(category)
