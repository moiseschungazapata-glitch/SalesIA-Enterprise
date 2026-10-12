"""API tests for phase 08 inventory and transactional sales."""

from collections.abc import Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
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
    Employee,
    Inventory,
    InventoryMovement,
    Order,
    OrderDetail,
    Payment,
    Product,
    Role,
    Sale,
    SaleDetail,
    User,
)

ADMIN_EMAIL = "operations.admin@salesia.example.com"
ADMIN_PASSWORD = "operations-admin-2026"
SELLER_EMAIL = "operations.seller@salesia.example.com"
SELLER_PASSWORD = "operations-seller-2026"
MANAGER_EMAIL = "operations.manager@salesia.example.com"
MANAGER_PASSWORD = "operations-manager-2026"


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
            Employee.__table__,
            Category.__table__,
            Product.__table__,
            Inventory.__table__,
            Order.__table__,
            OrderDetail.__table__,
            Sale.__table__,
            SaleDetail.__table__,
            Payment.__table__,
            InventoryMovement.__table__,
        ],
    )

    with Session(test_engine, expire_on_commit=False) as database_session:
        company = Company(name="SalesIA Operations Test", slug="salesia-operations-test")
        other_company = Company(name="Other Operations", slug="other-operations")
        roles = {
            code: Role(code=code, name=name)
            for code, name in [
                ("administrator", "Administrador"),
                ("seller", "Vendedor"),
                ("manager", "Gerente"),
            ]
        }
        database_session.add_all([company, other_company, *roles.values()])
        database_session.flush()

        users = [
            User(
                company_id=company.id,
                role_id=roles[role].id,
                name=name,
                email=email,
                password_hash=hash_password(password),
                active=True,
            )
            for role, name, email, password in [
                ("administrator", "Operations Admin", ADMIN_EMAIL, ADMIN_PASSWORD),
                ("seller", "Operations Seller", SELLER_EMAIL, SELLER_PASSWORD),
                ("manager", "Operations Manager", MANAGER_EMAIL, MANAGER_PASSWORD),
            ]
        ]
        database_session.add_all(users)
        category = Category(company_id=company.id, name="General", active=True)
        database_session.add(category)
        database_session.flush()
        customers = [
            Customer(
                company_id=company.id,
                customer_type="person",
                document_type="DNI",
                document_number="12345678",
                name="Ana Torres",
                active=True,
            ),
            Customer(
                company_id=company.id,
                customer_type="person",
                document_type="DNI",
                document_number="87654321",
                name="Cliente Inactivo",
                active=False,
            ),
        ]
        database_session.add_all(customers)
        products = [
            Product(
                company_id=company.id,
                category_id=category.id,
                sku="TEC-001",
                name="Teclado",
                unit_price=Decimal("150.00"),
                active=True,
            ),
            Product(
                company_id=company.id,
                category_id=category.id,
                sku="MOU-001",
                name="Mouse",
                unit_price=Decimal("50.00"),
                active=True,
            ),
            Product(
                company_id=company.id,
                category_id=category.id,
                sku="OLD-001",
                name="Producto Inactivo",
                unit_price=Decimal("20.00"),
                active=False,
            ),
            Product(
                company_id=company.id,
                category_id=category.id,
                sku="NEW-001",
                name="Producto Nuevo",
                unit_price=Decimal("35.00"),
                active=True,
            ),
        ]
        database_session.add_all(products)
        database_session.flush()
        database_session.add_all(
            [
                Inventory(company_id=company.id, product_id=products[0].id, quantity=10),
                Inventory(company_id=company.id, product_id=products[1].id, quantity=3),
                Inventory(company_id=company.id, product_id=products[2].id, quantity=4),
                Inventory(company_id=company.id, product_id=products[3].id, quantity=0),
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


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def entity_id(session: Session, model: type[object], name: str) -> int:
    entity = session.scalar(select(model).where(model.name == name))  # type: ignore[attr-defined]
    assert entity is not None
    return entity.id  # type: ignore[attr-defined, no-any-return]


def test_inventory_permissions_and_manual_ledger(
    client: TestClient, session: Session
) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    seller = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    manager = login(client, MANAGER_EMAIL, MANAGER_PASSWORD)
    product_id = entity_id(session, Product, "Teclado")

    assert client.get("/api/v1/inventory", headers=seller).status_code == 200
    assert client.get("/api/v1/inventory/movements", headers=seller).status_code == 403
    assert client.get("/api/v1/inventory/movements", headers=manager).status_code == 200
    forbidden = client.post(
        "/api/v1/inventory/movements",
        headers=seller,
        json={
            "product_id": product_id,
            "movement_type": "entry",
            "quantity": 2,
            "reason": "Intento sin permiso",
        },
    )
    assert forbidden.status_code == 403

    created = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": product_id,
            "movement_type": "entry",
            "quantity": 5,
            "reason": "Reposicion de mercaderia",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["stock_before"] == 10
    assert created.json()["stock_after"] == 15

    outgoing = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": product_id,
            "movement_type": "adjustment_out",
            "quantity": 4,
            "reason": "Correccion de conteo",
        },
    )
    assert outgoing.status_code == 201
    assert outgoing.json()["stock_after"] == 11

    movements = client.get(
        f"/api/v1/inventory/movements?product_id={product_id}&type=entry",
        headers=manager,
    )
    assert movements.status_code == 200
    assert movements.json()["total"] == 1


def test_inventory_rejects_invalid_manual_operations(
    client: TestClient, session: Session
) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    product_id = entity_id(session, Product, "Mouse")
    inactive_id = entity_id(session, Product, "Producto Inactivo")
    new_product_id = entity_id(session, Product, "Producto Nuevo")

    insufficient = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": product_id,
            "movement_type": "adjustment_out",
            "quantity": 10,
            "reason": "Salida imposible",
        },
    )
    inactive = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": inactive_id,
            "movement_type": "entry",
            "quantity": 1,
            "reason": "No debe aplicar",
        },
    )
    invalid_sale_type = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": product_id,
            "movement_type": "sale",
            "quantity": 1,
            "reason": "Venta manual",
        },
    )
    initial = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": new_product_id,
            "movement_type": "initial",
            "quantity": 6,
            "reason": "Carga inicial",
        },
    )
    repeated_initial = client.post(
        "/api/v1/inventory/movements",
        headers=admin,
        json={
            "product_id": new_product_id,
            "movement_type": "initial",
            "quantity": 1,
            "reason": "Carga inicial repetida",
        },
    )

    assert insufficient.status_code == 409
    assert insufficient.json()["error"]["code"] == "INSUFFICIENT_STOCK"
    assert inactive.status_code == 409
    assert inactive.json()["error"]["code"] == "PRODUCT_INACTIVE"
    assert invalid_sale_type.status_code == 422
    assert initial.status_code == 201
    assert initial.json()["stock_after"] == 6
    assert repeated_initial.status_code == 409
    assert repeated_initial.json()["error"]["code"] == "INITIAL_STOCK_ALREADY_RECORDED"
    inventory = session.scalar(select(Inventory).where(Inventory.product_id == product_id))
    assert inventory is not None and inventory.quantity == 3


def test_sale_is_atomic_and_uses_server_prices(client: TestClient, session: Session) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    keyboard_id = entity_id(session, Product, "Teclado")
    mouse_id = entity_id(session, Product, "Mouse")
    payload = {
        "customer_id": customer_id,
        "payment_method": "card",
        "items": [
            {"product_id": keyboard_id, "quantity": 2},
            {"product_id": mouse_id, "quantity": 1},
        ],
    }

    response = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json=payload,
    )
    assert response.status_code == 201, response.text
    sale = response.json()
    assert sale["number"] == f"V-{sale['id']:06d}"
    assert sale["total"] == "350.00"
    assert sale["payment"]["method"] == "card"
    assert sale["payment"]["amount"] == "350.00"
    assert [item["unit_price"] for item in sale["items"]] == ["150.00", "50.00"]

    stocks = dict(
        session.execute(
            select(Inventory.product_id, Inventory.quantity).where(
                Inventory.product_id.in_([keyboard_id, mouse_id])
            )
        ).all()
    )
    assert stocks == {keyboard_id: 8, mouse_id: 2}
    assert session.scalar(select(func.count(Payment.id))) == 1
    assert session.scalar(select(func.count(SaleDetail.id))) == 2
    assert (
        session.scalar(
            select(func.count(InventoryMovement.id)).where(
                InventoryMovement.movement_type == "sale"
            )
        )
        == 2
    )


def test_sale_idempotency_prevents_duplicates(client: TestClient, session: Session) -> None:
    seller = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    product_id = entity_id(session, Product, "Teclado")
    key = str(uuid4())
    payload = {
        "customer_id": customer_id,
        "payment_method": "cash",
        "items": [{"product_id": product_id, "quantity": 1}],
    }
    headers = {**seller, "Idempotency-Key": key}

    first = client.post("/api/v1/sales", headers=headers, json=payload)
    repeated = client.post("/api/v1/sales", headers=headers, json=payload)
    changed = client.post(
        "/api/v1/sales",
        headers=headers,
        json={**payload, "items": [{"product_id": product_id, "quantity": 2}]},
    )

    assert first.status_code == 201
    assert repeated.status_code == 201
    assert repeated.json()["id"] == first.json()["id"]
    assert changed.status_code == 409
    assert changed.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert session.scalar(select(func.count(Sale.id))) == 1
    inventory = session.scalar(select(Inventory).where(Inventory.product_id == product_id))
    assert inventory is not None and inventory.quantity == 9


def test_pending_sale_accepts_partial_payments_and_refund(
    client: TestClient, session: Session
) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    product_id = entity_id(session, Product, "Teclado")
    sale_response = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": customer_id,
            "payment_method": "cash",
            "payment_amount": "0",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    assert sale_response.status_code == 201, sale_response.text
    sale = sale_response.json()
    assert sale["payment_status"] == "pending"
    assert Decimal(sale["paid_amount"]) == Decimal("0.00")
    assert sale["balance_due"] == "150.00"

    payment_response = client.post(
        "/api/v1/payments",
        headers=admin,
        json={
            "sale_id": sale["id"],
            "method": "bank_transfer",
            "amount": "60.00",
            "reference": "OP-TEST-001",
        },
    )
    assert payment_response.status_code == 201, payment_response.text
    payment = payment_response.json()
    assert payment["payment_status"] == "partial"
    assert payment["balance_due"] == "90.00"

    refund_response = client.post(
        f"/api/v1/payments/{payment['id']}/refund",
        headers=admin,
        json={"reason": "Prueba de devolución"},
    )
    assert refund_response.status_code == 200, refund_response.text
    assert refund_response.json()["status"] == "refunded"
    assert refund_response.json()["payment_status"] == "refunded"
    assert refund_response.json()["balance_due"] == "150.00"


def test_administrator_configures_seller_profile_and_manager_can_read(
    client: TestClient, session: Session
) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    manager = login(client, MANAGER_EMAIL, MANAGER_PASSWORD)
    seller_id = session.scalar(select(User.id).where(User.email == SELLER_EMAIL))
    assert seller_id is not None

    updated = client.put(
        f"/api/v1/sellers/{seller_id}",
        headers=admin,
        json={
            "employee_code": "VEN-LIM-01",
            "phone": "999111222",
            "document_number": "76543210",
            "hire_date": "2026-10-01",
            "zone": "Lima Centro",
            "monthly_target": "10000.00",
            "commission_percent": "5.00",
            "employment_status": "active",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["employee_code"] == "VEN-LIM-01"
    assert updated.json()["zone"] == "Lima Centro"

    listing = client.get("/api/v1/sellers", headers=manager)
    assert listing.status_code == 200, listing.text
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["commission_percent"] == "5.00"


def test_failed_sale_does_not_change_any_stock(client: TestClient, session: Session) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    keyboard_id = entity_id(session, Product, "Teclado")
    mouse_id = entity_id(session, Product, "Mouse")

    response = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": customer_id,
            "payment_method": "bank_transfer",
            "items": [
                {"product_id": keyboard_id, "quantity": 2},
                {"product_id": mouse_id, "quantity": 99},
            ],
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_STOCK"
    stocks = dict(
        session.execute(
            select(Inventory.product_id, Inventory.quantity).where(
                Inventory.product_id.in_([keyboard_id, mouse_id])
            )
        ).all()
    )
    assert stocks == {keyboard_id: 10, mouse_id: 3}
    assert session.scalar(select(func.count(Sale.id))) == 0


def test_sale_validates_customer_product_and_request(client: TestClient, session: Session) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    manager = login(client, MANAGER_EMAIL, MANAGER_PASSWORD)
    inactive_customer_id = entity_id(session, Customer, "Cliente Inactivo")
    active_customer_id = entity_id(session, Customer, "Ana Torres")
    inactive_product_id = entity_id(session, Product, "Producto Inactivo")
    product_id = entity_id(session, Product, "Teclado")

    no_key = client.post(
        "/api/v1/sales",
        headers=admin,
        json={
            "customer_id": active_customer_id,
            "payment_method": "cash",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    manager_forbidden = client.post(
        "/api/v1/sales",
        headers={**manager, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": active_customer_id,
            "payment_method": "cash",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    inactive_customer = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": inactive_customer_id,
            "payment_method": "cash",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    inactive_product = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": active_customer_id,
            "payment_method": "cash",
            "items": [{"product_id": inactive_product_id, "quantity": 1}],
        },
    )
    empty_sale = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": active_customer_id,
            "payment_method": "cash",
            "items": [],
        },
    )
    invalid_payment = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json={
            "customer_id": active_customer_id,
            "payment_method": "crypto",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )

    assert no_key.status_code == 422
    assert manager_forbidden.status_code == 403
    assert inactive_customer.status_code == 409
    assert inactive_customer.json()["error"]["code"] == "CUSTOMER_INACTIVE"
    assert inactive_product.status_code == 409
    assert inactive_product.json()["error"]["code"] == "PRODUCT_INACTIVE"
    assert empty_sale.status_code == 422
    assert empty_sale.json()["error"]["code"] == "EMPTY_SALE"
    assert invalid_payment.status_code == 422
    assert invalid_payment.json()["error"]["code"] == "INVALID_PAYMENT_METHOD"


def test_seller_only_sees_own_sales(client: TestClient, session: Session) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    seller = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    manager = login(client, MANAGER_EMAIL, MANAGER_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    product_id = entity_id(session, Product, "Teclado")
    payload = {
        "customer_id": customer_id,
        "payment_method": "cash",
        "items": [{"product_id": product_id, "quantity": 1}],
    }
    admin_sale = client.post(
        "/api/v1/sales",
        headers={**admin, "Idempotency-Key": str(uuid4())},
        json=payload,
    ).json()
    seller_sale = client.post(
        "/api/v1/sales",
        headers={**seller, "Idempotency-Key": str(uuid4())},
        json=payload,
    ).json()

    seller_list = client.get("/api/v1/sales", headers=seller)
    manager_list = client.get("/api/v1/sales", headers=manager)
    denied = client.get(f"/api/v1/sales/{admin_sale['id']}", headers=seller)
    own = client.get(f"/api/v1/sales/{seller_sale['id']}", headers=seller)

    assert seller_list.status_code == 200
    assert seller_list.json()["total"] == 1
    assert seller_list.json()["items"][0]["id"] == seller_sale["id"]
    assert manager_list.json()["total"] == 2
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "SALE_ACCESS_DENIED"
    assert own.status_code == 200


def test_openapi_publishes_phase_eight_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/inventory" in paths
    assert "/api/v1/inventory/movements" in paths
    assert "/api/v1/sales" in paths
    assert "/api/v1/sales/{sale_id}" in paths
    assert "/api/v1/orders" in paths
    assert "/api/v1/orders/{order_id}" in paths
    assert "/api/v1/orders/{order_id}/status" in paths
    assert "/api/v1/orders/{order_id}/convert" in paths


def test_order_lifecycle_converts_atomically_to_sale(
    client: TestClient, session: Session
) -> None:
    seller = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    product_id = entity_id(session, Product, "Teclado")
    payload = {
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "quantity": 2}],
    }

    created = client.post("/api/v1/orders", headers=seller, json=payload)
    assert created.status_code == 201, created.text
    order = created.json()
    assert order["number"] == f"P-{order['id']:06d}"
    assert order["status"] == "pending"
    assert order["total"] == "300.00"
    stock = session.scalar(select(Inventory.quantity).where(Inventory.product_id == product_id))
    assert stock == 10

    approved = client.post(
        f"/api/v1/orders/{order['id']}/status",
        headers=seller,
        json={"status": "approved"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    converted = client.post(
        f"/api/v1/orders/{order['id']}/convert",
        headers={**seller, "Idempotency-Key": str(uuid4())},
        json={"payment_method": "card"},
    )
    assert converted.status_code == 201, converted.text
    assert converted.json()["order"]["status"] == "converted"
    assert converted.json()["sale"]["total"] == "300.00"
    stock = session.scalar(select(Inventory.quantity).where(Inventory.product_id == product_id))
    assert stock == 8

    repeated = client.post(
        f"/api/v1/orders/{order['id']}/convert",
        headers={**seller, "Idempotency-Key": str(uuid4())},
        json={"payment_method": "card"},
    )
    assert repeated.status_code == 409


def test_order_permissions_edit_and_cancel(client: TestClient, session: Session) -> None:
    admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    seller = login(client, SELLER_EMAIL, SELLER_PASSWORD)
    manager = login(client, MANAGER_EMAIL, MANAGER_PASSWORD)
    customer_id = entity_id(session, Customer, "Ana Torres")
    product_id = entity_id(session, Product, "Mouse")
    payload = {
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "quantity": 1}],
    }
    assert client.post("/api/v1/orders", headers=manager, json=payload).status_code == 403
    order = client.post("/api/v1/orders", headers=seller, json=payload).json()
    assert client.get("/api/v1/orders", headers=admin).json()["total"] == 1

    updated = client.patch(
        f"/api/v1/orders/{order['id']}",
        headers=seller,
        json={**payload, "items": [{"product_id": product_id, "quantity": 2}]},
    )
    assert updated.status_code == 200
    assert updated.json()["total"] == "100.00"
    cancelled = client.post(
        f"/api/v1/orders/{order['id']}/status",
        headers=seller,
        json={"status": "cancelled"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert client.patch(
        f"/api/v1/orders/{order['id']}", headers=seller, json=payload
    ).status_code == 409
