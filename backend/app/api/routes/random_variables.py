"""Persistent random-variable analysis endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.statistics import AnalysisExecutionResponse, RandomVariableRequest
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/random-variables", tags=["random-variables"])

AnalyticsUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/analyze",
    response_model=AnalysisExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def analyze_random_variable(
    payload: RandomVariableRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    result = AnalyticsService(
        session, current_user.company_id, current_user.id
    ).analyze_random_variable(payload)
    session.commit()
    return AnalysisExecutionResponse.model_validate(result)
