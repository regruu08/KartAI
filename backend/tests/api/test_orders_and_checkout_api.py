"""API integration tests for Fit sizing, Risk evaluation, Incentive quote, and Orders.

Tests all Phase 4 and Phase 5 endpoints per ADR-002, ADR-003, ADR-004, ADR-015, and AGENTS.md §6.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_fit_recommend_endpoint(async_client: AsyncClient) -> None:
    """Test POST /v1/catalog/skus/SKU-01/fit returns deterministic sizing recommendation."""
    payload = {
        "known_brand": "Zara",
        "known_size": "M",
        "fit_preference": "tailored",
        "height_cm": 165.0,
    }
    response = await async_client.post("/v1/catalog/skus/SKU-01/fit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sku_id"] == "SKU-01"
    assert "recommended_size" in data
    assert data["confidence_level"] in ["High", "Medium", "Low (Insufficient Data)"]
    assert "fit_zone_breakdown" in data
    assert "bust" in data["fit_zone_breakdown"]


@pytest.mark.asyncio
async def test_fit_recommend_missing_sku_returns_404(async_client: AsyncClient) -> None:
    """Test POST /v1/catalog/skus/SKU-INVALID/fit returns 404."""
    payload = {
        "known_brand": "Zara",
        "known_size": "M",
        "fit_preference": "tailored",
    }
    response = await async_client.post("/v1/catalog/skus/NON-EXISTENT/fit", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_risk_evaluate_endpoint(async_client: AsyncClient) -> None:
    """Test POST /v1/risk/evaluate returns 3-point checklist and guaranteed COD."""
    payload = {
        "street_address": "Flat 402, Sunshine Apartments, Near Metro Pillar 120",
        "pin_code": "110001",
        "payment_method": "COD",
        "has_used_fit_twin": True,
        "is_bracketing": False,
    }
    response = await async_client.post("/v1/risk/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["risk_score_index"] <= 100
    assert data["risk_level"] in ["Low", "Review", "Elevated"]
    assert data["cod_remains_available"] is True
    assert len(data["checks"]) == 3
    check_ids = [c["id"] for c in data["checks"]]
    assert "address_quality" in check_ids
    assert "serviceable_pin" in check_ids
    assert "rto_risk" in check_ids


@pytest.mark.asyncio
async def test_incentive_quote_endpoint(async_client: AsyncClient) -> None:
    """Test POST /v1/incentive/quote returns margin-safe closed-form quote."""
    payload = {
        "cart_total_inr": "1899.00",
        "risk_score_index": 55,
        "current_payment": "COD",
        "has_used_fit_twin": True,
    }
    response = await async_client.post("/v1/incentive/quote", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["eligible_for_incentive"] is True
    assert float(data["recommended_discount_inr"]) > 0.0
    assert data["cod_remains_available"] is True
    assert "nudge_copy" in data


@pytest.mark.asyncio
async def test_order_creation_and_lifecycle(async_client: AsyncClient) -> None:
    """Test complete order creation, retrieval, landmark verification, and NDR reschedule."""
    # 1. Create order
    create_payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "Priya Sharma",
        "customer_phone": "9876543210",
        "street_address": "House 12, Sector 15",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "COD",
        "applied_discount_inr": "0.00",
        "has_used_fit_twin": True,
        "is_bracketing": False,
        "known_brand": "Zara",
        "known_size": "M",
    }
    create_res = await async_client.post("/v1/orders", json=create_payload)
    assert create_res.status_code == 201
    order = create_res.json()
    order_id = order["id"]
    assert order["customer_name"] == "Priya Sharma"
    assert order["order_status"] == "Placed"
    assert order["tier"] == "Tier-1"

    # 2. Get order by ID
    get_res = await async_client.get(f"/v1/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == order_id

    # 3. List orders
    list_res = await async_client.get("/v1/orders?limit=10")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 151

    # 4. WhatsApp simulator address verification
    verify_payload = {
        "landmark": "Near Community Center",
        "delivery_slot": "10 AM - 1 PM",
        "opt_in_whatsapp": True,
    }
    verify_res = await async_client.post(f"/v1/orders/{order_id}/verify", json=verify_payload)
    assert verify_res.status_code == 200
    updated = verify_res.json()
    assert updated["order_status"] == "Safe_For_Dispatch"
    assert updated["address_status"] == "Complete"
    assert "Community Center" in updated["street_address"]

    # 5. NDR Reschedule
    ndr_payload = {
        "reschedule_date": "2026-11-29",
        "reschedule_slot": "2 PM - 5 PM",
    }
    ndr_res = await async_client.post(f"/v1/orders/{order_id}/ndr", json=ndr_payload)
    assert ndr_res.status_code == 200
    assert ndr_res.json()["order_status"] == "Delivery_Rescheduled"


@pytest.mark.asyncio
async def test_verify_order_missing_landmark_when_needed_returns_422(
    async_client: AsyncClient,
) -> None:
    """Verify POST /v1/orders/{id}/verify returns 422 if address needs landmark but landmark is omitted."""
    create_payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "Rohan Gupta",
        "customer_phone": "9876543211",
        "street_address": "Flat 304, Green Glen Layout",  # Lacks landmark -> NeedsLandmark
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "COD",
        "applied_discount_inr": "0.00",
        "has_used_fit_twin": True,
        "is_bracketing": False,
        "known_brand": "Zara",
        "known_size": "M",
    }
    create_res = await async_client.post("/v1/orders", json=create_payload)
    assert create_res.status_code == 201
    order = create_res.json()
    order_id = order["id"]
    assert order["address_status"] == "NeedsLandmark"

    # Attempt verify without landmark
    verify_payload = {
        "delivery_slot": "10 AM - 1 PM",
        "opt_in_whatsapp": True,
    }
    verify_res = await async_client.post(f"/v1/orders/{order_id}/verify", json=verify_payload)
    assert verify_res.status_code == 422
    assert "landmark" in verify_res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_order_persists_clarified_landmark_in_delivery_event(
    async_client: AsyncClient,
) -> None:
    """Verify clarified landmark is persisted in DeliveryEventModel.clarified_landmark."""
    create_payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "Rohan Gupta",
        "customer_phone": "9876543211",
        "street_address": "Flat 304, Green Glen Layout",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "COD",
        "applied_discount_inr": "0.00",
        "has_used_fit_twin": True,
        "is_bracketing": False,
        "known_brand": "Zara",
        "known_size": "M",
    }
    create_res = await async_client.post("/v1/orders", json=create_payload)
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    exact_landmark = "Opposite Gate 3, City Mall"
    verify_payload = {
        "landmark": exact_landmark,
        "delivery_slot": "2 PM - 6 PM",
        "opt_in_whatsapp": True,
    }
    verify_res = await async_client.post(f"/v1/orders/{order_id}/verify", json=verify_payload)
    assert verify_res.status_code == 200
    assert exact_landmark in verify_res.json()["street_address"]
    assert verify_res.json()["address_status"] == "Complete"
