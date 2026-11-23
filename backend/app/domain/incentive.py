"""Closed-form margin-safe dynamic incentive solver for ReturnZero AI.

Calculates the mathematically allowable cash discount to convert high-risk COD orders
to prepaid (UPI) while strictly preserving positive merchant gross margin headroom.
Incorporates anti-abuse coupon stacking caps and repeat doorstep refusal guardrails.
Reference: ADR-002, ADR-014, AGENTS.md §5 (E2, E14), §6.2 & §9.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from app.domain.money import (
    DEFAULT_STEP,
    ZERO_CURRENCY,
    floor_to_step,
    format_currency,
    quantize_currency,
    to_decimal,
)

# Standard benchmark constants (Shipway FY25 cohort benchmark & pitch deck defaults)
DEFAULT_COD_RTO_RATE: Final[Decimal] = Decimal("0.26")
DEFAULT_PREPAID_RTO_RATE: Final[Decimal] = Decimal("0.02")
DEFAULT_COST_PER_RTO: Final[Decimal] = Decimal("200.00")

# Merchant margin governance constants (ADR-002)
MARGIN_FLOOR: Final[Decimal] = Decimal("8.00")  # Minimum retained cash headroom
MINIMUM_OFFER: Final[Decimal] = Decimal("25.00")  # Lowest economically viable consumer discount
MAXIMUM_OFFER: Final[Decimal] = Decimal("40.00")  # Pitch deck ceiling for instant discount

# Anti-abuse governance constants (ADR-014)
MAX_COMBINED_DISCOUNT_PCT: Final[Decimal] = Decimal("0.20")  # 20% max GMV discount cap
MAX_DOORSTEP_REFUSALS_FOR_CASH: Final[int] = 3  # 3 refusals switches to non-cash gift

# Decision reason codes (ADR-014)
REASON_INSUFFICIENT_MARGIN: Final[str] = "REASON_INSUFFICIENT_MARGIN"
REASON_ELEVATED_RISK_CONVERTIBLE: Final[str] = "REASON_ELEVATED_RISK_CONVERTIBLE"
REASON_PREPAID_OPTIMAL: Final[str] = "REASON_PREPAID_OPTIMAL"
REASON_LOW_RISK: Final[str] = "REASON_LOW_RISK"
REASON_COUPON_CAP: Final[str] = "REASON_COUPON_CAP"
REASON_REPEAT_REFUSAL: Final[str] = "REASON_REPEAT_REFUSAL"

ReasonCode = Literal[
    "REASON_INSUFFICIENT_MARGIN",
    "REASON_ELEVATED_RISK_CONVERTIBLE",
    "REASON_PREPAID_OPTIMAL",
    "REASON_LOW_RISK",
    "REASON_COUPON_CAP",
    "REASON_REPEAT_REFUSAL",
]


@dataclass(frozen=True)
class IncentiveQuoteResult:
    eligible_for_incentive: bool
    recommended_discount_inr: Decimal
    expected_savings_inr: Decimal
    headroom_inr: Decimal
    reason_code: str
    nudge_copy: str
    cod_remains_available: bool = True  # Fairness mandate: COD never hard-blocked (ADR-002)


def calculate_incentive_quote(
    cart_total_inr: Decimal | int | str,
    risk_score_index: int,
    current_payment: str = "COD",
    has_used_fit_twin: bool = True,
    applied_coupon_discount_inr: Decimal | int | str = ZERO_CURRENCY,
    doorstep_refusal_count: int = 0,
    upi_gateway_fee_pct: Decimal | int | str = ZERO_CURRENCY,
    historical_cod_rto_rate: Decimal = DEFAULT_COD_RTO_RATE,
    historical_prepaid_rto_rate: Decimal = DEFAULT_PREPAID_RTO_RATE,
    direct_cost_per_rto: Decimal = DEFAULT_COST_PER_RTO,
    margin_floor: Decimal = MARGIN_FLOOR,
    min_offer: Decimal = MINIMUM_OFFER,
    max_offer: Decimal = MAXIMUM_OFFER,
) -> IncentiveQuoteResult:
    """Calculate margin-safe prepaid incentive quote using closed-form avoided loss equation.

    Equation:
      D_max = (P_COD - P_prepaid) * Cost_RTO - Fees - MarginFloor

    Pure domain function with zero side effects. Follows ADR-002, ADR-014, and AGENTS.md §6.2.
    """
    cart_total = to_decimal(cart_total_inr)
    coupon_discount = to_decimal(applied_coupon_discount_inr)
    fee_pct = to_decimal(upi_gateway_fee_pct)

    # 1. Guardrail: Prepaid orders do not require incentive nudges
    if current_payment.strip().upper() != "COD":
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_PREPAID_OPTIMAL,
            nudge_copy="Prepaid payment confirmed. Priority dispatch secured.",
            cod_remains_available=True,
        )

    # 2. Guardrail: Low-risk orders proceed with standard checkout
    if risk_score_index < 40:
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_LOW_RISK,
            nudge_copy="Standard checkout active.",
            cod_remains_available=True,
        )

    # 3. Anti-Abuse Guardrail: Repeat Doorstep Refusals (ADR-014)
    if doorstep_refusal_count >= MAX_DOORSTEP_REFUSALS_FOR_CASH:
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_REPEAT_REFUSAL,
            nudge_copy="Pay via UPI to receive a complimentary garment care kit + guaranteed express delivery.",
            cod_remains_available=True,
        )

    # 4. Anti-Abuse Guardrail: Coupon Stacking Cap <= 20% GMV (ADR-014)
    max_allowable_combined_discount = quantize_currency(cart_total * MAX_COMBINED_DISCOUNT_PCT)
    remaining_gmv_headroom = max_allowable_combined_discount - coupon_discount
    if remaining_gmv_headroom < min_offer:
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_COUPON_CAP,
            nudge_copy="Maximum promotional coupon discount applied to this order.",
            cod_remains_available=True,
        )

    # 5. Closed-Form Mathematical Optimization Equation (ADR-002)
    # Expected avoided loss = (0.26 - 0.02) * 200 = ₹48.00
    expected_avoided_loss = quantize_currency(
        (historical_cod_rto_rate - historical_prepaid_rto_rate) * direct_cost_per_rto
    )
    payment_fees = quantize_currency(cart_total * fee_pct)
    max_allowable_discount = expected_avoided_loss - payment_fees - margin_floor

    # Bound maximum allowable discount by remaining GMV coupon cap headroom
    if max_allowable_discount > remaining_gmv_headroom:
        max_allowable_discount = remaining_gmv_headroom

    # Check minimum economic viability floor
    if max_allowable_discount < min_offer:
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_INSUFFICIENT_MARGIN,
            nudge_copy="Standard checkout active.",
            cod_remains_available=True,
        )

    # 6. Offer Discretization with Strict Floor Rounding to ₹5 Step (ADR-002)
    floored_discount = floor_to_step(max_allowable_discount, DEFAULT_STEP)
    offered_discount = min(max_offer, floored_discount)

    if offered_discount < min_offer:
        return IncentiveQuoteResult(
            eligible_for_incentive=False,
            recommended_discount_inr=ZERO_CURRENCY,
            expected_savings_inr=ZERO_CURRENCY,
            headroom_inr=ZERO_CURRENCY,
            reason_code=REASON_INSUFFICIENT_MARGIN,
            nudge_copy="Standard checkout active.",
            cod_remains_available=True,
        )

    # Expected net direct operational savings retained after incentive and fees
    expected_savings = expected_avoided_loss - offered_discount - payment_fees
    # Headroom = amount above discount before hitting zero margin
    headroom = expected_avoided_loss - offered_discount - payment_fees

    # Construct persuasive customer nudge copy
    symbol_str = format_currency(offered_discount, include_symbol=True)
    if has_used_fit_twin:
        nudge = f"We verified your fit! Pay via UPI now to save {symbol_str} and secure priority dispatch."
    else:
        nudge = f"Switch to instant UPI now to save {symbol_str} and secure priority dispatch."

    return IncentiveQuoteResult(
        eligible_for_incentive=True,
        recommended_discount_inr=offered_discount,
        expected_savings_inr=expected_savings,
        headroom_inr=headroom,
        reason_code=REASON_ELEVATED_RISK_CONVERTIBLE,
        nudge_copy=nudge,
        cod_remains_available=True,
    )
