"""Authenticated transactional sales routes."""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE, SELLER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.sales import SaleCreate, SaleListItemResponse, SaleListResponse, SaleResponse
from app.services.operations import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])

SalesCreator = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, SELLER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=SaleListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_sales(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    number: Annotated[str | None, Query(max_length=30)] = None,
    customer_id: Annotated[int | None, Query(gt=0)] = None,
    seller_id: Annotated[int | None, Query(gt=0)] = None,
    sale_status: Annotated[Literal["confirmed"] | None, Query(alias="status")] = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SaleListResponse:
    items, total = SalesService(
        session,
        current_user.company_id,
        current_user.id,
        current_user.role,
    ).list(
        page=page,
        page_size=page_size,
        number=number,
        customer_id=customer_id,
        seller_id=seller_id,
        status=sale_status,
        date_from=date_from,
        date_to=date_to,
    )
    return SaleListResponse(
        items=[SaleListItemResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_sale(
    payload: SaleCreate,
    current_user: SalesCreator,
    session: DatabaseSession,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> SaleResponse:
    sale = SalesService(
        session,
        current_user.company_id,
        current_user.id,
        current_user.role,
    ).create(payload, idempotency_key)
    session.commit()
    return SaleResponse.model_validate(sale)


@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def get_sale(
    sale_id: int,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> SaleResponse:
    sale = SalesService(
        session,
        current_user.company_id,
        current_user.id,
        current_user.role,
    ).get(sale_id)
    return SaleResponse.model_validate(sale)
