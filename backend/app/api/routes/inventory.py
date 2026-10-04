"""Authenticated inventory routes."""

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.inventory import (
    InventoryItemResponse,
    InventoryListResponse,
    InventoryMovementCreate,
    InventoryMovementListResponse,
    InventoryMovementResponse,
)
from app.services.operations import InventoryService
from app.services.security import record_audit

router = APIRouter(prefix="/inventory", tags=["inventory"])

AdminUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]
InventoryAuditor = Annotated[
    Principal,
    Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE)),
]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=InventoryListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_inventory(
    current_user: CurrentUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=100)] = None,
    active: bool | None = None,
) -> InventoryListResponse:
    items, total = InventoryService(session, current_user.company_id, current_user.id).list(
        page=page,
        page_size=page_size,
        search=search,
        active=active,
    )
    return InventoryListResponse(
        items=[InventoryItemResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/movements",
    response_model=InventoryMovementListResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def list_movements(
    current_user: InventoryAuditor,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    product_id: Annotated[int | None, Query(gt=0)] = None,
    movement_type: Annotated[
        Literal["initial", "entry", "adjustment_in", "adjustment_out", "sale"] | None,
        Query(alias="type"),
    ] = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> InventoryMovementListResponse:
    items, total = InventoryService(
        session, current_user.company_id, current_user.id
    ).list_movements(
        page=page,
        page_size=page_size,
        product_id=product_id,
        movement_type=movement_type,
        date_from=date_from,
        date_to=date_to,
    )
    return InventoryMovementListResponse(
        items=[InventoryMovementResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/movements",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_movement(
    payload: InventoryMovementCreate,
    request: Request,
    current_user: AdminUser,
    session: DatabaseSession,
) -> InventoryMovementResponse:
    movement = InventoryService(
        session, current_user.company_id, current_user.id
    ).create_movement(payload)
    record_audit(
        session, company_id=current_user.company_id, user_id=current_user.id,
        action="inventory.adjust", entity_type="inventory_movement", entity_id=movement.id,
        request=request,
        changes={"product_id": payload.product_id, "movement_type": payload.movement_type},
    )
    session.commit()
    return InventoryMovementResponse.model_validate(movement)
