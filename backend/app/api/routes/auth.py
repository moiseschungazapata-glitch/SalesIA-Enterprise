"""Authentication routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.exceptions import AppError
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse, SessionUser
from app.schemas.common import ErrorResponse
from app.services.identity import authenticate_user
from app.services.security import SessionService, record_audit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def login(
    payload: LoginRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    try:
        user = authenticate_user(
            session,
            str(payload.email),
            payload.password.get_secret_value(),
        )
    except AppError:
        failure = session.info.pop("login_failure", None)
        if failure:
            record_audit(
                session,
                company_id=failure["company_id"],
                user_id=failure["user_id"],
                action="auth.login_failed",
                entity_type="session",
                request=request,
                changes={"temporarily_locked": failure["locked"]},
            )
            session.commit()
        else:
            session.rollback()
            logger.warning("Rejected login for an unknown account")
        raise

    access_token = create_access_token(user.id)
    auth_session = SessionService(session, user.company_id, user.id).create(
        access_token, request
    )
    record_audit(
        session,
        company_id=user.company_id,
        user_id=user.id,
        action="auth.login",
        entity_type="session",
        entity_id=auth_session.id,
        request=request,
    )
    session.commit()
    return LoginResponse(
        access_token=access_token.encoded,
        expires_in=access_token.expires_in,
        user=AuthUser(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
        ),
    )


@router.get(
    "/me",
    response_model=SessionUser,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def me(current_user: CurrentUser) -> SessionUser:
    return SessionUser(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        active=current_user.active,
    )


@router.post(
    "/logout",
    status_code=204,
    responses={401: {"model": ErrorResponse}},
)
def logout(
    request: Request,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_db)],
) -> None:
    if current_user.session_id is not None:
        SessionService(session, current_user.company_id, current_user.id).revoke(
            current_user.session_id, "logout"
        )
    record_audit(
        session,
        company_id=current_user.company_id,
        user_id=current_user.id,
        action="auth.logout",
        entity_type="session",
        entity_id=current_user.session_id,
        request=request,
    )
    session.commit()
