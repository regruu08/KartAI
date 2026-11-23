"""Unit tests for Decimal monetary utilities in app.domain.money.

Verifies strict Decimal precision, floor rounding to step, Indian currency formatting,
and explicit rejection of float arithmetic per AGENTS.md §6.2 and ADR-002.
"""

from decimal import Decimal

import pytest

from app.domain.money import (
    DEFAULT_STEP,
    ZERO_CURRENCY,
    floor_to_step,
    format_currency,
    percentage_of,
    quantize_currency,
    safe_add,
    safe_sub,
    to_decimal,
)


class TestToDecimal:
    """Tests conversion and strict float rejection."""

    def test_converts_int_to_decimal(self) -> None:
        assert to_decimal(1899) == Decimal("1899")

    def test_converts_str_to_decimal(self) -> None:
        assert to_decimal("1899.50") == Decimal("1899.50")

    def test_preserves_decimal_instance(self) -> None:
        d = Decimal("40.00")
        assert to_decimal(d) is d

    def test_strictly_rejects_float(self) -> None:
        with pytest.raises(TypeError, match="Float arithmetic on currency is strictly forbidden"):
            to_decimal(1899.0)  # type: ignore[arg-type]

    def test_rejects_unsupported_types(self) -> None:
        with pytest.raises(TypeError, match="Unsupported monetary type"):
            to_decimal(None)  # type: ignore[arg-type]


class TestQuantizeCurrency:
    """Tests commercial rounding to 2 decimal places."""

    def test_quantizes_to_two_places(self) -> None:
        assert quantize_currency(Decimal("40.005")) == Decimal("40.01")
        assert quantize_currency(Decimal("40.004")) == Decimal("40.00")
        assert quantize_currency(Decimal("0")) == Decimal("0.00")


class TestFormatCurrency:
    """Tests 2-decimal formatting with and without Indian grouping symbol."""

    def test_format_without_symbol(self) -> None:
        assert format_currency(Decimal("1899")) == "1899.00"
        assert format_currency(Decimal("40.5")) == "40.50"
        assert format_currency(ZERO_CURRENCY) == "0.00"

    def test_format_with_symbol_small_amount(self) -> None:
        assert format_currency(Decimal("40.00"), include_symbol=True) == "₹40.00"
        assert format_currency(Decimal("500.00"), include_symbol=True) == "₹500.00"

    def test_format_with_symbol_thousands_grouping(self) -> None:
        assert format_currency(Decimal("1899.00"), include_symbol=True) == "₹1,899.00"
        assert format_currency(Decimal("28600.00"), include_symbol=True) == "₹28,600.00"
        assert format_currency(Decimal("343200.00"), include_symbol=True) == "₹3,43,200.00"

    def test_format_with_symbol_negative_amount(self) -> None:
        assert format_currency(Decimal("-50.00"), include_symbol=True) == "-₹50.00"


class TestFloorToStep:
    """Tests strict floor rounding to step (ADR-002)."""

    def test_floor_to_five_rupee_step(self) -> None:
        # Standard ₹5 step tests
        assert floor_to_step(Decimal("40.00"), DEFAULT_STEP) == Decimal("40.00")
        assert floor_to_step(Decimal("44.99"), DEFAULT_STEP) == Decimal("40.00")
        assert floor_to_step(Decimal("45.00"), DEFAULT_STEP) == Decimal("45.00")
        assert floor_to_step(Decimal("48.00"), DEFAULT_STEP) == Decimal("45.00")
        assert floor_to_step(Decimal("24.99"), DEFAULT_STEP) == Decimal("20.00")
        assert floor_to_step(Decimal("11.51"), DEFAULT_STEP) == Decimal("10.00")

    def test_zero_or_negative_step_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Rounding step must be strictly positive"):
            floor_to_step(Decimal("40.00"), Decimal("0.00"))


class TestMonetaryOperations:
    """Tests percentage calculation, safe addition, and subtraction."""

    def test_percentage_of_gmv(self) -> None:
        assert percentage_of(Decimal("1899.00"), Decimal("0.20")) == Decimal("379.80")
        assert percentage_of(Decimal("1500.00"), Decimal("0.015")) == Decimal("22.50")

    def test_safe_add(self) -> None:
        assert safe_add(Decimal("10.50"), Decimal("20.25"), Decimal("5.25")) == Decimal("36.00")
        assert safe_add() == Decimal("0.00")

    def test_safe_sub(self) -> None:
        assert safe_sub(Decimal("100.00"), Decimal("40.00"), Decimal("8.00")) == Decimal("52.00")
