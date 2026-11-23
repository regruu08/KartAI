# Repository Audit & Architectural Assessment: ReturnZero AI

**Date:** 23 November 2026  
**Auditor:** Principal AI Systems & Architecture Engineer  
**Hackathon:** Code to Cart: AI x E-Commerce (KartAI X CodeXcelerate)  
**Team:** BioXtreme (Aditya Kumar, Anuj Singh, Sudheesh Singh, Suryansh Singh)

---

## 1. Stack & System Topology

| Layer | Selected Technology | Version / Spec | Justification |
| :--- | :--- | :--- | :--- |
| **Frontend Storefront** | Next.js App Router, React, Tailwind CSS | Next.js 14.2+, React 19, Tailwind v3 | Server components, ultra-fast initial load (<600ms), KartAI Lavender/Electric Purple design system. |
| **Backend API Gateway** | FastAPI | Python 3.11+ | Asynchronous high-throughput REST API with native Pydantic v2 validation contracts. |
| **VLM Multimodal AI** | Google Gemini 3.8 Flash | `google-genai` SDK | Sub-second multimodal extraction from raw garment images and size charts with structured output schema. |
| **Decision Engines** | Deterministic Python | Pure Python 3.11 | Deterministic tolerance delta sizing and margin-safe unit economic calculations. Eliminates LLM hallucination. |
| **Data & Persistence** | SQLite (Async) / SQLAlchemy 2.0 | `aiosqlite`, `sqlalchemy` | Zero cloud provisioning overhead for hackathon demo; 1-line connection string migration to PostgreSQL. |
| **Delivery Simulator** | In-Browser React WhatsApp | Framer Motion, Lucide | Eliminates 48-hour Meta WhatsApp Cloud API verification delays; guarantees 100% stable interactive demo. |

---

## 2. Risk & Quality Assessment (P0 / P1 / P2)

### P0 (Deployment & Demo Blockers)
- **External Telecom Dependency:** Relying on live WhatsApp/Twilio APIs fails during hackathons due to template approval and public webhook connectivity.  
  *Mitigation:* Native in-browser WhatsApp phone mockup running the identical backend state machine and webhook contracts.
- **LLM Rate-Limits (HTTP 429) & Latency:** Multimodal calls can experience latency spikes or quota depletion.  
  *Mitigation:* Three-tier fallback engine (Tier 1: in-memory cache, Tier 2: live Gemini 3.8 Flash, Tier 3: pre-computed verified catalog fixtures).

### P1 (Correctness & Consumer Fairness)
- **Non-Deterministic Sizing Advice:** Generative text models give variable size recommendations for identical inputs.  
  *Mitigation:* Sizing is calculated strictly via mathematical tolerance delta intervals against brand conversion matrices (Zara, H&M, Uniqlo).
- **Punitive COD Blacklisting:** Blocking COD destroys top-line conversion and violates consumer protection guidelines.  
  *Mitigation:* COD remains 100% available; high RTO risk triggers an optional, margin-safe dynamic UPI discount.

### P2 (Performance & Experience)
- **Empty Database Syndrome:** Judges viewing the dashboard without historical data see empty charts.  
  *Mitigation:* High-fidelity seed cohort with 150 realistic Indian e-commerce orders and real-time state synchronization.

---

## 3. Recommended Implementation Roadmap

1. **Scaffold Directory Structure:** Create clean `backend/` and `frontend/` workspaces.
2. **Backend Services:** Implement FastAPI app, Pydantic schemas, Gemini 3.8 Flash pipeline with fallbacks, deterministic sizing engine, risk and incentive service, and SQLite database models.
3. **Seed Database:** Load 150 historical orders and 4 curated fashion SKUs.
4. **Frontend Applications:** Build Storefront PDP, Fit-Twin slide-over drawer, Dynamic Checkout Shield modal, In-browser WhatsApp simulator, and Merchant Command Center.
5. **Quality Verification:** Execute unit tests on sizing and margin solvers; test complete end-to-end user loop.
