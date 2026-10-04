"""Direct service tests for phase 13 session revocation and account lockout."""

from datetime import UTC, datetime

import pytest
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.models.company import Company
from app.models.governance import AuditLog
from app.models.identity import AuthSession, Role, User
from app.services.identity import authenticate_user
from app.services.security import SessionService, record_audit


def http_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/login",
            "headers": [(b"user-agent", b"SalesIA security test")],
            "client": ("127.0.0.1", 12345),
            "state": {"request_id": "phase13-test"},
        }
    )


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            Company.__table__,
            Role.__table__,
            User.__table__,
            AuthSession.__table__,
            AuditLog.__table__,
        ],
    )
    database_session = Session(engine, expire_on_commit=False)
    company = Company(name="Security Test", slug="security-test")
    role = Role(code="administrator", name="Administrador")
    database_session.add_all([company, role])
    database_session.flush()
    database_session.add(
        User(
            company_id=company.id,
            role_id=role.id,
            name="Security Admin",
            email="security@salesia.example.com",
            password_hash=hash_password("security-password-2026"),
            active=True,
        )
    )
    database_session.commit()
    yield database_session
    database_session.close()
    engine.dispose()


def test_token_requires_an_active_server_session(session: Session) -> None:
    user = session.scalar(select(User))
    assert user is not None
    token = create_access_token(user.id)
    auth_session = SessionService(session, user.company_id, user.id).create(
        token, http_request()
    )
    record_audit(
        session,
        company_id=user.company_id,
        user_id=user.id,
        action="auth.login",
        entity_type="session",
        entity_id=auth_session.id,
        request=http_request(),
    )
    session.commit()

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token.encoded)
    principal = get_current_user(credentials, session)
    assert principal.session_id == auth_session.id

    SessionService(session, user.company_id, user.id).revoke(auth_session.id)
    session.commit()
    with pytest.raises(AppError) as revoked:
        get_current_user(credentials, session)
    assert revoked.value.code == "INVALID_TOKEN"
    assert session.scalar(select(AuditLog.action)) == "auth.login"


def test_repeated_failures_lock_the_account(session: Session) -> None:
    for _ in range(settings.login_max_failed_attempts):
        with pytest.raises(AppError) as rejected:
            authenticate_user(
                session,
                "security@salesia.example.com",
                "wrong-password-2026",
            )
        assert rejected.value.code == "INVALID_CREDENTIALS"
        session.commit()

    user = session.scalar(select(User))
    assert user is not None
    assert user.locked_until is not None
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=UTC)
    assert locked_until > datetime.now(UTC)

    with pytest.raises(AppError) as locked:
        authenticate_user(
            session,
            "security@salesia.example.com",
            "security-password-2026",
        )
    assert locked.value.code == "ACCOUNT_LOCKED"
