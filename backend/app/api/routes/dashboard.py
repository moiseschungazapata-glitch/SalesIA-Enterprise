"""Authenticated routes for the phase 10 executive dashboard."""

from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

DashboardUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def get_dashboard_summary(
    current_user: DashboardUser,
    session: DatabaseSession,
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    branch: Annotated[Literal["main"], Query()] = "main",
    seller_id: Annotated[int | None, Query(gt=0)] = None,
    category_id: Annotated[int | None, Query(gt=0)] = None,
) -> DashboardSummaryResponse:
    summary = DashboardService(session, current_user.company_id).summary(
        date_from=date_from,
        date_to=date_to,
        branch=branch,
        seller_id=seller_id,
        category_id=category_id,
    )
    return DashboardSummaryResponse.model_validate(summary)
