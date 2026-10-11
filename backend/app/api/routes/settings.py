"""Tenant commercial settings."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, Principal, require_roles
from app.core.security import ADMIN_ROLE
from app.db.session import get_db
from app.models.company import Company
from app.schemas.settings import CommercialSettingsResponse, CommercialSettingsUpdate
from app.services.security import record_audit

router = APIRouter(prefix="/commercial-settings", tags=["commercial-settings"])
DatabaseSession = Annotated[Session, Depends(get_db)]
Administrator = Annotated[Principal, Depends(require_roles(ADMIN_ROLE))]


def response(company: Company) -> CommercialSettingsResponse:
    return CommercialSettingsResponse(
        tax_rate=company.tax_rate,
        prices_include_tax=company.prices_include_tax,
        max_discount_percent=company.max_discount_percent,
    )


@router.get("", response_model=CommercialSettingsResponse)
def get_settings(current_user: CurrentUser, session: DatabaseSession) -> CommercialSettingsResponse:
    return response(session.get_one(Company, current_user.company_id))


@router.patch("", response_model=CommercialSettingsResponse)
def update_settings(
    payload: CommercialSettingsUpdate,
    request: Request,
    current_user: Administrator,
    session: DatabaseSession,
) -> CommercialSettingsResponse:
    company = session.get_one(Company, current_user.company_id)
    before = response(company).model_dump(mode="json")
    company.tax_rate = payload.tax_rate
    company.prices_include_tax = payload.prices_include_tax
    company.max_discount_percent = payload.max_discount_percent
    record_audit(
        session,
        company_id=company.id,
        user_id=current_user.id,
        action="commercial_settings.update",
        entity_type="company",
        entity_id=company.id,
        request=request,
        changes={"before": before, "after": payload.model_dump(mode="json")},
    )
    session.commit()
    return response(company)
