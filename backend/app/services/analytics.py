"""Phase 09 statistical services with persistent, company-scoped analyses."""

from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.analytics import (
    BayesAnalysis,
    Dataset,
    DatasetVariable,
    Observation,
    RandomVariable,
    StatisticalAnalysis,
    StatisticalResult,
)
from app.models.sales import Sale, SaleDetail
from app.schemas.statistics import (
    BayesRequest,
    EventProbabilityRequest,
    NumericSeriesRequest,
    RandomVariableRequest,
    SalesComparisonRequest,
)
from app.statistics.engine import (
    arithmetic_mean,
    bayes_posterior,
    compare_mean_median,
    discrete_distribution,
    event_probability,
    median,
)

VARIABLE_CATALOG = [
    {
        "name": "sale_total",
        "label": "Monto total de venta",
        "variable_type": "quantitative_continuous",
        "data_type": "decimal",
        "unit": "PEN",
        "description": "Importe final de cada venta confirmada.",
    },
    {
        "name": "items_per_sale",
        "label": "Unidades por venta",
        "variable_type": "quantitative_discrete",
        "data_type": "integer",
        "unit": "unidades",
        "description": "Cantidad total de unidades incluidas en una venta.",
    },
    {
        "name": "payment_method",
        "label": "Metodo de pago",
        "variable_type": "qualitative",
        "data_type": "text",
        "unit": None,
        "description": "Categoria del medio utilizado para pagar la venta.",
    },
    {
        "name": "seller",
        "label": "Vendedor",
        "variable_type": "qualitative",
        "data_type": "text",
        "unit": None,
        "description": "Usuario responsable de registrar la venta.",
    },
    {
        "name": "product_quantity",
        "label": "Cantidad de producto",
        "variable_type": "quantitative_discrete",
        "data_type": "integer",
        "unit": "unidades",
        "description": "Numero de unidades vendidas de un producto.",
    },
]


class AnalyticsService:
    def __init__(self, session: Session, company_id: int, user_id: int) -> None:
        self.session = session
        self.company_id = company_id
        self.user_id = user_id

    @staticmethod
    def variable_catalog() -> list[dict[str, Any]]:
        return VARIABLE_CATALOG

    def analyze_series(
        self, payload: NumericSeriesRequest, analysis_type: str
    ) -> dict[str, Any]:
        dataset, variable = self._create_series_dataset(
            name=payload.name.strip(),
            source_type="manual",
            variable_name=payload.variable_name,
            variable_label=payload.variable_label.strip(),
            variable_type=str(payload.variable_type),
            unit=payload.unit,
            values=payload.values,
            source_ids=None,
            observed_at=None,
            filters={},
        )
        return self._complete_series_analysis(
            dataset, variable, payload.values, analysis_type, {"source": "manual"}
        )

    def analyze_sales(self, payload: SalesComparisonRequest) -> dict[str, Any]:
        filters = [Sale.company_id == self.company_id, Sale.status == "confirmed"]
        if payload.date_from:
            filters.append(Sale.created_at >= datetime.combine(payload.date_from, time.min))
        if payload.date_to:
            filters.append(
                Sale.created_at
                < datetime.combine(payload.date_to + timedelta(days=1), time.min)
            )

        item_count = func.sum(SaleDetail.quantity)
        rows = self.session.execute(
            select(Sale.id, Sale.number, Sale.created_at, Sale.total, item_count)
            .join(SaleDetail, SaleDetail.sale_id == Sale.id)
            .where(*filters)
            .group_by(Sale.id)
            .order_by(Sale.created_at, Sale.id)
        ).all()
        if not rows:
            raise AppError(
                "ANALYTICS_NO_SALES",
                "No hay ventas confirmadas en el periodo seleccionado",
                status_code=409,
            )

        is_total = payload.metric == "sale_total"
        values = [Decimal(str(row.total if is_total else row[4])) for row in rows]
        variable_name = "sale_total" if is_total else "items_per_sale"
        variable_label = "Monto total de venta" if is_total else "Unidades por venta"
        variable_type = "quantitative_continuous" if is_total else "quantitative_discrete"
        unit = "PEN" if is_total else "unidades"
        date_label = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        dataset, variable = self._create_series_dataset(
            name=f"Ventas - {variable_label} - {date_label}",
            source_type="sales_snapshot",
            variable_name=variable_name,
            variable_label=variable_label,
            variable_type=variable_type,
            unit=unit,
            values=values,
            source_ids=[str(row.id) for row in rows],
            observed_at=[row.created_at for row in rows],
            filters={
                "metric": payload.metric,
                "date_from": payload.date_from.isoformat() if payload.date_from else None,
                "date_to": payload.date_to.isoformat() if payload.date_to else None,
            },
        )
        return self._complete_series_analysis(
            dataset,
            variable,
            values,
            "comparison",
            {"source": "sales", "metric": payload.metric},
        )

    def analyze_event_probability(self, payload: EventProbabilityRequest) -> dict[str, Any]:
        dataset = self._create_dataset(
            f"Probabilidad - {payload.event_name.strip()}",
            "manual",
            {"event_name": payload.event_name.strip()},
        )
        variable = DatasetVariable(
            dataset_id=dataset.id,
            name="event_outcome",
            label=payload.event_name.strip(),
            variable_type="quantitative_discrete",
            data_type="integer",
            source_field=None,
            unit="casos",
        )
        self.session.add(variable)
        self.session.flush()
        probability = event_probability(payload.favorable_cases, payload.total_observations)
        analysis = self._create_analysis(
            dataset.id,
            "frequency",
            {
                "event_name": payload.event_name.strip(),
                "favorable_cases": payload.favorable_cases,
                "total_observations": payload.total_observations,
            },
        )
        results = [
            self._result(analysis.id, variable.id, "favorable_cases", payload.favorable_cases),
            self._result(
                analysis.id, variable.id, "total_observations", payload.total_observations
            ),
            self._result(analysis.id, variable.id, "probability", probability),
        ]
        self._finish(analysis)
        return self._execution(dataset, variable, analysis, payload.total_observations, results)

    def analyze_random_variable(self, payload: RandomVariableRequest) -> dict[str, Any]:
        variable_type = (
            "quantitative_discrete"
            if payload.random_variable_type == "discrete"
            else "quantitative_continuous"
        )
        dataset, variable = self._create_series_dataset(
            name=payload.name.strip(),
            source_type="manual",
            variable_name=payload.variable_name,
            variable_label=payload.variable_label.strip(),
            variable_type=variable_type,
            unit=payload.unit,
            values=payload.values,
            source_ids=None,
            observed_at=None,
            filters={"random_variable_type": str(payload.random_variable_type)},
        )
        mean_value = arithmetic_mean(payload.values)
        median_value = median(payload.values)
        distribution = discrete_distribution(payload.values)
        random_variable = RandomVariable(
            dataset_id=dataset.id,
            name=payload.variable_name,
            variable_type=str(payload.random_variable_type),
            distribution={"values": distribution},
            expected_value=mean_value,
            variance=None,
        )
        self.session.add(random_variable)
        analysis = self._create_analysis(
            dataset.id,
            "random_variable",
            {"random_variable_type": str(payload.random_variable_type)},
        )
        results = [
            self._result(analysis.id, variable.id, "sample_size", len(payload.values)),
            self._result(analysis.id, variable.id, "mean", mean_value),
            self._result(analysis.id, variable.id, "median", median_value),
            self._result(analysis.id, variable.id, "minimum", min(payload.values)),
            self._result(analysis.id, variable.id, "maximum", max(payload.values)),
            self._result(
                analysis.id,
                variable.id,
                "distribution",
                None,
                details={"values": distribution},
            ),
        ]
        self._finish(analysis)
        self.session.flush()
        response = self._execution(dataset, variable, analysis, len(payload.values), results)
        response["random_variable_id"] = random_variable.id
        return response

    def analyze_bayes(self, payload: BayesRequest) -> dict[str, Any]:
        try:
            posterior = bayes_posterior(
                payload.probability_a,
                payload.probability_b_given_a,
                payload.probability_b,
            )
        except ValueError as exc:
            raise AppError("INVALID_BAYES_PROBABILITIES", str(exc), status_code=422) from exc
        dataset = self._create_dataset(
            f"Bayes - {payload.event_a.strip()} dado {payload.event_b.strip()}",
            "manual",
            {"event_a": payload.event_a.strip(), "event_b": payload.event_b.strip()},
        )
        analysis = self._create_analysis(
            dataset.id,
            "bayes",
            {
                "event_a": payload.event_a.strip(),
                "event_b": payload.event_b.strip(),
                "probability_a": str(payload.probability_a),
                "probability_b_given_a": str(payload.probability_b_given_a),
                "probability_b": str(payload.probability_b),
            },
        )
        self.session.add(
            BayesAnalysis(
                analysis_id=analysis.id,
                event_a=payload.event_a.strip(),
                event_b=payload.event_b.strip(),
                probability_a=payload.probability_a,
                probability_b_given_a=payload.probability_b_given_a,
                probability_b=payload.probability_b,
                posterior=posterior,
            )
        )
        result = self._result(analysis.id, None, "posterior", posterior)
        self._finish(analysis)
        return self._execution(dataset, None, analysis, 0, [result])

    def history(self, page: int, page_size: int) -> tuple[list[dict[str, Any]], int]:
        analyses = self.session.execute(
            select(StatisticalAnalysis, Dataset)
            .join(Dataset, Dataset.id == StatisticalAnalysis.dataset_id)
            .where(StatisticalAnalysis.company_id == self.company_id)
            .order_by(StatisticalAnalysis.created_at.desc(), StatisticalAnalysis.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        total = self.session.scalar(
            select(func.count(StatisticalAnalysis.id)).where(
                StatisticalAnalysis.company_id == self.company_id
            )
        )
        items = []
        for analysis, dataset in analyses:
            results = self.session.execute(
                select(StatisticalResult, DatasetVariable)
                .outerjoin(DatasetVariable, DatasetVariable.id == StatisticalResult.variable_id)
                .where(StatisticalResult.analysis_id == analysis.id)
                .order_by(StatisticalResult.id)
            ).all()
            variable = next((row[1] for row in results if row[1] is not None), None)
            observation_count = self.session.scalar(
                select(func.count(Observation.id)).where(Observation.dataset_id == dataset.id)
            )
            item = self._execution(
                dataset,
                variable,
                analysis,
                int(observation_count or 0),
                [row[0] for row in results],
            )
            item.update(status=analysis.status, parameters=analysis.parameters)
            items.append(item)
        return items, int(total or 0)

    def _create_dataset(self, name: str, source_type: str, filters: dict[str, Any]) -> Dataset:
        dataset = Dataset(
            company_id=self.company_id,
            created_by_user_id=self.user_id,
            name=name,
            description="Dataset generado por el motor estadistico de SalesIA.",
            source_type=source_type,
            filters=filters,
            period_start=None,
            period_end=None,
        )
        self.session.add(dataset)
        self.session.flush()
        return dataset

    def _create_series_dataset(
        self,
        *,
        name: str,
        source_type: str,
        variable_name: str,
        variable_label: str,
        variable_type: str,
        unit: str | None,
        values: list[Decimal],
        source_ids: list[str] | None,
        observed_at: list[datetime] | None,
        filters: dict[str, Any],
    ) -> tuple[Dataset, DatasetVariable]:
        dataset = self._create_dataset(name, source_type, filters)
        variable = DatasetVariable(
            dataset_id=dataset.id,
            name=variable_name,
            label=variable_label,
            variable_type=variable_type,
            data_type="integer" if variable_type == "quantitative_discrete" else "decimal",
            source_field=variable_name if source_type == "sales_snapshot" else None,
            unit=unit,
        )
        self.session.add(variable)
        self.session.flush()
        self.session.add_all(
            [
                Observation(
                    dataset_id=dataset.id,
                    variable_id=variable.id,
                    source_record_id=source_ids[index] if source_ids else None,
                    ordinal=index + 1,
                    value_numeric=value,
                    value_text=None,
                    observed_at=observed_at[index] if observed_at else None,
                )
                for index, value in enumerate(values)
            ]
        )
        return dataset, variable

    def _complete_series_analysis(
        self,
        dataset: Dataset,
        variable: DatasetVariable,
        values: list[Decimal],
        analysis_type: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        analysis = self._create_analysis(dataset.id, analysis_type, parameters)
        results: list[StatisticalResult] = []
        if analysis_type == "mean":
            results.append(self._result(analysis.id, variable.id, "mean", arithmetic_mean(values)))
        elif analysis_type == "median":
            results.append(self._result(analysis.id, variable.id, "median", median(values)))
        else:
            comparison = compare_mean_median(values)
            results.extend(
                [
                    self._result(analysis.id, variable.id, "mean", comparison.mean),
                    self._result(analysis.id, variable.id, "median", comparison.median),
                    self._result(analysis.id, variable.id, "difference", comparison.difference),
                    self._result(
                        analysis.id,
                        variable.id,
                        "interpretation",
                        None,
                        text_value=comparison.relation,
                    ),
                ]
            )
        results.append(self._result(analysis.id, variable.id, "sample_size", len(values)))
        self._finish(analysis)
        return self._execution(dataset, variable, analysis, len(values), results)

    def _create_analysis(
        self, dataset_id: int, analysis_type: str, parameters: dict[str, Any]
    ) -> StatisticalAnalysis:
        analysis = StatisticalAnalysis(
            company_id=self.company_id,
            dataset_id=dataset_id,
            requested_by_user_id=self.user_id,
            analysis_type=analysis_type,
            status="pending",
            parameters=parameters,
            error_message=None,
        )
        self.session.add(analysis)
        self.session.flush()
        return analysis

    def _result(
        self,
        analysis_id: int,
        variable_id: int | None,
        metric: str,
        numeric_value: Decimal | int | None,
        *,
        text_value: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> StatisticalResult:
        result = StatisticalResult(
            analysis_id=analysis_id,
            variable_id=variable_id,
            metric=metric,
            numeric_value=Decimal(numeric_value) if numeric_value is not None else None,
            text_value=text_value,
            details=details or {},
        )
        self.session.add(result)
        return result

    def _finish(self, analysis: StatisticalAnalysis) -> None:
        analysis.status = "completed"
        analysis.completed_at = datetime.now(UTC)
        self.session.flush()

    @staticmethod
    def _execution(
        dataset: Dataset,
        variable: DatasetVariable | None,
        analysis: StatisticalAnalysis,
        observation_count: int,
        results: list[StatisticalResult],
    ) -> dict[str, Any]:
        return {
            "analysis_id": analysis.id,
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "analysis_type": analysis.analysis_type,
            "variable_name": variable.name if variable else None,
            "variable_label": variable.label if variable else None,
            "variable_type": variable.variable_type if variable else None,
            "observation_count": observation_count,
            "results": [
                {
                    "metric": result.metric,
                    "numeric_value": result.numeric_value,
                    "text_value": result.text_value,
                    "details": result.details,
                }
                for result in results
            ],
            "created_at": analysis.created_at,
            "completed_at": analysis.completed_at,
        }
