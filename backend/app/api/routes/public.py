"""Public, privacy-limited endpoints used before authentication."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.schemas.security import AnonymousVisitCreate
from app.services.security import AnonymousVisitService

router = APIRouter(prefix="/public", tags=["public"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("/visits", status_code=204)
def record_anonymous_visit(
    payload: AnonymousVisitCreate,
    request: Request,
    session: DatabaseSession,
) -> None:
    company_id = session.scalar(
        select(Company.id).where(Company.active.is_(True)).order_by(Company.id).limit(1)
    )
    if company_id is None:
        return
    AnonymousVisitService(session, company_id).record(request, payload.model_dump())
    session.commit()
