"""Shared FastAPI dependencies for authentication and authorization."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import ALLOWED_ROLES, decode_access_token
from app.db.session import get_db
from app.models.company import Company
from app.models.identity import Role, User

bearer_scheme = HTTPBearer(bearerFormat="JWT", auto_error=False)


@dataclass(frozen=True)
class Principal:
    id: int
    company_id: int
    name: str
    email: str
    role: str
    active: bool
    created_at: datetime
    updated_at: datetime


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(
            "INVALID_TOKEN",
            "Debe enviar un token de acceso",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)
    row = session.execute(
        select(User, Role.code, Role.active, Company.active)
        .join(Role, Role.id == User.role_id)
        .join(Company, Company.id == User.company_id)
        .where(User.id == user_id)
    ).one_or_none()

    if row is None:
        raise AppError(
            "INVALID_TOKEN",
            "El usuario del token ya no existe",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, role_code, role_is_active, company_is_active = row
    if not user.active:
        raise AppError("USER_INACTIVE", "El usuario esta inactivo", status_code=403)
    if role_code not in ALLOWED_ROLES or not role_is_active or not company_is_active:
        raise AppError("FORBIDDEN", "El usuario no tiene un rol valido", status_code=403)

    return Principal(
        id=user.id,
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        role=role_code,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


CurrentUser = Annotated[Principal, Depends(get_current_user)]


def require_roles(*allowed_roles: str) -> Callable[[CurrentUser], Principal]:
    allowed = frozenset(allowed_roles)

    def authorize(current_user: CurrentUser) -> Principal:
        if current_user.role not in allowed:
            raise AppError(
                "FORBIDDEN",
                "No tiene permiso para realizar esta operacion",
                status_code=403,
            )
        return current_user

    return authorize
