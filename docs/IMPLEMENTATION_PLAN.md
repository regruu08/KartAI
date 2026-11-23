# ReturnZero AI — Phased Implementation Plan

**Project:** ReturnZero AI (Team BioXtreme)  
**Hackathon:** Code to Cart Round 2 Buildathon (KartAI x CodeXcelerate)  
**Target Root:** `c:\Users\anujs\OneDrive\Desktop\kart_com`  
**Date:** 2026-11-23  
**Status:** Approved Master Blueprint (Phases 0 through 8)  

---

## Executive Overview & Architectural Invariants

This implementation plan defines the exhaustive engineering execution sequence for ReturnZero AI across **Phases 0 through 8**. Each phase is an atomic, independently verifiable increment. No phase may commence until all quality gates, type checks, test coverage floors, and claims constraints of the preceding phase pass cleanly.

### Core Architectural Invariants
1. **Generative AI is strictly isolated to unstructured interpretation:** Gemini 3.8 Flash extracts attributes from garment photos/descriptions and normalizes conversational addresses. It is never used for arithmetic, risk scoring, or size selection.
2. **Deterministic Domain Core:** All sizing recommendations, risk scores, cash incentive headroom, anti-abuse checks, and financial scenarios are pure, deterministic Python code with $\ge 95\%$ unit test coverage.
3. **No Dark Patterns & Guaranteed COD:** Cash on Delivery remains 100% available at all times (`cod_remains_available: true`). Dynamic UPI discounts are purely optional positive nudges.
4. **Zero-Hallucination Data Gap Reporting:** Missing merchant measurements (e.g. SKU-03 missing sleeve length) are explicitly flagged as gaps and lower the computed confidence band.
5. **Separation of Live Telemetry & Financial Projections:** The dashboard strictly segregates real database aggregations (150 seeded orders) from the interactive 10,000-shipment scenario model.
6. **Zero External Telecom or Payment Gateway Blockers:** The in-browser WhatsApp simulator and simulated UPI modal eliminate third-party credential dependencies and verification delays.

---

## Phase Execution Summary & Dependency Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 0: Scaffolding, Tooling, Quality Harness & Day-0 Cloud Config     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Pure Domain Core & Mathematical Invariants (No I/O)            │
│ (money, sizing, risk, incentive, address, scenario)                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Database Schema, Async Repositories, Lifespan Seeding & Reset  │
│ (SQLite+Postgres models, 150-order deterministic seed, CRUD routes)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│ Phase 3: Gemini VLM Adapter,      │ │ Phase 4: Storefront PDP, Fit-Twin │
│ Resilient Extractor & Normalizer  │ │ Drawer & WhatsApp Simulator       │
│ (Dual-key, 4s timeout, fixtures)  │ │ (Catalog display, size recommendation,│
└─────────────────┬─────────────────┘ │ in-browser conversational machine)│
                  │                   └─────────────────┬─────────────────┘
                  │                                     │
                  └──────────────────┬──────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 5: Checkout Shield, Risk/Incentive APIs & Order Flow              │
│ (OrderReviewModal, dynamic UPI solver, anti-abuse, real order sync)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 6: Merchant Command Center Dashboard                              │
│ (Live DB KPI row, Order Stream, City Tier Chart, 10k Scenario Modeler)  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 7: Disaster Prevention Hardening & Full Resilience Suite          │
│ (Circuit breakers, offline fallbacks, Lighthouse >=90, claims check)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 8: Cloud Deployment (Vercel + Render), Golden Demo & Release      │
│ (Production smoke tests, demo video recording, Unstop submission)       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Phase Breakdown

### Phase 0: Scaffolding, Tooling & Quality Harness

#### 1. Objective & Scope
Establish the monorepo workspace structure, dependency management configurations, strict linting/typing rules, pre-commit hooks, CI/CD pipeline, and Day-0 deployment scripts. Verify that all automated checkers, claims enforcement, and local development run cleanly before application code is authored.

#### 2. Exact Source Code Files to Create
- `backend/pyproject.toml` (Configures Python 3.11, Ruff lint/format, Mypy strict mode, Pytest with coverage options)
- `backend/Dockerfile` (Multi-stage slim Python 3.11 container, non-root user, dynamic `$PORT` binding, `/healthz` healthcheck)
- `backend/app/__init__.py`
- `backend/app/main.py` (FastAPI app factory, lifespan placeholder, CORS middleware, `/healthz` endpoint)
- `backend/app/config.py` (Centralized `Settings(BaseSettings)` using `pydantic-settings`; `SecretStr` for API keys)
- `frontend/package.json` (Next.js 14.2.x, React 18.3.x, React-DOM 18.3.x, Tailwind CSS, Zustand, TanStack Query, Lucide React, Recharts)
- `frontend/tsconfig.json` (`strict: true`, `noUncheckedIndexedAccess: true`, `@/*` path alias)
- `frontend/tailwind.config.ts` (Canonical KartAI Lavender tokens: `canvas`, `surface`, `brand`, `brandHover`, `ink`, `inkMuted`, `border`, `borderLight`, `accentEmerald`, `accentRose`, `accentAmber`)
- `frontend/next.config.js` (Image domains, headers, strict mode)
- `frontend/app/layout.tsx` (Root HTML layout, Inter font, metadata, Toast provider)
- `frontend/app/globals.css` (Tailwind directives, custom scrollbars, glassmorphism utilities)
- `scripts/check_claims.py` (Scans repo for forbidden strings per `AGENTS.md` §10; exits 1 on detection)
- `scripts/smoke_test.py` (Cross-platform health check script exercising `/healthz` and baseline ping)
- `.github/workflows/ci.yml` (GitHub Actions workflow enforcing backend lint/type/test, frontend lint/tsc/test/build, and check_claims)
- `.pre-commit-config.yaml` (Local git pre-commit hooks for Ruff and claims checks)
- `.gitignore` (Ignores `.env*`, `*.db`, `node_modules/`, `__pycache__/`, `.next/`, `coverage/`)

#### 3. Exact Test Files to Create
- `backend/tests/conftest.py` (Async client fixture, test settings fixture)
- `backend/tests/api/test_healthz.py` (Verifies `GET /healthz` returns `{"status": "ok", "service": "returnzero-backend"}`)
- `frontend/tests/smoke.test.tsx` (Renders basic React tree to confirm testing library setup)

#### 4. Exact Gate Commands Required
```powershell
# Backend Quality Gate
ruff check backend/
ruff format --check backend/
mypy --strict backend/app/
pytest backend/tests/api/test_healthz.py

# Frontend Quality Gate
npm --prefix frontend run lint
npx --prefix frontend prettier --check .
npx --prefix frontend tsc --noEmit
npm --prefix frontend run test
npm --prefix frontend run build

# Claims & Pre-Flight Scripts
python scripts/check_claims.py
python scripts/smoke_test.py http://localhost:8000
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Python 3.11 installed, Node.js 20 LTS installed, repository initialized (`git init`).
- **Deliverables:** Working backend and frontend skeletons, green CI/pre-commit pipeline, functional `/healthz` endpoint.

---

### Phase 1: Pure Domain Modeling & Mathematical Invariants

#### 1. Objective & Scope
Implement the pure business logic and mathematical engines in `backend/app/domain/`. These modules are 100% pure: zero I/O, zero network calls, zero database imports, zero system clock or unseeded random calls. Implement Decimal monetary arithmetic, the closed-form incentive solver, deterministic sizing rules with computed confidence, pure address quality evaluation, frozen risk configuration, and the 10,000-shipment financial scenario model.

#### 2. Exact Source Code Files to Create
- `backend/app/domain/__init__.py`
- `backend/app/domain/money.py` (Decimal-based currency handling, 2-decimal formatting, rounding helpers)
- `backend/app/domain/sizing.py` (Pure sizing recommendation function, ease calculation, tolerance intervals, dynamic categorical confidence band computation: `High`, `Medium`, `Low`, gap detection)
- `backend/app/domain/risk.py` (Explainable risk scoring function, frozen `RiskConfig` dataclass with weights, Order Review checklist generator)
- `backend/app/domain/incentive.py` (Closed-form margin-safe solver: $D_{\max} = (P_{\text{COD}} - P_{\text{prepaid}}) \times \text{Cost}_{\text{RTO}} - \text{Fees} - \text{MarginFloor}$, floor rounding to ₹5 step, ₹40 cap, anti-abuse coupon cap $\le 20\%$ GMV, 3-refusal non-cash gift, reason code assignment)
- `backend/app/domain/address.py` (Pure `address_quality()` evaluator: flat regex, Indian landmark keyword dictionary, PIN regex, classifying into `Complete`, `NeedsLandmark`, `Poor`)
- `backend/app/domain/scenario.py` (Pure 10,000-shipment financial projection model reproducing deck economics with zero error)
- `backend/app/data/__init__.py`
- `backend/app/data/brand_matrices.py` (Standardized brand conversion tables for Zara, H&M, Uniqlo)
- `backend/app/data/serviceable_pins.py` (Synthetic demo lane lists: Tier-1, Tier-2, Tier-3, high-risk lanes)

#### 3. Exact Test Files to Create
- `backend/tests/unit/test_money.py` (Decimal precision, floor rounding, negative prevention)
- `backend/tests/unit/test_sizing.py` (All 4 ease preferences: tight, tailored/regular, relaxed, oversized; zero-stretch rejection; missing sleeve gap note; computed confidence levels)
- `backend/tests/unit/test_risk.py` (Frozen weights, COD vs prepaid points, checklist structure)
- `backend/tests/unit/test_incentive.py` (Cart ₹1,899 default 0% fee -> ₹40 offer; fee 1.5% -> ineligible with `REASON_INSUFFICIENT_MARGIN`; coupon cap abuse; repeat refusal non-cash perk)
- `backend/tests/unit/test_address.py` (English and Hinglish landmark keywords, missing house numbers, complete vs poor classifications)
- `backend/tests/unit/test_scenario.py` (Exact deck reproduction: 1,760 baseline RTO -> 1,487 combined RTO; avoided 273; gross ₹54,600; net ₹28,600/month; conservative net ₹5,200/month)
- `backend/tests/property/test_domain_properties.py` (Hypothesis property-based tests verifying invariants: discount never exceeds 20% GMV, risk index always in $[0, 100]$, confidence band always one of High/Medium/Low)

#### 4. Exact Gate Commands Required
```powershell
ruff check backend/app/domain/
mypy --strict backend/app/domain/
pytest --cov=app/domain --cov-report=term-missing --cov-fail-under=95 backend/tests/unit/ backend/tests/property/
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 0 complete and green.
- **Deliverables:** Complete, thoroughly tested pure domain package with $\ge 95\%$ test coverage floor.

---

### Phase 2: Database Schema, Async Repositories, Lifespan Seeding & Demo Reset API

#### 1. Objective & Scope
Implement the asynchronous database persistence layer using SQLAlchemy 2.0 and `aiosqlite`. Define relational models for SKUs, orders, fit logs, interventions, and delivery events with composite indexes. Implement the repository layer, idempotent startup lifespan seeding with 150 realistic Indian orders spanning 30 days, Pydantic v2 API schemas, and the secret-guarded `POST /v1/demo/reset` endpoint.

#### 2. Exact Source Code Files to Create
- `backend/app/db/__init__.py`
- `backend/app/db/models.py` (`SkuModel`, `OrderModel`, `FitLogModel`, `IncentiveInterventionModel`, `DeliveryEventModel`)
- `backend/app/db/session.py` (Async engine, async sessionmaker, dependency `get_db_session()`)
- `backend/app/db/repositories.py` (`SkuRepository`, `OrderRepository`, `AnalyticsRepository`)
- `backend/app/db/seed.py` (Deterministic lifespan seeder using `random.Random(20261128)`; inserts 4 curated SKUs and 150 historical orders if table empty)
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/api_contracts.py` (Pydantic v2 request/response models with `extra="forbid"`, PIN validation, status StrEnums)
- `backend/app/services/__init__.py`
- `backend/app/services/catalog_service.py` (Catalog retrieval and database attribute synchronization)
- `backend/app/services/analytics_service.py` (Live DB KPI aggregations: order count, COD share %, isolated RTO %, isolated customer return %, savings)
- `backend/app/api/__init__.py`
- `backend/app/api/catalog.py` (`GET /v1/catalog/skus`, `GET /v1/catalog/skus/{sku_id}`)
- `backend/app/api/analytics.py` (`GET /v1/analytics/overview`, `GET /v1/analytics/scenario`)
- `backend/app/api/demo.py` (`POST /v1/demo/reset` guarded by `DEMO_MODE=true` and `X-Demo-Token`)

#### 3. Exact Test Files to Create
- `backend/tests/unit/test_seed.py` (Verifies 150 orders seeded, 65% COD, tier distribution, idempotency on restart)
- `backend/tests/api/test_catalog_api.py` (Verifies SKU listings, attribute payloads, 404 on invalid ID)
- `backend/tests/api/test_analytics_api.py` (Verifies dynamic aggregation against seeded DB; verifies scenario endpoint)
- `backend/tests/api/test_demo_api.py` (Verifies reset token security: 403 on invalid token; 200 on valid token restoring exactly 150 rows)

#### 4. Exact Gate Commands Required
```powershell
ruff check backend/
mypy --strict backend/app/
pytest --cov=app --cov-report=term-missing --cov-fail-under=85 backend/tests/
python scripts/smoke_test.py http://localhost:8000
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 1 domain modules complete.
- **Deliverables:** Database schema active, 150-order dataset populated and queryable, working analytics and demo reset APIs.

---

### Phase 3: Gemini VLM Adapter, Resilient Extractor & Normalizer

#### 1. Objective & Scope
Implement the multimodal vision and text extraction pipeline. Connect to the Google GenAI SDK (`google-genai`) behind strict `Protocol` abstractions with `GEMINI_MODEL_ID` configuration (`gemini-3.8-flash`). Enforce non-blocking async execution, hard 4.0-second timeouts, automatic dual-key failover (`PRIMARY_GEMINI_API_KEY` -> `BACKUP_GEMINI_API_KEY`), 60-second in-memory circuit breaker, and seamless fallback to verified benchmark fixtures (`backend/app/data/fixtures/<sku>.json`). Implement conversational address normalizer with regex fallback.

#### 2. Exact Source Code Files to Create
- `backend/app/integrations/__init__.py`
- `backend/app/integrations/gemini/__init__.py`
- `backend/app/integrations/gemini/adapter.py` (Async client adapter, dual-key rotation, timeout enforcement, circuit breaker)
- `backend/app/integrations/gemini/prompts.py` (Deterministic extraction prompts with zero-hallucination and missing-data instructions)
- `backend/app/integrations/gemini/extractor.py` (VLM catalog attribute extractor, schema validator, provenance assignment)
- `backend/app/integrations/gemini/normalizer.py` (Conversational address & landmark normalizer with deterministic regex fallback)
- `backend/app/integrations/gemini/cache.py` (In-memory TTL cache keyed by `hash(sku_id, image_sha256, model_id, prompt_version)`)
- `backend/app/data/fixtures/sku_01.json` (Verified benchmark fixture: Chanderi Silk Kurta)
- `backend/app/data/fixtures/sku_02.json` (Verified benchmark fixture: Linen Shirt)
- `backend/app/data/fixtures/sku_03.json` (Verified benchmark fixture: Denim Jacket with missing sleeve length)
- `backend/app/data/fixtures/sku_04.json` (Verified benchmark fixture: Floral Rayon Maxi Dress)
- `backend/app/api/catalog.py` (Add route `POST /v1/catalog/skus/{sku_id}/extract`)
- `scripts/check_gemini.py` (Standalone live Gemini health verification script)
- `scripts/record_fixtures.py` (Utility script to refresh fixture benchmarks from live responses)

#### 3. Exact Test Files to Create
- `backend/tests/unit/test_gemini_adapter.py` (Mocked SDK responses, Interactions vs Models protocol compliance)
- `backend/tests/resilience/test_gemini_resilience.py` (Simulated 429 quota exhaustion -> backup key switch; simulated $>4.0$s timeout -> fixture fallback; circuit breaker tripping after 3 consecutive failures; zero 500 errors)
- `backend/tests/api/test_extract_api.py` (POST extract endpoint tests, cache hits, provenance tags)

#### 4. Exact Gate Commands Required
```powershell
ruff check backend/
mypy --strict backend/app/
pytest --cov=app --cov-report=term-missing --cov-fail-under=85 backend/tests/
python scripts/check_gemini.py
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 2 complete; `PRIMARY_GEMINI_API_KEY` available (or mock mode active).
- **Deliverables:** Fully resilient 3-tier VLM extraction pipeline with 100% demo uptime guarantee.

---

### Phase 4: Storefront PDP, Fit-Twin Drawer & WhatsApp Phone Simulator

#### 1. Objective & Scope
Construct the mobile-first Next.js storefront pages and UI components. Build the Product Detail Page (PDP) for the 4 curated SKUs with fabric specification badges and size selector. Build the "Check My Fit" slide-over drawer connecting to the sizing engine with brand reference selection (Zara/H&M/Uniqlo) and transparent fit zone breakdown. Build the in-browser iPhone WhatsApp simulator component executing post-order delivery assurance with explicit consent opt-in, landmark clarification, and slot booking.

#### 2. Exact Source Code Files to Create
- `frontend/lib/api/schema.d.ts` (TypeScript types generated from backend OpenAPI specification)
- `frontend/lib/api/client.ts` (Typed API client wrapper using `fetch` with error boundaries)
- `frontend/lib/store.ts` (Zustand client store managing selected size, cart items, fit-verified state, and placed order)
- `frontend/app/page.tsx` (Catalog grid page showcasing the 4 curated fashion SKUs)
- `frontend/app/products/[skuId]/page.tsx` (Rich PDP with fabric specs, image gallery, fit button, and add-to-cart)
- `frontend/components/fit-twin/FitDrawer.tsx` (Check My Fit slide-over drawer: brand selector, size conversion, ease breakdown, gap warning)
- `frontend/components/fit-twin/FitZoneBreakdown.tsx` (Visual bust/waist/hip ease comparison component)
- `frontend/components/fit-twin/CatalogIntelligencePanel.tsx` (PDP accordion displaying extracted attributes and provenance badge)
- `frontend/components/simulator/conversationMachine.ts` (State machine managing consent, address branch, landmark input, and delivery slot)
- `frontend/components/simulator/WhatsAppPhoneSimulator.tsx` (High-fidelity iPhone 15 frame, WhatsApp header, simulated typing indicator, sticky "Simulated" ribbon)
- `frontend/components/simulator/ChatBubble.tsx` (Incoming/outgoing speech bubbles with timestamp and delivery ticks)
- `frontend/app/simulator/page.tsx` (Simulator page dynamically loaded with the active storefront order)

#### 3. Exact Test Files to Create
- `frontend/tests/components/FitDrawer.test.tsx` (Renders brand selector, submits recommendation, renders recommended size and gap warning)
- `frontend/tests/components/CatalogIntelligencePanel.test.tsx` (Displays provenance badge and missing data warnings)
- `frontend/tests/components/conversationMachine.test.ts` (State machine transitions: Consent -> Address check -> Landmark -> Slot -> Confirmed; opt-out "STOP" handling)
- `frontend/tests/components/WhatsAppPhoneSimulator.test.tsx` (Simulator rendering, message dispatch, quick-reply chip interaction)

#### 4. Exact Gate Commands Required
```powershell
npm --prefix frontend run lint
npx --prefix frontend tsc --noEmit
npm --prefix frontend run test
npm --prefix frontend run build
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 2 & 3 backend APIs running; frontend design tokens configured.
- **Deliverables:** Interactive Storefront PDP, working Check My Fit drawer, and authentic in-browser WhatsApp simulator.

---

### Phase 5: Checkout Shield, Risk/Incentive APIs & Order Flow

#### 1. Objective & Scope
Implement the full checkout review flow and backend transaction APIs. Build `POST /v1/risk/evaluate`, `POST /v1/incentive/quote`, and `POST /v1/orders` endpoints. On the frontend, build the Checkout page and `OrderReviewModal` rendering the 3-point risk checklist (`Address complete`, `Serviceable PIN`, `RTO risk band`), guaranteed COD choice, and the dynamic UPI incentive nudge modal. Connect order submission directly to the WhatsApp simulator and live order stream.

#### 2. Exact Source Code Files to Create
- `backend/app/services/risk_service.py` (Coordinates risk scoring, address quality, and checklist compilation)
- `backend/app/services/incentive_service.py` (Coordinates margin solver, fee configuration, and anti-abuse verification)
- `backend/app/services/verification_service.py` (Handles WhatsApp webhook confirmations, address updates, and NDR recovery)
- `backend/app/api/risk.py` (`POST /v1/risk/evaluate`)
- `backend/app/api/incentive.py` (`POST /v1/incentive/quote`)
- `backend/app/api/orders.py` (`POST /v1/orders`, `GET /v1/orders`, `GET /v1/orders/{id}`, `POST /v1/orders/{id}/verify`, `POST /v1/orders/{id}/ndr`)
- `frontend/app/checkout/page.tsx` (Address form, cart item summary, bracketing detection alert, payment mode selection)
- `frontend/components/checkout/OrderReviewModal.tsx` (3-point risk checklist review, transparent UPI discount offer, standard COD fallback button)
- `frontend/components/checkout/UpiConversionModal.tsx` (Interactive modal displaying ₹40 UPI discount, instant conversion, dispatch priority badge)
- `frontend/app/confirmation/[orderId]/page.tsx` (Order confirmation page with CTA: *"Open Delivery Assurance WhatsApp Simulator"*)

#### 3. Exact Test Files to Create
- `backend/tests/api/test_risk_api.py` (Tests complete address vs needs landmark; validates checklist output)
- `backend/tests/api/test_incentive_api.py` (Tests default fee quote, elevated fee quote, coupon stacking limit)
- `backend/tests/api/test_orders_api.py` (Order creation, order retrieval, verify landmark mutation, NDR reschedule mutation)
- `frontend/tests/components/OrderReviewModal.test.tsx` (Asserts COD is never blocked, asserts discount copy is conditional on fit verification)
- `frontend/tests/pages/Checkout.test.tsx` (Form submission, modal trigger, redirect to confirmation)

#### 4. Exact Gate Commands Required
```powershell
# Backend
ruff check backend/
mypy --strict backend/app/
pytest --cov=app --cov-report=term-missing --cov-fail-under=85 backend/tests/

# Frontend
npm --prefix frontend run lint
npx --prefix frontend tsc --noEmit
npm --prefix frontend run test
npm --prefix frontend run build

# Integration Smoke Test
python scripts/smoke_test.py http://localhost:8000
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 4 frontend components and Phase 2 database active.
- **Deliverables:** Seamless end-to-end purchasing loop: PDP -> Fit Drawer -> Checkout -> OrderReviewModal -> Confirmation -> Order in Database.

---

### Phase 6: Merchant Command Center Dashboard

#### 1. Objective & Scope
Construct the real-time merchant analytics dashboard (`frontend/app/dashboard/page.tsx`). Strictly separate live database telemetry from the interactive 10,000-shipment financial scenario model. Build the live KPI overview cards (updating within ~3s via TanStack Query), the real-time Order Stream table with status tags, the Geographic/Tier RTO breakdown chart (Recharts), SKU intelligence cards with missing data warnings, and the dynamic incentive equation card with fee/RTO cost what-if sliders.

#### 2. Exact Source Code Files to Create
- `frontend/app/dashboard/page.tsx` (Master dashboard layout, TanStack Query polling provider, tab switching)
- `frontend/components/dashboard/OverviewKPIs.tsx` (7 glassmorphic metric cards: Shipped Orders, COD Share, Isolated RTO %, Isolated Customer Return %, Conversions, Incentive Spend, Modelled Direct Savings)
- `frontend/components/dashboard/OrderStreamTable.tsx` (Live table displaying order ID, customer, payment mode, risk band, incentive reason code, and status with real-time updates)
- `frontend/components/dashboard/TierRtoChart.tsx` (Responsive Recharts bar chart showing RTO rates across Tier-1, Tier-2, and Tier-3 cities)
- `frontend/components/dashboard/SkuIntelligenceCards.tsx` (SKU feedback cards highlighting orders, return rates, and merchant measurement gap action alerts)
- `frontend/components/dashboard/ScenarioModelPanel.tsx` (Interactive 10,000-shipment financial simulator with sliders for monthly volume, COD %, fees, and RTO costs; reproducing deck numbers)
- `frontend/components/dashboard/IncentiveEquationCard.tsx` (Live mathematical display of $D_{\max}$ formula with interactive sliders; setting fee to 1.5% visibly withdraws offer)
- `frontend/components/dashboard/RupeesSavedTicker.tsx` (Animated counter displaying modelled direct operating savings)
- `frontend/components/dashboard/DemoResetButton.tsx` (Header control to trigger `POST /v1/demo/reset` and refresh UI state)

#### 3. Exact Test Files to Create
- `frontend/tests/components/OverviewKPIs.test.tsx` (Verifies live KPI rendering, tooltips, separation of RTO vs customer returns)
- `frontend/tests/components/ScenarioModelPanel.test.tsx` (Verifies interactive calculation reproducing deck numbers: 273 avoided RTO, ₹28,600 net savings)
- `frontend/tests/components/OrderStreamTable.test.tsx` (Verifies status tag styling, reason code badges, mutation updates)
- `backend/tests/integration/test_dashboard_data_sync.py` (Placing an order via `/v1/orders` immediately increments `/v1/analytics/overview` total from 150 to 151)

#### 4. Exact Gate Commands Required
```powershell
# Frontend Checks
npm --prefix frontend run lint
npx --prefix frontend tsc --noEmit
npm --prefix frontend run test
npm --prefix frontend run build

# Backend Checks
ruff check backend/
mypy --strict backend/app/
pytest --cov=app --cov-report=term-missing --cov-fail-under=85 backend/tests/

# Compliance
python scripts/check_claims.py
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phase 2 analytics endpoints and Phase 5 order flow active.
- **Deliverables:** High-impact, production-grade Merchant Command Center with real-time order stream and auditable financial scenario model.

---

### Phase 7: Disaster Prevention Hardening & Full Integration / Resilience Suite

#### 1. Objective & Scope
Perform exhaustive resilience hardening, disaster drill verification, accessibility audits, and documentation authoring per `DEMO_DAY_DISASTER_PREVENTION.md` and `PRE_EVENT_CHECKLIST.md`. Ensure every React component is wrapped in an `ErrorBoundary`, skeleton loaders eliminate layout shifts, all interactive elements meet WCAG AA standards, Lighthouse mobile scores $\ge 90$, and zero unhandled exceptions can occur during live evaluation.

#### 2. Exact Source Code Files to Create / Modify
- `frontend/components/ui/ErrorBoundary.tsx` (Modular error boundary with localized retry states)
- `frontend/components/ui/SkeletonCard.tsx` (Animated shimmer loading states for dashboard tiles and PDP)
- `docs/ARCHITECTURE.md` (Detailed system architecture, sequence diagrams, latency SLA documentation)
- `docs/API.md` (Complete OpenAPI specification and endpoint documentation)
- `docs/DEMO_SCRIPT.md` (Exact 2-minute spoken narrative and click sequence for video recording and judge presentations)
- `README.md` (Judge-facing production documentation: problem statement, architecture diagram, local setup instructions, live deployment links, team profiles, claims audit trail)

#### 3. Exact Test Files to Create
- `backend/tests/resilience/test_disaster_scenarios.py` (Simulates total network cut, corrupted image input, missing fields, database lock recovery)
- `frontend/tests/resilience/accessibility.test.tsx` (WCAG AA color contrast, ARIA tags, keyboard navigation in drawers and modals)
- `frontend/tests/integration/golden_path.test.tsx` (End-to-end integration test: Browse catalog -> Check My Fit -> Add to Cart -> Checkout -> Accept UPI Discount -> Confirm Order -> WhatsApp Landmark Clarification -> Merchant Dashboard Update)

#### 4. Exact Gate Commands Required
```powershell
# Full Project Gate
ruff check backend/
ruff format --check backend/
mypy --strict backend/app/
pytest --cov=app --cov-report=term-missing --cov-fail-under=85 backend/tests/

npm --prefix frontend run lint
npx --prefix frontend prettier --check .
npx --prefix frontend tsc --noEmit
npm --prefix frontend run test
npm --prefix frontend run build

python scripts/check_claims.py
python scripts/smoke_test.py http://localhost:8000
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Phases 0–6 completely implemented.
- **Deliverables:** Crash-proof codebase, comprehensive documentation, verified 2-minute demo script, and green quality gates across both stacks.

---

### Phase 8: Cloud Deployment (Vercel + Render), Golden Demo Verification & Final Documentation

#### 1. Objective & Scope
Deploy the production artifacts to cloud hosting: Next.js frontend to Vercel and FastAPI backend container to Render (or Cloud Run). Verify production environment variables, execute the remote smoke test suite against live cloud URLs, verify zero CORS issues, record the high-definition 2-minute demo video following `docs/DEMO_SCRIPT.md`, and complete the Unstop submission portal checklist.

#### 2. Exact Source Code Files to Create / Modify
- `render.yaml` (Infrastructure-as-code deployment specification for Render web service)
- `vercel.json` (Vercel routing, caching headers, and rewrites if needed)
- `docs/PREFLIGHT.md` (Pre-submission verification checklist, live URL verification, submission metadata)

#### 3. Exact Test Files & Verification Scripts to Run
- `scripts/smoke_test.py https://returnzero-backend.onrender.com` (Remote production API health and smoke test suite)
- `scripts/check_claims.py` (Final clean repository scan)

#### 4. Exact Gate Commands Required
```powershell
# Production Cloud Verification
python scripts/smoke_test.py https://returnzero-backend.onrender.com
python scripts/check_claims.py
git status --porcelain # Must be completely clean
git log -n 5 --oneline
```

#### 5. Input Prerequisites & Output Deliverables
- **Prerequisites:** Vercel account, Render account, Google AI Studio production API keys, OBS Studio for screen recording.
- **Deliverables:** Live, publicly accessible web applications on Vercel and Render, unlisted YouTube demo video link, public GitHub repository, and completed Unstop submission before Hour 47.

---

## Complete Quality Gate Command Reference

| Check Type | Target | Exact Command (PowerShell) | Threshold / Exit Criteria |
|---|---|---|---|
| Python Linting | Backend | `ruff check backend/` | 0 errors |
| Python Formatting | Backend | `ruff format --check backend/` | 0 formatting diffs |
| Python Static Typing | Backend | `mypy --strict backend/app/` | 0 type errors; no `Any` |
| Domain Unit Testing | Backend | `pytest --cov=app/domain --cov-fail-under=95 backend/tests/unit/` | $\ge 95\%$ domain coverage |
| Overall Backend Testing | Backend | `pytest --cov=app --cov-fail-under=85 backend/tests/` | $\ge 85\%$ total coverage |
| Frontend Linting | Frontend | `npm --prefix frontend run lint` | 0 warnings, 0 errors |
| Frontend Formatting | Frontend | `npx --prefix frontend prettier --check .` | 0 formatting diffs |
| Frontend Static Typing | Frontend | `npx --prefix frontend tsc --noEmit` | 0 type errors; strict |
| Frontend Unit Testing | Frontend | `npm --prefix frontend run test` | 100% tests passing |
| Frontend Build | Frontend | `npm --prefix frontend run build` | Next.js production build exits 0 |
| Claims & Truthfulness | Repository | `python scripts/check_claims.py` | 0 forbidden strings |
| API Smoke Test | Service | `python scripts/smoke_test.py [URL]` | All 5 critical flows pass |
