"""Endpoints for phase 11 deterministic business insights."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.insights import (
    InsightGenerationRequest,
    InsightGenerationResponse,
    InsightListResponse,
)
from app.services.insights import InsightService
from app.services.security import record_audit

router = APIRouter(prefix="/insights", tags=["insights"])

InsightsUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/generate",
    response_model=InsightGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def generate_insights(
    payload: InsightGenerationRequest,
    request: Request,
    current_user: InsightsUser,
    session: DatabaseSession,
) -> InsightGenerationResponse:
    result = InsightService(
        session, current_user.company_id, current_user.id
    ).generate(payload)
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="insight.generate",
        entity_type="statistical_analysis",
        entity_id=result.analysis_id,
        request=request,
        changes={"generated_count": result.generated_count},
    )
    session.commit()
    return InsightGenerationResponse.model_validate(result)


@router.get("", response_model=InsightListResponse)
def list_insights(
    current_user: InsightsUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
    category: Annotated[
        Literal["sales", "products", "sellers", "customers", "statistics"] | None,
        Query(),
    ] = None,
    severity: Annotated[Literal["info", "warning", "critical"] | None, Query()] = None,
    active: Annotated[bool | None, Query()] = None,
) -> InsightListResponse:
    items, total = InsightService(
        session, current_user.company_id, current_user.id
    ).history(
        page=page,
        page_size=page_size,
        category=category,
        severity=severity,
        active=active,
    )
    return InsightListResponse(items=items, total=total, page=page, page_size=page_size)
