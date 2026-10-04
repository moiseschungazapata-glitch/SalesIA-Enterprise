"""Integration tests for phase 11 explainable business insights."""

from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import Principal, require_roles
from app.core.exceptions import AppError
from app.core.security import ADMIN_ROLE, MANAGER_ROLE
from app.db.base import Base
from app.main import app
from app.models import (
    Category,
    Company,
    Customer,
    Dataset,
    DatasetVariable,
    Insight,
    Observation,
    Product,
    Role,
    Sale,
    SaleDetail,
    StatisticalAnalysis,
    StatisticalResult,
    User,
)
from app.schemas.insights import InsightGenerationRequest, InsightGenerationResponse
from app.services.insights import InsightService


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
            Dataset.__table__,
            DatasetVariable.__table__,
            Observation.__table__,
            StatisticalAnalysis.__table__,
            StatisticalResult.__table__,
            Insight.__table__,
        ],
    )
    with Session(engine, expire_on_commit=False) as database_session:
        company = Company(
            name="SalesIA Insights Test",
            slug="salesia-insights-test",
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
            name="Administradora Insights",
            email="insights.admin@salesia.example.com",
            password_hash="not-used-by-service-tests",
            active=True,
        )
        customer = Customer(
            company_id=company.id,
            customer_type="person",
            document_type="DNI",
            document_number="12345678",
            name="Cliente Insights",
            active=True,
        )
        category = Category(company_id=company.id, name="Tecnologia", active=True)
        database_session.add_all([admin, customer, category])
        database_session.flush()
        product = Product(
            company_id=company.id,
            category_id=category.id,
            sku="INS-001",
            name="Producto Insights",
            unit_price=Decimal("100.00"),
            active=True,
        )
        database_session.add(product)
        database_session.flush()
        for index, amount in enumerate((Decimal("100.00"), Decimal("300.00")), start=1):
            sale = Sale(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=admin.id,
                number=f"I-{index:06d}",
                idempotency_key=uuid4(),
                request_hash=str(index) * 64,
                status="confirmed",
                currency="PEN",
                total=amount,
                created_at=datetime(2026, 10, index, 15, tzinfo=UTC),
            )
            database_session.add(sale)
            database_session.flush()
            database_session.add(
                SaleDetail(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=int(amount / Decimal("100.00")),
                    unit_price=Decimal("100.00"),
                    subtotal=amount,
                    sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    category_name_snapshot=category.name,
                )
            )
        database_session.commit()
        yield database_session
    engine.dispose()


def service(session: Session) -> InsightService:
    company = session.scalars(select(Company)).one()
    admin = session.scalars(select(User)).one()
    return InsightService(session, company.id, admin.id)


def request(date_from: date, date_to: date) -> InsightGenerationRequest:
    return InsightGenerationRequest(
        date_from=date_from,
        date_to=date_to,
        branch="main",
    )


def test_generation_persists_explainable_evidence(session: Session) -> None:
    result = service(session).generate(request(date(2026, 10, 1), date(2026, 10, 2)))
    session.commit()
    response = InsightGenerationResponse.model_validate(result)

    assert response.generated_count >= 5
    assert response.items[0].dataset_id == response.dataset_id
    assert response.items[0].analysis_id == response.analysis_id
    assert all("value" in item.evidence for item in response.items)
    assert all("rule_code" in item.evidence for item in response.items)
    assert session.query(Observation).count() == 2
    analysis = session.get(StatisticalAnalysis, response.analysis_id)
    assert analysis is not None
    assert analysis.analysis_type == "insight"
    assert analysis.status == "completed"


def test_new_generation_preserves_history_and_deactivates_previous(session: Session) -> None:
    insights = service(session)
    first = insights.generate(request(date(2026, 10, 1), date(2026, 10, 2)))
    session.commit()
    second = insights.generate(request(date(2026, 10, 1), date(2026, 10, 2)))
    session.commit()

    current, current_total = insights.history(
        page=1, page_size=100, category=None, severity=None, active=True
    )
    archived, archived_total = insights.history(
        page=1, page_size=100, category=None, severity=None, active=False
    )
    assert current_total == second["generated_count"]
    assert archived_total == first["generated_count"]
    assert all(item["active"] for item in current)
    assert all(not item["active"] for item in archived)


def test_empty_period_creates_numeric_warning(session: Session) -> None:
    result = service(session).generate(request(date(2026, 9, 1), date(2026, 9, 2)))
    session.commit()

    assert result["generated_count"] == 1
    insight = result["items"][0]
    assert insight["rule_code"] == "sales.no_activity"
    assert insight["severity"] == "warning"
    assert insight["evidence"]["value"] == 0


def test_insight_route_permissions_and_openapi_contract() -> None:
    seller = Principal(
        id=2,
        company_id=1,
        name="Vendedor",
        email="insights.seller@salesia.example.com",
        role="seller",
        active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    authorize = require_roles(ADMIN_ROLE, MANAGER_ROLE)

    with pytest.raises(AppError) as error:
        authorize(seller)
    assert error.value.code == "FORBIDDEN"
    paths = app.openapi()["paths"]
    assert "/api/v1/insights" in paths
    assert "/api/v1/insights/generate" in paths
