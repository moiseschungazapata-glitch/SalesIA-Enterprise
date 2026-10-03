"""Authenticated endpoints for descriptive statistics and analysis history."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.statistics import (
    AnalysisExecutionResponse,
    AnalysisHistoryResponse,
    NumericSeriesRequest,
    SalesComparisonRequest,
    VariableDefinitionResponse,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])

AnalyticsUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/variables", response_model=list[VariableDefinitionResponse])
def list_statistical_variables(
    _current_user: AnalyticsUser,
) -> list[VariableDefinitionResponse]:
    return [
        VariableDefinitionResponse.model_validate(item)
        for item in AnalyticsService.variable_catalog()
    ]


@router.post(
    "/sales/compare",
    response_model=AnalysisExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def compare_sales_statistics(
    payload: SalesComparisonRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    result = AnalyticsService(session, current_user.company_id, current_user.id).analyze_sales(
        payload
    )
    session.commit()
    return AnalysisExecutionResponse.model_validate(result)


def _execute_manual(
    payload: NumericSeriesRequest,
    current_user: Principal,
    session: Session,
    analysis_type: str,
) -> AnalysisExecutionResponse:
    result = AnalyticsService(
        session, current_user.company_id, current_user.id
    ).analyze_series(payload, analysis_type)
    session.commit()
    return AnalysisExecutionResponse.model_validate(result)


@router.post("/mean", response_model=AnalysisExecutionResponse, status_code=status.HTTP_201_CREATED)
def calculate_mean(
    payload: NumericSeriesRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    return _execute_manual(payload, current_user, session, "mean")


@router.post(
    "/median", response_model=AnalysisExecutionResponse, status_code=status.HTTP_201_CREATED
)
def calculate_median(
    payload: NumericSeriesRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    return _execute_manual(payload, current_user, session, "median")


@router.post(
    "/compare", response_model=AnalysisExecutionResponse, status_code=status.HTTP_201_CREATED
)
def compare_mean_and_median(
    payload: NumericSeriesRequest,
    current_user: AnalyticsUser,
    session: DatabaseSession,
) -> AnalysisExecutionResponse:
    return _execute_manual(payload, current_user, session, "comparison")


@router.get("/analyses", response_model=AnalysisHistoryResponse)
def list_analysis_history(
    current_user: AnalyticsUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AnalysisHistoryResponse:
    items, total = AnalyticsService(
        session, current_user.company_id, current_user.id
    ).history(page, page_size)
    return AnalysisHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
