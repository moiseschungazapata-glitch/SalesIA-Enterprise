"""Anonymous visit persistence before authentication."""

import pytest
from fastapi import Request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.company import Company
from app.models.identity import AnonymousVisit
from app.services.security import AnonymousVisitService


def public_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/public/visits",
            "headers": [
                (b"user-agent", b"SalesIA public visit test"),
                (b"x-forwarded-for", b"190.1.2.3"),
            ],
            "client": ("127.0.0.1", 12345),
            "state": {"request_id": "public-visit-test"},
        }
    )


def test_anonymous_visit_is_recorded_and_deduplicated() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[Company.__table__, AnonymousVisit.__table__],
    )
    payload = {
        "latitude": -12.0464,
        "longitude": -77.0428,
        "city": "Lima",
        "region": "Lima",
        "country": "Peru",
        "country_code": "PE",
        "isp": "Test ISP",
        "timezone": "America/Lima",
        "source": "device_location",
        "accuracy_m": 24.5,
    }

    with Session(engine, expire_on_commit=False) as session:
        company = Company(name="Public Test", slug="public-test")
        session.add(company)
        session.flush()
        service = AnonymousVisitService(session, company.id)
        service.record(public_request(), payload)
        session.commit()
        service.record(public_request(), payload)
        session.commit()

        visits = list(session.scalars(select(AnonymousVisit)))
        assert len(visits) == 1
        assert visits[0].ip_address == "190.1.2.3"
        assert visits[0].visit_count == 2
        assert visits[0].location_source == "device_location"
        assert float(visits[0].location_accuracy_m or 0) == pytest.approx(24.5)
        assert float(visits[0].latitude or 0) == pytest.approx(-12.0464)

    engine.dispose()
