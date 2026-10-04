"""Persistent phase 12 reports, printable views and CSV exports."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import Principal, require_roles
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.reports import (
    ReportDetailResponse,
    ReportGenerateRequest,
    ReportListResponse,
)
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])

ReportsUser = Annotated[Principal, Depends(require_roles(ADMIN_ROLE, MANAGER_ROLE))]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/generate",
    response_model=ReportDetailResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def generate_report(
    payload: ReportGenerateRequest,
    current_user: ReportsUser,
    session: DatabaseSession,
) -> ReportDetailResponse:
    report = ReportService(session, current_user.company_id, current_user.id).generate(payload)
    session.commit()
    return ReportDetailResponse.model_validate(report)


@router.get("", response_model=ReportListResponse)
def list_reports(
    current_user: ReportsUser,
    session: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
    report_type: Annotated[
        Literal["sales", "products", "customers", "sellers", "statistical"] | None,
        Query(),
    ] = None,
    report_status: Annotated[
        Literal["pending", "completed", "failed"] | None,
        Query(alias="status"),
    ] = None,
) -> ReportListResponse:
    items, total = ReportService(
        session, current_user.company_id, current_user.id
    ).history(
        page=page,
        page_size=page_size,
        report_type=report_type,
        status=report_status,
    )
    return ReportListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{report_id}", response_model=ReportDetailResponse)
def get_report(
    report_id: int,
    current_user: ReportsUser,
    session: DatabaseSession,
) -> ReportDetailResponse:
    report = ReportService(session, current_user.company_id, current_user.id).get(report_id)
    return ReportDetailResponse.model_validate(report)


@router.get("/{report_id}/export")
def export_report(
    report_id: int,
    current_user: ReportsUser,
    session: DatabaseSession,
    export_format: Annotated[Literal["csv"], Query(alias="format")] = "csv",
) -> Response:
    del export_format
    content, filename = ReportService(
        session, current_user.company_id, current_user.id
    ).csv_export(report_id)
    return Response(
        content=content.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
