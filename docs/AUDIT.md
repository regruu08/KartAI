# Repository Audit & Architectural Assessment: ReturnZero AI

**Date:** 25 November 2026  
**Scope:** Full-stack cold audit, environment/deployment review, AI Studio UI integration, and hackathon readiness  
**Team:** BioXtreme

---

## 1. Stack & Entry Points Summary

| Layer | Technology / Version | Entry Point / Key Paths | Notes |
| :--- | :--- | :--- | :--- |
| **Backend API** | FastAPI + SQLAlchemy 2.0 Async + Pydantic v2 | `backend/app/main.py`, `backend/app/config.py` | Targets Python 3.11 (`ci.yml`); includes Request-ID middleware & rate limiting. |
| **Domain Core** | Pure Python (`Decimal` money math) | `backend/app/domain/{sizing,risk,incentive,address,scenario}.py` | Zero I/O dependencies; 100% unit/property test coverage. |
| **VLM Integration** | `google-genai` (`gemini-3.8-flash`) | `backend/app/integrations/gemini/{adapter,extractor,normalizer,cache}.py` | 4.0s timeout, backup key failover, 60s circuit breaker, deterministic offline fixtures. |
| **Frontend Storefront** | Next.js `14.2.35`, React `18.3.1`, Tailwind CSS v3 | `frontend/app/{page,template,layout}.tsx` | Self-hosted `@fontsource` typography, offline SVG plates (`public/images/sku-01..04.svg`), Framer Motion transitions, Radix UI dialogs. |
| **Server Proxy** | Next.js App Router API Route | `frontend/app/api/demo/reset/route.ts` | Keeps `DEMO_TOKEN` server-side off client JS bundles. |
| **CI & Deploy** | GitHub Actions, Docker Compose, Render | `.github/workflows/ci.yml`, `docker-compose.yml`, `render.yaml` | `claims-policy`, `backend-quality` (Python 3.11 + `greenlet`), `frontend-quality` (Node 20). |

---

## 2. Audit Findings & Resolutions (P0 / P1 / P2)

### P0 — Deployment & Core Correctness (Resolved)
- **GitHub Actions SQLAlchemy Async ImportError:** Missing `greenlet` / `sqlalchemy[asyncio]` on Linux CI runners -> Fixed in `backend/requirements.txt` and `.github/workflows/ci.yml`.
- **Dashboard Prepaid Count Drop (`PREPAID` vs `Prepaid`):** `orders.py` persisted uppercase `"PREPAID"` while `AnalyticsRepository` queried `"Prepaid"` -> Normalized persisted values and made SQL aggregation case-insensitive.
- **Uncommitted Demo Reset & Test DB Pollution:** `POST /v1/demo/reset` relied on post-response cleanup and `pytest` mutated `backend/returnzero.db` -> Added explicit `await session.commit()` in `demo.py` and isolated `pytest` in a temporary SQLite file (`conftest.py`).
- **Stale Root Database & Non-Deterministic `.env` Loading:** Relative `DATABASE_URL` and `.env` differed between repo root and `backend/` -> Fixed via `Path(__file__)` resolution in `config.py` and removed stale root `returnzero.db`.

### P1 — Economic Math, Contract & Security Bugs (Resolved)
- **Gateway Fee Percentage Unit Bug:** `/v1/incentive/quote` passed `%` values (`1.5`) directly to domain `cart_total * fee_pct` without `/ 100` -> Fixed conversion in `api/incentive.py` and wired `upi_gateway_fee_pct` into `AnalyticsService` scenario projections.
- **Hardcoded Intervention Math & Discount Boundary Checks:** `orders.py` hardcoded `₹52.00 / ₹12.00` instead of `calculate_incentive_quote` (`₹48.00` avoided loss / `₹8.00` headroom) and didn't verify quote eligibility before creating prepaid orders -> Resolved and regression tested.
- **ADR-006 Disconnected DB Sizing & Fixture Mismatch:** `fit.py` ignored DB `SkuModel` dimensions and `sku_01.json` / `DEFAULT_LISTING_TEXTS` shoulders diverged from `CURATED_SKUS` -> Wired `custom_catalog` from DB SKUs and aligned shoulder dimensions + added `Levi's` and `Marks & Spencer` matrices.
- **Deploy & Secret Hygiene:** Unified `DEMO_TOKEN` across `render.yaml` (`DEMO_RESET_TOKEN` -> `DEMO_TOKEN`), `docker-compose.yml` (`NEXT_PUBLIC_DEMO_MODE` build arg), and server-side `/api/demo/reset` proxy; restored Tailwind color scales (`emerald`/`rose`/`amber`) broken by hex string overrides.

### P2 — Experience, Accessibility & Remaining Advisories
- **UI & Transition Upgrade:** Ported AI Studio luxury typography (`Playfair Display`, `Plus Jakarta Sans`, `JetBrains Mono`), search/category/fabric catalog filtering, 3-angle PDP gallery, Radix accessible drawers/modals, and `template.tsx` route transitions while enforcing `AGENTS.md §5 E5` (`₹28,600/mo` Net vs `₹54,600` Gross).
- **Known Deferred Dependency Advisories (Hackathon Scope):**
  - Frontend `npm audit` reports advisories on `next 14.2.35` / `vitest 2.1.x` (remediation requires Next 16 / React 19, intentionally deferred per `AGENTS.md §5 E10` and `ADR-021`).
  - `backend/requirements.txt` pins `pillow>=10.2.0,<13.0.0` (upgrade to `>=13.0.0` deferred unless tested in Linux Python 3.11 container).
  - Live Google Gemini 3.8 Flash network extraction requires setting `PRIMARY_GEMINI_API_KEY` in `backend/.env`.
