"""Real, company-scoped aggregations for the phase 10 dashboard."""

from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.catalog import Category, Product
from app.models.company import Company
from app.models.identity import Role, User
from app.models.sales import Sale, SaleDetail
from app.statistics.engine import arithmetic_mean, median

MONEY = Decimal("0.01")
PERCENTAGE = Decimal("0.01")
MAX_PERIOD_DAYS = 366


def _money(value: Decimal | int) -> Decimal:
    return Decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def _percentage(part: Decimal | int, total: Decimal | int) -> Decimal:
    total_value = Decimal(total)
    if total_value == 0:
        return Decimal("0.00")
    return (Decimal(part) * Decimal("100") / total_value).quantize(
        PERCENTAGE, rounding=ROUND_HALF_UP
    )


class DashboardService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def summary(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        branch: Literal["main"],
        seller_id: int | None,
        category_id: int | None,
    ) -> dict[str, Any]:
        timezone = self._company_timezone()
        start_date, end_date = self._period(date_from, date_to, timezone)
        self._validate_filter_ids(seller_id, category_id)
        start_at = datetime.combine(start_date, time.min, tzinfo=timezone).astimezone(UTC)
        end_at = datetime.combine(
            end_date + timedelta(days=1), time.min, tzinfo=timezone
        ).astimezone(UTC)

        conditions = [
            Sale.company_id == self.company_id,
            Sale.status == "confirmed",
            Sale.created_at >= start_at,
            Sale.created_at < end_at,
        ]
        if seller_id is not None:
            conditions.append(Sale.seller_id == seller_id)
        if category_id is not None:
            conditions.append(Product.category_id == category_id)

        sale_rows = self.session.execute(
            select(
                Sale.id,
                Sale.created_at,
                Sale.customer_id,
                Sale.seller_id,
                User.name.label("seller_name"),
                func.sum(SaleDetail.subtotal).label("revenue"),
                func.sum(SaleDetail.quantity).label("units"),
            )
            .join(SaleDetail, SaleDetail.sale_id == Sale.id)
            .join(Product, Product.id == SaleDetail.product_id)
            .join(User, User.id == Sale.seller_id)
            .where(*conditions)
            .group_by(
                Sale.id,
                Sale.created_at,
                Sale.customer_id,
                Sale.seller_id,
                User.name,
            )
            .order_by(Sale.created_at, Sale.id)
        ).all()

        totals = [Decimal(row.revenue) for row in sale_rows]
        sales_total = sum(totals, start=Decimal("0"))
        transactions = len(sale_rows)
        units_sold = sum(int(row.units) for row in sale_rows)
        ticket_average = (
            sales_total / Decimal(transactions) if transactions else Decimal("0")
        )
        mean_value = arithmetic_mean(totals) if totals else Decimal("0")
        median_value = median(totals) if totals else Decimal("0")
        granularity = self._granularity(start_date, end_date)

        return {
            "generated_at": datetime.now(UTC),
            "currency": "PEN",
            "period": {
                "date_from": start_date,
                "date_to": end_date,
                "granularity": granularity,
            },
            "applied_filters": {
                "branch": branch,
                "seller_id": seller_id,
                "category_id": category_id,
            },
            "filter_options": self._filter_options(),
            "kpis": {
                "sales_total": _money(sales_total),
                "transactions": transactions,
                "active_customers": len({row.customer_id for row in sale_rows}),
                "units_sold": units_sold,
                "ticket_average": _money(ticket_average),
                "sales_mean": _money(mean_value),
                "sales_median": _money(median_value),
            },
            "sales_by_period": self._period_series(
                sale_rows, start_date, end_date, granularity, timezone
            ),
            "sales_by_product": self._sales_by_product(conditions, sales_total),
            "sales_by_seller": self._sales_by_seller(sale_rows, sales_total),
            "ticket_distribution": self._ticket_distribution(totals),
        }

    def _company_timezone(self) -> ZoneInfo:
        company = self.session.scalar(
            select(Company).where(Company.id == self.company_id)
        )
        if company is None:
            raise AppError("COMPANY_NOT_FOUND", "La empresa no existe", status_code=404)
        try:
            return ZoneInfo(company.timezone)
        except ZoneInfoNotFoundError:
            return ZoneInfo("America/Lima")

    @staticmethod
    def _period(
        date_from: date | None, date_to: date | None, timezone: ZoneInfo
    ) -> tuple[date, date]:
        end_date = date_to or datetime.now(timezone).date()
        start_date = date_from or end_date.replace(day=1)
        if end_date < start_date:
            raise AppError(
                "INVALID_DASHBOARD_PERIOD",
                "La fecha final no puede ser anterior a la fecha inicial",
                status_code=422,
            )
        if (end_date - start_date).days + 1 > MAX_PERIOD_DAYS:
            raise AppError(
                "DASHBOARD_PERIOD_TOO_LARGE",
                "El periodo del dashboard no puede superar 366 dias",
                status_code=422,
            )
        return start_date, end_date

    def _validate_filter_ids(
        self, seller_id: int | None, category_id: int | None
    ) -> None:
        if seller_id is not None:
            seller_exists = self.session.scalar(
                select(User.id).where(
                    User.id == seller_id,
                    User.company_id == self.company_id,
                )
            )
            if seller_exists is None:
                raise AppError(
                    "DASHBOARD_SELLER_NOT_FOUND",
                    "El vendedor seleccionado no existe",
                    status_code=404,
                )
        if category_id is not None:
            category_exists = self.session.scalar(
                select(Category.id).where(
                    Category.id == category_id,
                    Category.company_id == self.company_id,
                )
            )
            if category_exists is None:
                raise AppError(
                    "DASHBOARD_CATEGORY_NOT_FOUND",
                    "La categoria seleccionada no existe",
                    status_code=404,
                )

    def _filter_options(self) -> dict[str, Any]:
        sellers = self.session.execute(
            select(User.id, User.name)
            .join(Role, Role.id == User.role_id)
            .where(
                User.company_id == self.company_id,
                User.active.is_(True),
                Role.code.in_(["administrator", "seller"]),
            )
            .order_by(User.name, User.id)
        ).all()
        categories = self.session.execute(
            select(Category.id, Category.name)
            .where(Category.company_id == self.company_id)
            .order_by(Category.name, Category.id)
        ).all()
        return {
            "branches": [{"id": "main", "label": "Sucursal principal"}],
            "sellers": [{"id": row.id, "label": row.name} for row in sellers],
            "categories": [{"id": row.id, "label": row.name} for row in categories],
        }

    @staticmethod
    def _granularity(start_date: date, end_date: date) -> Literal["day", "week", "month"]:
        days = (end_date - start_date).days + 1
        if days <= 31:
            return "day"
        if days <= 180:
            return "week"
        return "month"

    @staticmethod
    def _local_date(value: datetime, timezone: ZoneInfo) -> date:
        aware = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
        return aware.astimezone(timezone).date()

    @classmethod
    def _period_key(
        cls,
        value: date,
        granularity: Literal["day", "week", "month"],
    ) -> date:
        if granularity == "day":
            return value
        if granularity == "week":
            return value - timedelta(days=value.weekday())
        return value.replace(day=1)

    @classmethod
    def _period_series(
        cls,
        sale_rows: list[Any],
        start_date: date,
        end_date: date,
        granularity: Literal["day", "week", "month"],
        timezone: ZoneInfo,
    ) -> list[dict[str, Any]]:
        aggregates: dict[date, dict[str, Decimal | int]] = defaultdict(
            lambda: {"revenue": Decimal("0"), "transactions": 0}
        )
        for row in sale_rows:
            key = cls._period_key(cls._local_date(row.created_at, timezone), granularity)
            aggregates[key]["revenue"] = Decimal(aggregates[key]["revenue"]) + Decimal(
                row.revenue
            )
            aggregates[key]["transactions"] = int(aggregates[key]["transactions"]) + 1

        cursor = cls._period_key(start_date, granularity)
        last = cls._period_key(end_date, granularity)
        points: list[dict[str, Any]] = []
        while cursor <= last:
            item = aggregates[cursor]
            points.append(
                {
                    "period": cursor,
                    "revenue": _money(Decimal(item["revenue"])),
                    "transactions": int(item["transactions"]),
                }
            )
            if granularity == "day":
                cursor += timedelta(days=1)
            elif granularity == "week":
                cursor += timedelta(days=7)
            else:
                cursor = date(cursor.year + (cursor.month == 12), cursor.month % 12 + 1, 1)
        return points

    def _sales_by_product(
        self, conditions: list[Any], sales_total: Decimal
    ) -> list[dict[str, Any]]:
        rows = self.session.execute(
            select(
                SaleDetail.product_id,
                func.max(SaleDetail.product_name_snapshot).label("product_name"),
                func.sum(SaleDetail.subtotal).label("revenue"),
                func.count(func.distinct(Sale.id)).label("transactions"),
                func.sum(SaleDetail.quantity).label("units"),
            )
            .join(Sale, Sale.id == SaleDetail.sale_id)
            .join(Product, Product.id == SaleDetail.product_id)
            .where(*conditions)
            .group_by(SaleDetail.product_id)
            .order_by(func.sum(SaleDetail.subtotal).desc(), SaleDetail.product_id)
            .limit(10)
        ).all()
        return [
            {
                "id": row.product_id,
                "label": row.product_name,
                "revenue": _money(Decimal(row.revenue)),
                "transactions": int(row.transactions),
                "units": int(row.units),
                "share": _percentage(Decimal(row.revenue), sales_total),
            }
            for row in rows
        ]

    @staticmethod
    def _sales_by_seller(
        sale_rows: list[Any], sales_total: Decimal
    ) -> list[dict[str, Any]]:
        aggregates: dict[int, dict[str, Any]] = {}
        for row in sale_rows:
            item = aggregates.setdefault(
                row.seller_id,
                {
                    "id": row.seller_id,
                    "label": row.seller_name,
                    "revenue": Decimal("0"),
                    "transactions": 0,
                    "units": 0,
                },
            )
            item["revenue"] += Decimal(row.revenue)
            item["transactions"] += 1
            item["units"] += int(row.units)
        values = sorted(
            aggregates.values(), key=lambda item: (-item["revenue"], item["id"])
        )
        return [
            {
                **item,
                "revenue": _money(item["revenue"]),
                "share": _percentage(item["revenue"], sales_total),
            }
            for item in values
        ]

    @staticmethod
    def _ticket_distribution(totals: list[Decimal]) -> list[dict[str, Any]]:
        bands = [
            ("Menos de S/ 100", None, Decimal("100")),
            ("S/ 100 - 249", Decimal("100"), Decimal("250")),
            ("S/ 250 - 499", Decimal("250"), Decimal("500")),
            ("S/ 500 - 999", Decimal("500"), Decimal("1000")),
            ("S/ 1,000 o mas", Decimal("1000"), None),
        ]
        result = []
        for label, minimum, maximum in bands:
            frequency = sum(
                1
                for value in totals
                if (minimum is None or value >= minimum)
                and (maximum is None or value < maximum)
            )
            result.append(
                {
                    "label": label,
                    "frequency": frequency,
                    "percentage": _percentage(frequency, len(totals)),
                }
            )
        return result
