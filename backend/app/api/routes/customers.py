"""Authenticated customer catalog routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.customers import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from app.services.catalog import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=CustomerListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_customers(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    active: bool | None = None,
) -> CustomerListResponse:
    items, total = CustomerService(session, current_user.company_id).list(
        page=page,
        page_size=page_size,
        search=search,
        active=active,
    )
    return CustomerListResponse(
        items=[CustomerResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_customer(
    payload: CustomerCreate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> CustomerResponse:
    customer = CustomerService(session, current_user.company_id).create(payload)
    session.commit()
    return CustomerResponse.model_validate(customer)


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_customer(
    customer_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> CustomerResponse:
    customer = CustomerService(session, current_user.company_id).get(customer_id)
    return CustomerResponse.model_validate(customer)


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    current_user: AdminUser,
    session: DatabaseSession,
) -> CustomerResponse:
    customer = CustomerService(session, current_user.company_id).update(customer_id, payload)
    session.commit()
    return CustomerResponse.model_validate(customer)
