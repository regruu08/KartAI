# ReturnZero AI — Human Prerequisites & Action Checklist

**Project:** ReturnZero AI (Team BioXtreme)  
**Hackathon:** Code to Cart Round 2 Buildathon (KartAI x CodeXcelerate)  
**Target:** `c:\Users\anujs\OneDrive\Desktop\kart_com`  
**Date:** 2026-11-23  
**Status:** Actionable Human Checklist  

---

## Executive Summary

To maintain rapid development while enforcing strict engineering standards, this document outlines every human decision, API key, account credential, asset, and physical approval required across all phases of the project.

### Zero-Dependency Architecture Failsafe
Every single third-party dependency (API keys, cloud accounts, photography) is designed with an **engineered zero-dependency fallback**. If a human input is delayed, development proceeds without interruption using offline fixtures, seeded datasets, and local Docker containers.

---

## Master Checklist: Hard Blockers vs. Zero-Dependency Fallbacks

| ID | Phase Needed | Action / Input / Credential | Hard Blocker? | Fallback if Not Provided | Status |
|---|---|---|---|---|---|
| **H0** | **Pre-Phase 0** | **Explicit User Approval:** Review of planning docs and confirmation to "Proceed to Phase 0". | **YES (Hard Blocker)** | None. Agent pauses execution per execution protocol until approved. | **PENDING USER APPROVAL** |
| **H1** | **Pre-Phase 0** | **Git Repository Initialization & Remote:** Confirm `git init` and GitHub remote repository URL. | **YES (Hard Blocker)** | Agent can run local `git init`, but pushing requires GitHub repository creation. | PENDING |
| **H2** | **Phase 0** | **Confirm Hackathon Rules on Pre-Event Code:** Verify on KartAI Discord whether scaffolding prior to 28 Nov 00:00 IST is permitted. | No (Soft Check) | If restricted, keep code in local branch or planning mode until 00:00 IST. | PENDING |
| **H3** | **Phase 0 / 3** | **Google AI Studio Gemini API Keys:** Two keys: `PRIMARY_GEMINI_API_KEY` and `BACKUP_GEMINI_API_KEY`. | No (Zero-Dependency Fallback) | System automatically falls back to verified benchmark fixtures in `data/fixtures/*.json` with badge `Mode: Verified Catalog Benchmark`. | OPTIONAL / FALLBACK READY |
| **H4** | **Phase 2 / 3** | **Curated Garment Editorial Photos:** 2 high-res editorial photos (front + detail) for each of the 4 fashion SKUs. | No (Zero-Dependency Fallback) | System uses high-fidelity SVG/Unsplash sample apparel images with complete measurement tables. | FALLBACK READY |
| **H5** | **Phase 7** | **Team Profiles Confirmation for README:** Full legal names, LinkedIn profiles, and roles of the 4 team members. | No (Soft Check) | Defaults to registered team roster: Aditya Kumar, Anuj Singh, Sudheesh Singh, Suryansh Singh. | VERIFIED VIA ROSTER |
| **H6** | **Phase 8** | **Cloud Deployment Accounts (Vercel & Render):** Access tokens or dashboard linking for public hosting. | No (Zero-Dependency Fallback) | System runs 100% locally via multi-container `docker-compose.yml` with localhost URLs. | FALLBACK READY |
| **H7** | **Phase 8 / Final** | **2-Minute Demo Video Recording:** Screen recording via OBS Studio (1080p60) following `docs/DEMO_SCRIPT.md`. | **YES (Human Action)** | None. Humans must record spoken audio and upload unlisted video to YouTube. | REQUIRED AT HOUR 41 |
| **H8** | **Phase 8 / Final** | **Unstop Portal Submission:** Final submission form on Unstop before Hour 47 (10:59 PM IST, 29 Nov). | **YES (Human Action)** | None. Human team lead must click submit on the Unstop portal. | REQUIRED AT HOUR 47 |

---

## Detailed Human Actions by Phase

### Pre-Phase 0: Kickoff & Workspace Authorization
- [ ] **Action H0.1 — Review Planning Documents:**  
  Review the three foundational planning files:
  1. `docs/IMPLEMENTATION_PLAN.md`
  2. `docs/DECISIONS.md`
  3. `docs/HUMAN_TODO.md`
- [ ] **Action H0.2 — Issue Execution Approval:**  
  Provide explicit prompt instruction: **"Proceed to Phase 0"**. Per the binding protocol, the team must not scaffold directories or author application code until this explicit confirmation is granted.
- [ ] **Action H0.3 — Confirm Git Remote:**  
  Confirm whether an empty GitHub repository exists (e.g. `https://github.com/<org>/returnzero-ai`). If not, approve local `git init` and initialize `main` branch.

---

### Phase 0: Scaffolding, Tooling & Environment Configuration
- [ ] **Action H1.1 — Hackathon Discord Pre-Event Check:**  
  Post a message on the KartAI / CodeXcelerate Discord `#general` or `#announcements` channel:
  > *"Hi mentors! Are teams permitted to scaffold directory structure, CI scripts, and planning documents prior to the official 28 Nov 00:00 IST kickoff, or must git commits strictly begin at 00:00 IST?"*
  - If pre-event scaffolding is permitted: Proceed with Phase 0 immediately.
  - If pre-event scaffolding is forbidden: Hold commits on a local draft until 28 Nov 00:00 IST.
- [ ] **Action H1.2 — Local Python & Node Setup:**  
  Verify local machine has:
  - Python 3.11 (`python --version`)
  - Node.js 20 LTS (`node --version`)
  - PowerShell execution policy enabled for local venvs (`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)

---

### Phase 2 & 3: AI Extraction & Garment Photography
- [ ] **Action H3.1 — Obtain Google Gemini API Keys:**  
  1. Visit [Google AI Studio](https://aistudio.google.com/).
  2. Create an API key using Google Account #1 -> Label as `PRIMARY_GEMINI_API_KEY`.
  3. Create a second API key using Google Account #2 -> Label as `BACKUP_GEMINI_API_KEY`.
  4. Paste both into local `backend/.env` (never commit this file):
     ```bash
     GEMINI_MODEL_ID=gemini-3.8-flash
     PRIMARY_GEMINI_API_KEY=AIzaSy...
     BACKUP_GEMINI_API_KEY=AIzaSy...
     DEMO_MODE=true
     DEMO_TOKEN=rz-demo-2026-secret
     ```
  - *Fallback:* If API keys are not provided immediately, the backend operates in benchmark mode using verified fixtures from `backend/app/data/fixtures/`.
- [ ] **Action H4.1 — Curate 4 Garment Product Images:**  
  Provide high-resolution editorial photos (front angle + close-up fabric texture) for:
  1. **SKU-01:** Handcrafted Chanderi Silk Kurta (`chanderi_kurta_front.jpg`, `chanderi_kurta_detail.jpg`)
  2. **SKU-02:** Relaxed Linen Mandarin Shirt (`linen_shirt_front.jpg`, `linen_shirt_detail.jpg`)
  3. **SKU-03:** Denim Trucker Jacket (`denim_jacket_front.jpg`, `denim_jacket_detail.jpg`)
  4. **SKU-04:** Floral Rayon Maxi Dress (`maxi_dress_front.jpg`, `maxi_dress_detail.jpg`)
  - Place images in `frontend/public/products/<skuId>/`.
  - *Fallback:* High-quality royalty-free fashion photography from Unsplash or generated SVG mockups will be placed by default.

---

### Phase 7: Pre-Flight Review & Documentation
- [ ] **Action H5.1 — Confirm Team Roster & Attribution:**  
  Confirm author information for `README.md` and pitch materials:
  - **Aditya Kumar** — UI/UX Design & Next.js Frontend Lead
  - **Anuj Singh** — Backend Architecture & Data Engineering Lead
  - **Sudheesh Singh** — AI Systems, Gemini VLM & Resilience Architect
  - **Suryansh Singh** — Product Strategy, Unit Economics & Narrative Lead
- [ ] **Action H5.2 — Review Demo Script:**  
  Read `docs/DEMO_SCRIPT.md` to rehearse the exact 2-minute demo flow before recording.

---

### Phase 8: Cloud Deployment & Final Submission
- [ ] **Action H6.1 — Vercel Deployment Link:**  
  1. Login to [Vercel](https://vercel.com).
  2. Import `frontend/` directory from the GitHub repository.
  3. Configure environment variable: `NEXT_PUBLIC_API_URL=https://returnzero-backend.onrender.com`.
  4. Deploy and confirm public HTTPS URL (e.g. `https://returnzero-ai.vercel.app`).
- [ ] **Action H6.2 — Render Deployment Link:**  
  1. Login to [Render](https://render.com).
  2. Create a new Web Service pointing to `backend/Dockerfile`.
  3. Set environment variables:
     - `GEMINI_MODEL_ID=gemini-3.8-flash`
     - `PRIMARY_GEMINI_API_KEY=[secret]`
     - `BACKUP_GEMINI_API_KEY=[secret]`
     - `CORS_ORIGINS=http://localhost:3000,https://returnzero-ai.vercel.app`
     - `DEMO_MODE=true`
     - `DEMO_TOKEN=[secret]`
  4. Deploy and confirm public HTTPS URL.
  - *Fallback:* If cloud deployment is not desired, the system runs locally via Docker Compose (`docker-compose up --build`) for a local live video demonstration.
- [ ] **Action H7.1 — Record 2-Minute Demo Video:**  
  - Launch OBS Studio (Canvas: 1920x1080 at 60 FPS, high-quality audio, no background noise).
  - Follow the step-by-step narrative in `docs/DEMO_SCRIPT.md`:
    - 0:00–0:25: Problem Hook & Storefront PDP
    - 0:25–0:50: "Check My Fit" Drawer & Transparent Size Recommendation
    - 0:50–1:15: Checkout Shield, Risk Checklist & Margin-Safe UPI Discount
    - 1:15–1:40: In-Browser WhatsApp Simulator & Address Landmark Normalization
    - 1:40–2:00: Merchant Command Center (Live KPIs vs 10k Scenario Modeler)
  - Upload video to YouTube as **Unlisted**.
- [ ] **Action H8.1 — Submit on Unstop Portal:**  
  - Set GitHub repository visibility to **Public**.
  - Open Unstop Code to Cart Buildathon submission page.
  - Verify all 4 team members are marked verified.
  - Submit:
    1. Public GitHub Repository Link
    2. Live Vercel Storefront URL
    3. Live Render API URL
    4. Unlisted YouTube Demo Video Link
    5. Brief writeup referencing `README.md`
  - **Hard Submission Deadline:** Submit at **Hour 47 (10:59 PM IST, 29 Nov)** to avoid last-minute portal jams.
