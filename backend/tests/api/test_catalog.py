"""API tests for phase 07 customers, categories, and products."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    AuditLog,
    AuthSession,
    Category,
    Company,
    Customer,
    Inventory,
    InventoryMovement,
    Product,
    Role,
    User,
)

ADMIN_EMAIL = "catalog.admin@salesia.example.com"
ADMIN_PASSWORD = "catalog-admin-2026"
SELLER_EMAIL = "catalog.seller@salesia.example.com"
SELLER_PASSWORD = "catalog-seller-2026"


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
            Customer.__table__,
            Category.__table__,
            Product.__table__,
            Inventory.__table__,
            InventoryMovement.__table__,
        ],
    )

    with Session(test_engine, expire_on_commit=False) as database_session:
        company = Company(name="SalesIA Catalog Test", slug="salesia-catalog-test")
        other_company = Company(name="Other Company", slug="other-company")
        admin_role = Role(code="administrator", name="Administrador")
        seller_role = Role(code="seller", name="Vendedor")
        manager_role = Role(code="manager", name="Gerente")
        database_session.add_all(
            [company, other_company, admin_role, seller_role, manager_role]
        )
        database_session.flush()
        database_session.add_all(
            [
                User(
                    company_id=company.id,
                    role_id=admin_role.id,
                    name="Catalog Admin",
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    active=True,
                ),
                User(
                    company_id=company.id,
                    role_id=seller_role.id,
                    name="Catalog Seller",
                    email=SELLER_EMAIL,
                    password_hash=hash_password(SELLER_PASSWORD),
                    active=True,
                ),
                Category(
                    company_id=company.id,
                    name="General",
                    description="Categoria inicial",
                    active=True,
                ),
                Customer(
                    company_id=other_company.id,
                    customer_type="person",
                    document_type="DNI",
                    document_number="87654321",
                    name="Cliente de otra empresa",
                    active=True,
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


def test_catalog_reads_require_authentication_and_allow_seller(client: TestClient) -> None:
    missing = client.get("/api/v1/customers")
    seller_headers = bearer(login(client, SELLER_EMAIL, SELLER_PASSWORD))

    assert missing.status_code == 401
    assert client.get("/api/v1/customers", headers=seller_headers).status_code == 200
    assert client.get("/api/v1/categories", headers=seller_headers).status_code == 200
    assert client.get("/api/v1/products", headers=seller_headers).status_code == 200

    forbidden = client.post(
        "/api/v1/customers",
        headers=seller_headers,
        json={
            "customer_type": "person",
            "document_type": "DNI",
            "document_number": "12345678",
            "name": "No autorizado",
        },
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_administrator_manages_customers_with_document_rules(client: TestClient) -> None:
    headers = bearer(login(client, ADMIN_EMAIL, ADMIN_PASSWORD))
    created_response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "customer_type": "person",
            "document_type": "DNI",
            "document_number": "12345678",
            "name": "  Ana   Torres  ",
            "phone": "999 888 777",
            "email": "ANA@EXAMPLE.COM",
            "address": "Lima",
        },
    )

    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["name"] == "Ana Torres"
    assert created["email"] == "ana@example.com"
    assert created["active"] is True

    duplicate = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "customer_type": "person",
            "document_type": "DNI",
            "document_number": "12345678",
            "name": "Duplicado",
        },
    )
    invalid_document = client.post(
        "/api/v1/customers",
        headers=headers,
        json={
            "customer_type": "company",
            "document_type": "DNI",
            "document_number": "12345678",
            "name": "Empresa invalida",
        },
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "DOCUMENT_ALREADY_EXISTS"
    assert invalid_document.status_code == 422
    assert invalid_document.json()["error"]["code"] == "INVALID_DOCUMENT"

    detail = client.get(f"/api/v1/customers/{created['id']}", headers=headers)
    updated = client.patch(
        f"/api/v1/customers/{created['id']}",
        headers=headers,
        json={"active": False, "email": None},
    )
    listing = client.get(
        "/api/v1/customers?search=12345678&active=false",
        headers=headers,
    )

    assert detail.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["active"] is False
    assert updated.json()["email"] is None
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["name"] == "Ana Torres"


def test_customers_are_isolated_by_company(client: TestClient) -> None:
    headers = bearer(login(client, ADMIN_EMAIL, ADMIN_PASSWORD))
    response = client.get("/api/v1/customers", headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_administrator_manages_categories(client: TestClient) -> None:
    headers = bearer(login(client, ADMIN_EMAIL, ADMIN_PASSWORD))
    created_response = client.post(
        "/api/v1/categories",
        headers=headers,
        json={
            "name": "  Tecnologia  ",
            "description": "Equipos tecnologicos",
        },
    )

    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["name"] == "Tecnologia"

    duplicate = client.post(
        "/api/v1/categories",
        headers=headers,
        json={"name": "tecnologia"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "CATEGORY_ALREADY_EXISTS"

    updated = client.patch(
        f"/api/v1/categories/{created['id']}",
        headers=headers,
        json={"active": False, "description": None},
    )
    listing = client.get(
        "/api/v1/categories?search=tec&active=false",
        headers=headers,
    )

    assert updated.status_code == 200
    assert updated.json()["active"] is False
    assert updated.json()["description"] is None
    assert listing.json()["total"] == 1


def test_product_creation_records_initial_stock_and_supports_updates(
    client: TestClient, session: Session
) -> None:
    headers = bearer(login(client, ADMIN_EMAIL, ADMIN_PASSWORD))
    category = session.scalar(select(Category).where(Category.name == "General"))
    assert category is not None

    created_response = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "sku": "tec-001",
            "name": "  Teclado   mecanico  ",
            "description": "Teclado empresarial",
            "category_id": category.id,
            "unit_price": "150.00",
            "initial_stock": 10,
        },
    )

    assert created_response.status_code == 201, created_response.text
    created = created_response.json()
    assert created["sku"] == "TEC-001"
    assert created["name"] == "Teclado mecanico"
    assert created["unit_price"] == "150.00"
    assert created["stock"] == 10

    inventory = session.scalar(select(Inventory).where(Inventory.product_id == created["id"]))
    movement = session.scalar(
        select(InventoryMovement).where(InventoryMovement.product_id == created["id"])
    )
    assert inventory is not None and inventory.quantity == 10
    assert movement is not None
    assert movement.movement_type == "initial"
    assert movement.stock_before == 0
    assert movement.stock_after == 10

    listing = client.get(
        f"/api/v1/products?search=teclado&category_id={category.id}&active=true",
        headers=headers,
    )
    updated = client.patch(
        f"/api/v1/products/{created['id']}",
        headers=headers,
        json={"unit_price": "175.50", "active": False},
    )

    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["stock"] == 10
    assert updated.status_code == 200
    assert updated.json()["unit_price"] == "175.50"
    assert updated.json()["active"] is False
    assert updated.json()["stock"] == 10


def test_product_rejects_duplicate_sku_and_inactive_category(
    client: TestClient, session: Session
) -> None:
    headers = bearer(login(client, ADMIN_EMAIL, ADMIN_PASSWORD))
    active_category = session.scalar(select(Category).where(Category.name == "General"))
    assert active_category is not None
    inactive_category = Category(
        company_id=active_category.company_id,
        name="Inactiva",
        active=False,
    )
    session.add(inactive_category)
    session.commit()

    payload = {
        "sku": "PRO-001",
        "name": "Producto base",
        "category_id": active_category.id,
        "unit_price": "25.00",
        "initial_stock": 0,
    }
    first = client.post("/api/v1/products", headers=headers, json=payload)
    duplicate = client.post(
        "/api/v1/products",
        headers=headers,
        json={**payload, "sku": "pro-001", "name": "Duplicado"},
    )
    inactive = client.post(
        "/api/v1/products",
        headers=headers,
        json={**payload, "sku": "PRO-002", "category_id": inactive_category.id},
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "SKU_ALREADY_EXISTS"
    assert inactive.status_code == 409
    assert inactive.json()["error"]["code"] == "CATEGORY_INACTIVE"


def test_openapi_publishes_phase_seven_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/customers" in paths
    assert "/api/v1/customers/{customer_id}" in paths
    assert "/api/v1/categories" in paths
    assert "/api/v1/categories/{category_id}" in paths
    assert "/api/v1/products" in paths
    assert "/api/v1/products/{product_id}" in paths
