# ReturnZero AI — API Specification

**Base URL:** `http://localhost:8000` (Local) / Cloud URL (Production)  
**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI) / `/redoc`

---

## 1. System Health
- **`GET /healthz`**
  - Returns service status, UTC timestamp, environment, and Gemini configuration state.
  - Response: `{"status": "ok", "service": "returnzero-backend", "gemini_configured": true}`

---

## 2. Product Catalog & Fit Intelligence
- **`GET /v1/catalog/skus`**
  - Lists the 4 curated fashion apparel SKUs with full garment specifications.
- **`GET /v1/catalog/skus/{sku_id}`**
  - Retrieves single SKU details, size measurement table, and provenance.
- **`POST /v1/catalog/skus/{sku_id}/extract`**
  - Triggers 3-tier multimodal attribute extraction (cache -> live Gemini 3.8 Flash -> benchmark fixture).
- **`POST /v1/catalog/skus/{sku_id}/fit`**
  - Evaluates shopper reference brand & size against garment specs using pure domain EOM rules.
  - Body: `{"known_brand": "Zara", "known_size": "M", "fit_preference": "tailored", "height_cm": 165}`
  - Response: Recommended size, categorical confidence band (High/Medium/Low), fit score index, and zone-by-zone ease breakdown.

---

## 3. Operational Risk & Closed-Form Incentive
- **`POST /v1/risk/evaluate`**
  - Generates 0-100 risk score and 3-point checklist (`Address complete`, `Serviceable PIN`, `RTO risk band`).
  - Fairness mandate: `cod_remains_available: true`.
- **`POST /v1/incentive/quote`**
  - Solves closed-form $D_{\max}$ discount from avoided RTO loss.
  - Body: `{"cart_total_inr": "1899.00", "risk_score_index": 55, "current_payment": "COD"}`
  - Response: `{"eligible_for_incentive": true, "recommended_discount_inr": "40.00", "cod_remains_available": true}`

---

## 4. Customer Orders & Delivery Assurance
- **`POST /v1/orders`**
  - Persists new customer order with risk score, tier classification, and initial delivery event.
- **`GET /v1/orders`**
  - Returns descending list of recent orders for the real-time merchant stream.
- **`GET /v1/orders/{order_id}`**
  - Returns single order by ID or order number.
- **`POST /v1/orders/{order_id}/verify`**
  - Handles WhatsApp simulator address/landmark verification.
  - Transitions order status to `Safe_For_Dispatch` and logs `Address_Verified` event.
- **`POST /v1/orders/{order_id}/ndr`**
  - Coordinates non-delivery report (NDR) reschedule to a preferred date and slot.

---

## 5. Merchant Telemetry & Scenario Analytics
- **`GET /v1/analytics/overview`**
  - Dynamically aggregates live metrics from 150 seeded database rows (orders, RTO count, customer returns, incentives disbursed, direct savings).
- **`GET /v1/analytics/scenario`**
  - Evaluates pure 10,000-shipment financial projection model reproducing pitch deck economics.
- **`POST /v1/demo/reset`**
  - Guards: `X-Demo-Token: secret-demo-token-2026`.
  - Resets database state to exactly 150 seeded orders and 4 curated SKUs.
