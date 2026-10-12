"""Seller profiles and performance endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.sellers import SellerListResponse, SellerProfileUpdate, SellerResponse
from app.services.security import record_audit
from app.services.sellers import SellerService

router = APIRouter(prefix="/sellers", tags=["sellers"])
DatabaseSession = Annotated[Session, Depends(get_db)]
SellerReader = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
SellerAdministrator = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]


@router.get("", response_model=SellerListResponse)
def list_sellers(current_user: SellerReader, session: DatabaseSession) -> SellerListResponse:
    items = SellerService(session, current_user.company_id).list()
    return SellerListResponse(items=items, total=len(items))


@router.put("/{user_id}", response_model=SellerResponse)
def update_seller(
    user_id: int,
    payload: SellerProfileUpdate,
    request: Request,
    current_user: SellerAdministrator,
    session: DatabaseSession,
) -> SellerResponse:
    result = SellerService(session, current_user.company_id).update(user_id, payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="seller.update",
        entity_type="employee",
        entity_id=result["employee_id"],
        request=request,
        changes=payload.model_dump(mode="json"),
    )
    session.commit()
    return SellerResponse.model_validate(result)
