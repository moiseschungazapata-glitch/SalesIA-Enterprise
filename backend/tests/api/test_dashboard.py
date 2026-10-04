"""Integration tests for the phase 10 real analytics dashboard."""

from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import Principal, require_roles
from app.core.exceptions import AppError
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.base import Base
from app.main import app
from app.models import Category, Company, Customer, Product, Role, Sale, SaleDetail, User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard import DashboardService

ADMIN_EMAIL = "dashboard.admin@salesia.example.com"
SELLER_EMAIL = "dashboard.seller@salesia.example.com"


@pytest.fixture
def session() -> Generator[Session, None, None]:
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
            Customer.__table__,
            Category.__table__,
            Product.__table__,
            Sale.__table__,
            SaleDetail.__table__,
        ],
    )
    with Session(engine, expire_on_commit=False) as database_session:
        company = Company(
            name="SalesIA Dashboard Test",
            slug="salesia-dashboard-test",
            timezone="America/Lima",
        )
        roles = {
            code: Role(code=code, name=name)
            for code, name in [
                ("administrator", "Administrador"),
                ("seller", "Vendedor"),
                ("manager", "Gerente"),
            ]
        }
        database_session.add_all([company, *roles.values()])
        database_session.flush()
        admin = User(
            company_id=company.id,
            role_id=roles["administrator"].id,
            name="Administradora Dashboard",
            email=ADMIN_EMAIL,
            password_hash="not-used-by-dashboard-service-tests",
            active=True,
        )
        seller_one = User(
            company_id=company.id,
            role_id=roles["seller"].id,
            name="Vendedor Uno",
            email=SELLER_EMAIL,
            password_hash="not-used-by-dashboard-service-tests",
            active=True,
        )
        seller_two = User(
            company_id=company.id,
            role_id=roles["seller"].id,
            name="Vendedor Dos",
            email="dashboard.seller2@salesia.example.com",
            password_hash="not-used-by-dashboard-service-tests",
            active=True,
        )
        database_session.add_all([admin, seller_one, seller_two])
        categories = [
            Category(company_id=company.id, name="Tecnologia", active=True),
            Category(company_id=company.id, name="Accesorios", active=True),
        ]
        customers = [
            Customer(
                company_id=company.id,
                customer_type="person",
                document_type="DNI",
                document_number="12345678",
                name="Cliente Uno",
                active=True,
            ),
            Customer(
                company_id=company.id,
                customer_type="company",
                document_type="RUC",
                document_number="20123456789",
                name="Cliente Dos",
                active=True,
            ),
        ]
        database_session.add_all([*categories, *customers])
        database_session.flush()
        products = [
            Product(
                company_id=company.id,
                category_id=categories[0].id,
                sku="TEC-001",
                name="Producto A",
                unit_price=Decimal("100.00"),
                active=True,
            ),
            Product(
                company_id=company.id,
                category_id=categories[1].id,
                sku="ACC-001",
                name="Producto B",
                unit_price=Decimal("100.00"),
                active=True,
            ),
            Product(
                company_id=company.id,
                category_id=categories[0].id,
                sku="TEC-002",
                name="Producto C",
                unit_price=Decimal("300.00"),
                active=True,
            ),
        ]
        database_session.add_all(products)
        database_session.flush()
        sale_specs = [
            (
                seller_one,
                customers[0],
                datetime(2026, 10, 1, 15, tzinfo=UTC),
                [(products[0], 1), (products[1], 2)],
            ),
            (
                seller_one,
                customers[1],
                datetime(2026, 10, 2, 15, tzinfo=UTC),
                [(products[0], 3)],
            ),
            (
                seller_two,
                customers[0],
                datetime(2026, 10, 3, 15, tzinfo=UTC),
                [(products[2], 3)],
            ),
        ]
        for index, (seller, customer, created_at, lines) in enumerate(sale_specs, start=1):
            total = sum(
                (product.unit_price * quantity for product, quantity in lines),
                start=Decimal("0"),
            )
            sale = Sale(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=seller.id,
                number=f"D-{index:06d}",
                idempotency_key=uuid4(),
                request_hash=str(index) * 64,
                status="confirmed",
                currency="PEN",
                total=total,
                created_at=created_at,
            )
            database_session.add(sale)
            database_session.flush()
            for product, quantity in lines:
                category = next(item for item in categories if item.id == product.category_id)
                database_session.add(
                    SaleDetail(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=product.unit_price,
                        subtotal=product.unit_price * quantity,
                        sku_snapshot=product.sku,
                        product_name_snapshot=product.name,
                        category_name_snapshot=category.name,
                    )
                )
        database_session.commit()
        yield database_session
    engine.dispose()


def test_dashboard_aggregates_real_sales(session: Session) -> None:
    company = session.query(Company).one()
    result = DashboardService(session, company.id).summary(
        date_from=date(2026, 10, 1),
        date_to=date(2026, 10, 3),
        branch="main",
        seller_id=None,
        category_id=None,
    )
    response = DashboardSummaryResponse.model_validate(result)

    assert response.kpis.sales_total == Decimal("1500.00")
    assert response.kpis.transactions == 3
    assert response.kpis.active_customers == 2
    assert response.kpis.units_sold == 9
    assert response.kpis.ticket_average == Decimal("500.00")
    assert response.kpis.sales_mean == Decimal("500.00")
    assert response.kpis.sales_median == Decimal("300.00")
    assert [point.revenue for point in response.sales_by_period] == [
        Decimal("300.00"), Decimal("300.00"), Decimal("900.00")
    ]
    assert response.sales_by_product[0].label == "Producto C"
    assert response.sales_by_seller[0].label == "Vendedor Dos"
    assert sum(point.frequency for point in response.ticket_distribution) == 3


def test_dashboard_filters_category_and_seller(session: Session) -> None:
    company = session.query(Company).one()
    category = session.query(Category).filter_by(name="Tecnologia").one()
    seller = session.query(User).filter_by(name="Vendedor Uno").one()
    service = DashboardService(session, company.id)

    category_result = service.summary(
        date_from=date(2026, 10, 1),
        date_to=date(2026, 10, 3),
        branch="main",
        seller_id=None,
        category_id=category.id,
    )
    seller_result = service.summary(
        date_from=date(2026, 10, 1),
        date_to=date(2026, 10, 3),
        branch="main",
        seller_id=seller.id,
        category_id=None,
    )

    assert category_result["kpis"]["sales_total"] == Decimal("1300.00")
    assert category_result["kpis"]["units_sold"] == 7
    assert {item["label"] for item in category_result["sales_by_product"]} == {
        "Producto A", "Producto C"
    }
    assert seller_result["kpis"]["sales_total"] == Decimal("600.00")
    assert seller_result["kpis"]["transactions"] == 2


def test_dashboard_route_permissions_and_openapi_contract() -> None:
    seller = Principal(
        id=2,
        company_id=1,
        name="Vendedor",
        email=SELLER_EMAIL,
        role="seller",
        active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    authorize = require_roles(ADMIN_ROLE, MANAGER_ROLE)

    with pytest.raises(AppError) as error:
        authorize(seller)
    assert error.value.code == "FORBIDDEN"
    assert "/api/v1/dashboard/summary" in app.openapi()["paths"]
