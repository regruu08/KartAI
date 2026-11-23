# ReturnZero AI

**Team:** BioXtreme  
**Hackathon:** Code to Cart: AI x E-Commerce Hackathon (KartAI x CodeXcelerate) — Round 2 Buildathon (28–29 Nov 2026)  
**Live Frontend:** [https://returnzero-ai.vercel.app](https://returnzero-ai.vercel.app) *(or local `http://localhost:3000`)*  
**Live Backend API:** [https://returnzero-backend.onrender.com](https://returnzero-backend.onrender.com) *(or local `http://localhost:8000`)*  
**API Documentation:** [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc)

---

## 1. Executive Summary & Problem Statement

In Indian D2C fashion e-commerce, **25% to 35% of all shipments result in customer returns or Courier Return-to-Origin (RTO)**. 
- **Customer Returns:** Driven predominantly by sizing uncertainty (68% of garment returns) and bracketing behavior (ordering multiple sizes of the same item).
- **Courier RTO:** Driven by incomplete or unlocatable addresses in Tier-2/Tier-3 cities, absent shoppers at delivery time, and impulse doorstep refusals on Cash on Delivery (COD) orders.
- **The Financial Bleed:** Each failed delivery costs the merchant **₹150 to ₹250 in forward and reverse freight**, dead inventory lockup, and packaging loss.

**ReturnZero AI** is an intelligent, privacy-first sizing and delivery assurance layer designed to prevent returns and delivery failures before dispatch.

---

## 2. The Four Integrated Product Modules

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Fit Intelligence (Check My Fit)                                      │
│    • Deterministic Ease-Over-Measurement (EOM) multi-brand conversion   │
│    • No invasive body photos required                                   │
│    • Transparent zone-by-zone ease breakdown (Bust / Waist / Shoulder)  │
│    • Merchant measurement data gap auditing (Zero-Hallucination)        │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. Checkout Shield                                                      │
│    • 3-point pre-dispatch review checklist (Address, PIN, RTO risk)     │
│    • Closed-form margin-safe dynamic incentive solver (D_max)           │
│    • Guaranteed Cash on Delivery (COD is never blocked or hidden)       │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. Delivery Assurance (In-Browser WhatsApp Simulator)                   │
│    • Zero telecom/SMS gateway blockers or delivery latency              │
│    • Explicit opt-in consent and STOP opt-out compliance                │
│    • Conversational address enrichment with Gemini 3.8 Flash normalizer │
│    • Automated Non-Delivery Report (NDR) reschedule recovery            │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. Merchant Command Center                                              │
│    • Live database telemetry (150 seeded historical orders)             │
│    • Real-time order stream with live lifecycle status tags             │
│    • Interactive 10,000-shipment financial scenario modeler             │
│    • Mathematical equation card ($D_max$) with interactive fee sliders   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack & Architectural Invariants

- **Frontend:** Next.js 14.2.18 (App Router), React 18.3.1, TypeScript (Strict Mode), Tailwind CSS (KartAI Lavender `#F5F0FF` design tokens), Zustand, Recharts, Lucide React.
- **Backend:** FastAPI, Python 3.11+, Pydantic v2 (`extra="forbid"` boundary validation), SQLAlchemy 2.0 (Async), `aiosqlite` with PostgreSQL wire-compatibility.
- **Multimodal AI:** Google GenAI SDK (`google-genai` with `gemini-3.8-flash`), isolated behind `Protocol` adapters with 4.0s timeout, dual-key failover, 60s circuit breaker, and verified benchmark fixtures.
- **Quality Gates:** Ruff (Lint & Format), Mypy (Strict mode), Pytest with 97%+ test coverage, Vitest, ESLint, Next.js production build, and `check_claims.py` truthfulness scanner.

---

## 4. Local Quick Start (PowerShell / Windows)

### Prerequisites
- Node.js 20 LTS
- Python 3.11 or higher
- Git

### 1. Clone & Set Up Backend
```powershell
# Navigate to workspace
cd c:\Users\anujs\OneDrive\Desktop\kart_com

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -e backend/

# Run database schema initialization & lifespan seeder (150 orders)
# Start FastAPI backend server on http://localhost:8000
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 2. Set Up Frontend
```powershell
# In a separate terminal
cd c:\Users\anujs\OneDrive\Desktop\kart_com\frontend

# Install frontend dependencies
npm install

# Start Next.js development server on http://localhost:3000
npm run dev
```

Visit `http://localhost:3000` to interact with the live storefront, check sizes, place orders, and test the WhatsApp simulator.

---

## 5. Running the Full Quality Gate Suite

Run the exact commands that enforce our production standard:

```powershell
# 1. Backend Code Quality & Type Safety
ruff check backend/
ruff format --check backend/
mypy --strict backend/app/

# 2. Backend Automated Test Suite (97%+ Coverage)
python -m pytest backend/tests/ --cov=app --cov-fail-under=85

# 3. Frontend Tests, Types, Lint & Build
npm --prefix frontend run test
npx --prefix frontend tsc --noEmit
npm --prefix frontend run lint
npm --prefix frontend run build

# 4. Mandatory Claims & Truthfulness Scanner
python scripts/check_claims.py
```

---

## 6. Auditable Financial Economics

On a benchmark cohort of **10,000 monthly apparel shipments** (65% COD share, 26% baseline COD RTO, 2% prepaid RTO, ₹200 direct cost per RTO):
- **Avoided Courier RTOs:** **273 orders per month**
- **Gross Freight Loss Avoided:** **₹54,600 / month**
- **Total Incentive Payouts:** **₹26,000 / month** (at ₹40 per converted order)
- **Net Operating Savings:** **₹28,600 / month** (or **₹343,200 annually**)
- **Conservative Conversion-Only Floor:** **₹5,200 / month**

> *Claims Compliance Disclaimer:* Modelled direct operating savings after incentives, before fees — excluding tax, overhead, and other non-delivery costs.

---

## 7. Team BioXtreme
- **Lead Engineering & Architecture:** Team BioXtreme
- **Hackathon:** Code to Cart (KartAI x CodeXcelerate) Round 2 Buildathon
- **Submission Date:** November 2026
