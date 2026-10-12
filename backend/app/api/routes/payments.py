"""Payment management endpoints."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE, SELLER_ROLE
from app.db.session import get_db
from app.schemas.payments import PaymentAction, PaymentCreate, PaymentListResponse, PaymentResponse
from app.services.payments import PaymentService
from app.services.security import record_audit

router = APIRouter(prefix="/payments", tags=["payments"])
DatabaseSession = Annotated[Session, Depends(get_db)]
PaymentOperator = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, SELLER_ROLE))]
PaymentReader = Annotated[
    Principal, Depends(require_roles(ADMIN_ROLE, SELLER_ROLE, MANAGER_ROLE))
]


def service(session: Session, user: Principal) -> PaymentService:
    return PaymentService(session, user.company_id, user.id, user.role)


@router.get("", response_model=PaymentListResponse)
def list_payments(
    current_user: PaymentReader,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 100,
    payment_status: Annotated[
        Literal["completed", "cancelled", "refunded"] | None, Query(alias="status")
    ] = None,
) -> PaymentListResponse:
    items, total = service(session, current_user).list(page, page_size, payment_status)
    return PaymentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    request: Request,
    current_user: PaymentOperator,
    session: DatabaseSession,
) -> PaymentResponse:
    result = service(session, current_user).create(payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="payment.create",
        entity_type="payment",
        entity_id=result["id"],
        request=request,
        changes=payload.model_dump(mode="json"),
    )
    session.commit()
    return PaymentResponse.model_validate(result)


def reverse(
    payment_id: int,
    payload: PaymentAction,
    request: Request,
    user: Principal,
    session: Session,
    *,
    refund: bool,
) -> PaymentResponse:
    result = service(session, user).reverse(payment_id, refund=refund)
    action = "refund" if refund else "cancel"
    record_audit(
        session,
        company_id=user.company_id,
        user_id=user.id,
        action=f"payment.{action}",
        entity_type="payment",
        entity_id=payment_id,
        request=request,
        changes={"reason": payload.reason},
    )
    session.commit()
    return PaymentResponse.model_validate(result)


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    payload: PaymentAction,
    request: Request,
    current_user: PaymentOperator,
    session: DatabaseSession,
) -> PaymentResponse:
    return reverse(payment_id, payload, request, current_user, session, refund=True)


@router.post("/{payment_id}/cancel", response_model=PaymentResponse)
def cancel_payment(
    payment_id: int,
    payload: PaymentAction,
    request: Request,
    current_user: PaymentOperator,
    session: DatabaseSession,
) -> PaymentResponse:
    return reverse(payment_id, payload, request, current_user, session, refund=False)
