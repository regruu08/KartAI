# AGENTS.md — ReturnZero AI (Team BioXtreme)

> Standing instructions for the AI coding agent. Read this file completely before touching code, and re-read §5 (decisions) and §11 (working agreement) at the start of every phase.
> Place this file at the **repo root**. It also works under the names `CLAUDE.md`, `GEMINI.md`, `.cursorrules` or `.github/copilot-instructions.md` if your tool expects one of those.

---

## 0. Mission

Build **ReturnZero AI** — a working, deployed, demo-able prototype for the *Code to Cart: AI x E-Commerce Hackathon (KartAI x CodeXcelerate)*, Round 2 buildathon (28 Nov 2026 00:00 IST → 29 Nov 2026 23:59 IST).

Deliverables the code must support: (1) live public HTTPS prototype, (2) public GitHub repo with production-grade docs, (3) 2–3 minute demo video, (4) submission form.

Judging priorities: **working prototype + meaningful use of AI**, **real e-commerce value**, **UX**, **presentation**. Code quality is a first-class goal of the owner: the repo will be read by judges. Optimise for *correct, honest, clean, tested, demo-proof*, in that order.

---

## 1. Product in 60 seconds

ReturnZero AI is a fit-intelligence and delivery-assurance layer for D2C fashion.

| Pillar | What the shopper/merchant sees | Brains |
|---|---|---|
| **1. Fit Intelligence** | PDP button **"Check My Fit"** → shopper enters known brand+size (e.g. *Zara M*), height, fit preference. No photo. Gets **recommended size + reasons + confidence band + explicit "missing merchant data" warnings**. | Gemini parses product image + listing text into structured, uncertainty-aware attributes; a **deterministic** engine does the sizing math. |
| **2. Checkout Shield** | Transparent order review (address complete? PIN serviceable? risk band) and an **optional** margin-safe UPI incentive ("Save ₹40 via instant UPI + Priority Dispatch"). **COD is never blocked.** | Explainable rule-based risk index + incentive solver (closed-form equation). No fake ML. |
| **3. Delivery Assurance** | In-browser **WhatsApp-style simulator**: consent → address/landmark clarification → delivery-window confirmation → NDR recovery. | State machine + (Gemini or rule-based) address normaliser. |
| **Merchant Intelligence Layer** | Dashboard: RTO vs customer returns **shown separately**, conversion, estimated savings, SKU-level alerts, order stream. | SQL aggregations over persisted state. |

**Engineering principle (verbatim from the submitted deck):** *AI interprets unstructured product images; deterministic code governs fit recommendations, risk rules, and financial calculations.*

**Golden demo path (must work flawlessly, locally and deployed):**
Storefront → PDP (Chanderi Kurta) → Check My Fit (Zara M, tailored) → **Size L** + reasons → add to cart → checkout, choose COD → risk review + UPI incentive modal → accept (or continue COD) → order persisted → open WhatsApp simulator for that order → landmark → slot → `Safe_For_Dispatch` → Dashboard counters update live (150 → 151 orders).

---

## 2. Source-of-truth hierarchy

The repo contains documents written at different times. **When they disagree, higher wins.**

1. **Submitted Round-1 deck (PDF)** and `gpt/FINAL_DECK_COPY.md` + `gpt/SOURCES_AND_ASSUMPTIONS.md` — canonical for *claims, numbers, definitions, scope, naming* (e.g. "Check My Fit").
2. **This file (§5 decisions/errata)** — canonical where the tech specs are wrong or ambiguous.
3. `tech_docs/*` — canonical for *structure and intent* of each module (schemas, endpoints, file targets, UI behaviour), subject to §5.
4. `ROUND_2_BUILDATHON_PLAYBOOK.md`, `DEMO_DAY_DISASTER_PREVENTION.md`, `PRE_EVENT_CHECKLIST.md` — operational guidance.
5. **STALE — never copy numbers or architecture from:** root `00_…05_*.md`, `research/RESEARCH_INDEX.md` Q&A answers, `gpt/ChatGPT-Study…md`. They still contain Gemini *2.0* Flash, XGBoost, pgvector, "single casual photo", ₹18,000 Cr, 32% COD-remorse, etc. — all explicitly **removed** in `SOURCES_AND_ASSUMPTIONS.md` §D.

Do **not** edit the original spec documents. Put new documentation in `docs/`.

---

## 3. Non-negotiable product principles

1. **Honesty over polish.** Zero fabricated performance claims. Every number shown in UI/README is either (a) computed from data in the DB, (b) a labelled scenario output of the documented model, or (c) a cited benchmark from `SOURCES_AND_ASSUMPTIONS.md`.
2. **Never guess what can be computed; never compute what must be interpreted.** Gemini extracts/interprets; Python decides.
3. **Uncertainty is a feature.** Missing data is surfaced (`missing_critical_data`, `data_gaps_warning`, lower confidence band), never filled in.
4. **COD is always available.** `cod_remains_available` is always `true`; no blacklisting; incentives are optional, clearly worded, with the "continue with COD" option fully visible. No fake urgency/countdowns, no pre-ticked prepaid, no hidden fees (CCPA dark-pattern guidelines).
5. **Everything synthetic is labelled.** Seed orders, risk-lane lists, WhatsApp messages: UI badge "Synthetic demo data" / "Simulated — no real WhatsApp message is sent".
6. **Reproducible.** Same input → same output for sizing/risk/incentive. Seeds are deterministic. Math can be recomputed by a judge from the README.
7. **Demo-proof.** A judge must never see a red error box, spinner that never ends, `NaN`, empty dashboard, or white screen.
8. **Scope fence.** No 3D/body scans, no trained ML models, no real payment collection, no real WhatsApp/SMS/telecom APIs.

---

## 4. Repository layout (monorepo)

```
.
├── AGENTS.md                  # this file
├── README.md                  # judge-facing (see BUILD_PLAN Phase 7)
├── Makefile                   # + documented PowerShell equivalents (owner is on Windows)
├── docker-compose.yml
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── docs/                      # ARCHITECTURE.md, DECISIONS.md (ADR log), ASSUMPTIONS.md, DEMO_SCRIPT.md, API.md
├── scripts/                   # smoke_test.py, check_gemini.py, record_fixtures.py (cross-platform: Python/Node only)
├── backend/
│   ├── pyproject.toml         # ruff, mypy, pytest, coverage config
│   ├── requirements.txt / requirements-dev.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py            # app factory, lifespan, middleware, exception handlers
│   │   ├── config.py          # pydantic-settings: the ONLY place env vars are read
│   │   ├── api/               # routers (thin): catalog.py fit.py risk.py incentive.py orders.py analytics.py demo.py
│   │   ├── schemas/           # Pydantic v2 request/response + enums (StrEnum)
│   │   ├── domain/            # PURE logic, no I/O: money.py sizing.py risk.py incentive.py address.py scenario.py
│   │   ├── services/          # orchestration: catalog_service, fit_service, order_service, verification_service, analytics_service
│   │   ├── integrations/      # gemini/ (client adapter, prompts, extractor, normaliser, cache, fallback), 
│   │   ├── db/                # models.py, session.py, repositories.py, seed.py
│   │   └── data/              # brand_matrices.py, fixtures/*.json, serviceable_pins.py
│   └── tests/                 # unit/, api/, integration/, conftest.py (fake Gemini, in-memory sqlite)
└── frontend/
    ├── app/                   # per tech_docs/03 route tree
    ├── components/            # fit-twin/ checkout/ simulator/ dashboard/ ui/
    ├── lib/                   # api client (typed from OpenAPI), store.ts (zustand), formatters, constants
    ├── tests/                 # vitest + testing-library; e2e/ (playwright)
    └── tailwind.config.ts     # single design-token source (tech_docs/03 names)
```

Layering rule (enforced by review and an import-linter/ruff rule if feasible): `api → services → (domain, integrations, db)`. **`domain/` imports nothing from the rest of the app.** Routers contain no business logic.

---

## 5. Binding decisions & spec errata

The tech specs contain defects. These resolutions are **binding**. Record each in `docs/DECISIONS.md` as a short ADR (context → decision → consequence).

| ID | Spec says | Problem | Resolution |
|---|---|---|---|
| **E1** | Gemini model `gemini-3.8-flash`; code uses `client.models.generate_content(... response_schema=…)` | Model ID is correct per the team's 18-Nov review (and appears in Google's current docs), but Google's current structured-output docs show the Python SDK's **Interactions API** (`client.interactions.create(model=, input=, response_format={type:"text", mime_type:"application/json", schema:…})`, result via `.output_text`). The spec snippet may be outdated. | Model ID comes **only** from `GEMINI_MODEL_ID`. Before writing the adapter, check the installed `google-genai` version and the official docs; use whatever the installed SDK documents. Isolate the SDK call in **one** adapter class behind a `Protocol` so an SDK change touches one file. `scripts/check_gemini.py` does a live smoke call and prints model, latency and parsed output. Do not use the deprecated `google-generativeai` package. |
| **E2** | Incentive solver: `pg_fee = 1.5% × cart`, min offer ₹25, `round(x/5)*5` | At ₹1,899 cart: 48 − 28.49 − 8 = **₹11.5** → ineligible, so the spec's **own smoke test fails** and the deck's "₹40 with ₹8 headroom" (stated *before payment fees*) cannot be reproduced. `round()` can also round **up** past the margin floor (17.5 → 20). | Implement exactly the deck equation: `D_max = (P_cod − P_prepaid) × Cost_RTO − Fees − MarginFloor`. `UPI_GATEWAY_FEE_PCT` is a **configurable, visible assumption**, default `0.0` (deck figures are "before payment fees"), so defaults give `48 − 0 − 8 = ₹40`. Offer = `min(₹40 cap, floor_to_₹5(D_max))`; eligible only if `D_max ≥ ₹25` (`MIN_OFFER`). Use **floor**, never round-to-nearest. Show the live equation + assumptions on the dashboard and add a "what-if" control (fee %, RTO cost) — setting fee to 1.5% *visibly withdraws the offer*; that honesty is a selling point. Tests: default → ₹40; fee 1.5% @ ₹1,899 → ineligible with reason `REASON_INSUFFICIENT_MARGIN`. |
| **E3** | Risk scorer | (a) Adds factor text "−15% risk mitigation" but changes no score. (b) `"near" not in address` is brittle. (c) Magic numbers inline. (d) "High-risk PINs" presented as fact. | (a) Fit-verified adds **no penalty** and says exactly that; no invented "−15%". (b) Replace with one shared `address_quality()` (length, house/flat number regex, landmark keyword set incl. common Hindi/Hinglish tokens, PIN format `^\d{6}$`) used by **both** risk scorer and WhatsApp simulator → returns `Complete \| NeedsLandmark \| Poor`. (c) All weights/thresholds in one frozen `RiskConfig`. (d) PIN lists live in `data/` and are labelled **synthetic demo lane list** in code, UI and README. Reconcile the seed PINs with the list (spec uses Bhatinda 151001 vs risk list 143001). Add the **Order Review checklist** from the deck (`Address complete`, `Serviceable PIN`, `RTO risk band`) as `checks: [{id,label,status}]` in the risk response. |
| **E4** | Sizing engine returns `confidence_level="High"` always; docs show "94%" / "0.87" | Hard-coded confidence is exactly the "fabricated claim" the deck promises not to make. Waist unused; `oversized` preference falls into the `tight` branch (desired ease 1.0); ease table ≠ code thresholds; height ignored. | Confidence **computed**: inputs = which garment measurements exist (chest/shoulder/waist/length), whether shopper gave exact measurements vs brand-matrix estimate, `stretch_category == unknown`, and penalty margin between best and runner-up size. Output band `High/Medium/Low (Insufficient Data)`. If a number is shown, call it **"fit score (heuristic)"**, deterministic, documented in code, **never** "accuracy" or "probability". Desired-ease map covers all four preferences as named constants (`tight 1.0, tailored 2.5, relaxed 4.0, oversized 6.0` — labelled heuristics). Encode the ease table once in `EASE_RULES` (hard floor + comfortable range per stretch class) and unit-test every row. Include waist in the penalty with lower weight. Missing shoulder → Medium + the exact notice text from spec 04 §5; missing sleeve length (SKU-03) → the note from the checklist. Height is used only for a length-fit note when `length_inches` exists; otherwise report "height not used (garment length unavailable)" in `data_gaps`. UI label for `tailored` is **"Regular"** (matches the deck). |
| **E5** | Dashboard hard-codes ₹54,600 / 14.9% / 6.2%; `/v1/analytics/overview` lists fixed numbers | Those are the **deck's scenario** outputs, not results of the 150 seeded orders. Presenting them as live metrics is a fabricated claim. | Two clearly separated panels: **(1) "Live (synthetic) order data"** — every figure computed by one `analytics_service` from DB rows; **(2) "Scenario model — 10,000 shipments/month"** — computed by pure `domain/scenario.py` with editable inputs, defaulting to the deck. Tests must reproduce the deck exactly: baseline 1,690 + 70 = **1,760** RTO; combined 1,404 + 83 = **1,487**; avoided **273**; gross **₹54,600**; incentives 650 × 40 = **₹26,000**; net **₹28,600/mo = ₹3,43,200/yr**; conversion-only case **156** avoided, **₹5,200/mo, ₹62,400/yr**. Label: *"modelled direct operating savings after incentives, before fees — not net profit."* RTO and customer-return metrics are always separate (definitions in `SOURCES_AND_ASSUMPTIONS.md` §B). The "Rupees Saved Ticker" is labelled **"Estimated direct savings (modelled)"**. |
| **E6** | `recommend_fit` uses a hard-coded catalog inside `SizingEngine`; `vlm_service` is instantiated but never called | The deck promises a **live Gemini call** on product images. As specced, Gemini is dead code. | Catalog attributes live in the DB (`skus`). `POST /v1/catalog/skus/{id}/extract` runs the extractor (cache → live Gemini → verified fixture) and persists attributes **with provenance** (`live_gemini \| cache \| fixture \| manual`). The sizing engine reads persisted attributes, so missing fields flow into confidence and warnings. PDP shows a "Catalog intelligence" panel (extracted attributes, ⚠ missing fields, provenance badge e.g. `Live · gemini-3.8-flash` / `Mode: Verified Catalog Benchmark`). |
| **E7** | Endpoints inconsistent (`/v1/orders/verify` vs `/v1/orders/{id}/verify` + `order_id` in body); missing endpoints | Ambiguous contract; frontend needs more. | Use the endpoint table in §7. `order_id` is a **path** param only. |
| **E8** | `allow_origins=["*"]` + `allow_credentials=True` | Invalid/insecure combination. | Origins from `CORS_ORIGINS` (comma-separated), `allow_credentials=False`. |
| **E9** | Dockerfile runs `python -m database.seed_orders` each start; that module only defines a generator | Nothing inserts; re-running would duplicate. `random` unseeded; `datetime.utcnow()` deprecated; `FIT_LOG` entity missing from models. | Seeding runs in app lifespan, **idempotent** (only if tables empty), **deterministic** (`random.Random(20261128)`), timezone-aware datetimes, includes `FitLogModel`. `POST /v1/demo/reset` (guarded by `DEMO_MODE=true` + `X-Demo-Token`) restores the pristine 150-order state. Seed composition per `PRE_EVENT_CHECKLIST.md` §3 (65/35 COD/prepaid; 40/35/25 tier split; all six outcome statuses; every row `is_synthetic=true`). |
| **E10** | "Next.js 14 / React 18/19" | Next 14 App Router targets React 18. | Pin **Next.js 14.2.x (latest patch) + React 18.3**. If `npm audit` reports high/critical advisories in the framework, upgrade to a currently supported major and log it as an ADR. |
| **E11** | Two Tailwind token sets (`tech_docs/03` vs `PRE_EVENT_CHECKLIST`) | Duplicate source of truth. | Use the `tech_docs/03` names (`canvas, surface, brand, ink, border, accent`). No raw hex in components. |
| **E12** | Copy: "We verified your fit!", "Priority 48-hour dispatch", "10%–28% conversion shift", "94% confidence" | Shown even when the shopper skipped fit check; dispatch promise has no backing; conversion range is unsourced. | Nudge copy is **conditional** on the actual state. "Priority Dispatch" must set a real `dispatch_priority` flag on the simulated order or be removed. The conversion range and all numbers in the §10 forbidden list never appear anywhere. |
| **E13** | SKU count: playbook says 15 SKUs, checklist/deck say 4 | Inconsistent. | **4 curated SKUs** (Chanderi Kurta, Linen Mandarin Shirt, Denim Trucker Jacket with intentionally missing sleeve length, Floral Rayon Maxi Dress). |
| **E14** | Anti-abuse rules (coupon stacking ≤20% of GMV; 3 consecutive refusals → non-cash incentive) described but not coded | Spec/code gap. | Implement both as small pure functions + tests (P1, after core). Persist `reason_code` for **every** incentive decision (`REASON_INSUFFICIENT_MARGIN`, `REASON_ELEVATED_RISK_CONVERTIBLE`, `REASON_PREPAID_OPTIMAL`, `REASON_LOW_RISK`, `REASON_COUPON_CAP`, `REASON_REPEAT_REFUSAL`). |
| **E15** | WhatsApp state machine: address <15 chars → ask landmark; >25 → clean; 15–25 undefined; conversation hard-codes Aarav/#RZ-1042 | Gap; demo not tied to the real order. | Branch via `address_quality()`. Conversation is generated from the actual order. Add an explicit **consent/opt-in** first step (deck: "consent-based"), opt-out ("STOP") handling, banner "Simulated — no real WhatsApp message is sent", and a demo **NDR toggle**. |
| **E16** | Gemini calls inside `async def` use the sync client; no timeout; backup key never used | Blocks the event loop; the ">4.0 s → fixture" rule is unimplemented. | Use the SDK's async client or `run_in_threadpool`; hard timeout `GEMINI_TIMEOUT_S=4.0`; on 429/quota/timeout try `BACKUP_GEMINI_API_KEY` once, then fixture; a small circuit breaker (3 consecutive failures → skip live for 60 s). Cache key = `(sku_id, image_sha256, model_id, prompt_version)` with TTL. |

---

## 6. Code-quality standards (the owner's explicit priority)

### 6.1 Universal
- **Small, typed, named.** Functions ≤ ~40 lines, one responsibility; no magic numbers/strings (named constants or enums); no dead code, no commented-out code, no `TODO` left in `main`.
- Comments explain **why** (assumption, source, trade-off), not what. Every heuristic constant cites its origin (`# Shipway FY25 cohort benchmark`, `# heuristic, see ADR-004`).
- Conventional Commits (`feat(sizing): …`), small atomic commits, one concern per commit. Never commit secrets, `.env`, `*.db`, `node_modules`, build output.
- No `print`/`console.log` in committed code — use logging.
- Public functions have docstrings with an example for non-obvious math.

### 6.2 Backend (Python 3.11)
- **Tooling gate (must be green):** `ruff check` + `ruff format --check`, `mypy --strict` (no untyped defs, no `Any` in domain/services), `pytest` with coverage.
- **Coverage:** ≥ 95% on `domain/`, ≥ 85% on `services/` and `integrations/`, overall ≥ 85%. Coverage is a floor, not the goal — tests must assert behaviour.
- **Money = `Decimal`** in the domain; API exposes JSON numbers with 2 dp via one shared annotated type. No float arithmetic on money; percentages as `Decimal` too.
- **Config:** one `Settings(BaseSettings)` (pydantic-settings); `os.getenv` forbidden elsewhere; fail fast with a clear message on invalid config; secrets as `SecretStr`.
- **Pydantic v2 everywhere** at boundaries; `Literal`/`StrEnum` for closed sets; `extra="forbid"` on request models; validators for PIN (`^\d{6}$`), phone, positive amounts, size labels.
- **Domain purity:** `domain/*` are pure functions/dataclasses — no DB, network, clock, randomness (inject `now`/`rng`). This is what makes them trivially testable and auditable.
- **DI & testability:** services receive dependencies via FastAPI `Depends`; Gemini sits behind `CatalogExtractor` / `AddressNormalizer` Protocols; tests use fakes — **no test touches the network**. One opt-in `@pytest.mark.live` test for real Gemini (skipped without a key).
- **Errors:** typed domain exceptions → global handlers → `{"error": "...", "message": "human readable", "request_id": "..."}` with correct status codes (422 validation, 404, 409, 429, 502/503 for upstream). Never leak stack traces or keys. Request-ID middleware + structured (JSON) logs; never log phone numbers/addresses at INFO.
- **DB:** SQLAlchemy 2.0 async, repository functions, indexes on `orders(created_at, payment_method, order_status)`, `create_all` at startup is acceptable (note the Alembic path in ADR). Use SQLite in dev/test; keep types PostgreSQL-compatible (no SQLite-only features).
- **Resilience:** timeouts on every outbound call; bounded retries; Pillow-validated uploads (jpeg/png/webp only, ≤ 5 MB, resized to ≤ 1024 px, EXIF stripped); simple per-IP rate limit on Gemini-backed endpoints to protect quota on a public URL.
- **OpenAPI is the contract:** accurate `response_model`, `summary`, examples. `/docs` must be pleasant for a judge to use.

### 6.3 Frontend (Next.js 14, TypeScript)
- **Strict TS** (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes` if practical); **no `any`**; ESLint (`next/core-web-vitals` + `@typescript-eslint/strict`) and Prettier clean; `tsc --noEmit` clean.
- **Types come from the backend:** generate `lib/api/schema.d.ts` from `/openapi.json` (`openapi-typescript`) and wrap with one small typed fetch client; validate untrusted responses at the boundary (zod) for the money-critical endpoints. No hand-duplicated DTOs.
- **State:** zustand for UI/cart/session state; TanStack Query (or SWR) for server state (dashboard polling every ~3 s + invalidation after mutations — satisfies "reflects within seconds" honestly).
- **Resilience UX:** an Error Boundary around **each** module (drawer, checkout modal, simulator, each dashboard card); skeleton loaders (no layout shift); `sonner` toasts for friendly messages; every `fetch` has a timeout and a visible fallback state. A judge must never see a blank screen.
- **Accessibility:** semantic HTML, labelled inputs, focus trap + `Esc` + return-focus in the drawer/modal, `aria-live="polite"` for chat messages, keyboard-operable quick replies, WCAG AA contrast, honour `prefers-reduced-motion`.
- **Responsive:** mobile-first, verified at 375, 414, 430 px and 1440 px.
- **Performance:** server components/SSG where possible, `next/image`, fonts via `next/font`; Lighthouse (mobile) ≥ 90 Performance/Accessibility on PDP and dashboard.
- **Design:** Lavender `#F5F0FF` × Electric Purple `#7938F5` tokens only; bento cards (`rounded-bento`, `shadow-bento`); Framer Motion for purposeful micro-interactions only.
- Component rules: presentational components are pure; hooks hold logic; no component > ~200 lines; no business math in the frontend (render what the API returns).

### 6.4 Testing pyramid
1. **Unit (domain):** table-driven + property-based (`hypothesis`) — sizing determinism (same input twice → identical output), monotonicity (larger body reference never yields a smaller recommended size), non-stretch never recommended with negative shoulder ease unless the explicit fallback fires; incentive never exceeds `D_max`, never < ₹0, never offered on Prepaid/low-risk; risk score always within [0,100]; **`cod_remains_available` always true**.
2. **Golden tests (must exist):** Zara M + Chanderi (non-stretch) + tailored → **L**; H&M M + Linen + tailored → **M**; Denim with missing sleeve → note present and confidence ≤ Medium; unknown SKU → `Low (Insufficient Data)`; scenario model reproduces every deck number in E5.
3. **API tests:** `httpx.AsyncClient` against the app with in-memory SQLite + fake Gemini: happy paths, validation errors, 404s, idempotent seed, state sync (create order → appears in analytics → verify via simulator → status changes).
4. **Resilience tests:** fake Gemini raising timeout / 429 / malformed JSON → response still succeeds via backup key or fixture, with `provenance` set correctly and no 5xx.
5. **Frontend:** Vitest + Testing Library for the drawer, checkout modal, simulator reducer, dashboard cards (loading/empty/error/data states).
6. **E2E:** Playwright runs the **golden demo path** on 375 px and desktop, against local stack and (parameterised) the deployed URL.
7. `scripts/smoke_test.py` — extended from the spec; must pass against local and deployed backends.

### 6.5 Security & privacy
- Secrets only in env; `.env*` git-ignored; commit `.env.example`; add a secret scan (gitleaks or detect-secrets) to pre-commit and CI.
- Synthetic PII only (fake names/phones). Do not log full addresses/phones at INFO.
- Dependency hygiene: pinned versions; `pip-audit` and `npm audit` reviewed before release.
- The demo-reset endpoint and any admin route are disabled unless `DEMO_MODE=true` and a token matches.

### 6.6 CI (GitHub Actions) — green on every push to `main`
`backend`: ruff → mypy → pytest+coverage gate. `frontend`: lint → typecheck → vitest → `next build`. `e2e`: start stack → Playwright golden path. Cache dependencies. Branch protection not required, but never push a red `main`.

---

## 7. API contract (v1)

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | liveness (+ `{model_id, db: ok, gemini_configured: bool}` — never the key) |
| GET | `/v1/catalog/skus` | list the 4 SKUs (+ provenance summary) |
| GET | `/v1/catalog/skus/{sku_id}` | merged attributes, `missing_critical_data`, size table, provenance |
| POST | `/v1/catalog/skus/{sku_id}/extract` | run extraction (cache → live Gemini → fixture) and persist; returns attrs + `source` |
| POST | `/v1/fit/recommend` | deterministic size recommendation (+ `fit_log` row) |
| POST | `/v1/risk/evaluate` | risk index, level, factors, `checks`, `cod_remains_available=true` |
| POST | `/v1/incentive/quote` | margin-safe offer with `reason_code` and the evaluated equation terms |
| POST | `/v1/orders` | create order from checkout (persists risk + incentive + fit link) |
| GET | `/v1/orders`, `/v1/orders/{id}` | order stream / detail |
| POST | `/v1/orders/{id}/verify` | consent, landmark, slot, cancel → new status (+ normalised address) |
| POST | `/v1/orders/{id}/ndr` | demo NDR trigger / reattempt resolution |
| GET | `/v1/analytics/overview` | live metrics computed from DB (RTO and customer-return rates separate) |
| GET | `/v1/analytics/scenario` | scenario model with query overrides, defaults = deck |
| POST | `/v1/demo/reset` | guarded; restores pristine seed |

Request/response models: start from `tech_docs/02` §2, apply §5 changes (remove `order_id` from verify body; add `checks`, `reason_code`, `provenance`, `data_gaps`, `request_id` on errors).

---

## 8. Gemini integration rules

- Extraction prompt = `tech_docs/01` §3 (keep the four rules: accuracy over completion, zero hallucination, fabric integrity, objective drape). Version it (`PROMPT_VERSION`) and include it in the cache key.
- Schema = `tech_docs/01` §2. Validate every response with Pydantic; on invalid JSON → one repair retry → fixture.
- `temperature=0.1`; images downscaled to ≤ 1024 px JPEG q85 before sending.
- **Fixtures** (`data/fixtures/<sku>.json`): must be *real* extractor outputs recorded once via `scripts/record_fixtures.py` and human-reviewed. If recorded outputs are unavailable, hand-author conservative ones with `provenance: "manual_fixture"` — never present a fixture as a live call.
- UI must tell the truth about the source: `Live`, `Cached`, or `Verified Catalog Benchmark` badge on every AI-derived panel.
- The Address Normaliser uses structured output too, with a **deterministic rule-based fallback** so the simulator works offline.
- Never send real PII to Gemini; demo data is synthetic.

---

## 9. Reference math (for tests and README)

- Incentive: `Eligible Discount ≤ (P_COD_fail − P_prepaid_fail) × Direct_RTO_Cost − Payment_Fees − Margin_Floor`; defaults `0.26, 0.02, ₹200, fee 0%, floor ₹8` → expected avoided loss **₹48**, max discount **₹40**, headroom **₹8**.
- Scenario (10,000 shipments, 65% COD, 26% COD RTO, 2% prepaid RTO, ₹200/RTO, ₹40/converted order, 10% of COD converted, optional −2 pp residual COD RTO): see E5 for every expected output.
- Direct failed-delivery cost components (illustrative, Amazon Shipping/Pragma): forward ₹40–120, reverse ₹60–150, handling ₹30–80, COD ₹25–50. **₹200 is a scenario input, not an India average.**

---

## 10. Claims & copy policy

**Allowed benchmark wording (verbatim-safe):**
- "Shipway's FY25 shipment data reported around 26% COD RTO and under 2% prepaid RTO." (never "India's national RTO is 26%")
- "In Meesho's disclosed marketplace data, COD delivery-success was 75.85% vs 96.39% prepaid (six months to Sept 2025)." (delivery success ≠ RTO)
- "GS1 India and Kanvic estimate ₹1,900 crore in annual return costs attributable to poor product data."

**Forbidden anywhere in code, UI, README, demo script:** ₹18,000 crore / $2.2B; 30–35% national RTO; 53% / 32% / 15% root-cause splits; 67% abandonment due to fit; 85% don't use tape measures; 2.4 Mt CO₂ / 420 g CO₂ per RTO; 44% fit-return reduction; 58% RTO reduction; ₹54.1 lakh net profit; "100% accuracy", "guaranteed fit", "sub-800 ms vision"; "94% confidence"; "10–28% conversion shift"; "XGBoost"; "Gemini 2.0".
Savings are always "modelled direct operating savings after incentives, before fees — not net profit". Do not claim ReturnZero is the first to do RTO scoring or WhatsApp automation; the differentiator is **connecting fit data to order and SKU outcomes**.

---

## 11. Working agreement for the agent

1. **Plan first.** Before coding, produce `docs/IMPLEMENTATION_PLAN.md` mapping BUILD_PLAN phases to concrete files; flag any spec ambiguity not already covered by §5 (don't silently improvise — add an ADR).
2. **Work phase by phase** (BUILD_PLAN.md). Do not start a phase until the previous phase's gate is green.
3. **Test-first for `domain/`.** Write the golden/property tests, see them fail, then implement.
4. **Verify, don't assume.** Run the commands. Read real output. If a library API is uncertain, read the installed package/official docs — do not guess signatures. Report what you actually ran.
5. **Never fake green.** Do not weaken, skip or delete a test to pass. Do not hard-code values to satisfy a test. Do not tweak a constant to "make the offer appear" (see E2).
6. **Stay in scope** (§3.8). Park nice-to-haves in `docs/BACKLOG.md`.
7. **Windows-friendly.** The owner uses Windows (PowerShell). Prefer Python/Node scripts over bash; use `pathlib`; document both PowerShell and bash commands; avoid symlinks and `rm -rf`-style assumptions.
8. **Ask only when blocked** on something only a human can supply (API keys, product photos, account access, deployment credentials, rule clarifications). Otherwise make the best reversible decision, log it as an ADR, and continue.
9. **End every phase with a report:** what was built (files), commands run + results (lint/type/test/coverage numbers), decisions/ADRs added, open risks, and the exact human actions needed next.

### Definition of Done (per phase and for release)
- [ ] All quality gates green (ruff, mypy, pytest + coverage floors, eslint, tsc, vitest, build, e2e where applicable).
- [ ] No `TODO/FIXME`, no placeholder text, no `lorem ipsum`, no hard-coded demo numbers outside `domain/scenario.py` defaults and seed data.
- [ ] Every user-visible number traceable per §3.1; forbidden claims grep returns nothing (`scripts/check_claims.py` greps for §10 strings in code + docs and fails CI).
- [ ] Failure modes from `DEMO_DAY_DISASTER_PREVENTION.md` have an implemented countermeasure and a test.
- [ ] README + docs updated; commands in docs actually work from a clean clone.

---

## 12. Out of scope (do not build)

3D/avatar/body-scan features · custom model training or "fake ML" scores · real payment collection or gateway integration · real WhatsApp/SMS/Twilio/Meta integration · user accounts/auth for shoppers · multi-merchant tenancy · anything not required by the four demo modules.
