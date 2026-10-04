"""Integration tests for phase 12 persistent reports."""

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
    Inventory,
    Observation,
    Product,
    Report,
    Role,
    Sale,
    SaleDetail,
    StatisticalAnalysis,
    StatisticalResult,
    User,
)
from app.schemas.reports import ReportDetailResponse, ReportGenerateRequest
from app.services.reports import ReportService


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
            Inventory.__table__,
            Sale.__table__,
            SaleDetail.__table__,
            Dataset.__table__,
            DatasetVariable.__table__,
            Observation.__table__,
            StatisticalAnalysis.__table__,
            StatisticalResult.__table__,
            Insight.__table__,
            Report.__table__,
        ],
    )
    with Session(engine, expire_on_commit=False) as database_session:
        company = Company(
            name="SalesIA Reports Test",
            slug="salesia-reports-test",
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
            name="Administradora Reports",
            email="reports.admin@salesia.example.com",
            password_hash="not-used-by-service-tests",
            active=True,
        )
        customer = Customer(
            company_id=company.id,
            customer_type="person",
            document_type="DNI",
            document_number="12345678",
            name="Cliente Reports",
            email="cliente@salesia.example.com",
            active=True,
        )
        category = Category(company_id=company.id, name="Tecnologia", active=True)
        database_session.add_all([admin, customer, category])
        database_session.flush()
        product = Product(
            company_id=company.id,
            category_id=category.id,
            sku="REP-001",
            name="Producto Reports",
            unit_price=Decimal("100.00"),
            active=True,
        )
        database_session.add(product)
        database_session.flush()
        database_session.add(
            Inventory(company_id=company.id, product_id=product.id, quantity=8, version=1)
        )
        sale = Sale(
            company_id=company.id,
            customer_id=customer.id,
            seller_id=admin.id,
            number="R-000001",
            idempotency_key=uuid4(),
            request_hash="1" * 64,
            status="confirmed",
            currency="PEN",
            total=Decimal("200.00"),
            created_at=datetime(2026, 10, 1, 15, tzinfo=UTC),
        )
        database_session.add(sale)
        database_session.flush()
        database_session.add(
            SaleDetail(
                sale_id=sale.id,
                product_id=product.id,
                quantity=2,
                unit_price=Decimal("100.00"),
                subtotal=Decimal("200.00"),
                sku_snapshot=product.sku,
                product_name_snapshot=product.name,
                category_name_snapshot=category.name,
            )
        )
        dataset = Dataset(
            company_id=company.id,
            created_by_user_id=admin.id,
            name="Dataset Reports",
            source_type="manual",
            filters={},
        )
        database_session.add(dataset)
        database_session.flush()
        analysis = StatisticalAnalysis(
            company_id=company.id,
            dataset_id=dataset.id,
            requested_by_user_id=admin.id,
            analysis_type="mean",
            status="completed",
            parameters={},
            created_at=datetime(2026, 10, 1, 16, tzinfo=UTC),
            completed_at=datetime(2026, 10, 1, 16, tzinfo=UTC),
        )
        database_session.add(analysis)
        database_session.flush()
        database_session.add(
            StatisticalResult(
                analysis_id=analysis.id,
                variable_id=None,
                metric="mean",
                numeric_value=Decimal("200.00"),
                text_value=None,
                details={},
            )
        )
        database_session.commit()
        yield database_session
    engine.dispose()


def report_service(session: Session) -> ReportService:
    company = session.scalars(select(Company)).one()
    admin = session.scalars(select(User)).one()
    return ReportService(session, company.id, admin.id)


@pytest.mark.parametrize(
    ("report_type", "expected_rows"),
    [
        ("sales", 1),
        ("products", 1),
        ("customers", 1),
        ("sellers", 1),
        ("statistical", 1),
    ],
)
def test_generates_each_required_report(
    session: Session, report_type: str, expected_rows: int
) -> None:
    result = report_service(session).generate(
        ReportGenerateRequest(
            report_type=report_type,
            date_from=date(2026, 10, 1),
            date_to=date(2026, 10, 2),
        )
    )
    session.commit()
    response = ReportDetailResponse.model_validate(result)

    assert response.status == "completed"
    assert response.row_count == expected_rows
    assert response.content.columns
    assert response.content.summary


def test_report_history_detail_and_csv_export(session: Session) -> None:
    reports = report_service(session)
    generated = reports.generate(
        ReportGenerateRequest(
            report_type="sales",
            date_from=date(2026, 10, 1),
            date_to=date(2026, 10, 2),
        )
    )
    session.commit()

    history, total = reports.history(
        page=1, page_size=50, report_type="sales", status="completed"
    )
    detail = reports.get(generated["id"])
    csv_content, filename = reports.csv_export(generated["id"])

    assert total == 1
    assert history[0]["row_count"] == 1
    assert detail["content"]["rows"][0]["number"] == "R-000001"
    assert csv_content.startswith("\ufeffVenta,Fecha,Cliente")
    assert "R-000001" in csv_content
    assert filename == f"salesia-sales-{generated['id']}.csv"


def test_report_route_permissions_and_openapi_contract() -> None:
    seller = Principal(
        id=2,
        company_id=1,
        name="Vendedor",
        email="reports.seller@salesia.example.com",
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
    assert "/api/v1/reports" in paths
    assert "/api/v1/reports/generate" in paths
    assert "/api/v1/reports/{report_id}" in paths
    assert "/api/v1/reports/{report_id}/export" in paths
