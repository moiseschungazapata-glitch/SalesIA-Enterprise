"""Service, schema and OpenAPI tests for the phase 09 statistical motor."""

from collections.abc import Generator
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models import (
    BayesAnalysis,
    Category,
    Company,
    Customer,
    Dataset,
    DatasetVariable,
    Observation,
    Product,
    RandomVariable,
    Role,
    Sale,
    SaleDetail,
    StatisticalAnalysis,
    StatisticalResult,
    User,
)
from app.schemas.statistics import (
    AnalysisExecutionResponse,
    AnalysisHistoryItemResponse,
    BayesRequest,
    EventProbabilityRequest,
    NumericSeriesRequest,
    RandomVariableRequest,
    SalesComparisonRequest,
)
from app.services.analytics import AnalyticsService

ADMIN_EMAIL = "analytics.admin@salesia.example.com"


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
            BayesAnalysis.__table__,
            RandomVariable.__table__,
        ],
    )
    with Session(test_engine, expire_on_commit=False) as database_session:
        company = Company(name="SalesIA Analytics Test", slug="salesia-analytics-test")
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
            name="Analytics Admin",
            email=ADMIN_EMAIL,
            password_hash=hash_password("analytics-admin-2026"),
            active=True,
        )
        seller = User(
            company_id=company.id,
            role_id=roles["seller"].id,
            name="Analytics Seller",
            email="analytics.seller@salesia.example.com",
            password_hash=hash_password("analytics-seller-2026"),
            active=True,
        )
        database_session.add_all([admin, seller])
        customer = Customer(
            company_id=company.id,
            customer_type="person",
            document_type="DNI",
            document_number="12345678",
            name="Cliente Analytics",
            active=True,
        )
        category = Category(company_id=company.id, name="Analytics", active=True)
        database_session.add_all([customer, category])
        database_session.flush()
        product = Product(
            company_id=company.id,
            category_id=category.id,
            sku="ANA-001",
            name="Producto Analytics",
            unit_price=Decimal("100.00"),
            active=True,
        )
        database_session.add(product)
        database_session.flush()
        for index, (total, quantity) in enumerate(
            [(Decimal("100.00"), 1), (Decimal("300.00"), 3)], start=1
        ):
            sale = Sale(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=seller.id,
                number=f"V-{index:06d}",
                idempotency_key=uuid4(),
                request_hash=str(index) * 64,
                status="confirmed",
                currency="PEN",
                total=total,
            )
            database_session.add(sale)
            database_session.flush()
            database_session.add(
                SaleDetail(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=Decimal("100.00"),
                    subtotal=total,
                    sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    category_name_snapshot=category.name,
                )
            )
        database_session.commit()
        yield database_session
    test_engine.dispose()


def service(session: Session) -> AnalyticsService:
    admin = session.scalar(select(User).where(User.email == ADMIN_EMAIL))
    assert admin is not None
    return AnalyticsService(session, admin.company_id, admin.id)


def metric(response: dict[str, object], name: str) -> Decimal | None:
    results = response["results"]
    assert isinstance(results, list)
    result = next(item for item in results if item["metric"] == name)
    return result["numeric_value"]


def test_sales_comparison_uses_real_sales_and_persists_results(session: Session) -> None:
    result = service(session).analyze_sales(SalesComparisonRequest(metric="sale_total"))
    session.commit()
    response = AnalysisExecutionResponse.model_validate(result)

    assert response.variable_type == "quantitative_continuous"
    assert response.observation_count == 2
    assert metric(result, "mean") == Decimal("200.000000")
    assert metric(result, "median") == Decimal("200.000000")
    assert metric(result, "difference") == Decimal("0.000000")
    assert session.scalar(select(func.count(Dataset.id))) == 1
    assert session.scalar(select(func.count(Observation.id))) == 2
    assert session.scalar(select(func.count(StatisticalAnalysis.id))) == 1
    assert session.scalar(select(func.count(StatisticalResult.id))) == 5


def test_manual_probability_random_variable_bayes_and_history(session: Session) -> None:
    analytics = service(session)
    manual = analytics.analyze_series(
        NumericSeriesRequest(
            name="Muestra de control",
            variable_name="ticket",
            variable_label="Ticket",
            unit="PEN",
            values=[Decimal("1"), Decimal("2"), Decimal("100")],
        ),
        "comparison",
    )
    event = analytics.analyze_event_probability(
        EventProbabilityRequest(
            event_name="Compra completada", favorable_cases=7, total_observations=10
        )
    )
    random = analytics.analyze_random_variable(
        RandomVariableRequest(
            name="Unidades por pedido",
            variable_name="units",
            variable_label="Unidades",
            variable_type="quantitative_discrete",
            random_variable_type="discrete",
            values=[Decimal("1"), Decimal("1"), Decimal("2"), Decimal("4")],
        )
    )
    bayes = analytics.analyze_bayes(
        BayesRequest(
            event_a="Cliente recurrente",
            event_b="Compra este mes",
            probability_a=Decimal("0.4"),
            probability_b_given_a=Decimal("0.75"),
            probability_b=Decimal("0.5"),
        )
    )
    session.commit()

    assert metric(manual, "mean") == Decimal("34.333333")
    assert metric(manual, "median") == Decimal("2.000000")
    assert metric(event, "probability") == Decimal("0.7000000")
    assert metric(random, "mean") == Decimal("2.000000")
    assert metric(bayes, "posterior") == Decimal("0.6000000")

    history, total = analytics.history(1, 20)
    assert total == 4
    assert {AnalysisHistoryItemResponse.model_validate(item).analysis_type for item in history} == {
        "comparison",
        "frequency",
        "random_variable",
        "bayes",
    }


def test_invalid_bayes_is_rejected_without_persistence(session: Session) -> None:
    with pytest.raises(AppError) as error:
        service(session).analyze_bayes(
            BayesRequest(
                event_a="Evento A",
                event_b="Evento B",
                probability_a=Decimal("0.9"),
                probability_b_given_a=Decimal("0.9"),
                probability_b=Decimal("0.2"),
            )
        )

    assert error.value.code == "INVALID_BAYES_PROBABILITIES"
    assert session.scalar(select(func.count(StatisticalAnalysis.id))) == 0


def test_openapi_publishes_phase_nine_routes() -> None:
    paths = app.openapi()["paths"]

    assert "/api/v1/statistics/mean" in paths
    assert "/api/v1/statistics/median" in paths
    assert "/api/v1/statistics/compare" in paths
    assert "/api/v1/statistics/sales/compare" in paths
    assert "/api/v1/probability/events" in paths
    assert "/api/v1/probability/bayes" in paths
    assert "/api/v1/random-variables/analyze" in paths
