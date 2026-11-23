"""Decimal monetary arithmetic utilities for ReturnZero AI.

Enforces strict Decimal precision for all financial calculations in compliance with
AGENTS.md §6.2 and ADR-002. Float arithmetic on currency is strictly forbidden.
"""

from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal

# Canonical currency step for Indian retail checkout incentives (ADR-002)
DEFAULT_STEP: Decimal = Decimal("5.00")
ZERO_CURRENCY: Decimal = Decimal("0.00")
CURRENCY_QUANTIZATION: Decimal = Decimal("0.01")


def to_decimal(value: Decimal | int | str) -> Decimal:
    """Convert an int, str, or Decimal to a Decimal.

    Rejects floats explicitly to prevent floating point inaccuracies in monetary math.
    """
    if isinstance(value, float):
        raise TypeError(
            "Float arithmetic on currency is strictly forbidden. "
            "Pass amounts as str, int, or Decimal."
        )
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        return Decimal(str(value))
    raise TypeError(f"Unsupported monetary type: {type(value).__name__}")


def quantize_currency(amount: Decimal) -> Decimal:
    """Quantize decimal amount to 2 decimal places using standard commercial rounding."""
    return amount.quantize(CURRENCY_QUANTIZATION, rounding=ROUND_HALF_UP)


def format_currency(amount: Decimal, include_symbol: bool = False) -> str:
    """Format decimal amount as a 2-decimal string (e.g. '1899.00' or '₹1,899.00')."""
    quantized = quantize_currency(amount)
    if not include_symbol:
        return f"{quantized:.2f}"

    # Format with Indian grouping if symbol requested
    sign = "-" if quantized < 0 else ""
    abs_amt = abs(quantized)
    parts = f"{abs_amt:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while remaining:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        groups.reverse()
        formatted_int = ",".join(groups) + "," + last_three
    else:
        formatted_int = integer_part

    return f"{sign}₹{formatted_int}.{decimal_part}"


def floor_to_step(amount: Decimal, step: Decimal = DEFAULT_STEP) -> Decimal:
    """Floor an amount to the nearest step (e.g. floor to ₹5.00 per ADR-002).

    Guarantees that offer discretization never rounds up past merchant margin headroom.
    """
    if step <= Decimal("0.00"):
        raise ValueError("Rounding step must be strictly positive.")
    multiplier = (amount / step).quantize(Decimal("1"), rounding=ROUND_FLOOR)
    return quantize_currency(multiplier * step)


def percentage_of(amount: Decimal, percentage: Decimal) -> Decimal:
    """Calculate percentage of an amount (e.g. 0.20 * 1899.00)."""
    return quantize_currency(amount * percentage)


def safe_add(*amounts: Decimal) -> Decimal:
    """Safely sum multiple Decimal amounts."""
    total = ZERO_CURRENCY
    for a in amounts:
        total += a
    return quantize_currency(total)


def safe_sub(minuend: Decimal, *subtrahends: Decimal) -> Decimal:
    """Safely subtract multiple Decimal amounts from minuend."""
    result = minuend
    for s in subtrahends:
        result -= s
    return quantize_currency(result)
