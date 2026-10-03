"""Unit tests for the deterministic phase 09 statistical engine."""

from decimal import Decimal

import pytest

from app.statistics.engine import (
    arithmetic_mean,
    bayes_posterior,
    compare_mean_median,
    discrete_distribution,
    event_probability,
    median,
)


def test_mean_and_median_support_odd_and_even_series() -> None:
    assert arithmetic_mean([Decimal("10"), Decimal("20"), Decimal("30")]) == Decimal(
        "20.000000"
    )
    assert median([Decimal("9"), Decimal("1"), Decimal("5")]) == Decimal("5.000000")
    assert median([Decimal("1"), Decimal("3"), Decimal("7"), Decimal("9")]) == Decimal(
        "5.000000"
    )


def test_comparison_explains_outlier_effect() -> None:
    result = compare_mean_median([Decimal("1"), Decimal("2"), Decimal("100")])

    assert result.mean == Decimal("34.333333")
    assert result.median == Decimal("2.000000")
    assert result.difference == Decimal("32.333333")
    assert "valores altos" in result.relation


def test_probability_bayes_and_discrete_distribution() -> None:
    assert event_probability(7, 10) == Decimal("0.7000000")
    assert bayes_posterior(Decimal("0.4"), Decimal("0.75"), Decimal("0.5")) == Decimal(
        "0.6000000"
    )
    assert discrete_distribution([Decimal("1"), Decimal("1"), Decimal("2")]) == [
        {"value": "1", "frequency": 2, "probability": "0.6666667"},
        {"value": "2", "frequency": 1, "probability": "0.3333333"},
    ]


def test_empty_or_inconsistent_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        arithmetic_mean([])
    with pytest.raises(ValueError):
        event_probability(11, 10)
    with pytest.raises(ValueError):
        bayes_posterior(Decimal("0.9"), Decimal("0.9"), Decimal("0.2"))
