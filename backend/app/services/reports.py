"""Persistent report snapshots and CSV export for phase 12."""

import csv
import json
from datetime import UTC, date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal
from io import StringIO
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.analytics import Dataset, StatisticalAnalysis, StatisticalResult
from app.models.catalog import Category, Product
from app.models.company import Company
from app.models.customer import Customer
from app.models.governance import Report
from app.models.identity import Role, User
from app.models.inventory import Inventory
from app.models.sales import Sale, SaleDetail
from app.schemas.reports import ReportGenerateRequest

MAX_REPORT_DAYS = 366
MONEY = Decimal("0.01")

REPORT_TITLES = {
    "sales": "Reporte de ventas",
    "products": "Reporte de productos",
    "customers": "Reporte de clientes",
    "sellers": "Reporte de vendedores",
    "statistical": "Reporte estadístico",
}


def _money(value: Decimal | int | None) -> str:
    return str(Decimal(value or 0).quantize(MONEY, rounding=ROUND_HALF_UP))


class ReportService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    def generate(self, payload: ReportGenerateRequest) -> dict[str, Any]:
        date_from, date_to, start_at, end_at = self._period(
            payload.date_from, payload.date_to
        )
        content = getattr(self, f"_{payload.report_type}_content")(start_at, end_at)
        timestamp = datetime.now(UTC)
        report = Report(
            company_id=self.company_id,
            requested_by_user_id=self.user_id,
            report_type=payload.report_type,
            title=payload.title or REPORT_TITLES[payload.report_type],
            parameters={
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
            },
            status="completed",
            content=content,
            file_path=None,
            error_message=None,
            generated_at=timestamp,
        )
        self.session.add(report)
        self.session.flush()
        return self._serialize(report, include_content=True)

    def history(
        self,
        *,
        page: int,
        page_size: int,
        report_type: str | None,
        status: str | None,
    ) -> tuple[list[dict[str, Any]], int]:
        conditions = [Report.company_id == self.company_id]
        if report_type is not None:
            conditions.append(Report.report_type == report_type)
        if status is not None:
            conditions.append(Report.status == status)
        total = self.session.scalar(select(func.count(Report.id)).where(*conditions))
        reports = self.session.scalars(
            select(Report)
            .where(*conditions)
            .order_by(Report.created_at.desc(), Report.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return [self._serialize(item) for item in reports], int(total or 0)

    def get(self, report_id: int) -> dict[str, Any]:
        report = self.session.scalar(
            select(Report).where(
                Report.id == report_id,
                Report.company_id == self.company_id,
            )
        )
        if report is None:
            raise AppError("REPORT_NOT_FOUND", "El reporte no existe", status_code=404)
        return self._serialize(report, include_content=True)

    def csv_export(self, report_id: int) -> tuple[str, str]:
        report = self.get(report_id)
        columns = report["content"]["columns"]
        rows = report["content"]["rows"]
        stream = StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow([column["label"] for column in columns])
        for row in rows:
            writer.writerow([self._csv_value(row.get(column["key"])) for column in columns])
        filename = f"salesia-{report['report_type']}-{report_id}.csv"
        return "\ufeff" + stream.getvalue(), filename

    def _period(
        self, date_from: date | None, date_to: date | None
    ) -> tuple[date, date, datetime, datetime]:
        company = self.session.get(Company, self.company_id)
        if company is None:
            raise AppError("COMPANY_NOT_FOUND", "La empresa no existe", status_code=404)
        try:
            timezone = ZoneInfo(company.timezone)
        except ZoneInfoNotFoundError:
            timezone = ZoneInfo("America/Lima")
        end_date = date_to or datetime.now(timezone).date()
        start_date = date_from or end_date.replace(day=1)
        if end_date < start_date:
            raise AppError(
                "INVALID_REPORT_PERIOD",
                "La fecha final no puede ser anterior a la fecha inicial",
                status_code=422,
            )
        if (end_date - start_date).days + 1 > MAX_REPORT_DAYS:
            raise AppError(
                "REPORT_PERIOD_TOO_LARGE",
                "El periodo del reporte no puede superar 366 dias",
                status_code=422,
            )
        start_at = datetime.combine(start_date, time.min, tzinfo=timezone).astimezone(UTC)
        end_at = datetime.combine(
            end_date + timedelta(days=1), time.min, tzinfo=timezone
        ).astimezone(UTC)
        return start_date, end_date, start_at, end_at

    def _sales_content(self, start_at: datetime, end_at: datetime) -> dict[str, Any]:
        records = self.session.execute(
            select(
                Sale.number,
                Sale.created_at,
                Customer.name.label("customer"),
                User.name.label("seller"),
                func.sum(SaleDetail.quantity).label("units"),
                Sale.total,
                Sale.currency,
            )
            .join(Customer, Customer.id == Sale.customer_id)
            .join(User, User.id == Sale.seller_id)
            .join(SaleDetail, SaleDetail.sale_id == Sale.id)
            .where(*self._sale_conditions(start_at, end_at))
            .group_by(
                Sale.id,
                Sale.number,
                Sale.created_at,
                Customer.name,
                User.name,
                Sale.total,
                Sale.currency,
            )
            .order_by(Sale.created_at.desc(), Sale.id.desc())
        ).all()
        rows = [
            {
                "number": row.number,
                "date": row.created_at.isoformat(),
                "customer": row.customer,
                "seller": row.seller,
                "units": int(row.units),
                "total": _money(row.total),
                "currency": row.currency,
            }
            for row in records
        ]
        revenue = sum((Decimal(row.total) for row in records), start=Decimal("0"))
        return {
            "columns": [
                {"key": "number", "label": "Venta", "format": "text"},
                {"key": "date", "label": "Fecha", "format": "datetime"},
                {"key": "customer", "label": "Cliente", "format": "text"},
                {"key": "seller", "label": "Vendedor", "format": "text"},
                {"key": "units", "label": "Unidades", "format": "integer"},
                {"key": "total", "label": "Total", "format": "money"},
            ],
            "rows": rows,
            "summary": {
                "transactions": len(rows),
                "revenue": _money(revenue),
                "ticket_average": _money(revenue / len(rows) if rows else 0),
            },
        }

    def _products_content(self, start_at: datetime, end_at: datetime) -> dict[str, Any]:
        sale_match = and_(
            Sale.id == SaleDetail.sale_id,
            *self._sale_conditions(start_at, end_at),
        )
        records = self.session.execute(
            select(
                Product.sku,
                Product.name,
                Category.name.label("category"),
                Product.unit_price,
                Product.active,
                func.coalesce(Inventory.quantity, 0).label("stock"),
                func.coalesce(
                    func.sum(case((Sale.id.is_not(None), SaleDetail.quantity), else_=0)), 0
                ).label("units_sold"),
                func.coalesce(
                    func.sum(case((Sale.id.is_not(None), SaleDetail.subtotal), else_=0)), 0
                ).label("revenue"),
            )
            .join(Category, Category.id == Product.category_id)
            .outerjoin(Inventory, Inventory.product_id == Product.id)
            .outerjoin(SaleDetail, SaleDetail.product_id == Product.id)
            .outerjoin(Sale, sale_match)
            .where(Product.company_id == self.company_id)
            .group_by(
                Product.id,
                Product.sku,
                Product.name,
                Category.name,
                Product.unit_price,
                Product.active,
                Inventory.quantity,
            )
            .order_by(Product.name, Product.id)
        ).all()
        rows = [
            {
                "sku": row.sku,
                "product": row.name,
                "category": row.category,
                "price": _money(row.unit_price),
                "stock": int(row.stock),
                "units_sold": int(row.units_sold),
                "revenue": _money(row.revenue),
                "status": "Activo" if row.active else "Inactivo",
            }
            for row in records
        ]
        return {
            "columns": [
                {"key": "sku", "label": "SKU", "format": "text"},
                {"key": "product", "label": "Producto", "format": "text"},
                {"key": "category", "label": "Categoría", "format": "text"},
                {"key": "price", "label": "Precio", "format": "money"},
                {"key": "stock", "label": "Stock", "format": "integer"},
                {"key": "units_sold", "label": "Vendidas", "format": "integer"},
                {"key": "revenue", "label": "Facturación", "format": "money"},
                {"key": "status", "label": "Estado", "format": "status"},
            ],
            "rows": rows,
            "summary": {
                "products": len(rows),
                "active_products": sum(1 for row in records if row.active),
                "units_sold": sum(int(row.units_sold) for row in records),
                "revenue": _money(sum((Decimal(row.revenue) for row in records), Decimal(0))),
            },
        }

    def _customers_content(self, start_at: datetime, end_at: datetime) -> dict[str, Any]:
        sale_match = and_(
            Sale.customer_id == Customer.id,
            *self._sale_conditions(start_at, end_at),
        )
        records = self.session.execute(
            select(
                Customer.name,
                Customer.document_type,
                Customer.document_number,
                Customer.email,
                Customer.active,
                func.count(Sale.id).label("transactions"),
                func.coalesce(func.sum(Sale.total), 0).label("spent"),
                func.max(Sale.created_at).label("last_purchase"),
            )
            .outerjoin(Sale, sale_match)
            .where(Customer.company_id == self.company_id)
            .group_by(Customer.id)
            .order_by(Customer.name, Customer.id)
        ).all()
        rows = [
            {
                "customer": row.name,
                "document": f"{row.document_type} {row.document_number}",
                "email": row.email or "—",
                "transactions": int(row.transactions),
                "spent": _money(row.spent),
                "last_purchase": row.last_purchase.isoformat() if row.last_purchase else None,
                "status": "Activo" if row.active else "Inactivo",
            }
            for row in records
        ]
        return {
            "columns": [
                {"key": "customer", "label": "Cliente", "format": "text"},
                {"key": "document", "label": "Documento", "format": "text"},
                {"key": "email", "label": "Correo", "format": "text"},
                {"key": "transactions", "label": "Compras", "format": "integer"},
                {"key": "spent", "label": "Total comprado", "format": "money"},
                {"key": "last_purchase", "label": "Última compra", "format": "datetime"},
                {"key": "status", "label": "Estado", "format": "status"},
            ],
            "rows": rows,
            "summary": {
                "customers": len(rows),
                "buyers": sum(1 for row in records if row.transactions > 0),
                "transactions": sum(int(row.transactions) for row in records),
                "revenue": _money(sum((Decimal(row.spent) for row in records), Decimal(0))),
            },
        }

    def _sellers_content(self, start_at: datetime, end_at: datetime) -> dict[str, Any]:
        sale_match = and_(
            Sale.seller_id == User.id,
            *self._sale_conditions(start_at, end_at),
        )
        records = self.session.execute(
            select(
                User.name,
                User.email,
                Role.name.label("role"),
                User.active,
                func.count(Sale.id).label("transactions"),
                func.coalesce(func.sum(Sale.total), 0).label("revenue"),
                func.max(Sale.created_at).label("last_sale"),
            )
            .join(Role, Role.id == User.role_id)
            .outerjoin(Sale, sale_match)
            .where(
                User.company_id == self.company_id,
                Role.code.in_(["administrator", "seller"]),
            )
            .group_by(User.id, Role.name)
            .order_by(User.name, User.id)
        ).all()
        rows = [
            {
                "seller": row.name,
                "email": row.email,
                "role": row.role,
                "transactions": int(row.transactions),
                "revenue": _money(row.revenue),
                "last_sale": row.last_sale.isoformat() if row.last_sale else None,
                "status": "Activo" if row.active else "Inactivo",
            }
            for row in records
        ]
        return {
            "columns": [
                {"key": "seller", "label": "Vendedor", "format": "text"},
                {"key": "email", "label": "Correo", "format": "text"},
                {"key": "role", "label": "Rol", "format": "text"},
                {"key": "transactions", "label": "Ventas", "format": "integer"},
                {"key": "revenue", "label": "Facturación", "format": "money"},
                {"key": "last_sale", "label": "Última venta", "format": "datetime"},
                {"key": "status", "label": "Estado", "format": "status"},
            ],
            "rows": rows,
            "summary": {
                "sellers": len(rows),
                "active_sellers": sum(1 for row in records if row.active),
                "transactions": sum(int(row.transactions) for row in records),
                "revenue": _money(sum((Decimal(row.revenue) for row in records), Decimal(0))),
            },
        }

    def _statistical_content(self, start_at: datetime, end_at: datetime) -> dict[str, Any]:
        analyses = self.session.execute(
            select(StatisticalAnalysis, Dataset.name.label("dataset_name"))
            .join(Dataset, Dataset.id == StatisticalAnalysis.dataset_id)
            .where(
                StatisticalAnalysis.company_id == self.company_id,
                StatisticalAnalysis.created_at >= start_at,
                StatisticalAnalysis.created_at < end_at,
            )
            .order_by(StatisticalAnalysis.created_at.desc(), StatisticalAnalysis.id.desc())
        ).all()
        rows = []
        for analysis, dataset_name in analyses:
            results = self.session.scalars(
                select(StatisticalResult)
                .where(StatisticalResult.analysis_id == analysis.id)
                .order_by(StatisticalResult.metric, StatisticalResult.id)
            ).all()
            result_text = "; ".join(
                f"{item.metric}={self._result_value(item)}" for item in results
            ) or "Sin resultados"
            rows.append(
                {
                    "analysis_id": analysis.id,
                    "date": analysis.created_at.isoformat(),
                    "type": analysis.analysis_type,
                    "dataset": dataset_name,
                    "status": analysis.status,
                    "results": result_text,
                }
            )
        return {
            "columns": [
                {"key": "analysis_id", "label": "Análisis", "format": "integer"},
                {"key": "date", "label": "Fecha", "format": "datetime"},
                {"key": "type", "label": "Tipo", "format": "text"},
                {"key": "dataset", "label": "Dataset", "format": "text"},
                {"key": "status", "label": "Estado", "format": "status"},
                {"key": "results", "label": "Resultados", "format": "text"},
            ],
            "rows": rows,
            "summary": {
                "analyses": len(rows),
                "completed": sum(1 for analysis, _ in analyses if analysis.status == "completed"),
                "datasets": len({analysis.dataset_id for analysis, _ in analyses}),
            },
        }

    def _sale_conditions(self, start_at: datetime, end_at: datetime) -> list[Any]:
        return [
            Sale.company_id == self.company_id,
            Sale.status == "confirmed",
            Sale.created_at >= start_at,
            Sale.created_at < end_at,
        ]

    @staticmethod
    def _result_value(result: StatisticalResult) -> str:
        if result.numeric_value is not None:
            return str(result.numeric_value)
        if result.text_value is not None:
            return result.text_value
        return json.dumps(result.details, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def _csv_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    @staticmethod
    def _serialize(report: Report, *, include_content: bool = False) -> dict[str, Any]:
        content = report.content or {"columns": [], "rows": [], "summary": {}}
        result = {
            "id": report.id,
            "report_type": report.report_type,
            "title": report.title,
            "parameters": report.parameters,
            "status": report.status,
            "row_count": len(content.get("rows", [])),
            "created_at": report.created_at,
            "generated_at": report.generated_at,
        }
        if include_content:
            result["content"] = content
        return result
