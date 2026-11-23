"""Risk Evaluation API Endpoints for ReturnZero AI.

Provides explainable operational risk scoring and 3-point order review checklist.
Reference: ADR-003, AGENTS.md §5 (E3), §6.2 & §7.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.domain.risk import evaluate_order_risk
from app.schemas.api_contracts import (
    OrderReviewCheckItem,
    RiskEvaluateRequest,
    RiskEvaluateResponse,
)

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=RiskEvaluateResponse,
    summary="Evaluate order operational risk and generate review checklist",
    description="Evaluates 0-100 risk score and 3-point checklist (address, PIN, RTO band). COD is guaranteed.",
    tags=["Risk"],
)
async def evaluate_risk(request: RiskEvaluateRequest) -> RiskEvaluateResponse:
    """Evaluate order risk index and 3-point checklist."""
    result = evaluate_order_risk(
        payment_method=request.payment_method,
        street_address=request.street_address,
        pin_code=request.pin_code,
        has_used_fit_twin=request.has_used_fit_twin,
        is_bracketing=request.is_bracketing,
    )
    checklist_items = [
        OrderReviewCheckItem(id=c.id, label=c.label, status=c.status) for c in result.checks
    ]
    return RiskEvaluateResponse(
        risk_score_index=result.risk_score_index,
        risk_level=result.risk_level,
        contributing_factors=result.contributing_factors,
        checks=checklist_items,
        cod_remains_available=True,
    )
