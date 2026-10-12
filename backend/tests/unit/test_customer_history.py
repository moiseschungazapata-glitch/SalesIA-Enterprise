"""Customer commercial history aggregation tests."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import (
    Category,
    Company,
    Customer,
    Order,
    Payment,
    Product,
    Role,
    Sale,
    SaleDetail,
    User,
)
from app.services.catalog import CustomerService


def test_customer_history_consolidates_commercial_activity() -> None:
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
            Payment.__table__,
            Order.__table__,
        ],
    )
    with Session(engine, expire_on_commit=False) as session:
        company = Company(name="History Test", slug="history-test")
        role = Role(code="seller", name="Vendedor")
        session.add_all([company, role])
        session.flush()
        seller = User(
            company_id=company.id,
            role_id=role.id,
            name="Seller Test",
            email="seller-history@example.com",
            password_hash="not-used",
            active=True,
        )
        customer = Customer(
            company_id=company.id,
            customer_type="person",
            document_type="DNI",
            document_number="12345678",
            name="Cliente History",
            active=False,
        )
        category = Category(company_id=company.id, name="General", active=True)
        session.add_all([seller, customer, category])
        session.flush()
        product = Product(
            company_id=company.id,
            category_id=category.id,
            sku="HIS-001",
            name="Producto History",
            unit_price=Decimal("50.00"),
            active=True,
        )
        session.add(product)
        session.flush()
        sale = Sale(
            company_id=company.id,
            customer_id=customer.id,
            seller_id=seller.id,
            number="V-000001",
            idempotency_key=uuid4(),
            request_hash="a" * 64,
            total=Decimal("100.00"),
            subtotal=Decimal("100.00"),
            payment_status="partial",
            paid_amount=Decimal("60.00"),
        )
        order = Order(
            company_id=company.id,
            customer_id=customer.id,
            seller_id=seller.id,
            number="P-000001",
            status="pending",
            total=Decimal("50.00"),
            subtotal=Decimal("50.00"),
        )
        session.add_all([sale, order])
        session.flush()
        session.add_all(
            [
                SaleDetail(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=2,
                    unit_price=Decimal("50.00"),
                    gross_subtotal=Decimal("100.00"),
                    subtotal=Decimal("100.00"),
                    sku_snapshot=product.sku,
                    product_name_snapshot=product.name,
                    category_name_snapshot=category.name,
                ),
                Payment(
                    sale_id=sale.id,
                    method="card",
                    amount=Decimal("60.00"),
                    status="completed",
                    reference="TEST-001",
                    registered_by_id=seller.id,
                ),
            ]
        )
        session.commit()

        history = CustomerService(session, company.id).history(
            customer.id, user_id=seller.id, role="seller"
        )

        assert history["customer"].active is False
        assert history["summary"]["sales_count"] == 1
        assert history["summary"]["orders_count"] == 1
        assert history["summary"]["units_purchased"] == 2
        assert history["summary"]["total_purchased"] == Decimal("100.00")
        assert history["summary"]["total_paid"] == Decimal("60.00")
        assert history["summary"]["balance_due"] == Decimal("40.00")
        assert history["sales"][0]["seller_name"] == "Seller Test"
        assert history["payments"][0]["reference"] == "TEST-001"
        assert history["products"][0]["units"] == 2

    engine.dispose()
