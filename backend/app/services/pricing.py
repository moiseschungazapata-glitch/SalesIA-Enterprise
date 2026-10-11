"""Single source of truth for taxes and commercial discounts."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.core.exceptions import AppError

CENT = Decimal("0.01")
HUNDRED = Decimal("100")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PricedLine:
    product_id: int
    gross_subtotal: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    subtotal: Decimal


@dataclass(frozen=True)
class PricingSummary:
    lines: list[PricedLine]
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total: Decimal


def calculate_pricing(
    lines: list[tuple[int, Decimal, int, Decimal]],
    *,
    tax_rate: Decimal,
    prices_include_tax: bool,
    max_discount_percent: Decimal,
    general_discount_percent: Decimal,
) -> PricingSummary:
    percentages = [general_discount_percent, *(line[3] for line in lines)]
    if any(value < 0 or value > max_discount_percent for value in percentages):
        raise AppError(
            "DISCOUNT_LIMIT_EXCEEDED",
            f"El descuento máximo permitido es {max_discount_percent}%",
            status_code=422,
            details={"max_discount_percent": str(max_discount_percent)},
        )

    priced: list[PricedLine] = []
    item_discount_total = Decimal("0")
    net_lines_total = Decimal("0")
    for product_id, unit_price, quantity, discount_percent in lines:
        gross = money(unit_price * quantity)
        discount = money(gross * discount_percent / HUNDRED)
        net = money(gross - discount)
        priced.append(PricedLine(product_id, gross, discount_percent, discount, net))
        item_discount_total += discount
        net_lines_total += net

    general_discount = money(net_lines_total * general_discount_percent / HUNDRED)
    discounted_total = money(net_lines_total - general_discount)
    if discounted_total <= 0:
        raise AppError("INVALID_TOTAL", "El total debe ser mayor que cero", status_code=422)

    if prices_include_tax:
        divisor = Decimal("1") + tax_rate / HUNDRED
        subtotal = money(discounted_total / divisor) if divisor else discounted_total
        tax_total = money(discounted_total - subtotal)
        total = discounted_total
    else:
        subtotal = discounted_total
        tax_total = money(subtotal * tax_rate / HUNDRED)
        total = money(subtotal + tax_total)

    return PricingSummary(
        lines=priced,
        subtotal=subtotal,
        discount_total=money(item_discount_total + general_discount),
        tax_total=tax_total,
        total=total,
    )
