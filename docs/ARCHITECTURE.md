# ReturnZero AI — System Architecture & Latency SLA

**Project:** ReturnZero AI (Team BioXtreme)  
**Hackathon:** Code to Cart Round 2 Buildathon (KartAI x CodeXcelerate)  
**Target:** D2C Fashion Apparel Fit Intelligence & Delivery Assurance Layer

---

## 1. High-Level System Architecture

```
Shopper Browser (Next.js 14 Storefront)
   │
   ├─► Check My Fit Drawer ──► POST /v1/catalog/skus/{id}/fit ──► Pure Sizing Engine (EOM Matrices)
   │
   ├─► Checkout Shield ─────► POST /v1/risk/evaluate ─────────► Frozen Risk Evaluator + Landmark Dict
   │                         └─► POST /v1/incentive/quote ────► Closed-Form Margin Solver (D_max)
   │
   ├─► In-Browser WhatsApp ──► POST /v1/orders/{id}/verify ───► Gemini 3.8 Flash / Regex Normalizer
   │   (Delivery Assurance)  └─► POST /v1/orders/{id}/ndr ──────► Courier Reschedule Coordinator
   │
Merchant Dashboard ─────────► GET /v1/analytics/overview ───► Live DB Aggregations (150 Orders)
                             └─► GET /v1/analytics/scenario ───► 10,000-Shipment Financial Simulator
```

---

## 2. Component Responsibility Matrix

| Subsystem | Tech Stack | Execution Latency SLA | Invariant Rules |
|---|---|---|---|
| **Fit-Twin Engine** | Python Domain (`app/domain/sizing.py`) | `< 10 ms` | Pure deterministic calculation; zero random or clock calls; categorical confidence bands (High/Medium/Low); explicit gap warnings. |
| **VLM Extractor** | Google GenAI SDK (`gemini-3.8-flash`) | `< 4.0 s` | Multimodal VLM isolated strictly to unstructured garment text/photo extraction; dual-key rotation; 4.0s timeout; 60s circuit breaker; benchmark fixture fallback. |
| **Operational Risk Evaluator** | Python Domain (`app/domain/risk.py`) | `< 5 ms` | Frozen dataclass weights; explainable 3-point checklist; Cash on Delivery remains 100% available at all times (`cod_remains_available: true`). |
| **Margin-Safe Incentive Solver** | Python Domain (`app/domain/incentive.py`) | `< 5 ms` | Closed-form $D_{\max} = (P_{\text{COD}} - P_{\text{prepaid}}) \times \text{Cost}_{\text{RTO}} - \text{Fees} - \text{MarginFloor}$; ₹5 step floor rounding; ₹40 pitch deck cap; 20% GMV coupon limit; 3 doorstep refusals switch to non-cash perks. |
| **WhatsApp Delivery Simulator** | React 18 + Zustand + FastAPI | `< 50 ms` (Local UI) | In-browser iPhone 15 frame; explicit opt-in / STOP opt-out; sticky "Simulated" top banner; live database status sync to `Safe_For_Dispatch`. |
| **Merchant Command Center** | Next.js 14 + Recharts + SQLAlchemy | `< 30 ms` (API Query) | Strict separation between live database rows (150 seeded orders) and the interactive 10,000-shipment financial projection model. |

---

## 3. Resilience & Disaster Prevention Protocol

1. **Dual-Key Dynamic Deadline Budgeting:**
   Primary API key runs with a monotonic deadline timer. If primary exhausts the budget or hits 429 quota limits, failover rotates to secondary key within the 4.5s ceiling; if both fail, verified benchmark fixture responds seamlessly with zero 500 errors.

2. **No External Payment or Telecom Gateways:**
   In-browser WhatsApp simulator and simulated UPI payment modal eliminate third-party webhook drops, SMS gateway delivery delays, and live credit card authentication barriers during demo evaluation.

3. **Deterministic Persistence:**
   SQLite async engine (`aiosqlite`) with PostgreSQL wire-compatibility (ADR-019). Lifespan seeder populates 150 realistic Indian orders deterministically using `random.Random(20261128)`.
