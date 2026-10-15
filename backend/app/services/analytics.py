"""Phase 09 statistical services with persistent, company-scoped analyses."""

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import exists, func, select
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
from app.models.company import Company
from app.models.customer import Customer
from app.models.orders import Order
from app.models.sales import Payment, Sale, SaleDetail
from app.schemas.statistics import (
    AutomaticBayesRequest,
    AutomaticEventProbabilityRequest,
    BayesRequest,
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

    def analyze_series(self, payload: NumericSeriesRequest, analysis_type: str) -> dict[str, Any]:
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
                Sale.created_at < datetime.combine(payload.date_to + timedelta(days=1), time.min)
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

    def analyze_automatic_event_probability(
        self, payload: AutomaticEventProbabilityRequest
    ) -> dict[str, Any]:
        period_filters: list[Any] = []
        event_name: str
        variable_name: str
        source_field: str

        if payload.event_type == "order_conversion":
            event_name = "Pedido convertido en venta"
            variable_name = "order_converted"
            source_field = "orders.status"
            period_filters = [Order.company_id == self.company_id, Order.status != "draft"]
            if payload.date_from:
                period_filters.append(
                    Order.created_at >= datetime.combine(payload.date_from, time.min)
                )
            if payload.date_to:
                period_filters.append(
                    Order.created_at
                    < datetime.combine(payload.date_to + timedelta(days=1), time.min)
                )
            rows = self.session.execute(
                select(Order.id, Order.created_at, Order.status)
                .where(*period_filters)
                .order_by(Order.created_at, Order.id)
            ).all()
            favorable = [row.status == "converted" for row in rows]
        elif payload.event_type == "fully_paid_sale":
            event_name = "Venta pagada completamente"
            variable_name = "sale_fully_paid"
            source_field = "sales.payment_status"
            period_filters = [Sale.company_id == self.company_id, Sale.status == "confirmed"]
            if payload.date_from:
                period_filters.append(
                    Sale.created_at >= datetime.combine(payload.date_from, time.min)
                )
            if payload.date_to:
                period_filters.append(
                    Sale.created_at
                    < datetime.combine(payload.date_to + timedelta(days=1), time.min)
                )
            rows = self.session.execute(
                select(Sale.id, Sale.created_at, Sale.payment_status)
                .where(*period_filters)
                .order_by(Sale.created_at, Sale.id)
            ).all()
            favorable = [row.payment_status == "paid" for row in rows]
        else:
            event_name = "Pago realizado con tarjeta"
            variable_name = "card_payment"
            source_field = "payments.method"
            period_filters = [
                Sale.company_id == self.company_id,
                Payment.status == "completed",
            ]
            if payload.date_from:
                period_filters.append(
                    Payment.paid_at >= datetime.combine(payload.date_from, time.min)
                )
            if payload.date_to:
                period_filters.append(
                    Payment.paid_at
                    < datetime.combine(payload.date_to + timedelta(days=1), time.min)
                )
            rows = self.session.execute(
                select(Payment.id, Payment.paid_at.label("created_at"), Payment.method)
                .join(Sale, Sale.id == Payment.sale_id)
                .where(*period_filters)
                .order_by(Payment.paid_at, Payment.id)
            ).all()
            favorable = [row.method == "card" for row in rows]

        if not rows:
            raise AppError(
                "ANALYTICS_NO_OBSERVATIONS",
                "No hay observaciones reales en el periodo seleccionado",
                status_code=409,
            )

        values = [Decimal(1 if matches else 0) for matches in favorable]
        total_observations = len(values)
        favorable_cases = sum(favorable)
        probability = event_probability(favorable_cases, total_observations)
        date_label = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        filters = {
            "event_type": payload.event_type,
            "event_name": event_name,
            "date_from": payload.date_from.isoformat() if payload.date_from else None,
            "date_to": payload.date_to.isoformat() if payload.date_to else None,
        }
        dataset, variable = self._create_series_dataset(
            name=f"Probabilidad automatica - {event_name} - {date_label}",
            source_type="sales_snapshot",
            variable_name=variable_name,
            variable_label=event_name,
            variable_type="quantitative_discrete",
            unit="casos",
            values=values,
            source_ids=[str(row.id) for row in rows],
            observed_at=[row.created_at for row in rows],
            filters=filters,
        )
        dataset.period_start = payload.date_from
        dataset.period_end = payload.date_to
        variable.source_field = source_field
        analysis = self._create_analysis(
            dataset.id,
            "frequency",
            {**filters, "source": "salesia"},
        )
        results = [
            self._result(analysis.id, variable.id, "favorable_cases", favorable_cases),
            self._result(analysis.id, variable.id, "total_observations", total_observations),
            self._result(analysis.id, variable.id, "probability", probability),
            self._result(
                analysis.id,
                variable.id,
                "interpretation",
                None,
                text_value=(
                    f"{favorable_cases} de {total_observations} observaciones cumplieron "
                    f"el evento {event_name.lower()}."
                ),
            ),
        ]
        self._finish(analysis)
        return self._execution(dataset, variable, analysis, total_observations, results)

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

    def analyze_automatic_bayes(self, payload: AutomaticBayesRequest) -> dict[str, Any]:
        timezone = self._company_timezone()
        start_date, end_date = self._automatic_bayes_period(
            payload.date_from, payload.date_to, timezone
        )
        start_at = datetime.combine(start_date, time.min, tzinfo=timezone).astimezone(UTC)
        end_at = datetime.combine(
            end_date + timedelta(days=1), time.min, tzinfo=timezone
        ).astimezone(UTC)

        prior_purchase = exists().where(
            Sale.company_id == self.company_id,
            Sale.customer_id == Customer.id,
            Sale.status == "confirmed",
            Sale.payment_status != "refunded",
            Sale.created_at < start_at,
        )
        period_purchase = exists().where(
            Sale.company_id == self.company_id,
            Sale.customer_id == Customer.id,
            Sale.status == "confirmed",
            Sale.payment_status != "refunded",
            Sale.created_at >= start_at,
            Sale.created_at < end_at,
        )
        customer_rows = self.session.execute(
            select(
                Customer.id,
                Customer.created_at,
                prior_purchase.label("event_a"),
                period_purchase.label("event_b"),
            )
            .where(
                Customer.company_id == self.company_id,
                Customer.created_at < end_at,
            )
            .order_by(Customer.id)
        ).all()
        if not customer_rows:
            raise AppError(
                "BAYES_NO_CUSTOMERS",
                "No hay clientes registrados para el periodo seleccionado",
                status_code=409,
            )

        prior_customer_ids = {row.id for row in customer_rows if row.event_a}
        if not prior_customer_ids:
            raise AppError(
                "BAYES_NO_PRIOR_CUSTOMERS",
                "No hay clientes con compras anteriores al periodo seleccionado",
                status_code=409,
            )

        period_customer_ids = {row.id for row in customer_rows if row.event_b}
        if not period_customer_ids:
            raise AppError(
                "BAYES_NO_PERIOD_PURCHASES",
                "No hay clientes con compras en el periodo seleccionado",
                status_code=409,
            )

        intersection_ids = prior_customer_ids & period_customer_ids
        universe_size = len(customer_rows)
        event_a_cases = len(prior_customer_ids)
        event_b_cases = len(period_customer_ids)
        intersection_cases = len(intersection_ids)
        probability_a = event_probability(event_a_cases, universe_size)
        probability_b_given_a = event_probability(intersection_cases, event_a_cases)
        probability_b = event_probability(event_b_cases, universe_size)
        # For empirical counts, Bayes reduces exactly to |A ∩ B| / |B|.
        # Deriving it from independently rounded probabilities can push a valid
        # result slightly above 1 (for example, 2/3 × 1/2 ÷ 1/3).
        posterior = event_probability(intersection_cases, event_b_cases)

        event_a = "Cliente con compra anterior al periodo"
        event_b = "Cliente con compra en el periodo"
        timezone_name = timezone.key
        filters = {
            "scenario_type": payload.scenario_type,
            "date_from": start_date.isoformat(),
            "date_to": end_date.isoformat(),
            "timezone": timezone_name,
            "date_defaults": {
                "date_from": payload.date_from is None,
                "date_to": payload.date_to is None,
            },
            "universe_definition": (
                "Clientes de la empresa registrados antes del cierre del periodo"
            ),
            "sale_definition": "Ventas confirmadas y no reembolsadas",
            "universe_size": universe_size,
            "event_a_cases": event_a_cases,
            "event_b_cases": event_b_cases,
            "intersection_cases": intersection_cases,
        }
        date_label = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        dataset = self._create_dataset(
            f"Bayes automático - Recompra de clientes - {date_label}",
            "sales_snapshot",
            filters,
        )
        dataset.period_start = start_date
        dataset.period_end = end_date
        membership_variable = DatasetVariable(
            dataset_id=dataset.id,
            name="customer_bayes_membership",
            label="Pertenencia a eventos A y B",
            variable_type="qualitative",
            data_type="text",
            source_field="customers.id + sales.created_at",
            unit=None,
        )
        self.session.add(membership_variable)
        self.session.flush()
        self.session.add_all(
            [
                Observation(
                    dataset_id=dataset.id,
                    variable_id=membership_variable.id,
                    source_record_id=str(row.id),
                    ordinal=index,
                    value_numeric=None,
                    value_text=(
                        f"A={int(row.id in prior_customer_ids)};"
                        f"B={int(row.id in period_customer_ids)}"
                    ),
                    observed_at=row.created_at,
                )
                for index, row in enumerate(customer_rows, start=1)
            ]
        )

        parameters = {
            **filters,
            "source": "salesia",
            "event_a": event_a,
            "event_b": event_b,
            "probability_a": str(probability_a),
            "probability_b_given_a": str(probability_b_given_a),
            "probability_b": str(probability_b),
        }
        analysis = self._create_analysis(dataset.id, "bayes", parameters)
        self.session.add(
            BayesAnalysis(
                analysis_id=analysis.id,
                event_a=event_a,
                event_b=event_b,
                probability_a=probability_a,
                probability_b_given_a=probability_b_given_a,
                probability_b=probability_b,
                posterior=posterior,
            )
        )
        interpretation = (
            f"De {event_b_cases} clientes que compraron entre {start_date.isoformat()} "
            f"y {end_date.isoformat()}, {intersection_cases} ya habían comprado antes; "
            f"la probabilidad de que un comprador del periodo sea recurrente es "
            f"{(posterior * Decimal('100')).quantize(Decimal('0.01'))}%."
        )
        results = [
            self._result(analysis.id, membership_variable.id, "posterior", posterior),
            self._result(
                analysis.id, membership_variable.id, "probability_a", probability_a
            ),
            self._result(
                analysis.id,
                membership_variable.id,
                "probability_b_given_a",
                probability_b_given_a,
            ),
            self._result(analysis.id, membership_variable.id, "probability_b", probability_b),
            self._result(
                analysis.id, membership_variable.id, "universe_size", universe_size
            ),
            self._result(
                analysis.id, membership_variable.id, "event_a_cases", event_a_cases
            ),
            self._result(
                analysis.id, membership_variable.id, "event_b_cases", event_b_cases
            ),
            self._result(
                analysis.id,
                membership_variable.id,
                "intersection_cases",
                intersection_cases,
            ),
            self._result(
                analysis.id,
                membership_variable.id,
                "interpretation",
                None,
                text_value=interpretation,
                details={
                    "scenario_type": payload.scenario_type,
                    "date_from": start_date.isoformat(),
                    "date_to": end_date.isoformat(),
                    "timezone": timezone_name,
                },
            ),
        ]
        self._finish(analysis)
        return self._execution(
            dataset,
            membership_variable,
            analysis,
            universe_size,
            results,
        )

    def _company_timezone(self) -> ZoneInfo:
        company = self.session.scalar(select(Company).where(Company.id == self.company_id))
        if company is None:
            raise AppError("COMPANY_NOT_FOUND", "La empresa no existe", status_code=404)
        try:
            return ZoneInfo(company.timezone)
        except ZoneInfoNotFoundError:
            return ZoneInfo("America/Lima")

    @staticmethod
    def _automatic_bayes_period(
        date_from: date | None, date_to: date | None, timezone: ZoneInfo
    ) -> tuple[date, date]:
        end_date = date_to or datetime.now(timezone).date()
        start_date = date_from or end_date.replace(day=1)
        if end_date == date.max:
            raise AppError(
                "INVALID_BAYES_PERIOD",
                "La fecha final debe ser anterior al 31/12/9999",
                status_code=422,
            )
        if end_date < start_date:
            raise AppError(
                "INVALID_BAYES_PERIOD",
                "La fecha final no puede ser anterior a la fecha inicial",
                status_code=422,
            )
        return start_date, end_date

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
