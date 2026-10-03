"""Persistent event probability and Bayes endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.statistics import (
    AnalysisExecutionResponse,
    BayesRequest,
    EventProbabilityRequest,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/probability", tags=["probability"])

AnalyticsUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/events",
    response_model=AnalysisExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def calculate_event_probability(
    payload: EventProbabilityRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    result = AnalyticsService(
        session, current_user.company_id, current_user.id
    ).analyze_event_probability(payload)
    session.commit()
    return AnalysisExecutionResponse.model_validate(result)


@router.post(
    "/bayes",
    response_model=AnalysisExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def calculate_bayes(
    payload: BayesRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    result = AnalyticsService(session, current_user.company_id, current_user.id).analyze_bayes(
        payload
    )
    session.commit()
    return AnalysisExecutionResponse.model_validate(result)
