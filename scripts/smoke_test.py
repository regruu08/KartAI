#!/usr/bin/env python3
"""Comprehensive cross-platform smoke test for ReturnZero AI Backend API.

Exercises all core operational routes:
1. /healthz (liveness & model config)
2. /v1/catalog/skus (4 curated fashion SKUs)
3. /v1/fit/recommend (canonical sizing recommendation + fit_log persistence)
4. /v1/risk/evaluate (3-check order review + guaranteed COD)
5. /v1/incentive/quote (closed-form margin-safe discount: exactly ₹40.00 offer)
6. /v1/orders (order creation with synthetic flag & audit tracking)
7. /v1/orders/{order_id}/verify (WhatsApp delivery assurance & landmark normalization)
8. /v1/analytics/overview (live database aggregations)
9. /v1/analytics/scenario (10,000-order pitch deck economics reproduction)

Usage:
    python scripts/smoke_test.py [base_url]
Default base_url: http://localhost:8000
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any


def _request_json(
    url: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 8.0,
) -> tuple[int, dict[str, Any]]:
    req_headers = {
        "User-Agent": "ReturnZero-SmokeTest/2.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)

    body_bytes = None
    if data is not None:
        req_headers["Content-Type"] = "application/json"
        body_bytes = json.dumps(data).encode("utf-8")

    req = urllib.request.Request(url, data=body_bytes, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status_code = resp.status
        content = resp.read().decode("utf-8")
        return status_code, json.loads(content)


def run_full_smoke_suite(base_url: str) -> bool:
    base = base_url.rstrip("/")
    print("=" * 65)
    print(f"ReturnZero AI Full Operational Smoke Suite — Target: {base}")
    print("=" * 65)

    try:
        # Step 1: Healthcheck
        print("[1/9] Checking /healthz ...")
        status, health = _request_json(f"{base}/healthz")
        assert status == 200, f"Expected 200, got {status}"
        assert health.get("status") == "ok", f"Health status: {health.get('status')}"
        print(f"  -> PASS: service='{health.get('service')}', model='{health.get('model_id')}', gemini_configured={health.get('gemini_configured')}")

        # Step 2: Catalog SKUs
        print("[2/9] Checking /v1/catalog/skus ...")
        status, catalog = _request_json(f"{base}/v1/catalog/skus")
        assert status == 200
        assert catalog.get("total") == 4, f"Expected 4 SKUs, got {catalog.get('total')}"
        sku_ids = [s["id"] for s in catalog.get("skus", [])]
        print(f"  -> PASS: loaded 4 curated SKUs ({sku_ids})")

        # Step 3: Canonical Fit Sizing (/v1/fit/recommend)
        print("[3/9] Checking POST /v1/fit/recommend (Canonical sizing & audit)...")
        fit_payload = {
            "sku_id": "SKU-01",
            "known_brand": "Zara",
            "known_size": "M",
            "fit_preference": "tailored",
            "height_cm": 165.0,
        }
        status, fit = _request_json(f"{base}/v1/fit/recommend", method="POST", data=fit_payload)
        assert status == 200
        assert fit.get("recommended_size") == "L", f"Expected 'L', got {fit.get('recommended_size')}"
        print(f"  -> PASS: Zara M on SKU-01 -> Recommended Size {fit.get('recommended_size')} ({fit.get('confidence_level')} Confidence, score {fit.get('fit_score')}/100)")

        # Step 4: Risk Evaluation (/v1/risk/evaluate)
        print("[4/9] Checking POST /v1/risk/evaluate ...")
        risk_payload = {
            "street_address": "Flat 304, Green Glen Layout",
            "pin_code": "110001",
            "payment_method": "COD",
            "has_used_fit_twin": True,
            "is_bracketing": False,
        }
        status, risk = _request_json(f"{base}/v1/risk/evaluate", method="POST", data=risk_payload)
        assert status == 200
        assert risk.get("cod_remains_available") is True
        assert len(risk.get("checks", [])) == 3
        print(f"  -> PASS: Risk Index {risk.get('risk_score_index')}/100 ({risk.get('risk_level')}), 3-check review generated, COD Guaranteed")

        # Step 5: Incentive Quote (/v1/incentive/quote)
        print("[5/9] Checking POST /v1/incentive/quote ...")
        inc_payload = {
            "cart_total_inr": "1899.00",
            "risk_score_index": 55,
            "current_payment": "COD",
            "has_used_fit_twin": True,
        }
        status, inc = _request_json(f"{base}/v1/incentive/quote", method="POST", data=inc_payload)
        assert status == 200
        assert inc.get("eligible_for_incentive") is True
        assert inc.get("recommended_discount_inr") == "40.00", f"Expected ₹40.00, got {inc.get('recommended_discount_inr')}"
        print(f"  -> PASS: Offer=₹{inc.get('recommended_discount_inr')}, Headroom=₹{inc.get('headroom_inr')}, Reason={inc.get('reason_code')}")

        # Step 6: Order Creation (/v1/orders)
        print("[6/9] Checking POST /v1/orders ...")
        order_payload = {
            "sku_id": "SKU-01",
            "size": "L",
            "quantity": 1,
            "customer_name": "Smoke Test User",
            "customer_phone": "9876543210",
            "street_address": "House 10, Green Avenue",
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
        status, order = _request_json(f"{base}/v1/orders", method="POST", data=order_payload)
        assert status == 201
        order_id = order.get("id")
        assert order_id is not None
        print(f"  -> PASS: Order created: #{order.get('order_number')} (ID: {order_id}, Status: {order.get('order_status')})")

        # Step 7: Order Verification & Landmark Clarification (/v1/orders/{id}/verify)
        print(f"[7/9] Checking POST /v1/orders/{order_id}/verify ...")
        verify_payload = {
            "landmark": "Near Metro Pillar 120",
            "delivery_slot": "Morning (9 AM - 1 PM)",
            "opt_in_whatsapp": True,
        }
        status, verified_order = _request_json(f"{base}/v1/orders/{order_id}/verify", method="POST", data=verify_payload)
        assert status == 200
        assert verified_order.get("order_status") == "Safe_For_Dispatch"
        assert "Metro Pillar 120" in verified_order.get("street_address", "")
        print(f"  -> PASS: Verified & Normalised: status='{verified_order.get('order_status')}', address='{verified_order.get('street_address')}'")

        # Step 8: Live Analytics Overview (/v1/analytics/overview)
        print("[8/9] Checking GET /v1/analytics/overview ...")
        status, overview = _request_json(f"{base}/v1/analytics/overview")
        assert status == 200
        assert overview.get("total_orders", 0) >= 150
        print(f"  -> PASS: Total Orders={overview.get('total_orders')} (COD: {overview.get('cod_orders_count')}, Prepaid: {overview.get('prepaid_orders_count')}), RTO={overview.get('rto_rate_pct')}%, Direct Savings=₹{overview.get('estimated_direct_savings_inr')}")

        # Step 9: 10k Financial Scenario (/v1/analytics/scenario)
        print("[9/9] Checking GET /v1/analytics/scenario ...")
        status, scenario = _request_json(f"{base}/v1/analytics/scenario")
        assert status == 200
        combined = scenario.get("combined_case", {})
        assert combined.get("avoided_rto_shipments") == 273, f"Expected 273 avoided RTOs, got {combined.get('avoided_rto_shipments')}"
        assert combined.get("net_operating_savings_monthly_inr") == "28600.00", f"Expected 28600.00, got {combined.get('net_operating_savings_monthly_inr')}"
        print(f"  -> PASS: Deck parity verified! Avoided RTOs={combined.get('avoided_rto_shipments')}, Monthly Net Savings=₹{combined.get('net_operating_savings_monthly_inr')}")

        # Step 10 (Cleanup): Reset DB to pristine 150-order seed state per B3
        print("\n[*] Resetting database to pristine 150-order state (/v1/demo/reset)...")
        status, reset_res = _request_json(
            f"{base}/v1/demo/reset",
            method="POST",
            data={},
            headers={"X-Demo-Token": "returnzero-demo-secret-2026"},
        )
        assert status == 200 and reset_res.get("status") == "ok"
        print(f"  -> PASS: Clean state restored! Orders in DB: {reset_res.get('seeded_orders')}")

        print("\n" + "=" * 65)
        print("[SUCCESS] ALL 9 OPERATIONAL SMOKE TESTS PASSED WITH ZERO ERRORS.")
        print("=" * 65)
        return True

    except AssertionError as exc:
        print(f"\n[FAIL] Assertion error: {exc}", file=sys.stderr)
        return False
    except urllib.error.HTTPError as exc:
        print(f"\n[FAIL] HTTP error {exc.code}: {exc.reason}", file=sys.stderr)
        return False
    except Exception as exc:
        print(f"\n[FAIL] Unexpected error: {exc}", file=sys.stderr)
        return False


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success = run_full_smoke_suite(base_url)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
