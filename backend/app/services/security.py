"""Security session lifecycle and append-only audit operations."""

from datetime import UTC, datetime
from typing import Any

from fastapi import Request
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import AccessToken, hash_token_jti
from app.models.governance import AuditLog
from app.models.identity import AuthSession, User


def request_metadata(request: Request) -> tuple[str | None, str | None, str | None]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    request_id = getattr(request.state, "request_id", None)
    return ip_address, user_agent[:300] if user_agent else None, request_id


def record_audit(
    session: Session,
    *,
    company_id: int,
    user_id: int | None,
    action: str,
    entity_type: str,
    request: Request,
    entity_id: str | int | None = None,
    changes: dict[str, Any] | None = None,
) -> AuditLog:
    ip_address, _user_agent, request_id = request_metadata(request)
    entry = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        changes=changes or {},
        request_id=request_id,
        ip_address=ip_address,
    )
    session.add(entry)
    return entry


class SessionService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    def create(self, token: AccessToken, request: Request) -> AuthSession:
        ip_address, user_agent, _request_id = request_metadata(request)
        auth_session = AuthSession(
            company_id=self.company_id,
            user_id=self.user_id,
            token_jti_hash=hash_token_jti(token.jti),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=token.expires_at,
            last_seen_at=datetime.now(UTC),
        )
        self.session.add(auth_session)
        self.session.flush()
        return auth_session

    def list(self) -> list[AuthSession]:
        return list(
            self.session.scalars(
                select(AuthSession)
                .where(
                    AuthSession.company_id == self.company_id,
                    AuthSession.user_id == self.user_id,
                    AuthSession.revoked_at.is_(None),
                    AuthSession.expires_at > datetime.now(UTC),
                )
                .order_by(AuthSession.created_at.desc(), AuthSession.id.desc())
                .limit(50)
            )
        )

    def revoke(self, session_id: int, reason: str = "user_revoked") -> int:
        auth_session = self.session.scalar(
            select(AuthSession).where(
                AuthSession.id == session_id,
                AuthSession.company_id == self.company_id,
                AuthSession.user_id == self.user_id,
            )
        )
        if auth_session is None:
            raise AppError("SESSION_NOT_FOUND", "La sesion no existe", status_code=404)
        if auth_session.revoked_at is not None:
            return 0
        auth_session.revoked_at = datetime.now(UTC)
        auth_session.revoke_reason = reason
        self.session.flush()
        return 1

    def revoke_others(self, current_session_id: int) -> int:
        result = self.session.execute(
            update(AuthSession)
            .where(
                AuthSession.company_id == self.company_id,
                AuthSession.user_id == self.user_id,
                AuthSession.id != current_session_id,
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC), revoke_reason="revoke_others")
        )
        return int(result.rowcount or 0)

    def revoke_all(self, reason: str) -> int:
        result = self.session.execute(
            update(AuthSession)
            .where(
                AuthSession.company_id == self.company_id,
                AuthSession.user_id == self.user_id,
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC), revoke_reason=reason)
        )
        return int(result.rowcount or 0)


class AuditService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        action: str | None = None,
        user_id: int | None = None,
    ) -> tuple[list[tuple[AuditLog, str | None]], int]:
        conditions = [AuditLog.company_id == self.company_id]
        if action:
            conditions.append(AuditLog.action == action)
        if user_id is not None:
            conditions.append(AuditLog.user_id == user_id)
        total = self.session.scalar(select(func.count(AuditLog.id)).where(*conditions))
        rows = self.session.execute(
            select(AuditLog, User.name)
            .outerjoin(User, User.id == AuditLog.user_id)
            .where(*conditions)
            .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return rows, int(total or 0)
