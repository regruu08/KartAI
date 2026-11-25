"""API tests for /v1/analytics overview and scenario modeler endpoints.

Verifies dynamic live database telemetry aggregations and exact mathematical parity
with pitch deck unit economics in scenario modeler per ADR-005, E5, and AGENTS.md §7.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analytics_overview_dynamic_telemetry(async_client: AsyncClient) -> None:
    """Verify GET /v1/analytics/overview aggregates dynamic metrics from seeded rows."""
    response = await async_client.get("/v1/analytics/overview")
    assert response.status_code == 200

    data = response.json()
    assert data["total_orders"] == 150
    assert data["cod_orders_count"] == 98
    assert data["prepaid_orders_count"] == 52
    assert round(data["cod_share_pct"], 1) == 65.3

    # RTO and customer return metrics are strictly separated (ADR-005)
    assert data["rto_count"] == 43
    assert round(data["rto_rate_pct"], 1) == 28.7
    assert data["customer_return_count"] == 12
    assert round(data["customer_return_rate_pct"], 1) == 8.0

    assert data["delivered_kept_count"] == 85
    assert data["converted_to_upi_count"] > 0
    assert float(data["estimated_direct_savings_inr"]) > 0.0

    # Geographical tier breakdown
    assert len(data["tier_breakdown"]) == 3
    tiers = {t["tier"]: t for t in data["tier_breakdown"]}
    assert "Tier-1" in tiers
    assert "Tier-2" in tiers
    assert "Tier-3" in tiers

    assert tiers["Tier-1"]["total_orders"] == 60
    assert tiers["Tier-1"]["rto_count"] == 11
    assert round(tiers["Tier-1"]["rto_rate_pct"], 1) == 18.3

    assert tiers["Tier-2"]["total_orders"] == 52
    assert tiers["Tier-2"]["rto_count"] == 16
    assert round(tiers["Tier-2"]["rto_rate_pct"], 1) == 30.8

    assert tiers["Tier-3"]["total_orders"] == 38
    assert tiers["Tier-3"]["rto_count"] == 16
    assert round(tiers["Tier-3"]["rto_rate_pct"], 1) == 42.1

    # SKU intelligence breakdown
    assert len(data["sku_breakdown"]) == 4
    sku_03 = next(s for s in data["sku_breakdown"] if s["sku_id"] == "SKU-03")
    assert sku_03["has_missing_measurements"] is True
    assert sku_03["alert_message"] == "Add sleeve length to improve fit confidence"

    # Binding attribution
    assert "modelled direct operating savings" in data["disclaimer"]


@pytest.mark.asyncio
async def test_analytics_scenario_deck_economic_parity(async_client: AsyncClient) -> None:
    """Verify GET /v1/analytics/scenario reproduces pitch deck figures with zero error."""
    response = await async_client.get("/v1/analytics/scenario")
    assert response.status_code == 200

    data = response.json()
    combined = data["combined_case"]
    conservative = data["conservative_conversion_only_case"]

    # Baseline 10,000 shipments
    assert combined["baseline_cod_shipments"] == 6500
    assert combined["baseline_prepaid_shipments"] == 3500
    assert combined["baseline_cod_rto_shipments"] == 1690
    assert combined["baseline_prepaid_rto_shipments"] == 70
    assert combined["baseline_total_rto_shipments"] == 1760

    # Combined Scenario (Conversion + 2pp residual COD improvement)
    assert combined["converted_shipments"] == 650
    assert combined["new_cod_shipments"] == 5850
    assert combined["new_prepaid_shipments"] == 4150
    assert combined["new_cod_rto_shipments"] == 1404
    assert combined["new_prepaid_rto_shipments"] == 83
    assert combined["new_total_rto_shipments"] == 1487
    assert combined["avoided_rto_shipments"] == 273
    assert float(combined["gross_avoided_loss_inr"]) == 54600.00
    assert float(combined["total_incentives_paid_inr"]) == 26000.00
    assert float(combined["net_operating_savings_monthly_inr"]) == 28600.00
    assert float(combined["net_operating_savings_annual_inr"]) == 343200.00

    # Conservative Scenario (Conversion-only case)
    assert conservative["avoided_rto_shipments"] == 156
    assert float(conservative["gross_avoided_loss_inr"]) == 31200.00
    assert float(conservative["total_incentives_paid_inr"]) == 26000.00
    assert float(conservative["net_operating_savings_monthly_inr"]) == 5200.00
    assert float(conservative["net_operating_savings_annual_inr"]) == 62400.00

    # Attribution
    assert "modelled direct operating savings" in data["disclaimer"]


@pytest.mark.asyncio
async def test_analytics_scenario_custom_overrides(async_client: AsyncClient) -> None:
    """Verify GET /v1/analytics/scenario with custom merchant parameters."""
    response = await async_client.get(
        "/v1/analytics/scenario?monthly_shipments=5000&cod_share_pct=70.0"
    )
    assert response.status_code == 200

    data = response.json()
    combined = data["combined_case"]
    assert combined["baseline_cod_shipments"] == 3500
    assert combined["baseline_prepaid_shipments"] == 1500


@pytest.mark.asyncio
async def test_analytics_scenario_gateway_fee_deduction(async_client: AsyncClient) -> None:
    """Verify GET /v1/analytics/scenario wires upi_gateway_fee_pct into fees & net savings."""
    response = await async_client.get("/v1/analytics/scenario?upi_gateway_fee_pct=1.5")
    assert response.status_code == 200

    combined = response.json()["combined_case"]
    assert float(combined["total_payment_fees_inr"]) == 18518.50
    assert float(combined["net_operating_savings_monthly_inr"]) == 10081.50
