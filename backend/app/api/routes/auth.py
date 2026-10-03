"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse, SessionUser
from app.schemas.common import ErrorResponse
from app.services.identity import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def login(
    payload: LoginRequest,
    session: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    user = authenticate_user(
        session,
        str(payload.email),
        payload.password.get_secret_value(),
    )
    access_token, expires_in = create_access_token(user.id)
    session.commit()
    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in,
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
