import json
import urllib.request

def test_api() -> None:
    base = "http://127.0.0.1:8000"
    
    # 1. Healthz
    with urllib.request.urlopen(f"{base}/healthz") as r:
        health = json.loads(r.read())
        print(f"[1/7] Healthz: {health['status']} ({health['service']})")

    # 2. Catalog
    with urllib.request.urlopen(f"{base}/v1/catalog/skus") as r:
        skus = json.loads(r.read())
        print(f"[2/7] Catalog: {skus['total']} curated SKUs loaded")

    # 3. Fit recommendation
    req = urllib.request.Request(
        f"{base}/v1/catalog/skus/SKU-01/fit",
        data=json.dumps({"known_brand": "Zara", "known_size": "M", "fit_preference": "tailored", "height_cm": 165}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        fit = json.loads(r.read())
        print(f"[3/7] Sizing: Recommended Size {fit['recommended_size']} ({fit['confidence_level']} Confidence, score {fit['fit_score']}/100)")

    # 4. Risk Evaluation
    req = urllib.request.Request(
        f"{base}/v1/risk/evaluate",
        data=json.dumps({"street_address": "House 12, Sector 15", "pin_code": "110001", "payment_method": "COD"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        risk = json.loads(r.read())
        print(f"[4/7] Risk Evaluation: Index {risk['risk_score_index']}/100 ({risk['risk_level']}), Guaranteed COD: {risk['cod_remains_available']}")

    # 5. Incentive Quote
    req = urllib.request.Request(
        f"{base}/v1/incentive/quote",
        data=json.dumps({"cart_total_inr": "1899.00", "risk_score_index": 55, "current_payment": "COD"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        inc = json.loads(r.read())
        print(f"[5/7] Incentive Quote: Eligible: {inc['eligible_for_incentive']}, Discount: ₹{inc['recommended_discount_inr']} ({inc['reason_code']})")

    # 6. Live DB Telemetry
    with urllib.request.urlopen(f"{base}/v1/analytics/overview") as r:
        an = json.loads(r.read())
        print(f"[6/7] Live DB Telemetry: {an['total_orders']} orders ({an['cod_orders_count']} COD, {an['prepaid_orders_count']} Prepaid), RTO: {an['rto_rate_pct']}%, Direct Savings: ₹{an['estimated_direct_savings_inr']}")

    # 7. 10k Financial Scenario
    with urllib.request.urlopen(f"{base}/v1/analytics/scenario") as r:
        sc = json.loads(r.read())
        cb = sc["combined_case"]
        print(f"[7/7] 10k Scenario Model: Avoided RTOs: {cb['avoided_rto_shipments']}, Net Monthly Savings: ₹{cb['net_operating_savings_monthly_inr']}")

if __name__ == "__main__":
    test_api()
