# Project Context: ReturnZero AI

**Project Name:** ReturnZero AI  
**Event:** Code to Cart: AI x E-Commerce Hackathon (KartAI x CodeXcelerate)  
**Team:** BioXtreme  
**Repository Working Directory:** `c:\Users\anujs\OneDrive\Desktop\kart_com`

---

## 1. System Overview
ReturnZero AI is an AI-powered fit intelligence and delivery assurance layer for D2C fashion e-commerce:
1. **Fit Intelligence ("Check My Fit"):** Resolves sizing uncertainty and multi-size bracketing using Gemini 3.8 Flash structured extraction paired with a deterministic Ease-Over-Measurement (EOM) Python engine and brand conversion matrices (`Zara`, `H&M`, `Uniqlo`, `Levi's`, `Marks & Spencer`).
2. **Checkout Shield:** Evaluates 3-point order risk (`address_quality`, `serviceable_pin`, `rto_risk`) and calculates a closed-form margin-safe UPI discount (`D_max`) without ever blocking Cash on Delivery (COD).
3. **Delivery Assurance:** In-browser consent-based WhatsApp simulator capturing landmark clarifications, delivery time slots, opt-out (`STOP`), and simulated courier NDR rescheduling synced to SQLite.
4. **Merchant Command Center:** Live dashboard segregating operational DB telemetry (Blended RTO vs Customer Returns) from interactive 10,000-shipment financial scenario modeling.

---

## 2. Current Verified Tech Stack & Architecture
- **Backend:** FastAPI, Python 3.11+ (`3.14.3` verified locally; CI targets `3.11`), Pydantic v2 (`ConfigDict(extra="forbid")`), Google GenAI SDK (`google-genai`), SQLAlchemy 2.0 Async (`sqlalchemy[asyncio]`, `greenlet`, `aiosqlite`), `pillow>=10.2.0`.
- **Frontend:** Next.js `14.2.35` (App Router), React `18.3.1`, TypeScript (`strict`), Tailwind CSS v3, Framer Motion `11.x` (`template.tsx` route transitions & `<MotionConfig reducedMotion="user">`), Radix UI (`@radix-ui/react-dialog`), TanStack Query, Zustand, Recharts, Sonner.
- **Design Tokens (ADR-023):** Alabaster Canvas (`#FAF8FD`), Surface (`#FFFFFF`), Royal Violet (`#6D28D9`), Emerald Trust (`#059669`), Amber Warning (`#D97706`), typography via `Playfair Display`, `Plus Jakarta Sans`, and `JetBrains Mono`.
- **AI Integration:** Google Gemini 3.8 Flash (`gemini-3.8-flash`) behind a `Protocol` adapter with 4.0s timeout, primary/backup key failover, circuit breaker, SHA-256 prompt-version cache, and deterministic benchmark/rule fallbacks.

---

## 3. Security & Engineering Invariants
- **Generative Perception + Deterministic Computation:** Gemini extracts unstructured attributes and addresses; pure Python decides sizing, risk, and discount headroom.
- **Zero Hallucination & Explicit Uncertainty:** Missing measurements (`SKU-03` sleeve length) trigger `has_sleeve=False` data-gap notices and cap sizing confidence at `Medium`.
- **Consumer Fairness (CCPA Dark-Pattern Safe):** `cod_remains_available` is invariant `True`; UPI incentives show explicit avoided-RTO math alongside an equal-weight COD option.
- **Environment & Secret Hygiene:** Server-side Next.js Route Handler (`/api/demo/reset`) proxies `DEMO_TOKEN` so admin tokens never ship in `NEXT_PUBLIC_*` client JavaScript bundles. `config.py` resolves `.env` and SQLite paths deterministically across root and `backend/`.
