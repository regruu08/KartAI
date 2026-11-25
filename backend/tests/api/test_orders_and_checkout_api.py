"""API integration tests for Fit sizing, Risk evaluation, Incentive quote, and Orders.

Tests all Phase 4 and Phase 5 endpoints per ADR-002, ADR-003, ADR-004, ADR-015, and AGENTS.md §6.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.repositories import IncentiveRepository, SkuRepository
from app.main import create_app
from app.schemas.api_contracts import NormalizedAddressResult


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

    # Re-verify to ensure no duplicate landmark concatenation occurs (Bug 1 fix)
    verify_res_repeat = await async_client.post(
        f"/v1/orders/{order_id}/verify", json=verify_payload
    )
    assert verify_res_repeat.status_code == 200
    addr = verify_res_repeat.json()["street_address"]
    assert addr.count(exact_landmark) == 1
    assert "Near Near" not in addr


@pytest.mark.asyncio
async def test_order_creation_rejects_discount_exceeding_subtotal(
    async_client: AsyncClient,
) -> None:
    """Test POST /v1/orders rejects discount > subtotal with 422."""
    payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "Exploit Tester",
        "customer_phone": "9876543211",
        "street_address": "Flat 304, Green Glen Layout",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "COD",
        "applied_discount_inr": "50000.00",
    }
    res = await async_client.post("/v1/orders", json=payload)
    assert res.status_code == 422
    assert "cannot exceed order subtotal" in res.text

    # Reject any discount on COD orders
    cod_payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "COD Exploit Tester",
        "customer_phone": "9876543211",
        "street_address": "Flat 304, Green Glen Layout",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "COD",
        "applied_discount_inr": "25.00",
    }
    cod_res = await async_client.post("/v1/orders", json=cod_payload)
    assert cod_res.status_code == 422
    assert "Discounts cannot be applied to Cash on Delivery" in cod_res.text

    # Reject discount exceeding maximum incentive ceiling on Prepaid
    prepaid_payload = {
        "sku_id": "SKU-01",
        "size": "M",
        "quantity": 1,
        "customer_name": "Prepaid Exploit Tester",
        "customer_phone": "9876543211",
        "street_address": "Flat 304, Green Glen Layout",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "PREPAID",
        "applied_discount_inr": "500.00",
    }
    prepaid_res = await async_client.post("/v1/orders", json=prepaid_payload)
    assert prepaid_res.status_code == 422
    assert "exceeds maximum allowable incentive limit" in prepaid_res.text


@pytest.mark.asyncio
async def test_fit_recommend_rejects_empty_and_whitespace_size(async_client: AsyncClient) -> None:
    """Test POST /v1/fit/recommend rejects empty or whitespace-only known_size and known_brand with 422."""
    # Empty string known_size
    res_empty = await async_client.post(
        "/v1/fit/recommend",
        json={"sku_id": "SKU-01", "known_brand": "Zara", "known_size": ""},
    )
    assert res_empty.status_code == 422

    # Whitespace-only known_size
    res_space = await async_client.post(
        "/v1/fit/recommend",
        json={"sku_id": "SKU-01", "known_brand": "Zara", "known_size": "   "},
    )
    assert res_space.status_code == 422

    # Empty known_brand
    res_brand_empty = await async_client.post(
        "/v1/fit/recommend",
        json={"sku_id": "SKU-01", "known_brand": "", "known_size": "M"},
    )
    assert res_brand_empty.status_code == 422

    # Blank sku_id and missing SKU on /v1/fit/recommend
    res_blank_sku = await async_client.post(
        "/v1/fit/recommend",
        json={"sku_id": "   ", "known_brand": "Zara", "known_size": "M"},
    )
    assert res_blank_sku.status_code == 422

    res_missing_sku = await async_client.post(
        "/v1/fit/recommend",
        json={"sku_id": "SKU-999", "known_brand": "Zara", "known_size": "M"},
    )
    assert res_missing_sku.status_code == 404


@pytest.mark.asyncio
async def test_incentive_quote_api_gateway_fee_percentage_conversion(
    async_client: AsyncClient,
) -> None:
    """Verify POST /v1/incentive/quote converts percentage (1.5 -> 0.015) cleanly."""
    # Default 0% fee -> ₹40.00 offer, ₹48.00 avoided loss, ₹8.00 headroom
    res_zero = await async_client.post(
        "/v1/incentive/quote",
        json={
            "cart_total_inr": "1899.00",
            "risk_score_index": 55,
            "current_payment": "COD",
            "upi_gateway_fee_pct": "0.0",
        },
    )
    assert res_zero.status_code == 200
    d0 = res_zero.json()
    assert d0["eligible_for_incentive"] is True
    assert d0["recommended_discount_inr"] == "40.00"
    assert d0["expected_avoided_loss_inr"] == "48.00"
    assert d0["headroom_inr"] == "8.00"

    # 1.5% fee on ₹1,899 -> ₹28.49 fee -> D_max = 11.51 < 25 -> Ineligible
    res_fee = await async_client.post(
        "/v1/incentive/quote",
        json={
            "cart_total_inr": "1899.00",
            "risk_score_index": 55,
            "current_payment": "COD",
            "upi_gateway_fee_pct": "1.5",
        },
    )
    assert res_fee.status_code == 200
    d1 = res_fee.json()
    assert d1["eligible_for_incentive"] is False
    assert d1["recommended_discount_inr"] == "0.00"
    assert d1["reason_code"] == "REASON_INSUFFICIENT_MARGIN"

    # 0.5% fee on ₹1,899 -> ₹9.50 fee -> D_max = 30.50 -> floored to ₹30.00 offer
    res_half = await async_client.post(
        "/v1/incentive/quote",
        json={
            "cart_total_inr": "1899.00",
            "risk_score_index": 55,
            "current_payment": "COD",
            "upi_gateway_fee_pct": "0.5",
        },
    )
    assert res_half.status_code == 200
    d2 = res_half.json()
    assert d2["eligible_for_incentive"] is True
    assert d2["recommended_discount_inr"] == "30.00"


@pytest.mark.asyncio
async def test_prepaid_conversion_normalizes_payment_and_computes_intervention(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify PREPAID conversion normalizes to 'Prepaid', updates overview, and avoids hardcoded 52/12."""
    overview_before = (await async_client.get("/v1/analytics/overview")).json()

    create_payload = {
        "sku_id": "SKU-01",
        "size": "L",
        "quantity": 1,
        "customer_name": "Ananya Verma",
        "customer_phone": "9876501234",
        "street_address": "Flat 202, Lotus Plaza",
        "city": "Delhi",
        "state": "Delhi",
        "pin_code": "110001",
        "payment_method": "PREPAID",
        "applied_discount_inr": "40.00",
        "has_used_fit_twin": True,
        "is_bracketing": False,
        "known_brand": "Zara",
        "known_size": "M",
    }
    res = await async_client.post("/v1/orders", json=create_payload)
    assert res.status_code == 201
    order = res.json()
    assert order["payment_method"] == "Prepaid"
    assert order["dispatch_priority"] == "priority"
    assert order["total_inr"] == "1859.00"

    # Verify DB intervention uses domain math (48.00 / 8.00), not hardcoded 52.00 / 12.00
    interventions = await IncentiveRepository(db_session).get_by_order_id(order["id"])
    assert len(interventions) == 1
    assert interventions[0].expected_savings_inr == Decimal("48.00")
    assert interventions[0].retained_headroom_inr == Decimal("8.00")
    assert interventions[0].offered_discount_inr == Decimal("40.00")

    # Verify live analytics overview increments prepaid count & savings
    overview_after = (await async_client.get("/v1/analytics/overview")).json()
    assert overview_after["total_orders"] == overview_before["total_orders"] + 1
    assert overview_after["prepaid_orders_count"] == overview_before["prepaid_orders_count"] + 1
    assert overview_after["converted_to_upi_count"] == overview_before["converted_to_upi_count"] + 1
    assert Decimal(overview_after["estimated_direct_savings_inr"]) == (
        Decimal(overview_before["estimated_direct_savings_inr"]) + Decimal("48.00")
    )
    assert Decimal(overview_after["net_direct_savings_inr"]) == (
        Decimal(overview_before["net_direct_savings_inr"]) + Decimal("8.00")
    )


@pytest.mark.asyncio
async def test_orders_error_paths_and_whatsapp_opt_out_branches(
    async_client: AsyncClient,
) -> None:
    """Cover 404/422 branches, order_number lookup, STOP opt-out, and plain landmark prefixing."""
    # Invalid SKU and unsupported payment method on create
    bad_sku_res = await async_client.post(
        "/v1/orders",
        json={
            "sku_id": "SKU-DOES-NOT-EXIST",
            "size": "M",
            "customer_name": "Tester",
            "customer_phone": "9876543210",
            "street_address": "Flat 101, Residency",
            "city": "Delhi",
            "state": "Delhi",
            "pin_code": "110001",
            "payment_method": "COD",
        },
    )
    assert bad_sku_res.status_code == 404

    bad_pm_res = await async_client.post(
        "/v1/orders",
        json={
            "sku_id": "SKU-01",
            "size": "M",
            "customer_name": "Tester",
            "customer_phone": "9876543210",
            "street_address": "Flat 101, Residency",
            "city": "Delhi",
            "state": "Delhi",
            "pin_code": "110001",
            "payment_method": "CRYPTO",
        },
    )
    assert bad_pm_res.status_code == 422

    # Create NeedsLandmark order, retrieve by order_number, verify with non-prefixed landmark
    create_res = await async_client.post(
        "/v1/orders",
        json={
            "sku_id": "SKU-01",
            "size": "M",
            "customer_name": "Karan Mehta",
            "customer_phone": "9876543299",
            "street_address": "Flat 12, Green Park",
            "city": "Delhi",
            "state": "Delhi",
            "pin_code": "110001",
            "payment_method": "COD",
        },
    )
    assert create_res.status_code == 201
    order_number = create_res.json()["order_number"]

    by_num = await async_client.get(f"/v1/orders/{order_number}")
    assert by_num.status_code == 200

    verify_plain = await async_client.post(
        f"/v1/orders/{order_number}/verify",
        json={
            "landmark": "Hanuman Mandir",
            "delivery_slot": "Morning (9 AM - 1 PM)",
            "opt_in_whatsapp": True,
        },
    )
    assert verify_plain.status_code == 200
    assert verify_plain.json()["order_status"] == "Safe_For_Dispatch"
    assert "Hanuman Mandir" in verify_plain.json()["street_address"]

    # Opt-out via STOP
    opt_out_res = await async_client.post(
        f"/v1/orders/{order_number}/verify",
        json={"opt_in_whatsapp": False},
    )
    assert opt_out_res.status_code == 200
    assert opt_out_res.json()["consent_status"] == "opted_out"

    # NDR by order_number & 404s for missing orders
    ndr_ok = await async_client.post(
        f"/v1/orders/{order_number}/ndr",
        json={"reschedule_date": "2026-11-30", "reschedule_slot": "Evening (5 PM - 8 PM)"},
    )
    assert ndr_ok.status_code == 200
    assert ndr_ok.json()["order_status"] == "Delivery_Rescheduled"

    assert (
        await async_client.post(
            "/v1/orders/ORD-MISSING/verify",
            json={"landmark": "Near Temple", "opt_in_whatsapp": True},
        )
    ).status_code == 404
    assert (
        await async_client.post(
            "/v1/orders/ORD-MISSING/ndr",
            json={"reschedule_date": "2026-11-30", "reschedule_slot": "Morning"},
        )
    ).status_code == 404


@pytest.mark.asyncio
async def test_adr006_sizing_uses_persisted_db_sku_attributes(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Verify ADR-006: mutating DB SKU attributes directly affects /v1/fit/recommend."""
    repo = SkuRepository(db_session)
    sku = await repo.get_by_id("SKU-01")
    assert sku is not None
    original_sizes: dict[str, Any] = dict(sku.sizes_json)

    # Temporarily make SKU-01 DB shoulder measurements very generous in Size S so S fits Zara M
    sku.sizes_json = {
        "S": {"chest": 40.0, "waist": 34.0, "shoulder": 17.5, "length": 46.0},
        "M": {"chest": 44.0, "waist": 38.0, "shoulder": 19.0, "length": 47.0},
    }
    await repo.upsert(sku)
    await db_session.commit()

    try:
        fit_res = await async_client.post(
            "/v1/fit/recommend",
            json={
                "sku_id": "SKU-01",
                "known_brand": "Zara",
                "known_size": "M",
                "fit_preference": "tailored",
            },
        )
        assert fit_res.status_code == 200
        assert fit_res.json()["recommended_size"] == "S"

        legacy_fit_res = await async_client.post(
            "/v1/catalog/skus/SKU-01/fit",
            json={"known_brand": "Zara", "known_size": "M", "fit_preference": "tailored"},
        )
        assert legacy_fit_res.status_code == 200
        assert legacy_fit_res.json()["recommended_size"] == "S"
    finally:
        sku.sizes_json = original_sizes
        await repo.upsert(sku)
        await db_session.commit()


@pytest.mark.asyncio
async def test_prepaid_order_rejects_discount_when_gateway_fee_makes_ineligible() -> None:
    """Verify POST /v1/orders rejects ₹40 discount when UPI_GATEWAY_FEE_PCT=1.5% withdraws eligibility."""
    fee_settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        UPI_GATEWAY_FEE_PCT=1.5,
    )
    app = create_app(fee_settings)
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post(
                "/v1/orders",
                json={
                    "sku_id": "SKU-01",
                    "size": "L",
                    "quantity": 1,
                    "customer_name": "Fee Policy Shopper",
                    "customer_phone": "9876501234",
                    "street_address": "Flat 202, Lotus Plaza",
                    "city": "Delhi",
                    "state": "Delhi",
                    "pin_code": "110001",
                    "payment_method": "PREPAID",
                    "applied_discount_inr": "40.00",
                },
            )
            assert res.status_code == 422
            assert "margin-safe UPI incentive" in res.text


@pytest.mark.asyncio
async def test_verify_order_appends_landmark_when_normalizer_omits_it(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify verify_order appends landmark cleanly if live normalizer omits it from sanitized_address."""
    create_res = await async_client.post(
        "/v1/orders",
        json={
            "sku_id": "SKU-01",
            "size": "M",
            "customer_name": "Meera Nair",
            "customer_phone": "9876543288",
            "street_address": "Flat 18, Rose Apartments",
            "city": "Delhi",
            "state": "Delhi",
            "pin_code": "110001",
            "payment_method": "COD",
        },
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]

    class _OmitLandmarkNormalizer:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def normalize(
            self, raw_address: str, landmark: str | None = None
        ) -> NormalizedAddressResult:
            return NormalizedAddressResult(
                sanitized_address="Flat 18, Rose Apartments",
                landmark=landmark,
                delivery_instructions="Deliver to address.",
                confidence="high",
                provenance="live_gemini",
            )

    monkeypatch.setattr("app.api.orders.AddressNormalizer", _OmitLandmarkNormalizer)

    verify_res = await async_client.post(
        f"/v1/orders/{order_id}/verify",
        json={
            "landmark": "Metro Gate 2",
            "opt_in_whatsapp": True,
        },
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["street_address"] == "Flat 18, Rose Apartments, Near Metro Gate 2"
