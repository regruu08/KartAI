# ReturnZero AI — Architectural Decision Records (ADRs)

**Project:** ReturnZero AI (Team BioXtreme)  
**Hackathon:** Code to Cart Round 2 Buildathon (KartAI x CodeXcelerate)  
**Date:** 2026-11-23  
**Status:** Canonical & Binding Architecture Decisions  

---

## Index of Architectural Decision Records

| ADR ID | Title | Erratum / Ref | Status | Date |
|---|---|---|---|---|
| [ADR-001](#adr-001-gemini-sdk-adapter-isolation-and-configurable-model-protocol) | Gemini SDK Adapter Isolation and Configurable Model Protocol | E1 | Accepted | 2026-11-23 |
| [ADR-002](#adr-002-incentive-solver-headroom-floor-discretization-and-configurable-fee-policy) | Incentive Solver Headroom, Floor Discretization, and Configurable Fee Policy | E2 | Accepted | 2026-11-23 |
| [ADR-003](#adr-003-pure-address-quality-evaluation-frozen-riskconfig-and-synthetic-lane-demarcation) | Pure Address Quality Evaluation, Frozen RiskConfig, and Synthetic Lane Demarcation | E3 | Accepted | 2026-11-23 |
| [ADR-004](#adr-004-computed-fit-confidence-bands-comprehensive-eom-rules-and-garment-gap-reporting) | Computed Fit Confidence Bands, Comprehensive EOM Rules, and Garment Gap Reporting | E4 | Accepted | 2026-11-23 |
| [ADR-005](#adr-005-strict-segregation-of-live-telemetry-aggregations-and-financial-scenario-modeling) | Strict Segregation of Live Telemetry Aggregations and Financial Scenario Modeling | E5 | Accepted | 2026-11-23 |
| [ADR-006](#adr-006-database-backed-catalog-state-with-extraction-provenance-and-sizing-integration) | Database-Backed Catalog State with Extraction Provenance and Sizing Integration | E6 | Accepted | 2026-11-23 |
| [ADR-007](#adr-007-rest-api-parameter-normalization-and-canonical-route-architecture) | REST API Parameter Normalization and Canonical Route Architecture | E7 | Accepted | 2026-11-23 |
| [ADR-008](#adr-008-strict-cors-origin-parsing-and-credentials-policy) | Strict CORS Origin Parsing and Credentials Policy | E8 | Accepted | 2026-11-23 |
| [ADR-009](#adr-009-idempotent-lifespan-database-seeding-seeded-rng-and-demo-state-reset) | Idempotent Lifespan Database Seeding, Seeded RNG, and Demo State Reset | E9 | Accepted | 2026-11-23 |
| [ADR-010](#adr-010-frontend-framework-pinning--nextjs-142-and-react-183) | Frontend Framework Pinning — Next.js 14.2 and React 18.3 | E10 | Accepted | 2026-11-23 |
| [ADR-011](#adr-011-canonical-design-system-token-standardization) | Canonical Design System Token Standardization | E11 | Accepted | 2026-11-23 |
| [ADR-012](#adr-012-state-conditional-copy-architecture-and-claims-governance) | State-Conditional Copy Architecture and Claims Governance | E12 | Accepted | 2026-11-23 |
| [ADR-013](#adr-013-4-sku-catalog-scope-and-fabric-uncertainty-demonstration) | 4-SKU Catalog Scope and Fabric Uncertainty Demonstration | E13 | Accepted | 2026-11-23 |
| [ADR-014](#adr-014-margin-anti-abuse-controls-and-intervention-reason-codes) | Margin Anti-Abuse Controls and Intervention Reason Codes | E14 | Accepted | 2026-11-23 |
| [ADR-015](#adr-015-conversational-state-machine-completeness-consent-flow-and-dynamic-order-binding) | Conversational State Machine Completeness, Consent Flow, and Dynamic Order Binding | E15 | Accepted | 2026-11-23 |
| [ADR-016](#adr-016-non-blocking-async-gemini-integration-dual-key-failover-and-resilient-circuit-breakers) | Non-Blocking Async Gemini Integration, Dual-Key Failover, and Resilient Circuit Breakers | E16 | Accepted | 2026-11-23 |
| [ADR-017](#adr-017-d2c-fashion-focus-alignment-and-explicit-rejection-of-stale-q-commerce--pharmacy-specs) | D2C Fashion Focus Alignment and Explicit Rejection of Stale Q-Commerce / Pharmacy Specs | Spec Ambiguity | Accepted | 2026-11-23 |
| [ADR-018](#adr-018-in-browser-whatsapp-simulator-vs-live-metatwilio-telecom-dependency-elimination) | In-Browser WhatsApp Simulator vs Live Meta/Twilio Telecom Dependency Elimination | Spec Ambiguity | Accepted | 2026-11-23 |
| [ADR-019](#adr-019-local-async-sqlite-persistence-with-postgresql-compatibility-for-hackathon-zero-dependency-delivery) | Local Async SQLite Persistence with PostgreSQL Compatibility for Zero-Dependency Delivery | Spec Ambiguity | Accepted | 2026-11-23 |
| [ADR-020](#adr-020-disambiguation-and-segregation-of-blended-rto-vs-cod-only-rto-and-customer-returns) | Disambiguation and Segregation of Blended RTO vs. COD-Only RTO and Customer Returns | Item B4 / §B | Accepted | 2026-11-24 |
| [ADR-021](#adr-021-nextjs-142-patch-upgrade-to-14235-and-dependency-vulnerability-audit) | Next.js 14.2 Patch Upgrade to 14.2.35 and Dependency Vulnerability Audit | Item B5 / E10 | Accepted | 2026-11-24 |
| [ADR-022](#adr-022-boundary-validation-address-sanitization-and-state-resilience-bug-fixes) | Boundary Validation, Address Sanitization, and State Resilience Bug Fixes | Plan Bugs 1-6 | Accepted | 2026-11-24 |

---

## ADR-001: Gemini SDK Adapter Isolation and Configurable Model Protocol

- **Status:** Accepted
- **Errata Reference:** Erratum E1 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/01_GEMINI_VLM_PIPELINE.md` lines 83 and 126 hardcoded the model string `gemini-3.8-flash` and invoked synchronous `client.models.generate_content(... response_schema=...)`. The official Google GenAI SDK (`google-genai`) has been transitioning towards the modern Interactions API (`client.interactions.create(model=..., input=..., response_format=...)`) alongside `client.models.generate_content`. Directly scattering raw SDK method calls across extraction services creates brittle code that breaks upon SDK minor upgrades. Furthermore, legacy docs mentioned the deprecated `google-generativeai` package alongside the current `google-genai` library.
- **Decision & Binding Resolution:**  
  1. The Gemini model identifier must originate strictly from the environment variable `GEMINI_MODEL_ID` via `Settings`, defaulting to `gemini-3.8-flash`. Hardcoding the model string in service logic is strictly prohibited.
  2. The deprecated `google-generativeai` package is strictly banned. Only the official `google-genai` library is permitted in dependencies.
  3. All Gemini SDK calls are fully isolated behind Python `typing.Protocol` interfaces (`CatalogExtractor`, `AddressNormalizer`) implemented in `backend/app/integrations/gemini/adapter.py`. No other file in the repository may import or invoke the SDK directly.
  4. Implement `scripts/check_gemini.py` as an executable health script to verify the live API connection, latency, model ID, and schema validation.
- **Consequences:**  
  - *Positive:* Upgrading or modifying SDK calls touches exactly one file (`adapter.py`). All services interact with pure typed Protocols.
  - *Negative:* Requires maintaining adapter abstraction and mock implementations for unit testing.
  - *Invariants:* Zero direct imports of `google.genai` outside `backend/app/integrations/gemini/`.
- **Affected Files & Tests:**  
  - `backend/app/integrations/gemini/adapter.py`
  - `backend/app/integrations/gemini/extractor.py`
  - `backend/app/integrations/gemini/normalizer.py`
  - `backend/app/config.py`
  - `scripts/check_gemini.py`
  - `backend/tests/unit/test_gemini_adapter.py`
  - `backend/tests/resilience/test_gemini_resilience.py`

---

## ADR-002: Incentive Solver Headroom, Floor Discretization, and Configurable Fee Policy

- **Status:** Accepted
- **Errata Reference:** Erratum E2 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/05_RTO_RISK_AND_INCENTIVE_OPTIMIZER.md` lines 116–127 implemented an incentive equation deducting a 1.5% gateway fee (`pg_fee = 0.015 * cart_total`), yielding $D_{\max} = (0.26 - 0.02) \times 200 - (0.015 \times 1899) - 8 = ₹11.51$. Because $D_{\max} < ₹25$ (`MIN_OFFER`), the solver marked the ₹1,899 cart ineligible! This broke the spec's own smoke test (`tech_docs/08` lines 124–139), which asserted eligibility at ₹1,899. Furthermore, the submitted pitch deck stated "₹40 incentive with ₹8 headroom" *before payment gateway fees*, and using `round(x / 5.0) * 5.0` could round *up* past the margin floor, violating financial guarantees.
- **Decision & Binding Resolution:**  
  1. Implement strictly the pitch deck closed-form equation:  
     $$D_{\max} = (P_{\text{COD}} - P_{\text{prepaid}}) \times \text{Cost}_{\text{RTO}} - \text{Fees} - \text{MarginFloor}$$
  2. `UPI_GATEWAY_FEE_PCT` is made a configurable setting in `Settings`, defaulting to `0.0` (matching the pitch deck's figures before payment fees: $48 - 0 - 8 = ₹40$).
  3. Offer calculation uses strict mathematical floor rounding to the nearest ₹5:  
     $$\text{Offer} = \min(40.0, \lfloor D_{\max} / 5.0 \rfloor \times 5.0)$$
  4. Eligibility strictly requires $D_{\max} \ge 25.0$. If $D_{\max} < 25.0$, `eligible_for_incentive` is `False`, offer is `0.0`, and reason code is `REASON_INSUFFICIENT_MARGIN`.
  5. Expose dynamic fee percentage and RTO cost as interactive what-if sliders on the merchant dashboard. Setting fee to 1.5% at ₹1,899 visibly withdraws the offer, demonstrating margin protection to hackathon judges.
- **Consequences:**  
  - *Positive:* Reproduces exact pitch deck figures by default ($₹40$ offer, $₹8$ headroom). Passing smoke test guaranteed. Eliminates margin erosion from ceiling/nearest rounding.
  - *Negative:* Merchant must explicitly toggle fee simulation to test non-zero fee impacts.
  - *Invariants:* Discount rounding never rounds up. All monetary math uses Python `Decimal`.
- **Affected Files & Tests:**  
  - `backend/app/domain/incentive.py`
  - `backend/app/domain/money.py`
  - `backend/app/config.py`
  - `backend/app/schemas/api_contracts.py`
  - `frontend/components/dashboard/IncentiveEquationCard.tsx`
  - `scripts/smoke_test.py`
  - `backend/tests/unit/test_incentive.py`

---

## ADR-003: Pure Address Quality Evaluation, Frozen RiskConfig, and Synthetic Lane Demarcation

- **Status:** Accepted
- **Errata Reference:** Erratum E3 (from `AGENTS.md` §5)
- **Context & Problem:**  
  In `tech_docs/05`: (a) line 46 added a string `"Fit-Twin verified size match (-15% risk mitigation)"` to contributing factors without actually deducting points from the risk score; (b) line 59 checked `len(address) < 15 or "near" not in address.lower()`, which was brittle and failed valid Indian addresses lacking the English token "near"; (c) magic scoring weights (+25, +40, +20, +15) were hardcoded inline; (d) PIN codes like Bhatinda were inconsistently labelled (151001 in seed data vs 143001 in risk lists).
- **Decision & Binding Resolution:**  
  1. Fit verification is explicitly non-punitive and adds 0 penalty points. Misleading "−15%" text is eliminated.
  2. Implement a pure domain function `address_quality()` in `backend/app/domain/address.py`. It evaluates address length, flat/house number regex, PIN regex (`^\d{6}$`), and a comprehensive dictionary of Indian landmark keywords (`near`, `opp`, `behind`, `beside`, `mandir`, `temple`, `masjid`, `gurudwara`, `chowk`, `rasta`, `gali`, `marg`, `road`, `market`, `nagar`, `colony`, `phase`, `sector`). It classifies addresses into `Complete`, `NeedsLandmark`, or `Poor`.
  3. Shared by both the checkout risk evaluator and the WhatsApp delivery assurance simulator.
  4. All risk weights and thresholds are consolidated into a frozen `RiskConfig` dataclass in `backend/app/domain/risk.py`.
  5. Serviceable and high-risk PIN lists live in `backend/app/data/serviceable_pins.py` and are explicitly labelled **"synthetic demo lane list"** in code, UI, and documentation.
  6. Return the 3-point **Order Review checklist** (`Address complete`, `Serviceable PIN`, `RTO risk band`) as structured items in `POST /v1/risk/evaluate`.
- **Consequences:**  
  - *Positive:* Robust address classification across English and Hinglish vernaculars; consistent scoring; zero magic numbers; auditable checklist.
  - *Negative:* Synthetic PIN list represents simulated logistics data rather than live courier API feeds.
  - *Invariants:* `address_quality()` is pure and side-effect free.
- **Affected Files & Tests:**  
  - `backend/app/domain/address.py`
  - `backend/app/domain/risk.py`
  - `backend/app/data/serviceable_pins.py`
  - `backend/app/schemas/api_contracts.py`
  - `backend/app/api/risk.py`
  - `frontend/components/checkout/OrderReviewModal.tsx`
  - `backend/tests/unit/test_address.py`
  - `backend/tests/unit/test_risk.py`

---

## ADR-004: Computed Fit Confidence Bands, Comprehensive EOM Rules, and Garment Gap Reporting

- **Status:** Accepted
- **Errata Reference:** Erratum E4 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/04_DETERMINISTIC_SIZING_ENGINE.md` line 176 hardcoded `confidence_level="High"` for all sizing recommendations, while other marketing copy claimed unbacked numbers like "94% accuracy". Line 149 omitted the `oversized` fit preference, causing it to fall through to `1.0` (tight ease), recommending too small a size. Waist measurements were ignored in penalty functions, the ease table contradicted code thresholds, and shopper height was unused.
- **Decision & Binding Resolution:**  
  1. Fit confidence is computed dynamically based on: (a) availability of key garment measurements (chest, shoulder, waist, length); (b) shopper input precision (exact measurements vs brand conversion); (c) fabric stretch certainty; (d) penalty margin between the top size and runner-up size.
  2. Confidence bands are strictly categorical: `High`, `Medium`, or `Low (Insufficient Data)`. Any numeric score is explicitly labelled **"fit score (heuristic)"**, never "accuracy" or "probability".
  3. Calibrate desired-ease allowances across all four preferences as frozen constants: `tight: 1.0"`, `tailored: 2.5"` (labelled "Regular" in UI per deck), `relaxed: 4.0"`, `oversized: 6.0"`.
  4. Encode the comprehensive Ease-Over-Measurement (`EOM_RULES`) table covering hard negative-ease floors and comfortable ease ranges per stretch class (`non_stretch`, `slight_stretch`, `medium_stretch`, `high_stretch`).
  5. Include waist in sizing penalty calculation with calibrated weight.
  6. Detect and report missing measurements transparently. For SKU-03 (missing sleeve length), attach: `[Note: Sleeve length not specified by merchant; sizing calibrated via chest & shoulder circumference]`. For missing shoulder width, cap confidence at `Medium` with an explicit notice.
  7. Use shopper height exclusively for length-fit notes when garment length is provided; otherwise report "height not used (garment length unavailable)" in `missing_data_warnings`.
- **Consequences:**  
  - *Positive:* 100% deterministic, honest sizing logic. Complete preference coverage. Zero false claims of ML accuracy.
  - *Negative:* Requires granular sizing unit tests for all combinations of preferences and stretch classes.
  - *Invariants:* Rigid non-stretch garments with negative ease are strictly eliminated from recommendation.
- **Affected Files & Tests:**  
  - `backend/app/domain/sizing.py`
  - `backend/app/data/brand_matrices.py`
  - `backend/app/schemas/api_contracts.py`
  - `backend/app/api/fit.py`
  - `frontend/components/fit-twin/FitDrawer.tsx`
  - `backend/tests/unit/test_sizing.py`
  - `backend/tests/property/test_domain_properties.py`

---

## ADR-005: Strict Segregation of Live Telemetry Aggregations and Financial Scenario Modeling

- **Status:** Accepted
- **Errata Reference:** Erratum E5 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/06_DATABASE_AND_STATE_SYNC.md` lines 224–231 hardcoded static numbers (`total_shipped_orders: 150`, `cumulative_avoided_losses_inr: ₹54,600`, `net_direct_savings_inr: ₹28,600`) inside the `/v1/analytics/overview` endpoint. These numbers were the pitch deck's 10,000-shipment financial projection, not the actual aggregation of the 150 seeded database orders. Conflating scenario projections with live database telemetry violates auditability and claims integrity.
- **Decision & Binding Resolution:**  
  1. Strictly segregate the merchant dashboard into two independent sections:
     - **"Live (Synthetic) Order Data":** Aggregated dynamically from database rows (`orders`, `delivery_events`, `incentive_interventions`) by `analytics_service`. Reflects real seeded and placed orders (150 -> 151).
     - **"10,000-Shipment Financial Scenario Modeler":** A pure mathematical projection computed by `domain/scenario.py` with editable merchant sliders, defaulting to the exact deck economics.
  2. Implement unit tests confirming that `domain/scenario.py` reproduces the deck numbers with zero error:
     - Baseline RTO: $6,500 \times 26\% + 3,500 \times 2\% = 1,760$ shipments.
     - Combined RTO: $5,850 \times 24\% + 4,150 \times 2\% = 1,487$ shipments.
     - Avoided RTO: $1,760 - 1,487 = 273$ shipments.
     - Gross avoided logistics loss: $273 \times ₹200 = ₹54,600/\text{month}$.
     - Incentive disbursement: $650 \times ₹40 = ₹26,000/\text{month}$.
     - Net direct operating savings: $₹54,600 - ₹26,000 = ₹28,600/\text{month}$ ($₹3,43,200/\text{year}$).
     - Conservative (conversion-only): Avoided RTO: $156$, Net savings: $₹5,200/\text{month}$ ($₹62,400/\text{year}$).
  3. All savings labels must strictly read: *"modelled direct operating savings after incentives, before fees — not net profit."*
  4. RTO (courier delivery failure) and customer returns (post-delivery sizing/remorse returns) are reported in separate KPI cards.
- **Consequences:**  
  - *Positive:* 100% mathematically honest and auditable. Live database operations immediately mutate live KPIs without corrupting scenario models.
  - *Negative:* Requires two separate analytics endpoints (`/v1/analytics/overview` and `/v1/analytics/scenario`).
  - *Invariants:* The term "net profit" is strictly forbidden from all analytics responses and UI copy.
- **Affected Files & Tests:**  
  - `backend/app/domain/scenario.py`
  - `backend/app/services/analytics_service.py`
  - `backend/app/api/analytics.py`
  - `frontend/components/dashboard/OverviewKPIs.tsx`
  - `frontend/components/dashboard/ScenarioModelCard.tsx`
  - `frontend/components/dashboard/RupeesSavedTicker.tsx`
  - `backend/tests/unit/test_scenario.py`
  - `backend/tests/api/test_analytics_api.py`

---

## ADR-006: Database-Backed Catalog State with Extraction Provenance and Sizing Integration

- **Status:** Accepted
- **Errata Reference:** Erratum E6 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/02` line 166 instantiated `vlm_service = GeminiVLMService()`, but line 179 invoked `sizing_engine.calculate_recommendation()`, which accessed a static hardcoded catalog dictionary inside `SizingEngine` (`tech_docs/04` lines 90–111). Gemini extraction was dead code, disconnected from sizing calculations.
- **Decision & Binding Resolution:**  
  1. Curated SKU catalog attributes reside in the database `skus` table (`SkuModel`), storing measurements table, stretch category, drape notes, missing fields, and extraction provenance.
  2. Implement endpoint `POST /v1/catalog/skus/{id}/extract` which triggers the 3-tier multimodal extraction pipeline (TTL Cache -> Gemini 3.8 Flash -> Verified Benchmark Fixture) and persists extracted attributes with an auditable `provenance` tag (`live_gemini`, `cache`, `fixture`, `manual`).
  3. The sizing engine accepts persisted garment attributes directly from `catalog_service` / database, allowing missing measurements (e.g. missing sleeve length in SKU-03) to flow directly into confidence bands and shopper gap warnings.
  4. The Storefront PDP includes a "Catalog Intelligence" panel rendering extracted attributes and provenance badge (e.g., `Live · gemini-3.8-flash` or `Mode: Verified Catalog Benchmark`).
- **Consequences:**  
  - *Positive:* Seamlessly bridges Gemini AI extraction with deterministic sizing logic; live AI execution is genuinely reflected in sizing decisions.
  - *Negative:* Catalog lookup requires database query before sizing evaluation.
  - *Invariants:* Missing fields from VLM extraction are stored as `null` and never fabricated.
- **Affected Files & Tests:**  
  - `backend/app/db/models.py` (`SkuModel`)
  - `backend/app/services/catalog_service.py`
  - `backend/app/services/fit_service.py`
  - `backend/app/api/catalog.py`
  - `backend/app/api/fit.py`
  - `frontend/components/fit-twin/CatalogIntelligencePanel.tsx`
  - `backend/tests/api/test_catalog_api.py`
  - `backend/tests/integration/test_catalog_flow.py`

---

## ADR-007: REST API Parameter Normalization and Canonical Route Architecture

- **Status:** Accepted
- **Errata Reference:** Erratum E7 (from `AGENTS.md` §5)
- **Context & Problem:**  
  Specs contained conflicting route definitions. For example, `tech_docs/02` line 102 defined `order_id` inside the request body of `OrderVerificationRequest`, while line 191 defined the route as `POST /v1/orders/{order_id}/verify`. Essential administrative and operational endpoints (`GET /v1/catalog/skus`, `POST /v1/catalog/skus/{id}/extract`, `GET /v1/analytics/scenario`, `POST /v1/demo/reset`) were omitted from router registrations.
- **Decision & Binding Resolution:**  
  1. Standardize strictly on canonical RESTful conventions per `AGENTS.md` §7.
  2. Resource identifiers (`order_id`, `sku_id`) are passed exclusively as URL path parameters in mutation routes: `POST /v1/orders/{order_id}/verify`, `POST /v1/orders/{order_id}/ndr`, `POST /v1/catalog/skus/{sku_id}/extract`. Redundant ID fields are removed from request bodies.
  3. Fully implement and expose all missing routes:
     - `GET /v1/catalog/skus` & `GET /v1/catalog/skus/{sku_id}`
     - `POST /v1/catalog/skus/{sku_id}/extract`
     - `GET /v1/analytics/scenario`
     - `POST /v1/demo/reset`
- **Consequences:**  
  - *Positive:* Clean, predictable, industry-standard API surface; seamless TypeScript client generation via `openapi-typescript`.
  - *Negative:* Frontend clients must conform strictly to URL path parameter bindings.
  - *Invariants:* Path parameter names match across router signatures and schema definitions.
- **Affected Files & Tests:**  
  - `backend/app/api/catalog.py`
  - `backend/app/api/orders.py`
  - `backend/app/api/analytics.py`
  - `backend/app/api/demo.py`
  - `backend/app/schemas/api_contracts.py`
  - `frontend/lib/api/client.ts`
  - `backend/tests/api/test_orders_api.py`
  - `backend/tests/api/test_catalog_api.py`

---

## ADR-008: Strict CORS Origin Parsing and Credentials Policy

- **Status:** Accepted
- **Errata Reference:** Erratum E8 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/02` lines 158–163 configured `allow_origins=["*"]` combined with `allow_credentials=True`. Modern W3C Fetch and CORS standards explicitly forbid wildcard origins when credentials are allowed, causing browsers to reject cross-origin requests in production.
- **Decision & Binding Resolution:**  
  1. Parse allowed origins dynamically from `CORS_ORIGINS` environment variable as a comma-separated list of fully qualified domains (e.g. `http://localhost:3000,https://returnzero-ai.vercel.app`).
  2. Set `allow_credentials=False` because ReturnZero AI's demo storefront and dashboard do not use HTTP cookies or session credentials (state is managed client-side and via demo headers).
  3. Validate origins on FastAPI startup; log configured origins at application boot.
- **Consequences:**  
  - *Positive:* Browser compliance across Chrome, Safari, Firefox; zero cross-origin rejection in production deployments.
  - *Negative:* Deploying a new frontend domain requires updating `CORS_ORIGINS` on the backend container.
  - *Invariants:* `allow_credentials=True` is never combined with wildcard origins.
- **Affected Files & Tests:**  
  - `backend/app/main.py`
  - `backend/app/config.py`
  - `backend/tests/api/test_cors.py`

---

## ADR-009: Idempotent Lifespan Database Seeding, Seeded RNG, and Demo State Reset

- **Status:** Accepted
- **Errata Reference:** Erratum E9 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/08` line 60 ran `python -m database.seed_orders` in the Dockerfile CMD on every container start, but `seed_orders.py` in `tech_docs/06` only defined a generator function without executing database inserts. Running seeds on restart would either fail on primary keys or duplicate rows. Furthermore, `random` was unseeded, deprecated `datetime.utcnow()` was used throughout, and `FitLogModel` was omitted from model definitions despite existing in the ERD.
- **Decision & Binding Resolution:**  
  1. Database seeding executes inside the FastAPI **lifespan startup handler** and is strictly idempotent: it queries `SELECT COUNT(*) FROM orders` and inserts seed records only if the table is empty.
  2. Use a deterministic seeded random number generator: `rng = random.Random(20261128)` to ensure identical dataset generation across all environments.
  3. Use modern, timezone-aware UTC timestamps: `datetime.now(timezone.utc)`.
  4. Fully define `FitLogModel` in SQLAlchemy declarative models.
  5. Seed distribution strictly adheres to `PRE_EVENT_CHECKLIST.md` §3 (150 historical orders: 65% COD / 35% Prepaid; 40% Tier-1, 35% Tier-2, 25% Tier-3; all 6 outcome statuses; all marked `is_synthetic=True`).
  6. Implement `POST /v1/demo/reset` guarded by `DEMO_MODE=true` and `X-Demo-Token` header, allowing instant restoration of the database to the pristine 150-order state at any time.
- **Consequences:**  
  - *Positive:* Reliable startup on cold starts; zero duplication; deterministic analytics; instantaneous demo reset capability.
  - *Negative:* In-memory or SQLite database resets on container redeploy unless persistent volume is mounted.
  - *Invariants:* All seeded orders have `is_synthetic=True`.
- **Affected Files & Tests:**  
  - `backend/app/db/models.py`
  - `backend/app/db/seed.py`
  - `backend/app/api/demo.py`
  - `backend/app/main.py`
  - `backend/Dockerfile`
  - `backend/tests/unit/test_seed.py`
  - `backend/tests/api/test_demo_api.py`

---

## ADR-010: Frontend Framework Pinning — Next.js 14.2 and React 18.3

- **Status:** Accepted
- **Errata Reference:** Erratum E10 (from `AGENTS.md` §5)
- **Context & Problem:**  
  Specifications vaguely cited "Next.js 14 / React 18/19". React 19 introduced breaking typing changes (e.g. `useRef` typing, form action modifications) and hydration lifecycle adjustments that break third-party client UI libraries such as Framer Motion and Radix UI primitives.
- **Decision & Binding Resolution:**  
  1. Pin the frontend dependencies strictly to **Next.js 14.2.x (latest stable patch), React 18.3.x, and React-DOM 18.3.x**.
  2. If security audits (`npm audit`) flag high/critical advisories in transitive packages, evaluate an explicit override or patch without migrating to React 19 during the 48-hour sprint.
- **Consequences:**  
  - *Positive:* Total stability with ecosystem packages, zero React 19 hydration mismatches or peer-dependency compilation errors.
  - *Negative:* Foregoes experimental React 19 action features.
  - *Invariants:* `package.json` pins `react: "^18.3.1"` and `react-dom: "^18.3.1"`.
- **Affected Files & Tests:**  
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `frontend/tests/smoke.test.tsx`

---

## ADR-011: Canonical Design System Token Standardization

- **Status:** Accepted
- **Errata Reference:** Erratum E11 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/03` and `PRE_EVENT_CHECKLIST.md` §4 used conflicting token names for Tailwind configuration (`kartai.bg` vs `canvas`, `kartai.primary` vs `brand`), leading to inconsistent styling and broken CSS utility classes.
- **Decision & Binding Resolution:**  
  1. Adopt the canonical palette and token naming from `tech_docs/03`:
     - `canvas`: `#F5F0FF` (Soft Lavender background)
     - `surface`: `#FFFFFF` (Pure white container cards)
     - `brand`: `#7938F5` (Electric Purple primary CTA)
     - `brandHover`: `#6525E5`
     - `ink`: `#171321` (Deep charcoal primary text)
     - `inkMuted`: `#6B6280` (Muted body text)
     - `border`: `#D4C2FC` (Lavender border)
     - `borderLight`: `#E5D9FD`
     - `accentEmerald`: `#059669` (Success / verified badge)
     - `accentRose`: `#E11D48` (Warning / missing data)
     - `accentAmber`: `#F59E0B` (Review risk status)
  2. No raw hex codes are permitted in JSX component markup; all styling must use Tailwind semantic classes (`bg-canvas`, `text-ink`, `bg-brand`, etc.).
- **Consequences:**  
  - *Positive:* Cohesive, premium design aesthetic aligned with KartAI brand guidelines; easy theme modifications.
  - *Negative:* Components must strictly use configured design tokens.
  - *Invariants:* Zero inline hex colors in JSX markup.
- **Affected Files & Tests:**  
  - `frontend/tailwind.config.ts`
  - `frontend/app/globals.css`
  - `frontend/components/**/*.tsx`

---

## ADR-012: State-Conditional Copy Architecture and Claims Governance

- **Status:** Accepted
- **Errata Reference:** Erratum E12 (from `AGENTS.md` §5)
- **Context & Problem:**  
  Spec UI mockups showed static strings: *"We verified your fit!"*, *"Priority 48-hour dispatch"*, *"10%–28% conversion shift"*, and *"94% confidence"*, even when the user had completely bypassed the fit drawer or when no priority dispatch logic existed in the backend. These constitute fabricated claims and misleading dark patterns.
- **Decision & Binding Resolution:**  
  1. Nudge copy must be strictly conditional on actual application state:
     - Only display *"We verified your fit! Pay via UPI now to save ₹40..."* if `has_used_fit_twin` is `True`.
     - If fit was not used, display: *"Pay via UPI to save ₹40 and secure contactless delivery."*
  2. *"Priority Dispatch"* must set a real `dispatch_priority=True` boolean flag on the persisted order record in the database, displayed in the merchant order stream.
  3. Prohibit all fabricated strings, unsourced metrics, and buzzwords listed in `AGENTS.md` §10 (e.g. "₹18,000 crore", "30-35% national RTO", "53%/32%/15%", "100% accuracy", "XGBoost", "Gemini 2.0").
  4. Enforce this policy automatically via `scripts/check_claims.py` in pre-commit hooks and GitHub Actions CI.
- **Consequences:**  
  - *Positive:* 100% authentic, ethical, CCPA/DPDP-compliant UX. Builds high trust with evaluators.
  - *Negative:* Copy variations must be maintained and unit-tested for multiple transaction states.
  - *Invariants:* `scripts/check_claims.py` passes with zero violations.
- **Affected Files & Tests:**  
  - `backend/app/domain/incentive.py`
  - `backend/app/db/models.py` (`OrderModel.dispatch_priority`)
  - `frontend/components/checkout/OrderReviewModal.tsx`
  - `scripts/check_claims.py`
  - `backend/tests/unit/test_incentive.py`
  - `frontend/tests/components/OrderReviewModal.test.tsx`

---

## ADR-013: 4-SKU Catalog Scope and Fabric Uncertainty Demonstration

- **Status:** Accepted
- **Errata Reference:** Erratum E13 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `ROUND_2_BUILDATHON_PLAYBOOK.md` §3 mentioned 15 SKUs, while `PRE_EVENT_CHECKLIST.md` §2 and the pitch deck specified 4 curated fashion SKUs. Attempting to curate 15 rich fashion SKUs with multimodal imagery and measurement tables within 48 hours dilutes quality and risks incomplete metadata.
- **Decision & Binding Resolution:**  
  1. Standardize strictly on **4 curated high-fidelity D2C fashion SKUs**:
     - **SKU-01:** Handcrafted Chanderi Silk Anarkali Kurta (100% Chanderi Silk, zero-stretch 0% elastane, rigid armholes/shoulders, bust 38" M -> recommends Size L for Zara M shopper).
     - **SKU-02:** Relaxed Linen-Cotton Mandarin Collar Shirt (70% Cotton / 30% Linen, slight natural stretch, relaxed drape, chest 40" M -> confirms Size M for H&M M shopper).
     - **SKU-03:** Structured Denim Trucker Jacket (99% Cotton / 1% Spandex, 320 GSM twill, **intentionally missing sleeve length** to demonstrate honest AI uncertainty reporting and gap warnings).
     - **SKU-04:** Flowy Floral Rayon Tiered Maxi Dress (100% Viscose Rayon, fluid drape, smocked elastic waist).
  2. Store rich physical garment attributes, size tables, drape notes, and high-resolution editorial photos for all 4 SKUs.
- **Consequences:**  
  - *Positive:* Deep, polished, crash-proof showcase. SKU-03 provides a powerful live demonstration of responsible AI acknowledging missing data.
  - *Negative:* Catalog is fixed to 4 demo garments.
  - *Invariants:* SKU-03 missing sleeve length must trigger explicit UI warning and capped confidence.
- **Affected Files & Tests:**  
  - `backend/app/db/seed.py`
  - `backend/app/data/fixtures/*.json`
  - `frontend/public/products/`
  - `backend/tests/unit/test_sizing.py`
  - `backend/tests/api/test_catalog_api.py`

---

## ADR-014: Margin Anti-Abuse Controls and Intervention Reason Codes

- **Status:** Accepted
- **Errata Reference:** Erratum E14 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/05` §4 outlined anti-abuse guardrails (coupon stacking cap $\le 20\%$ of GMV; 3 consecutive doorstep refusals withhold cash discount in favor of non-cash gifts), but the code omitted them entirely, allowing unconstrained discount stacking that would destroy merchant gross margin.
- **Decision & Binding Resolution:**  
  1. Implement both anti-abuse guardrails as pure domain functions in `backend/app/domain/incentive.py`.
  2. Total allowable discount (merchant coupon + dynamic UPI incentive) is hard-capped at 20% of cart GMV. If remaining headroom $< ₹25$, cash offer is withheld with reason `REASON_COUPON_CAP`.
  3. If shopper history indicates 3 consecutive delivery refusals, cash incentive is withheld in favor of a non-monetary gift kit ("Complimentary garment care kit + guaranteed express delivery") with reason `REASON_REPEAT_REFUSAL`.
  4. Persist an explicit, auditable `reason_code` string on every evaluated `IncentiveInterventionModel` row:
     - `REASON_INSUFFICIENT_MARGIN`
     - `REASON_ELEVATED_RISK_CONVERTIBLE`
     - `REASON_PREPAID_OPTIMAL`
     - `REASON_LOW_RISK`
     - `REASON_COUPON_CAP`
     - `REASON_REPEAT_REFUSAL`
- **Consequences:**  
  - *Positive:* Bulletproof margin defense; fully explainable incentive decisions in database telemetry and admin dashboard.
  - *Negative:* Requires customer refusal count and coupon discount inputs in quote request payload.
  - *Invariants:* Cumulative discount never exceeds 20% of GMV.
- **Affected Files & Tests:**  
  - `backend/app/domain/incentive.py`
  - `backend/app/db/models.py` (`IncentiveInterventionModel.reason_code`)
  - `backend/app/schemas/api_contracts.py`
  - `backend/tests/unit/test_incentive.py`

---

## ADR-015: Conversational State Machine Completeness, Consent Flow, and Dynamic Order Binding

- **Status:** Accepted
- **Errata Reference:** Erratum E15 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/07` lines 30–31 branched address checks on `<15 chars` -> RequestLandmark and `>25 chars` -> RequestSlot, leaving addresses 15–25 chars in length completely unhandled. The simulator script hardcoded customer "Aarav" and order "#RZ-1042", lacked an explicit consent opt-in step, had no opt-out ("STOP") handler, and omitted transparency indicators.
- **Decision & Binding Resolution:**  
  1. Address branching uses the pure domain function `address_quality()` returning `Complete`, `NeedsLandmark`, or `Poor` (eliminating arbitrary character length gaps).
  2. Conversational state machine dynamically binds to the actual order placed by the user in the storefront (customer name, live order ID, SKU title, selected size).
  3. Step 1 of the conversation is an explicit consent opt-in (*"Namaste [Name]! Would you like delivery updates via WhatsApp?"*).
  4. Support opt-out keyword ("STOP") transitioning order to `Opted_Out` and halting automated messaging.
  5. Include sticky top transparency ribbon: **"Simulated — no real WhatsApp message is sent"**.
  6. Provide an interactive **NDR simulation toggle** in the simulator UI, allowing judges to simulate a doorstep delivery failure, select a reschedule time slot, and witness the order transition to `NDR_Resolved` in the database.
- **Consequences:**  
  - *Positive:* Comprehensive state machine with zero unhandled branches; authentic DPDP/WhatsApp policy compliance; dynamic integration with storefront orders.
  - *Negative:* State machine requires client-side state management alongside backend webhook calls.
  - *Invariants:* Address evaluation branches on `address_quality()`, never raw character counts.
- **Affected Files & Tests:**  
  - `frontend/components/simulator/conversationMachine.ts`
  - `frontend/components/simulator/WhatsAppPhoneSimulator.tsx`
  - `frontend/app/simulator/page.tsx`
  - `backend/app/api/orders.py`
  - `frontend/tests/components/conversationMachine.test.ts`
  - `backend/tests/api/test_orders_api.py`

---

## ADR-016: Non-Blocking Async Gemini Integration, Dual-Key Failover, and Resilient Circuit Breakers

- **Status:** Accepted
- **Errata Reference:** Erratum E16 (from `AGENTS.md` §5)
- **Context & Problem:**  
  `tech_docs/01` lines 126–134 invoked synchronous `client.models.generate_content()` inside an async FastAPI handler, blocking the Python event loop. No timeout was enforced, `BACKUP_GEMINI_API_KEY` was accepted in settings but never used on failure, and the promised fallback to verified fixtures upon latency $>4.0$s was completely unimplemented.
- **Decision & Binding Resolution:**  
  1. Execute Gemini calls non-blockingly using native async client methods or `starlette.concurrency.run_in_threadpool`.
  2. Enforce a strict hard timeout: `GEMINI_TIMEOUT_S = 4.0` seconds via `asyncio.wait_for`.
  3. Implement dual-key failover: on HTTP 429 quota exhaustion, timeout, or 5xx error, immediately attempt one retry using `BACKUP_GEMINI_API_KEY`.
  4. If backup key also fails or times out, immediately return pre-computed verified fixtures from `backend/app/data/fixtures/<sku>.json` with `provenance="fixture"` and UI badge `Mode: Verified Catalog Benchmark`. Never crash with a 500 error or red error box.
  5. In-memory circuit breaker: after 3 consecutive live API failures, automatically bypass live network calls for 60 seconds.
  6. Cache key computed as: `hash(sku_id, image_sha256, model_id, prompt_version)` with TTL cache.
- **Consequences:**  
  - *Positive:* 100% demo uptime guaranteed even under total Wi-Fi loss, quota exhaustion, or Google Cloud outages. Event loop remains responsive.
  - *Negative:* Requires maintaining verified fixture JSON files for all 4 SKUs.
  - *Invariants:* The application never throws an unhandled 500 error due to external AI provider failure.
- **Affected Files & Tests:**  
  - `backend/app/integrations/gemini/adapter.py`
  - `backend/app/integrations/gemini/extractor.py`
  - `backend/app/config.py`
  - `backend/app/data/fixtures/*.json`
  - `backend/tests/resilience/test_gemini_resilience.py`

---

## ADR-017: D2C Fashion Focus Alignment and Explicit Rejection of Stale Q-Commerce / Pharmacy Specs

- **Status:** Accepted
- **Ambiguity Reference:** Spec Discrepancy & Precedence Resolution
- **Context & Problem:**  
  Initial dispatch prompts mentioned generic multi-industry keywords ("grocery lists", "pharmacy prescriptions", "Blinkit/Zepto quick-commerce sync", "pgvector"). However, `AGENTS.md` §1, `FINAL_DECK_COPY.md`, and `SOURCES_AND_ASSUMPTIONS.md` §D explicitly document that ReturnZero AI was finalized exclusively as a **Fit Intelligence and Delivery Assurance layer for D2C Fashion Apparel**, and that all pharmacy, grocery, and vector search concepts were explicitly removed in Round 1.
- **Decision & Binding Resolution:**  
  1. The project scope is 100% focused on D2C Fashion Apparel in India (tackling the 26% COD RTO rate and sizing returns).
  2. All pharmacy, quick-commerce, prescription, and pgvector requirements are explicitly rejected as STALE.
  3. The VLM multimodal pipeline strictly processes fashion garment photos (front & detail views) and merchant size charts; shoppers do not upload photos.
- **Consequences:**  
  - *Positive:* Sharp, cohesive, award-winning problem statement aligned with the submitted pitch deck. Eliminates scope sprawl.
  - *Negative:* Disregards obsolete prompt keywords.
  - *Invariants:* System domain is strictly D2C fashion apparel.
- **Affected Files & Tests:**  
  - `docs/PROJECT_CONTEXT.md`
  - `backend/app/schemas/api_contracts.py`
  - `frontend/app/page.tsx`

---

## ADR-018: In-Browser WhatsApp Simulator vs Live Meta/Twilio Telecom Dependency Elimination

- **Status:** Accepted
- **Ambiguity Reference:** Buildathon Disaster Prevention & Scope Fence
- **Context & Problem:**  
  Integrating live Meta WhatsApp Cloud API or Twilio requires business verification taking 2–4 business days, webhook tunneling via ngrok that frequently disconnects during live demos, and asks hackathon judges to enter private phone numbers. `DEMO_DAY_DISASTER_PREVENTION.md` and `AGENTS.md` §3.8 explicitly designate live telecom integration as a fatal hackathon trap.
- **Decision & Binding Resolution:**  
  1. Eliminate external telecom dependencies entirely. Build an authentic in-browser iPhone WhatsApp simulator component (`frontend/components/simulator/WhatsAppPhoneSimulator.tsx`).
  2. The simulator executes the identical conversational state machine, payload validation, and calls the exact same backend webhook endpoints (`/v1/orders/{id}/verify`, `/v1/orders/{id}/ndr`) as a live webhook runner.
  3. Works 100% reliably in offline conditions, protects judge privacy, and requires zero external API credentials.
- **Consequences:**  
  - *Positive:* Flawless, zero-lag interactive live demo; zero telecom billing or approval blockers; zero ngrok disconnect risks.
  - *Negative:* Judges interact through the browser simulator rather than their physical handset.
  - *Invariants:* Backend webhook endpoints accept standard JSON payloads that match live webhook formats.
- **Affected Files & Tests:**  
  - `frontend/components/simulator/WhatsAppPhoneSimulator.tsx`
  - `frontend/app/simulator/page.tsx`
  - `backend/app/api/orders.py`
  - `frontend/tests/components/WhatsAppPhoneSimulator.test.tsx`

---

## ADR-019: Local Async SQLite Persistence with PostgreSQL Compatibility for Hackathon Zero-Dependency Delivery

- **Status:** Accepted
- **Ambiguity Reference:** Database Architecture & Provisioning Risk
- **Context & Problem:**  
  Relying on external cloud databases (e.g. Supabase, Neon, AWS RDS) introduces network latency, connection pooling failures, cloud credential friction, and database provisioning blockers during local development and rapid evaluation.
- **Decision & Binding Resolution:**  
  1. Use async SQLite (`sqlite+aiosqlite:///./returnzero.db`) via SQLAlchemy 2.0 async engine as the default persistence layer.
  2. Design all table schemas, data types, and indexes to be 100% PostgreSQL-compatible (using standard JSON, composite indexes, and UTC datetimes), enabling a 1-line connection string migration to PostgreSQL if required (`postgresql+asyncpg://...`).
  3. Combine with idempotent lifespan seeding (ADR-009) and `POST /v1/demo/reset` to guarantee instant recovery and zero data loss on serverless/container restarts.
- **Consequences:**  
  - *Positive:* Zero external database provisioning required; instantaneous local startup; seamless CI execution; zero network latency for database queries (<5ms).
  - *Negative:* Ephemeral container restarts on free hosts reset database to seed state (mitigated by automated lifespan re-seeding).
  - *Invariants:* All model definitions and queries are strictly compatible with both SQLite and PostgreSQL.
- **Affected Files & Tests:**  
  - `backend/app/db/models.py`
  - `backend/app/db/session.py`
  - `backend/app/db/repositories.py`
  - `backend/tests/conftest.py`

---

## ADR-020: Disambiguation and Segregation of Blended RTO vs. COD-Only RTO and Customer Returns

- **Status:** Accepted
- **Reference:** Audit Item B4 / `SOURCES_AND_ASSUMPTIONS.md` §B
- **Date:** 2026-11-24
- **Context & Problem:**  
  The dashboard showed "Courier RTO Rate 28.5%" (or 28.67% across 150 seeded orders). Without explicit labelling of the denominator, judges or observers may confuse this blended rate (`total_rto_orders / total_orders`) with COD-only RTO (which is ~40.8% in seed data, or ~26% in Shipway FY25 benchmark) or customer returns (post-delivery fit/defect returns, which is 8.0%).
- **Decision & Binding Resolution:**  
  1. Clearly label the primary KPI card as "Blended RTO Rate" with subtitle displaying COD and Prepaid RTO breakdowns: `COD: 40.8% · Prepaid: 5.8%`.
  2. Maintain strict separation between Courier RTO (failed delivery before handover) and Customer Return (post-delivery fit/defect return) in accordance with `SOURCES_AND_ASSUMPTIONS §B`.
  3. Ensure both backend `AnalyticsOverviewResponse` and frontend API types expose explicit `cod_rto_count`, `cod_rto_rate_pct`, `prepaid_rto_count`, and `prepaid_rto_rate_pct`.
  4. Attach tooltip descriptions citing `SOURCES_AND_ASSUMPTIONS §B` definitions on hover.
- **Consequences:**  
  - *Positive:* Eliminates any risk of judges misinterpreting blended telemetry as COD-only RTO; maintains auditable mathematical definitions across the dashboard.
  - *Negative:* Slightly more verbose subtitle on the RTO KPI card.
  - *Invariants:* Denominator of `rto_rate_pct` is always `total_orders`; denominator of `cod_rto_rate_pct` is always `cod_orders_count`.
- **Affected Files & Tests:**  
  - `backend/app/schemas/api_contracts.py`
  - `backend/app/db/repositories.py`
  - `frontend/lib/api/types.ts`
  - `frontend/components/dashboard/OverviewKPIs.tsx`
  - `docs/DECISIONS.md`
  - `docs/SOURCES_AND_ASSUMPTIONS.md`

---

## ADR-021: Next.js 14.2 Patch Upgrade to 14.2.35 and Dependency Vulnerability Audit

- **Status:** Accepted
- **Reference:** Audit Item B5 / Erratum E10 (`AGENTS.md` §5)
- **Date:** 2026-11-24
- **Context & Problem:**  
  The frontend package was previously pinned to `next@14.2.18`. While `AGENTS.md` Erratum E10 strictly forbids upgrading to Next.js 15 or React 19, newer security and stability patches within the 14.2.x series are recommended. `npm audit` flagged vulnerabilities in older dependencies while suggesting breaking major upgrades (`next@16`).
- **Decision & Binding Resolution:**  
  1. Upgrade `next` and `eslint-config-next` from `14.2.18` to `14.2.35` (the latest available release in the 14.2.x long-term stability branch).
  2. Reject `npm audit fix --force` which would introduce breaking upgrades to Next 15/16 and React 19 in direct violation of Erratum E10.
  3. Re-verify the full build (`next build`), typecheck (`tsc --noEmit`), and lint (`eslint`) to confirm 100% compilation and bundle pass.
- **Consequences:**  
  - *Positive:* Incorporates critical bug and regression fixes from 17 Next.js 14.2 patch releases without any breaking changes to the App Router or React 18.3 runtime.
  - *Negative:* None.
  - *Invariants:* `next` version remains strictly within `14.2.x`; `react` version remains strictly `18.3.1`.
- **Affected Files & Tests:**  
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `docs/DECISIONS.md`

---

## ADR-022: Boundary Validation, Address Sanitization, and State Resilience Bug Fixes

- **Status:** Accepted
- **Reference:** Implementation Plan Bugs 1–6 / Exploit Hardening
- **Date:** 2026-11-24
- **Context & Problem:**  
  During adversarial inspection and penetration analysis of the codebase, 6 edge-case and boundary vulnerabilities were identified:
  1. Repeated address verification in `orders.py` appended redundant `, Near {landmark}` and produced `Near Near` duplications.
  2. Frontend checkout evaluated incentives with a hardcoded `risk_score_index: 55` instead of awaiting the dynamic `evaluateRisk` result.
  3. `FitRecommendRequest` allowed empty or whitespace strings (`known_size: ""`), bypassing schema validation and corrupting explanation text.
  4. Direct navigation to `/simulator` without parameters defaulted to unbound `ORD-DEMO-001`, leading to 404s on verification.
  5. Invalid/non-existent SKUs on PDP (e.g. `/products/SKU-999`) silently rendered SKU-01 instead of a clean 404 state.
  6. Order confirmation page rendered hardcoded fallback strings (`"Priya Sharma"`, `"House 12, Sector 15, Delhi"`) during load or error states.
  7. Order creation permitted discounts exceeding the total cart value.
- **Decision & Binding Resolution:**  
  1. Update `orders.py` verification logic to guard against redundant landmark concatenation and strip duplicated landmark prefixes.
  2. Sequence `evaluateRisk` before `getIncentiveQuote` in `checkout/page.tsx`, passing the real `risk_score_index`.
  3. Enforce `min_length=1` and whitespace-stripping `@field_validator` on `known_brand` and `known_size` in `FitRecommendRequest`.
  4. In `simulator/page.tsx`, fetch the latest live order from `/v1/orders?limit=1` or fall back to canonical seeded order `RZ-1042`.
  5. In `products/[skuId]/page.tsx`, render an explicit `ProductNotFound` component with a back-link when the SKU is not in the catalog.
  6. In `confirmation/[orderId]/page.tsx`, remove hardcoded dummy recipient/address strings in favor of dynamic loading placeholders with proper loading and error states.
  7. In `orders.py`, reject `applied_discount_inr > subtotal`, any discount applied to COD orders, and discounts exceeding the ₹40.00 maximum incentive ceiling with HTTP 422 Unprocessable Content.
- **Consequences:**  
  - *Positive:* Hardens all boundaries against exploits and malformed payloads; guarantees database synchronicity across all direct navigation flows; prevents state desynchronization.
  - *Negative:* None.
  - *Invariants:* All requests must pass Pydantic boundary validation; real evaluated risk scores are always passed to the incentive solver; COD remains unblocked across all flows.
- **Affected Files & Tests:**  
  - `backend/app/api/orders.py`
  - `backend/app/schemas/api_contracts.py`
  - `backend/tests/api/test_orders_and_checkout_api.py`
  - `frontend/app/checkout/page.tsx`
  - `frontend/app/simulator/page.tsx`
  - `frontend/app/products/[skuId]/page.tsx`
  - `frontend/app/confirmation/[orderId]/page.tsx`
  - `frontend/tests/smoke.test.tsx`
  - `docs/DECISIONS.md`

---

## ADR-023: WCAG AA Violet Palette Refinement, Tailwind Scale Preservation, and Server-Side Demo Token Proxy

- **Status:** Accepted
- **Reference:** Phase B Implementation Plan (`frontend-design` pass + `AGENTS.md` §6 Engineering Standards)
- **Date:** 2026-11-25
- **Context & Problem:**  
  1. `frontend/tailwind.config.ts` previously defined `emerald`, `rose`, and `amber` as bare hex strings under `theme.extend.colors`, overwriting Tailwind's built-in 50–950 utility scales and silently breaking status badges (`bg-emerald-50`, `text-emerald-700`, `bg-amber-50`, etc.).
  2. The legacy `#7938F5` violet accent against `#F5F0FF` canvas yielded borderline contrast for small UI labels, and `frontend` had no Google font loading, route transition wrapper, or ErrorBoundary guardrails.
  3. `DemoResetButton.tsx` and `client.ts` hardcoded `"secret-demo-token-2026"` directly in client-side JS bundles (which failed with HTTP `403` against backend default `"returnzero-demo-secret-2026"` and violated secret hygiene).
- **Decision & Binding Resolution:**  
  1. Restore full Tailwind `emerald`/`rose`/`amber` color scales while refining brand tokens (`canvas: #FAF8FD`, `surface: #FFFFFF`, `subtle: #F9F6FE`, `brand: #6D28D9` for WCAG AA contrast, `brandHover: #5B21B6`, `ink: #171321`, `inkMuted: #585266`, `trust: #059669`, `warn: #D97706`, `danger: #B42318`).
  2. Load `Playfair Display`, `Plus Jakarta Sans`, and `JetBrains Mono` via self-hosted `@fontsource` packages (`@fontsource/playfair-display`, `@fontsource/plus-jakarta-sans`, `@fontsource/jetbrains-mono`) in `app/layout.tsx` paired with CSS custom properties in `app/globals.css` (preventing flaky build-time Google Fonts network failures), add GPU-composited `app/template.tsx` route transitions honoring `prefers-reduced-motion`, and wrap modules in `ErrorBoundary` + TanStack Query `AppProviders`.
  3. Proxy demo database resets through Next.js server route handler `POST /api/demo/reset`, keeping `DEMO_TOKEN` out of `NEXT_PUBLIC_*` client JavaScript bundles.
- **Consequences:**  
  - *Positive:* Preserves Tailwind utility scales, enforces WCAG AA contrast, delivers smooth cross-route transitions, and eliminates hardcoded/leaked client tokens.
  - *Negative:* None.
- **Affected Files & Tests:**  
  - `frontend/tailwind.config.ts`
  - `frontend/app/globals.css`
  - `frontend/app/layout.tsx`
  - `frontend/app/template.tsx`
  - `frontend/app/api/demo/reset/route.ts`
  - `frontend/components/providers/AppProviders.tsx`
  - `frontend/components/ui/ErrorBoundary.tsx`
  - `frontend/components/dashboard/DemoResetButton.tsx`
  - `frontend/lib/api/client.ts`
  - `frontend/lib/api/hooks.ts`
  - `frontend/lib/api/types.ts`
  - `frontend/lib/store.ts`
  - `docs/DECISIONS.md`
