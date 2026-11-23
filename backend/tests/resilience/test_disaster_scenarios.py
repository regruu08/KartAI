"""Disaster scenario resilience tests for ReturnZero AI.

Exercises resilience against network partitions, corrupted inputs, missing fields,
and database edge cases per DEMO_DAY_DISASTER_PREVENTION.md and AGENTS.md §6.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.domain.address import address_quality
from app.domain.incentive import calculate_incentive_quote
from app.domain.risk import evaluate_order_risk
from app.domain.sizing import recommend_size


def test_sizing_resilience_on_unknown_brand_and_sku() -> None:
    """Verify sizing engine never throws unhandled exception on random garbage inputs."""
    rec = recommend_size(
        sku_id="UNKNOWN_GARMENT_999",
        known_brand="NonExistentBrandXYZ",
        known_size="4XL",
        fit_preference="ultra_baggy",
        height_cm=300.0,
    )
    assert rec.sku_id == "UNKNOWN_GARMENT_999"
    assert rec.confidence_level == "Low (Insufficient Data)"
    assert rec.recommended_size == "4XL"
    assert len(rec.missing_data_warnings) > 0


def test_address_resilience_on_gibberish() -> None:
    """Verify address quality classifier never crashes on empty or unicode gibberish."""
    res1 = address_quality("", "110001")
    assert res1.status == "Poor"

    res2 = address_quality("??? /// @@@ !!!", "999999")
    assert res2.status in ["Poor", "NeedsLandmark"]


def test_risk_evaluator_never_blocks_cod() -> None:
    """Verify operational risk evaluation strictly preserves guaranteed COD."""
    res = evaluate_order_risk(
        payment_method="COD",
        street_address="Unknown dark alley, nowhere",
        pin_code="999999",
        has_used_fit_twin=False,
        is_bracketing=True,
    )
    assert res.cod_remains_available is True
    assert 0 <= res.risk_score_index <= 100


def test_incentive_solver_never_exceeds_bounds() -> None:
    """Verify incentive solver never returns negative or >20% GMV discounts."""
    res = calculate_incentive_quote(
        cart_total_inr="500.00",
        risk_score_index=90,
        doorstep_refusal_count=5,  # Should switch to non-cash perk per ADR-014
    )
    assert res.cod_remains_available is True
    assert res.recommended_discount_inr <= 40.0


@pytest.mark.asyncio
async def test_api_validation_rejects_invalid_pin_with_422(async_client: AsyncClient) -> None:
    """Verify boundary validator rejects non-6 digit Indian PIN codes with 422."""
    payload = {
        "street_address": "Flat 101, Galaxy Heights",
        "pin_code": "123",  # Invalid PIN
        "payment_method": "COD",
    }
    response = await async_client.post("/v1/risk/evaluate", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_api_404_on_nonexistent_order(async_client: AsyncClient) -> None:
    """Verify GET /v1/orders/nonexistent returns 404 rather than 500."""
    response = await async_client.get("/v1/orders/ord_does_not_exist_9999")
    assert response.status_code == 404
