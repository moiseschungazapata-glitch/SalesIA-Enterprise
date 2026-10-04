"""API tests for phase 05 authentication and user management."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password, verify_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.company import Company
from app.models.governance import AuditLog
from app.models.identity import AuthSession, Role, User

ADMIN_EMAIL = "admin@salesia.example.com"
ADMIN_PASSWORD = "correct-horse-2026"
SELLER_EMAIL = "seller@salesia.example.com"
SELLER_PASSWORD = "seller-password-2026"


@pytest.fixture
def session() -> Generator[Session, None, None]:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        test_engine,
        tables=[
            Company.__table__,
            Role.__table__,
            User.__table__,
            AuthSession.__table__,
            AuditLog.__table__,
        ],
    )

    with Session(test_engine, expire_on_commit=False) as database_session:
        company = Company(name="SalesIA Test", slug="salesia-test")
        admin_role = Role(code="administrator", name="Administrador")
        seller_role = Role(code="seller", name="Vendedor")
        manager_role = Role(code="manager", name="Gerente")
        database_session.add_all([company, admin_role, seller_role, manager_role])
        database_session.flush()
        database_session.add_all(
            [
                User(
                    company_id=company.id,
                    role_id=admin_role.id,
                    name="Admin Test",
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    active=True,
                ),
                User(
                    company_id=company.id,
                    role_id=seller_role.id,
                    name="Seller Test",
                    email=SELLER_EMAIL,
                    password_hash=hash_password(SELLER_PASSWORD),
                    active=True,
                ),
                User(
                    company_id=company.id,
                    role_id=manager_role.id,
                    name="Inactive Test",
                    email="inactive@salesia.example.com",
                    password_hash=hash_password("inactive-password-2026"),
                    active=False,
                ),
            ]
        )
        database_session.commit()
        yield database_session

    test_engine.dispose()


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_database() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_db] = override_database
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_and_current_session(client: TestClient) -> None:
    token = login(client, ADMIN_EMAIL.upper(), ADMIN_PASSWORD)

    response = client.get("/api/v1/auth/me", headers=bearer(token))

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Admin Test",
        "email": ADMIN_EMAIL,
        "role": "administrator",
        "active": True,
    }


def test_current_session_records_and_lists_approximate_ip_location(
    client: TestClient,
) -> None:
    token = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = bearer(token)

    updated = client.post(
        "/api/v1/security/sessions/current/location",
        headers=headers,
        json={
            "ip_address": "190.234.12.34",
            "latitude": -12.1219,
            "longitude": -77.0297,
            "city": "Lima",
            "region": "Lima",
            "country": "Peru",
            "country_code": "PE",
            "isp": "Proveedor de prueba",
            "timezone": "America/Lima",
        },
    )
    assert updated.status_code == 204

    response = client.get("/api/v1/security/access-locations", headers=headers)
    assert response.status_code == 200
    access = response.json()["items"][0]
    assert access["user_name"] == "Admin Test"
    assert access["ip_address"] == "190.234.12.34"
    assert access["latitude"] == pytest.approx(-12.1219)
    assert access["longitude"] == pytest.approx(-77.0297)
    assert access["city"] == "Lima"
    assert access["location_source"] == "public_ip"
    assert access["current"] is True


def test_invalid_and_inactive_logins_return_safe_errors(client: TestClient) -> None:
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": "incorrect-password-2026"},
    )
    unknown_email = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@salesia.example.com",
            "password": "incorrect-password-2026",
        },
    )
    inactive = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@salesia.example.com",
            "password": "inactive-password-2026",
        },
    )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert unknown_email.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert inactive.status_code == 403
    assert inactive.json()["error"]["code"] == "USER_INACTIVE"


def test_missing_or_invalid_token_is_rejected(client: TestClient) -> None:
    missing = client.get("/api/v1/auth/me")
    invalid = client.get("/api/v1/auth/me", headers=bearer("not-a-token"))

    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert missing.json()["error"]["code"] == "INVALID_TOKEN"
    assert invalid.json()["error"]["code"] == "INVALID_TOKEN"


def test_only_administrator_can_manage_users(client: TestClient) -> None:
    seller_token = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    admin_token = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    forbidden = client.get("/api/v1/users", headers=bearer(seller_token))
    allowed = client.get("/api/v1/users?page=1&page_size=2", headers=bearer(admin_token))

    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"
    assert allowed.status_code == 200
    assert allowed.json()["total"] == 3
    assert len(allowed.json()["items"]) == 2


def test_administrator_can_create_read_and_update_user(
    client: TestClient, session: Session
) -> None:
    token = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = bearer(token)
    create_response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "  Nueva   Gerente  ",
            "email": "New.Manager@SalesIA.Example.com",
            "password": "manager-password-2026",
            "role": "manager",
        },
    )

    assert create_response.status_code == 201, create_response.text
    created = create_response.json()
    assert created["name"] == "Nueva Gerente"
    assert created["email"] == "new.manager@salesia.example.com"
    assert created["role"] == "manager"
    assert "password" not in created

    stored_user = session.scalar(select(User).where(User.id == created["id"]))
    assert stored_user is not None
    assert stored_user.password_hash != "manager-password-2026"
    assert verify_password("manager-password-2026", stored_user.password_hash)

    get_response = client.get(f"/api/v1/users/{created['id']}", headers=headers)
    assert get_response.status_code == 200

    update_response = client.patch(
        f"/api/v1/users/{created['id']}",
        headers=headers,
        json={"active": False, "role": "seller"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["active"] is False
    assert update_response.json()["role"] == "seller"


def test_duplicate_email_and_validation_errors_are_uniform(client: TestClient) -> None:
    token = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = bearer(token)
    duplicate = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Duplicado",
            "email": ADMIN_EMAIL.upper(),
            "password": "another-password-2026",
            "role": "seller",
        },
    )
    invalid = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "X",
            "email": "not-an-email",
            "password": "short",
            "role": "unknown",
        },
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
    assert '"input"' not in invalid.text


def test_openapi_and_readiness_are_available(client: TestClient) -> None:
    openapi = client.get("/openapi.json")
    readiness = client.get("/health/ready")

    assert openapi.status_code == 200
    assert "/api/v1/auth/login" in openapi.json()["paths"]
    assert "/api/v1/users" in openapi.json()["paths"]
    assert openapi.json()["components"]["securitySchemes"]["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ready", "database": "connected"}
