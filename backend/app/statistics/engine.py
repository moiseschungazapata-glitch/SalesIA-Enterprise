"""Deterministic statistical calculations used by the phase 09 services."""

from collections import Counter
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

SIX_DECIMALS = Decimal("0.000001")
SEVEN_DECIMALS = Decimal("0.0000001")


def _rounded(value: Decimal, precision: Decimal = SIX_DECIMALS) -> Decimal:
    return value.quantize(precision, rounding=ROUND_HALF_UP)


def arithmetic_mean(values: list[Decimal]) -> Decimal:
    if not values:
        raise ValueError("Se necesita al menos una observacion")
    return _rounded(sum(values, start=Decimal("0")) / Decimal(len(values)))


def median(values: list[Decimal]) -> Decimal:
    if not values:
        raise ValueError("Se necesita al menos una observacion")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return _rounded(ordered[middle])
    return _rounded((ordered[middle - 1] + ordered[middle]) / Decimal("2"))


@dataclass(frozen=True)
class Comparison:
    mean: Decimal
    median: Decimal
    difference: Decimal
    relation: str


def compare_mean_median(values: list[Decimal]) -> Comparison:
    mean_value = arithmetic_mean(values)
    median_value = median(values)
    difference = _rounded(mean_value - median_value)
    if difference > 0:
        relation = "La media es mayor que la mediana; los valores altos elevan el promedio."
    elif difference < 0:
        relation = "La media es menor que la mediana; los valores bajos reducen el promedio."
    else:
        relation = "La media y la mediana coinciden en este conjunto de datos."
    return Comparison(mean_value, median_value, difference, relation)


def event_probability(favorable_cases: int, total_observations: int) -> Decimal:
    if total_observations <= 0:
        raise ValueError("El total de observaciones debe ser mayor que cero")
    if favorable_cases < 0 or favorable_cases > total_observations:
        raise ValueError("Los casos favorables deben estar entre cero y el total")
    return _rounded(Decimal(favorable_cases) / Decimal(total_observations), SEVEN_DECIMALS)


def bayes_posterior(
    probability_a: Decimal,
    probability_b_given_a: Decimal,
    probability_b: Decimal,
) -> Decimal:
    if probability_b <= 0:
        raise ValueError("P(B) debe ser mayor que cero")
    posterior = (probability_b_given_a * probability_a) / probability_b
    if posterior < 0 or posterior > 1:
        raise ValueError(
            "Las probabilidades son inconsistentes: el resultado de Bayes queda fuera de 0 y 1"
        )
    return _rounded(posterior, SEVEN_DECIMALS)


def discrete_distribution(values: list[Decimal]) -> list[dict[str, int | str]]:
    if not values:
        raise ValueError("Se necesita al menos una observacion")
    frequencies = Counter(values)
    total = Decimal(len(values))
    return [
        {
            "value": str(value),
            "frequency": frequency,
            "probability": str(_rounded(Decimal(frequency) / total, SEVEN_DECIMALS)),
        }
        for value, frequency in sorted(frequencies.items())
    ]
