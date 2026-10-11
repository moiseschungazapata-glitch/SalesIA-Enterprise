"""Commercial pricing rules."""

from decimal import Decimal

import pytest

from app.core.exceptions import AppError
from app.services.pricing import calculate_pricing


def test_included_igv_and_sequential_discounts() -> None:
    result = calculate_pricing(
        [(1, Decimal("150"), 2, Decimal("10"))],
        tax_rate=Decimal("18"),
        prices_include_tax=True,
        max_discount_percent=Decimal("30"),
        general_discount_percent=Decimal("5"),
    )
    assert result.lines[0].gross_subtotal == Decimal("300.00")
    assert result.discount_total == Decimal("43.50")
    assert result.subtotal == Decimal("217.37")
    assert result.tax_total == Decimal("39.13")
    assert result.total == Decimal("256.50")


def test_igv_is_added_when_catalog_prices_exclude_tax() -> None:
    result = calculate_pricing(
        [(1, Decimal("100"), 1, Decimal("0"))],
        tax_rate=Decimal("18"),
        prices_include_tax=False,
        max_discount_percent=Decimal("30"),
        general_discount_percent=Decimal("0"),
    )
    assert result.subtotal == Decimal("100.00")
    assert result.tax_total == Decimal("18.00")
    assert result.total == Decimal("118.00")


def test_discount_limit_is_enforced() -> None:
    with pytest.raises(AppError) as error:
        calculate_pricing(
            [(1, Decimal("100"), 1, Decimal("31"))],
            tax_rate=Decimal("18"),
            prices_include_tax=True,
            max_discount_percent=Decimal("30"),
            general_discount_percent=Decimal("0"),
        )
    assert error.value.code == "DISCOUNT_LIMIT_EXCEEDED"
