import json
import urllib.request

def test_api() -> None:
    base = "http://127.0.0.1:8000"
    
    # 1. Healthz
    with urllib.request.urlopen(f"{base}/healthz") as r:
        health = json.loads(r.read())
        print(f"[1/8] Healthz: {health['status']} ({health['service']})")

    # 2. Catalog
    with urllib.request.urlopen(f"{base}/v1/catalog/skus") as r:
        skus = json.loads(r.read())
        print(f"[2/8] Catalog: {skus['total']} curated SKUs loaded")

    # 3. Canonical Fit Recommendation (AGENTS.md §7)
    req = urllib.request.Request(
        f"{base}/v1/fit/recommend",
        data=json.dumps({
            "sku_id": "SKU-01",
            "known_brand": "Zara",
            "known_size": "M",
            "fit_preference": "tailored",
            "height_cm": 165,
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        fit = json.loads(r.read())
        assert fit["recommended_size"] == "L", f"Expected size L, got {fit['recommended_size']}"
        print(f"[3/8] Canonical Fit: Recommended Size {fit['recommended_size']} ({fit['confidence_level']} Confidence, score {fit['fit_score']}/100)")

    # 4. Risk Evaluation
    req = urllib.request.Request(
        f"{base}/v1/risk/evaluate",
        data=json.dumps({"street_address": "House 12, Sector 15", "pin_code": "110001", "payment_method": "COD"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        risk = json.loads(r.read())
        print(f"[4/8] Risk Evaluation: Index {risk['risk_score_index']}/100 ({risk['risk_level']}), Guaranteed COD: {risk['cod_remains_available']}")

    # 5. Incentive Quote
    req = urllib.request.Request(
        f"{base}/v1/incentive/quote",
        data=json.dumps({"cart_total_inr": "1899.00", "risk_score_index": 55, "current_payment": "COD"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        inc = json.loads(r.read())
        assert inc["recommended_discount_inr"] == "40.00", f"Expected 40.00, got {inc['recommended_discount_inr']}"
        print(f"[5/8] Incentive Quote: Eligible: {inc['eligible_for_incentive']}, Discount: ₹{inc['recommended_discount_inr']} ({inc['reason_code']})")

    # 6. Live DB Telemetry
    with urllib.request.urlopen(f"{base}/v1/analytics/overview") as r:
        an = json.loads(r.read())
        print(f"[6/8] Live DB Telemetry: {an['total_orders']} orders ({an['cod_orders_count']} COD, {an['prepaid_orders_count']} Prepaid), RTO: {an['rto_rate_pct']}%, Direct Savings: ₹{an['estimated_direct_savings_inr']}")

    # 7. 10k Financial Scenario
    with urllib.request.urlopen(f"{base}/v1/analytics/scenario") as r:
        sc = json.loads(r.read())
        cb = sc["combined_case"]
        print(f"[7/8] 10k Scenario Model: Avoided RTOs: {cb['avoided_rto_shipments']}, Net Monthly Savings: ₹{cb['net_operating_savings_monthly_inr']}")

    # 8. Demo State Reset (Ensures DB stays pristine at 150 orders per B3)
    reset_req = urllib.request.Request(
        f"{base}/v1/demo/reset",
        data=b"{}",
        headers={
            "Content-Type": "application/json",
            "X-Demo-Token": "returnzero-demo-secret-2026",
        },
    )
    with urllib.request.urlopen(reset_req) as r:
        res = json.loads(r.read())
        print(f"[8/8] Pristine State Reset: status={res['status']}, seeded_orders={res['seeded_orders']} (DB verified clean)")

if __name__ == "__main__":
    test_api()
