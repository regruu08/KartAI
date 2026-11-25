"""Incentive Quote API Endpoints for ReturnZero AI.

Provides closed-form dynamic incentive solver ensuring margin-safe prepaid nudges.
Reference: ADR-002, ADR-014, AGENTS.md §5 (E2, E14) & §7.
"""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter

from app.domain.incentive import calculate_incentive_quote
from app.schemas.api_contracts import (
    IncentiveQuoteRequest,
    IncentiveQuoteResponse,
)

router = APIRouter()


@router.post(
    "/quote",
    response_model=IncentiveQuoteResponse,
    summary="Calculate margin-safe prepaid incentive quote",
    description="Calculates D_max discount from avoided RTO loss and validates margin floor. COD is guaranteed.",
    tags=["Incentive"],
)
async def get_incentive_quote(request: IncentiveQuoteRequest) -> IncentiveQuoteResponse:
    """Calculate closed-form margin-safe incentive quote."""
    # Request accepts percentage points (e.g. 1.5 for 1.5%); domain solver uses decimal (0.015)
    fee_decimal = request.upi_gateway_fee_pct / Decimal("100")
    result = calculate_incentive_quote(
        cart_total_inr=request.cart_total_inr,
        risk_score_index=request.risk_score_index,
        current_payment=request.current_payment,
        has_used_fit_twin=request.has_used_fit_twin,
        applied_coupon_discount_inr=request.applied_coupon_discount_inr,
        doorstep_refusal_count=request.doorstep_refusal_count,
        upi_gateway_fee_pct=fee_decimal,
    )
    return IncentiveQuoteResponse(
        eligible_for_incentive=result.eligible_for_incentive,
        recommended_discount_inr=result.recommended_discount_inr,
        expected_avoided_loss_inr=result.expected_avoided_loss_inr,
        expected_savings_inr=result.expected_savings_inr,
        headroom_inr=result.headroom_inr,
        reason_code=result.reason_code,
        nudge_copy=result.nudge_copy,
        cod_remains_available=True,
    )
