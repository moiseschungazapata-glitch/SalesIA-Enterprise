"""Authenticated product catalog routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.schemas.catalog import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.common import ErrorResponse
from app.services.catalog import ProductRecord, ProductService

router = APIRouter(prefix="/products", tags=["products"])

AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


def _response(product: ProductRecord) -> ProductResponse:
    return ProductResponse.model_validate(product)


@router.get(
    "",
    response_model=ProductListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_products(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
    active: bool | None = None,
) -> ProductListResponse:
    items, total = ProductService(session, current_user.company_id, current_user.id).list(
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        active=active,
    )
    return ProductListResponse(
        items=[_response(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_product(
    payload: ProductCreate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> ProductResponse:
    product = ProductService(session, current_user.company_id, current_user.id).create(payload)
    session.commit()
    return _response(product)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_product(
    product_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> ProductResponse:
    product = ProductService(session, current_user.company_id, current_user.id).get(product_id)
    return _response(product)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> ProductResponse:
    product = ProductService(session, current_user.company_id, current_user.id).update(
        product_id, payload
    )
    session.commit()
    return _response(product)
