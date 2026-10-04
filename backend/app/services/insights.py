"""Explainable, deterministic insight rules with persistent evidence."""

from datetime import UTC, datetime, time
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.analytics import (
    Dataset,
    DatasetVariable,
    Insight,
    Observation,
    StatisticalAnalysis,
    StatisticalResult,
)
from app.schemas.insights import InsightGenerationRequest
from app.services.dashboard import DashboardService

PERCENTAGE = Decimal("0.01")
RULESET_VERSION = "phase11-v1"


def _percent(part: Decimal | int, total: Decimal | int) -> Decimal:
    denominator = Decimal(total)
    if denominator == 0:
        return Decimal("0.00")
    return (Decimal(part) * Decimal("100") / denominator).quantize(
        PERCENTAGE, rounding=ROUND_HALF_UP
    )


class InsightService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    def generate(self, payload: InsightGenerationRequest) -> dict[str, Any]:
        summary = DashboardService(self.session, self.company_id).summary(
            date_from=payload.date_from,
            date_to=payload.date_to,
            branch=payload.branch,
            seller_id=payload.seller_id,
            category_id=payload.category_id,
        )
        period = summary["period"]
        filters = {
            "branch": payload.branch,
            "seller_id": payload.seller_id,
            "category_id": payload.category_id,
            "date_from": period["date_from"].isoformat(),
            "date_to": period["date_to"].isoformat(),
            "ruleset": RULESET_VERSION,
        }
        timestamp = datetime.now(UTC)
        dataset = Dataset(
            company_id=self.company_id,
            created_by_user_id=self.user_id,
            name=f"Insights de ventas - {timestamp:%Y-%m-%d %H:%M UTC}",
            description="Serie agregada que sustenta insights empresariales explicables.",
            source_type="sales_snapshot",
            filters=filters,
            period_start=period["date_from"],
            period_end=period["date_to"],
        )
        self.session.add(dataset)
        self.session.flush()
        variable = DatasetVariable(
            dataset_id=dataset.id,
            name="period_revenue",
            label="Ventas por periodo",
            variable_type="quantitative_continuous",
            data_type="decimal",
            source_field="sale_details.subtotal",
            unit="PEN",
        )
        self.session.add(variable)
        self.session.flush()
        self.session.add_all(
            [
                Observation(
                    dataset_id=dataset.id,
                    variable_id=variable.id,
                    source_record_id=point["period"].isoformat(),
                    ordinal=index,
                    value_numeric=Decimal(point["revenue"]),
                    value_text=None,
                    observed_at=datetime.combine(point["period"], time.min, tzinfo=UTC),
                )
                for index, point in enumerate(summary["sales_by_period"], start=1)
            ]
        )
        analysis = StatisticalAnalysis(
            company_id=self.company_id,
            dataset_id=dataset.id,
            requested_by_user_id=self.user_id,
            analysis_type="insight",
            status="pending",
            parameters=filters,
            error_message=None,
        )
        self.session.add(analysis)
        self.session.flush()

        rules = self._evaluate(summary)
        self.session.execute(
            update(Insight)
            .where(Insight.company_id == self.company_id, Insight.active.is_(True))
            .values(active=False)
        )
        insight_models = []
        for rule in rules:
            evidence = {
                **rule["evidence"],
                "rule_code": rule["rule_code"],
                "category": rule["category"],
                "ruleset": RULESET_VERSION,
                "dataset_id": dataset.id,
                "analysis_id": analysis.id,
                "period_start": period["date_from"].isoformat(),
                "period_end": period["date_to"].isoformat(),
            }
            insight = Insight(
                company_id=self.company_id,
                analysis_id=analysis.id,
                title=rule["title"],
                description=rule["description"],
                severity=rule["severity"],
                evidence=evidence,
                active=True,
                generated_at=timestamp,
            )
            self.session.add(insight)
            insight_models.append(insight)

        kpis = summary["kpis"]
        self.session.add_all(
            [
                StatisticalResult(
                    analysis_id=analysis.id,
                    variable_id=variable.id,
                    metric="sales_total",
                    numeric_value=Decimal(kpis["sales_total"]),
                    text_value=None,
                    details={},
                ),
                StatisticalResult(
                    analysis_id=analysis.id,
                    variable_id=variable.id,
                    metric="transactions",
                    numeric_value=Decimal(kpis["transactions"]),
                    text_value=None,
                    details={},
                ),
                StatisticalResult(
                    analysis_id=analysis.id,
                    variable_id=variable.id,
                    metric="insight_count",
                    numeric_value=Decimal(len(insight_models)),
                    text_value=None,
                    details={"ruleset": RULESET_VERSION},
                ),
            ]
        )
        analysis.status = "completed"
        analysis.completed_at = timestamp
        self.session.flush()
        return {
            "analysis_id": analysis.id,
            "dataset_id": dataset.id,
            "generated_count": len(insight_models),
            "items": [self._serialize(item, analysis, dataset) for item in insight_models],
        }

    def history(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None,
        severity: str | None,
        active: bool | None,
    ) -> tuple[list[dict[str, Any]], int]:
        conditions = [Insight.company_id == self.company_id]
        if category is not None:
            conditions.append(Insight.evidence["category"].as_string() == category)
        if severity is not None:
            conditions.append(Insight.severity == severity)
        if active is not None:
            conditions.append(Insight.active.is_(active))

        total = self.session.scalar(select(func.count(Insight.id)).where(*conditions))
        rows = self.session.execute(
            select(Insight, StatisticalAnalysis, Dataset)
            .join(StatisticalAnalysis, StatisticalAnalysis.id == Insight.analysis_id)
            .join(Dataset, Dataset.id == StatisticalAnalysis.dataset_id)
            .where(*conditions)
            .order_by(Insight.generated_at.desc(), Insight.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return [self._serialize(*row) for row in rows], int(total or 0)

    @staticmethod
    def _serialize(
        insight: Insight, analysis: StatisticalAnalysis, dataset: Dataset
    ) -> dict[str, Any]:
        return {
            "id": insight.id,
            "analysis_id": analysis.id,
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "title": insight.title,
            "description": insight.description,
            "category": insight.evidence["category"],
            "rule_code": insight.evidence["rule_code"],
            "severity": insight.severity,
            "evidence": insight.evidence,
            "active": insight.active,
            "period_start": dataset.period_start,
            "period_end": dataset.period_end,
            "generated_at": insight.generated_at,
        }

    @staticmethod
    def _evaluate(summary: dict[str, Any]) -> list[dict[str, Any]]:
        kpis = summary["kpis"]
        transactions = int(kpis["transactions"])
        total = Decimal(kpis["sales_total"])
        if transactions == 0:
            return [
                {
                    "rule_code": "sales.no_activity",
                    "category": "sales",
                    "severity": "warning",
                    "title": "No se registraron ventas en el periodo",
                    "description": (
                        "El periodo seleccionado no contiene ventas confirmadas. "
                        "Amplia el rango o registra operaciones para obtener mas observaciones."
                    ),
                    "evidence": {
                        "metric": "transactions",
                        "value": 0,
                        "unit": "ventas",
                        "threshold": 1,
                    },
                }
            ]

        rules: list[dict[str, Any]] = [
            {
                "rule_code": "sales.period_summary",
                "category": "sales",
                "severity": "info",
                "title": "Actividad comercial del periodo",
                "description": (
                    f"Se confirmaron {transactions} ventas por un total de "
                    f"S/ {total:,.2f}."
                ),
                "evidence": {
                    "metric": "sales_total",
                    "value": str(total),
                    "unit": "PEN",
                    "transactions": transactions,
                },
            }
        ]

        mean_value = Decimal(kpis["sales_mean"])
        median_value = Decimal(kpis["sales_median"])
        gap = _percent(abs(mean_value - median_value), median_value) if median_value else Decimal(0)
        skewed = median_value > 0 and mean_value > median_value * Decimal("1.25")
        rules.append(
            {
                "rule_code": "statistics.ticket_shape",
                "category": "statistics",
                "severity": "warning" if skewed else "info",
                "title": (
                    "Ventas altas elevan el promedio"
                    if skewed
                    else "Media y mediana mantienen una relación estable"
                ),
                "description": (
                    f"La media es S/ {mean_value:,.2f} y la mediana S/ {median_value:,.2f}; "
                    f"la diferencia relativa es {gap} %."
                ),
                "evidence": {
                    "metric": "mean_median_gap",
                    "value": str(gap),
                    "unit": "percent",
                    "mean": str(mean_value),
                    "median": str(median_value),
                    "threshold": "25.00",
                },
            }
        )

        products = summary["sales_by_product"]
        if products:
            top_product = products[0]
            product_share = Decimal(top_product["share"])
            rules.append(
                {
                    "rule_code": "products.revenue_concentration",
                    "category": "products",
                    "severity": "warning" if product_share >= 50 else "info",
                    "title": "Producto con mayor participación",
                    "description": (
                        f"{top_product['label']} aporta {product_share} % de la facturación "
                        f"filtrada, equivalente a S/ {Decimal(top_product['revenue']):,.2f}."
                    ),
                    "evidence": {
                        "metric": "top_product_share",
                        "value": str(product_share),
                        "unit": "percent",
                        "product_id": top_product["id"],
                        "product": top_product["label"],
                        "revenue": str(top_product["revenue"]),
                        "threshold": "50.00",
                    },
                }
            )

        sellers = summary["sales_by_seller"]
        if sellers:
            top_seller = sellers[0]
            seller_share = Decimal(top_seller["share"])
            concentrated = len(sellers) > 1 and seller_share >= 60
            rules.append(
                {
                    "rule_code": "sellers.revenue_concentration",
                    "category": "sellers",
                    "severity": "warning" if concentrated else "info",
                    "title": "Participación principal del equipo comercial",
                    "description": (
                        f"{top_seller['label']} concentra {seller_share} % de la facturación "
                        f"y {top_seller['transactions']} ventas del periodo."
                    ),
                    "evidence": {
                        "metric": "top_seller_share",
                        "value": str(seller_share),
                        "unit": "percent",
                        "seller_id": top_seller["id"],
                        "seller": top_seller["label"],
                        "transactions": top_seller["transactions"],
                        "threshold": "60.00",
                    },
                }
            )

        customers = int(kpis["active_customers"])
        repeated_transactions = max(transactions - customers, 0)
        recurrence = _percent(repeated_transactions, transactions)
        rules.append(
            {
                "rule_code": "customers.recurrence_floor",
                "category": "customers",
                "severity": "info",
                "title": "Nivel mínimo de recurrencia observado",
                "description": (
                    f"{customers} clientes participaron en {transactions} ventas; al menos "
                    f"{recurrence} % de las operaciones corresponden a compras adicionales."
                ),
                "evidence": {
                    "metric": "minimum_recurrence",
                    "value": str(recurrence),
                    "unit": "percent",
                    "active_customers": customers,
                    "transactions": transactions,
                },
            }
        )

        periods = summary["sales_by_period"]
        active_periods = sum(1 for point in periods if Decimal(point["revenue"]) > 0)
        activity = _percent(active_periods, len(periods))
        rules.append(
            {
                "rule_code": "sales.period_continuity",
                "category": "sales",
                "severity": "warning" if activity < 40 else "info",
                "title": "Continuidad de ventas del periodo",
                "description": (
                    f"Hubo ventas en {active_periods} de {len(periods)} intervalos, "
                    f"equivalente a una actividad de {activity} %."
                ),
                "evidence": {
                    "metric": "active_period_share",
                    "value": str(activity),
                    "unit": "percent",
                    "active_periods": active_periods,
                    "total_periods": len(periods),
                    "threshold": "40.00",
                },
            }
        )
        return rules
