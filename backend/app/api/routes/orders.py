"""Commercial order endpoints."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE, SELLER_ROLE
from app.db.session import get_db
from app.schemas.orders import (
    OrderConversionResponse,
    OrderConvert,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
    OrderUpdate,
)
from app.schemas.sales import SaleResponse
from app.services.orders import OrderService
from app.services.security import record_audit

router = APIRouter(prefix="/orders", tags=["orders"])
OrderCreator = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, SELLER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


def service(session: Session, user: Principal) -> OrderService:
    return OrderService(session, user.company_id, user.id, user.role)


@router.get("", response_model=OrderListResponse)
def list_orders(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    order_status: Annotated[
        Literal["draft", "pending", "approved", "cancelled", "converted"] | None,
        Query(alias="status"),
    ] = None,
) -> OrderListResponse:
    items, total = service(session, current_user).list(page, page_size, order_status)
    return OrderListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate, request: Request, current_user: OrderCreator, session: DatabaseSession
) -> OrderResponse:
    result = service(session, current_user).create(payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="order.create",
        entity_type="order",
        entity_id=result["id"],
        request=request,
        changes={"items": len(payload.items)},
    )
    session.commit()
    return OrderResponse.model_validate(result)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, current_user: CurrentUser, session: DatabaseSession) -> OrderResponse:
    return OrderResponse.model_validate(service(session, current_user).get(order_id))


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    request: Request,
    current_user: OrderCreator,
    session: DatabaseSession,
) -> OrderResponse:
    result = service(session, current_user).update(order_id, payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="order.update",
        entity_type="order",
        entity_id=order_id,
        request=request,
    )
    session.commit()
    return OrderResponse.model_validate(result)


@router.post("/{order_id}/status", response_model=OrderResponse)
def change_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    request: Request,
    current_user: OrderCreator,
    session: DatabaseSession,
) -> OrderResponse:
    result = service(session, current_user).change_status(order_id, payload.status)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action=f"order.{payload.status}",
        entity_type="order",
        entity_id=order_id,
        request=request,
    )
    session.commit()
    return OrderResponse.model_validate(result)


@router.post(
    "/{order_id}/convert",
    response_model=OrderConversionResponse,
    status_code=status.HTTP_201_CREATED,
)
def convert_order(
    order_id: int,
    payload: OrderConvert,
    request: Request,
    current_user: OrderCreator,
    session: DatabaseSession,
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
) -> OrderConversionResponse:
    order, sale = service(session, current_user).convert(
        order_id, payload.payment_method.value, idempotency_key
    )
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="order.convert",
        entity_type="order",
        entity_id=order_id,
        request=request,
        changes={"sale_id": sale.id},
    )
    session.commit()
    return OrderConversionResponse(
        order=OrderResponse.model_validate(order), sale=SaleResponse.model_validate(sale)
    )
