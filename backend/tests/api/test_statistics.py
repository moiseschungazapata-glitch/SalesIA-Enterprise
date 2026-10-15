"""Service, schema and OpenAPI tests for the phase 09 statistical motor."""

from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError
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
    Order,
    Payment,
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
    AutomaticBayesRequest,
    AutomaticEventProbabilityRequest,
    BayesRequest,
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
            Order.__table__,
            Payment.__table__,
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


def test_manual_series_random_variable_bayes_and_history(session: Session) -> None:
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
    assert metric(random, "mean") == Decimal("2.000000")
    assert metric(bayes, "posterior") == Decimal("0.6000000")

    history, total = analytics.history(1, 20)
    assert total == 3
    assert {AnalysisHistoryItemResponse.model_validate(item).analysis_type for item in history} == {
        "comparison",
        "random_variable",
        "bayes",
    }


def test_automatic_probability_uses_salesia_orders_sales_and_payments(session: Session) -> None:
    company = session.scalars(select(Company)).one()
    customer = session.scalars(select(Customer)).one()
    seller = session.scalar(select(User).where(User.email != ADMIN_EMAIL))
    sales = session.scalars(select(Sale).order_by(Sale.id)).all()
    assert seller is not None
    assert len(sales) == 2

    session.add_all(
        [
            Order(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=seller.id,
                sale_id=sales[0].id,
                number="P-000001",
                status="converted",
                total=Decimal("100.00"),
            ),
            Order(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=seller.id,
                number="P-000002",
                status="cancelled",
                total=Decimal("100.00"),
            ),
            Order(
                company_id=company.id,
                customer_id=customer.id,
                seller_id=seller.id,
                number="P-000003",
                status="pending",
                total=Decimal("100.00"),
            ),
            Payment(
                sale_id=sales[0].id,
                method="card",
                amount=Decimal("100.00"),
                status="completed",
                registered_by_id=seller.id,
            ),
            Payment(
                sale_id=sales[1].id,
                method="cash",
                amount=Decimal("300.00"),
                status="completed",
                registered_by_id=seller.id,
            ),
        ]
    )
    session.commit()

    analytics = service(session)
    conversion = analytics.analyze_automatic_event_probability(
        AutomaticEventProbabilityRequest(event_type="order_conversion")
    )
    paid = analytics.analyze_automatic_event_probability(
        AutomaticEventProbabilityRequest(event_type="fully_paid_sale")
    )
    card = analytics.analyze_automatic_event_probability(
        AutomaticEventProbabilityRequest(event_type="card_payment")
    )
    session.commit()

    assert metric(conversion, "favorable_cases") == Decimal("1")
    assert metric(conversion, "total_observations") == Decimal("3")
    assert metric(conversion, "probability") == Decimal("0.3333333")
    assert metric(paid, "probability") == Decimal("1.0000000")
    assert metric(card, "probability") == Decimal("0.5000000")
    assert session.scalar(select(func.count(Observation.id))) == 7


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


def test_automatic_bayes_uses_unique_customers_real_sales_and_company_scope(
    session: Session,
) -> None:
    company = session.scalars(select(Company)).one()
    seller = session.scalar(select(User).where(User.email != ADMIN_EMAIL))
    existing_customer = session.scalars(select(Customer)).one()
    existing_sales = session.scalars(select(Sale).order_by(Sale.id)).all()
    assert seller is not None

    existing_customer.created_at = datetime(2026, 9, 1, 12, tzinfo=UTC)
    for sale in existing_sales:
        sale.payment_status = "refunded"

    recurring = Customer(
        company_id=company.id,
        customer_type="person",
        document_type="DNI",
        document_number="11111111",
        name="Cliente recurrente",
        active=True,
        created_at=datetime(2026, 9, 1, 12, tzinfo=UTC),
    )
    prior_only = Customer(
        company_id=company.id,
        customer_type="person",
        document_type="DNI",
        document_number="22222222",
        name="Cliente anterior",
        active=True,
        created_at=datetime(2026, 9, 1, 12, tzinfo=UTC),
    )
    new_buyer = Customer(
        company_id=company.id,
        customer_type="person",
        document_type="DNI",
        document_number="33333333",
        name="Cliente nuevo",
        active=True,
        created_at=datetime(2026, 10, 2, 12, tzinfo=UTC),
    )
    after_period = Customer(
        company_id=company.id,
        customer_type="person",
        document_type="DNI",
        document_number="44444444",
        name="Cliente posterior",
        active=True,
        created_at=datetime(2026, 11, 2, 12, tzinfo=UTC),
    )
    other_company = Company(name="Otra empresa", slug="otra-empresa")
    session.add_all([recurring, prior_only, new_buyer, after_period, other_company])
    session.flush()
    other_customer = Customer(
        company_id=other_company.id,
        customer_type="person",
        document_type="DNI",
        document_number="55555555",
        name="Cliente externo",
        active=True,
        created_at=datetime(2026, 9, 1, 12, tzinfo=UTC),
    )
    session.add(other_customer)
    session.flush()

    def add_sale(
        *, customer: Customer, company_id: int, number: str, created_at: datetime
    ) -> None:
        session.add(
            Sale(
                company_id=company_id,
                customer_id=customer.id,
                seller_id=seller.id,
                number=number,
                idempotency_key=uuid4(),
                request_hash=number.zfill(64)[-64:],
                status="confirmed",
                currency="PEN",
                total=Decimal("100.00"),
                payment_status="paid",
                paid_amount=Decimal("100.00"),
                created_at=created_at,
            )
        )

    add_sale(
        customer=recurring,
        company_id=company.id,
        number="BAYES-001",
        created_at=datetime(2026, 9, 15, 12, tzinfo=UTC),
    )
    add_sale(
        customer=recurring,
        company_id=company.id,
        number="BAYES-002",
        created_at=datetime(2026, 10, 5, 12, tzinfo=UTC),
    )
    add_sale(
        customer=recurring,
        company_id=company.id,
        number="BAYES-003",
        created_at=datetime(2026, 10, 6, 12, tzinfo=UTC),
    )
    add_sale(
        customer=prior_only,
        company_id=company.id,
        number="BAYES-004",
        created_at=datetime(2026, 9, 20, 12, tzinfo=UTC),
    )
    add_sale(
        customer=new_buyer,
        company_id=company.id,
        number="BAYES-005",
        created_at=datetime(2026, 10, 3, 12, tzinfo=UTC),
    )
    add_sale(
        customer=other_customer,
        company_id=other_company.id,
        number="BAYES-OTHER-001",
        created_at=datetime(2026, 9, 15, 12, tzinfo=UTC),
    )
    add_sale(
        customer=other_customer,
        company_id=other_company.id,
        number="BAYES-OTHER-002",
        created_at=datetime(2026, 10, 5, 12, tzinfo=UTC),
    )
    session.commit()

    result = service(session).analyze_automatic_bayes(
        AutomaticBayesRequest(
            scenario_type="repeat_customer_given_purchase",
            date_from=date(2026, 10, 1),
            date_to=date(2026, 10, 31),
        )
    )
    session.commit()

    assert result["analysis_type"] == "bayes"
    assert result["observation_count"] == 4
    assert metric(result, "universe_size") == Decimal("4")
    assert metric(result, "event_a_cases") == Decimal("2")
    assert metric(result, "event_b_cases") == Decimal("2")
    assert metric(result, "intersection_cases") == Decimal("1")
    assert metric(result, "probability_a") == Decimal("0.5000000")
    assert metric(result, "probability_b_given_a") == Decimal("0.5000000")
    assert metric(result, "probability_b") == Decimal("0.5000000")
    assert metric(result, "posterior") == Decimal("0.5000000")

    dataset = session.get(Dataset, result["dataset_id"])
    assert dataset is not None
    assert dataset.period_start == date(2026, 10, 1)
    assert dataset.period_end == date(2026, 10, 31)
    assert dataset.filters["timezone"] == "America/Lima"
    assert session.scalar(
        select(func.count(Observation.id)).where(Observation.dataset_id == dataset.id)
    ) == 4
    memberships = set(
        session.scalars(
            select(Observation.value_text).where(Observation.dataset_id == dataset.id)
        ).all()
    )
    assert memberships == {"A=0;B=0", "A=0;B=1", "A=1;B=0", "A=1;B=1"}

    persisted = session.scalar(
        select(BayesAnalysis).join(
            StatisticalAnalysis,
            StatisticalAnalysis.id == BayesAnalysis.analysis_id,
        )
    )
    assert persisted is not None
    assert persisted.posterior == Decimal("0.5000000")

    # Regression: independently rounded Bayes inputs for N=3, A=2, B=1,
    # A∩B=1 would produce a value slightly above 1. The count-based posterior
    # must remain the exact, valid probability 1.
    existing_customer.created_at = datetime(2026, 11, 2, 12, tzinfo=UTC)
    new_buyer_sale = session.scalar(select(Sale).where(Sale.number == "BAYES-005"))
    assert new_buyer_sale is not None
    new_buyer_sale.payment_status = "refunded"
    session.commit()

    rounded_edge = service(session).analyze_automatic_bayes(
        AutomaticBayesRequest(
            date_from=date(2026, 10, 1),
            date_to=date(2026, 10, 31),
        )
    )

    assert metric(rounded_edge, "universe_size") == Decimal("3")
    assert metric(rounded_edge, "event_a_cases") == Decimal("2")
    assert metric(rounded_edge, "event_b_cases") == Decimal("1")
    assert metric(rounded_edge, "intersection_cases") == Decimal("1")
    assert metric(rounded_edge, "posterior") == Decimal("1.0000000")


def test_automatic_bayes_reports_undefined_population_conditions(session: Session) -> None:
    with pytest.raises(ValidationError):
        AutomaticBayesRequest(date_to=date.max)

    customer = session.scalars(select(Customer)).one()
    sales = session.scalars(select(Sale)).all()
    customer.created_at = datetime(2026, 7, 1, 12, tzinfo=UTC)
    for sale in sales:
        sale.created_at = datetime(2026, 10, 15, 12, tzinfo=UTC)
        sale.payment_status = "paid"
    session.commit()

    with pytest.raises(AppError) as no_prior:
        service(session).analyze_automatic_bayes(
            AutomaticBayesRequest(
                date_from=date(2026, 8, 1),
                date_to=date(2026, 8, 31),
            )
        )
    assert no_prior.value.code == "BAYES_NO_PRIOR_CUSTOMERS"
    assert no_prior.value.status_code == 409

    with pytest.raises(AppError) as no_period:
        service(session).analyze_automatic_bayes(
            AutomaticBayesRequest(
                date_from=date(2026, 11, 1),
                date_to=date(2026, 11, 30),
            )
        )
    assert no_period.value.code == "BAYES_NO_PERIOD_PURCHASES"
    assert no_period.value.status_code == 409

    empty_company = Company(name="Empresa sin clientes", slug="empresa-sin-clientes")
    session.add(empty_company)
    session.flush()
    with pytest.raises(AppError) as no_customers:
        AnalyticsService(
            session, empty_company.id, service(session).user_id
        ).analyze_automatic_bayes(
            AutomaticBayesRequest(
                date_from=date(2026, 10, 1),
                date_to=date(2026, 10, 31),
            )
        )
    assert no_customers.value.code == "BAYES_NO_CUSTOMERS"
    assert no_customers.value.status_code == 409

    assert session.scalar(select(func.count(StatisticalAnalysis.id))) == 0


def test_automatic_bayes_defaults_to_current_company_month() -> None:
    timezone = ZoneInfo("America/Lima")
    today = datetime.now(timezone).date()

    start_date, end_date = AnalyticsService._automatic_bayes_period(
        None,
        None,
        timezone,
    )

    assert start_date == today.replace(day=1)
    assert end_date == today


def test_openapi_publishes_phase_nine_routes() -> None:
    paths = app.openapi()["paths"]

    assert "/api/v1/statistics/mean" in paths
    assert "/api/v1/statistics/median" in paths
    assert "/api/v1/statistics/compare" in paths
    assert "/api/v1/statistics/sales/compare" in paths
    assert "/api/v1/probability/events" in paths
    assert "/api/v1/probability/bayes" in paths
    assert "/api/v1/probability/bayes/automatic" in paths
    assert "/api/v1/random-variables/analyze" in paths
