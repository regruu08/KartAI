# BUILD_PLAN.md — ReturnZero AI: phased execution plan for the AI coding agent

> Companion to `AGENTS.md` (standing rules). This file says **what to build, in what order, and what "done" means for each phase.**
> Rule of the road: **a phase is finished only when its gate is green and its report is written.**

---

## 0. Kickoff prompt (paste this into your coding agent as the first message)

```text
You are the lead engineer for ReturnZero AI (Team BioXtreme), a hackathon prototype that must also be a
showcase of clean, tested, production-grade code.

1. Read, in this order and completely: AGENTS.md → BUILD_PLAN.md → gpt/FINAL_DECK_COPY.md →
   gpt/SOURCES_AND_ASSUMPTIONS.md → tech_docs/TECH_STACK_MASTER_ARCHITECTURE.md → tech_docs/01..08 →
   DEMO_DAY_DISASTER_PREVENTION.md → PRE_EVENT_CHECKLIST.md → ROUND_2_BUILDATHON_PLAYBOOK.md.
   Skim research/ only when you need evidence. Treat root 00_…05_*.md as STALE (see AGENTS.md §2).
2. AGENTS.md §5 lists known defects in the specs and their BINDING resolutions. Follow them.
3. Do NOT write code yet. First create docs/IMPLEMENTATION_PLAN.md (phases → concrete files and tests) and
   docs/DECISIONS.md (one ADR per errata item E1–E16 plus any new ambiguity you find). Show me a summary
   and the list of HUMAN INPUTS you need (keys, product photos, accounts, rules clarifications).
4. Then execute BUILD_PLAN.md phase by phase. After each phase run the gate commands, fix everything, commit,
   and give me the phase report (files, command output summaries, ADRs, risks, next human actions).
5. Never fake green, never invent numbers, never exceed scope. If a library API is uncertain, read the
   installed package or official docs. The owner is on Windows/PowerShell.

Begin with step 1–3 now.
```

---

## 1. Human prerequisites (the agent cannot do these — track them in `docs/HUMAN_TODO.md`)

| # | Item | Needed by | Notes |
|---|---|---|---|
| H1 | **Confirm event rules**: is code written *before* 28 Nov 00:00 IST allowed? Ask on the KartAI Discord / organiser. | **Before Phase 1** | Many buildathons require work to start inside the window. If pre-built code is not allowed, use the days before only for Phase 0 docs/plans/accounts and start coding at kickoff. Don't risk disqualification. |
| H2 | Two Gemini API keys (Google AI Studio, two Google accounts) → `PRIMARY_GEMINI_API_KEY`, `BACKUP_GEMINI_API_KEY` in local `.env` | Phase 3 | Never paste keys into chat/code/commits. |
| H3 | **Product photos** for 4 SKUs (≥2 each, front + detail; JPEG/PNG; you own the rights or they're licensed/AI-generated and labelled) → `frontend/public/products/<sku>/` | Phase 3–4 | The live-Gemini demo needs real garment images. Agent may use clearly-marked placeholder SVGs for layout only. |
| H4 | Accounts: GitHub (public repo), Vercel, Render (or Cloud Run), Unstop team access, YouTube/Loom | Phase 0 / 8 | Agent prepares configs; you click "connect". |
| H5 | Deployment secrets set in Vercel/Render dashboards (`GEMINI_*`, `CORS_ORIGINS`, `DEMO_TOKEN`, `NEXT_PUBLIC_API_URL`) | Phase 0 / 8 | |
| H6 | Real team roles/names for README (deck lists Aditya Kumar, Anuj Singh, Sudheesh Singh, Suryansh Singh) | Phase 7 | |
| H7 | Demo video recording + upload (unlisted), repo set **Public**, submission form | Phase 8 | Submit ≥ 60 min before the deadline. |

---

## 2. Phase map

| Phase | Name | Output | Gate |
|---|---|---|---|
| 0 | Recon, decisions, scaffold, CI, Day-0 deploy | repo skeleton, tooling, ADRs, hello-world deployed | CI green on empty app |
| 1 | Pure domain core (test-first) | `domain/*` + tests | ruff/mypy/pytest, domain coverage ≥ 95% |
| 2 | Persistence & API | DB models, seed, repositories, routers, errors | API tests green; OpenAPI clean |
| 3 | Gemini pipeline | extractor, cache, fallbacks, key rotation, address normaliser, fixtures | resilience tests green; live check script |
| 4 | Frontend foundation, storefront, Check My Fit, Checkout Shield | PDP flow working against real API | vitest + build + manual golden path to checkout |
| 5 | WhatsApp simulator, NDR, state sync | simulator tied to real orders | e2e up to `Safe_For_Dispatch` |
| 6 | Merchant dashboard | live metrics + scenario panel + order stream + SKU alerts | numbers reconcile with DB & deck |
| 7 | Hardening, a11y, perf, docs | README, ARCHITECTURE, claims check, Lighthouse | full e2e green, claims check clean |
| 8 | Release & demo-day readiness | deployed, smoke-tested, demo script | smoke test passes on public URLs |

---

## Phase 0 — Recon, decisions, scaffold, CI, Day-0 deploy

**Tasks**
1. Read all inputs (kickoff prompt). Write `docs/IMPLEMENTATION_PLAN.md` and `docs/DECISIONS.md` (ADR-001…: one per E1–E16 + new findings).
2. Scaffold the monorepo per `AGENTS.md` §4.
   - Backend: Python 3.11, `pyproject.toml` (ruff, mypy strict, pytest, coverage), `requirements.txt`, `requirements-dev.txt`, app factory with `/healthz`, `config.py` (pydantic-settings), request-ID middleware, global error handlers.
   - Frontend: Next.js 14.2 + React 18.3 + TypeScript strict + Tailwind (tokens from `tech_docs/03`) + ESLint/Prettier + Vitest + Playwright skeleton.
3. Tooling: `.gitignore` (blocks `.env*`, `*.db`, `node_modules`, `__pycache__`, `.next`), `.env.example` (backend + frontend; `GEMINI_MODEL_ID`, `GEMINI_TIMEOUT_S`, `UPI_GATEWAY_FEE_PCT`, `DEMO_MODE`, `DEMO_TOKEN`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_DEMO_MODE`), `Makefile` + PowerShell equivalents in README, `.pre-commit-config.yaml` (ruff, prettier, eslint, gitleaks/detect-secrets, end-of-file, trailing whitespace).
4. CI workflow (`.github/workflows/ci.yml`): backend and frontend jobs per `AGENTS.md` §6.6.
5. Deployment configs: `backend/Dockerfile` (slim, non-root user, healthcheck, `$PORT`, **no** seed in CMD — seeding is in lifespan), `docker-compose.yml`, `vercel.json` if needed, Render blueprint (`render.yaml`) or Cloud Run notes. Prepare for SQLite on a persistent disk **or** accept ephemeral data because seed + reset endpoint restore state (document the choice).
6. `scripts/check_claims.py` (greps `AGENTS.md` §10 forbidden strings across `backend/`, `frontend/`, `README.md`, `docs/` — excluding the files that *define* the list) and wire into CI.

**Gate:** `make check` (or PowerShell equivalent) green; CI green; hello-world frontend + `/healthz` reachable on public URLs (after H4/H5).

---

## Phase 1 — Pure domain core (test-first)

Implement in `backend/app/domain/` with **tests written first**. No I/O, no clock, no randomness.

1. `money.py` — `Decimal` helpers: `inr()`, `pct()`, `floor_to_step(value, step)`, serialisation type.
2. `scenario.py` — the deck's financial model as a pure function with typed `ScenarioInputs`/`ScenarioResult`. **Must reproduce exactly:** baseline COD RTO 1,690, prepaid RTO 70, total 1,760; combined COD 5,850 @24% = 1,404, prepaid 4,150 @2% = 83, total 1,487; avoided 273; gross ₹54,600; incentives ₹26,000; net ₹28,600/month; ₹3,43,200/year; conversion-only: 156 avoided, ₹5,200/month, ₹62,400/year. Property test: monotonic in conversion %, zero conversion → zero incentives.
3. `incentive.py` — solver per E2 (+ `reason_code`, returns the evaluated terms: expected avoided loss, fees, floor, `D_max`, offer). Anti-abuse functions per E14 (coupon cap 20% of GMV, repeat-refusal → non-cash offer). Config in a frozen dataclass.
4. `address.py` — `address_quality()` per E3/E15 (+ landmark keyword set incl. Hinglish tokens, PIN regex, serviceable-PIN check against `data/serviceable_pins.py`).
5. `risk.py` — `RiskConfig`, explainable factor list, score ∈ [0,100], level thresholds (<40 Low, <70 Review, else Elevated), `checks` list for the Order Review card. `cod_remains_available` is a constant `True`.
6. `sizing.py` + `data/brand_matrices.py` — per E4: brand matrices (Zara/H&M/Uniqlo; Mango/Levi's/Custom must degrade gracefully with a clear "brand matrix unavailable → Zara reference + lower confidence" path, not silently), `EASE_RULES`, desired-ease map for four preferences, penalty function including waist, computed confidence band + heuristic fit score, missing-data warnings, bracketing-suppression helper (`should_suppress_bracket`).

**Golden tests that must pass**
- Zara M + Chanderi Kurta + tailored → **L**; shoulder note mentions rigid fabric.
- H&M M + Linen Shirt + tailored → **M**.
- Denim jacket with `sleeve_length = None` → warning text from `PRE_EVENT_CHECKLIST.md` §2.3; confidence ≤ Medium.
- Unknown SKU → `Low (Insufficient Data)` and no invented size rationale.
- Incentive default → ₹40, reason `REASON_ELEVATED_RISK_CONVERTIBLE`; fee 1.5% @ ₹1,899 → ineligible, `REASON_INSUFFICIENT_MARGIN`.

**Gate:** `ruff`, `mypy --strict`, `pytest` green; `domain/` coverage ≥ 95%; property tests included.

---

## Phase 2 — Persistence & API

1. `db/models.py` (SQLAlchemy 2.0 async): `SkuModel` (+ `provenance`, `extracted_at`, `prompt_version`, `image_sha256`), `OrderModel` (+ `is_synthetic`, `dispatch_priority`, `selected_size`, `sku_id`, `used_fit_check`, `consent_status`), `FitLogModel`, `IncentiveInterventionModel` (+ `reason_code`), `DeliveryEventModel`. `StrEnum` for statuses (see `PRE_EVENT_CHECKLIST.md` §3 outcomes + `Placed`, `Safe_For_Dispatch`, `Address_Updated`, `Delivery_Rescheduled`, `Cancelled_Pre_Dispatch`, NDR states).
2. `db/session.py`, `db/repositories.py` (thin, typed), `db/seed.py` per E9 (deterministic RNG, idempotent, 4 SKUs + 150 orders with the specified distributions, all `is_synthetic=True`, timestamps spread over 30 days).
3. Schemas (`schemas/`) from `tech_docs/02` + §5 changes. `extra="forbid"`; validators; examples in OpenAPI.
4. Services + routers for every endpoint in `AGENTS.md` §7 **except** Gemini-backed extraction internals (stub with the fixture path now; real adapter in Phase 3).
5. `analytics_service`: compute from DB — total shipped orders, COD share, **RTO rate** (COD + prepaid, with definition), **customer-return rate** (separate), conversion (COD→prepaid accepted incentives), estimated direct savings (modelled, using the incentive equation terms), incentive spend, per-tier RTO, per-SKU table (orders, RTO %, fit-return %, missing-data flags, bracketing count).
6. Error model + handlers; rate limiter; CORS from env.

**Gate:** API tests (happy/validation/404/idempotent seed/state-sync) green; `/docs` renders every endpoint with examples; smoke script (extended) passes locally; the default incentive case returns ₹40 end-to-end.

---

## Phase 3 — Gemini pipeline

1. `integrations/gemini/adapter.py` — the **only** file importing the SDK (E1). `Protocol`s: `CatalogExtractor`, `AddressNormalizer`. Async-safe (E16), timeout, backup-key rotation, circuit breaker, structured logging of tier used + latency (no keys/PII).
2. `extractor.py` — 3-tier flow: TTL cache → live Gemini → fixture; image preprocessing (Pillow; ≤1024 px JPEG q85; type/size validation); schema validation + one repair retry; provenance on every result.
3. `prompts.py` — system prompt from `tech_docs/01` §3 + `PROMPT_VERSION`.
4. `normalizer.py` — Gemini structured output for address cleansing + deterministic rule-based fallback (title-case, expand common abbreviations, append landmark, produce `delivery_instructions`).
5. `scripts/check_gemini.py` (live smoke: model id, latency, parsed JSON) and `scripts/record_fixtures.py` (records real outputs for the 4 SKUs into `data/fixtures/`, prints diffs for human review).
6. Wire `POST /v1/catalog/skus/{id}/extract` and make the sizing flow consume persisted attributes (E6).
7. Fake adapters + resilience tests: timeout, 429, malformed JSON, missing key, both keys failing → fixture; **never a 5xx**; provenance correct; cache hit makes zero calls.

**Gate:** resilience tests green; `check_gemini.py` succeeds with the real key (human runs if the agent lacks the key); coverage floors met.

---

## Phase 4 — Frontend: foundation, storefront, Check My Fit, Checkout Shield

1. Foundation: Tailwind tokens, `next/font`, layout shell, `lib/api/` (OpenAPI-generated types + typed client + zod on critical responses), `lib/store.ts` (zustand per `tech_docs/03` §4, extended), query provider, `sonner` toaster, module-level `ErrorBoundary`, shared UI primitives (Button, Badge, Card/Bento, Skeleton, Drawer, Modal, ProvenanceBadge, SyntheticBadge).
2. Storefront home (`/`): 4 curated SKUs, real images, price, clean grid; mobile-first.
3. PDP (`/products/[skuId]`): gallery, size selector, **Check My Fit** button, "Catalog intelligence" panel (extracted attributes, ⚠ missing fields, provenance), add to cart.
4. **Check My Fit drawer:** brand pills, size, height, fit preference (UI label "Regular" for `tailored`), explicit "No photo required" note; result card = recommended size, confidence **band**, zone breakdown, reasons, data-gap warnings; loading skeleton; fully keyboard accessible; bracketing-suppression toast when applicable.
5. Cart + **Checkout** (`/checkout`): address form (PIN validation), payment choice; on COD → call risk + quote → **Order Review** (3 checks from the API) and the optional UPI incentive modal with equal-visibility "Continue with COD". Conditional copy per E12. Accepting simulates UPI success (no real payment) → `POST /v1/orders`.
6. Order confirmation page with a "Open WhatsApp delivery assurance (simulated)" CTA linking to the simulator for that order id.

**Gate:** vitest for drawer/checkout/modal states (loading, error, empty, data); `next build` clean; ESLint/tsc clean; manual golden path from `/` to order creation on 375 px and desktop.

---

## Phase 5 — WhatsApp simulator, NDR, state sync

1. Pure reducer/state machine (`conversationMachine.ts`) mirroring `tech_docs/07` §2 + E15: consent/opt-in → pre-dispatch notice → address evaluation (`address_quality` result comes from the API, not re-implemented) → landmark clarification → slot confirmation → `Safe_For_Dispatch`; NDR flow (demo toggle) → reattempt → `NDR_Resolved`; opt-out handling.
2. UI: iPhone frame, WhatsApp-style header/bubbles/read receipts, quick-reply chips (one-click for judges) **and** free-text input; typing indicator (~800 ms, respects reduced-motion); sticky "Simulated — no real WhatsApp message is sent" ribbon; toast `[Database Synced] Order #… marked 'Safe_For_Dispatch'`.
3. Each user action calls `POST /v1/orders/{id}/verify` or `/ndr`; backend persists `DeliveryEvent`s and updates order status; address normaliser used when a landmark is given.
4. Standalone route `/simulator?order=<id>` and an embedded panel after checkout.
5. Tests: reducer table tests (every transition incl. invalid events), component tests, API state-sync test (verify → status → analytics).

**Gate:** e2e golden path reaches `Safe_For_Dispatch`; order id in chat matches the placed order; works at 375 px.

---

## Phase 6 — Merchant dashboard

1. `/dashboard` with module-isolated cards (each has its own Error Boundary + skeleton):
   - **KPI row (live, synthetic):** total orders (150 → 151…), COD share, **RTO rate**, **customer-return rate** (separate cards, with definitions on hover/tooltip), accepted conversions, incentive spend, **Estimated direct savings (modelled)** with animated count-up.
   - **Order stream table:** payment method, risk band, intervention state, reason code, status; auto-refresh ~3 s + invalidation after mutations.
   - **Tier/RTO chart (recharts):** RTO by city tier.
   - **SKU intelligence cards (the deck's "SKU and inventory feedback"):** per SKU: RTO %, fit-return %, bracketing count, missing-measurement alerts with an actionable message ("Add sleeve length to improve fit confidence").
   - **Scenario panel:** 10,000-shipment model with editable assumptions, conservative case vs combined case side by side, the explicit "+2 pp residual COD RTO is an assumption" marker, and the label *modelled direct operating savings after incentives, before fees — not net profit*.
   - **Incentive equation card:** live `D_max = (0.26 − 0.02) × ₹200 − fees − ₹8`, with fee/RTO-cost what-if inputs.
2. "Synthetic demo data" badge on every live card; "Reset demo data" button visible only when `NEXT_PUBLIC_DEMO_MODE=true` (calls the guarded endpoint with the demo token).

**Gate:** with a freshly reset DB, numbers equal hand-computed values from the seed; placing an order from the storefront visibly updates the dashboard within ~3 s; scenario panel equals the deck's figures at defaults.

---

## Phase 7 — Hardening, accessibility, performance, documentation

1. **Failure-mode drills** (`DEMO_DAY_DISASTER_PREVENTION.md`): simulate Gemini 429/timeout/no key (UI shows `Mode: Verified Catalog Benchmark`, never an error box); kill the backend mid-session (frontend shows friendly retry state); empty-DB (reset restores); bad inputs (bad PIN, empty cart, `.heic` upload) → human messages; throw inside one dashboard card (others keep working).
2. **A11y pass:** axe checks in Playwright on PDP, checkout, simulator, dashboard; manual keyboard-only run of the golden path; contrast; reduced motion.
3. **Performance:** Lighthouse mobile ≥ 90 (Performance, Accessibility, Best Practices) on PDP and dashboard; verify Fit recommendation < 1.5 s typical; no layout shift.
4. **Security pass:** `pip-audit`, `npm audit`, secret scan, CORS tightened to real origins, demo endpoints guarded, rate limits verified.
5. **Docs:**
   - `README.md` (judge-facing): one-paragraph pitch; live URL, video link; **60-second quickstart** (PowerShell + bash); architecture diagram (Mermaid); the golden demo path with screenshots/GIF; **How AI is used vs what is deterministic**; endpoint table + link to `/docs`; test/quality badges and how to run them; the E2/E5 math reproduced; assumptions & limitations (honest!); sources table; team.
   - `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/ASSUMPTIONS.md` (copy of the sources/assumptions, reproduced calculations), `docs/DECISIONS.md` finalised, `docs/DEMO_SCRIPT.md` (2-minute script: hook 10 s → problem 15 s → fit demo 30 s → checkout shield 25 s → simulator 20 s → dashboard 15 s → close 5 s; mention what is simulated).
6. Final repo hygiene: no dead code, consistent naming, dependency pins, license file, issue-free `git status`.

**Gate:** all CI jobs + e2e green; `check_claims.py` clean; Lighthouse targets met; README instructions verified from a **clean clone** in a fresh directory.

---

## Phase 8 — Release & demo-day readiness

1. Deploy `main` to Vercel + Render/Cloud Run (human connects accounts). Confirm env vars. Run `scripts/smoke_test.py <public_backend_url>`; run Playwright golden path against the public frontend URL from an incognito context.
2. **Pre-flight checklist (Hour 45)** from `DEMO_DAY_DISASTER_PREVENTION.md` — execute and record results in `docs/PREFLIGHT.md`.
3. Verify: repo is **Public**; README renders; demo video link is **Unlisted** (not Private) and plays; second Gemini key configured; `/v1/demo/reset` works; cold-start time of the backend acknowledged in the demo script (warm it up before judging/recording).
4. Tag `v1.0.0`; attach demo video link in the release notes.
5. Submission is the human's job (H7): submit ≥ 60 minutes before 11:59 PM IST on 29 Nov.

**Gate:** smoke test and e2e pass against the public URLs; checklist fully ticked.

---

## 3. Reusable follow-up prompts (paste when needed)

**Quality audit pass**
```text
Act as a strict senior reviewer. Audit the repo against AGENTS.md §3, §5, §6, §10. Run every gate
(ruff, mypy, pytest+coverage, eslint, tsc, vitest, build, e2e, scripts/check_claims.py). List defects by severity with file:line,
fix all Critical/High, re-run the gates, and report before/after numbers. Do not weaken tests.
```

**Spec-conformance pass**
```text
Compare the implemented endpoints, schemas and UI behaviour against tech_docs/01–08 and AGENTS.md §7.
Produce a table: requirement → implemented? → evidence (file/test). Fix gaps that are in scope; log deviations as ADRs.
```

**Demo rehearsal pass**
```text
Run the golden demo path end to end (local, then public URL) at 375 px and 1440 px. Inject Gemini failure (429, timeout)
and backend downtime. Report anything a judge could perceive as broken (error boxes, blank screens, NaN, dead buttons,
layout shift, unlabeled synthetic data) and fix it.
```

**Honesty pass**
```text
Grep the UI, README, docs and demo script for every number. For each: source (SOURCES_AND_ASSUMPTIONS §), DB-computed,
or labelled scenario output. Remove or relabel anything else. Confirm the forbidden-claims list is absent.
```

---

## 4. Hour-by-hour mapping (if you compress to the 48-hour window)

| Playbook hour | Agent phases |
|---|---|
| 0–2 | Phase 0 (Day-0 deploy live by hour 2) |
| 2–8 | Phase 1 + Phase 2 |
| 8–14 | Phase 3 (Gemini live with fallbacks by hour 14) |
| 14–22 | Phase 4 → **Checkpoint 1 (hour 22): post a 30-s GIF on Discord #general** |
| 22–30 | Phase 5 |
| 30–36 | Phase 6 |
| 36–38 | Phase 7 (hardening) → **code freeze at hour 38** |
| 38–47 | Phase 7 docs, Phase 8, video recording at hour 41, submit at hour 47 |

If time runs short, cut in this order (never cut the golden path or honesty/labelling): anti-abuse edge cases (E14) → tier chart polish → what-if inputs → Lighthouse tuning → extra preference/brand coverage.
