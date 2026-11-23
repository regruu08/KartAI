# Project Context: ReturnZero AI

**Project Name:** ReturnZero AI  
**Event:** Code to Cart: AI x E-Commerce Hackathon (KartAI X CodeXcelerate)  
**Team:** BioXtreme  
**Repository Working Directory:** `c:\Users\anujs\OneDrive\Desktop\kart_com`

---

## 1. System Overview
ReturnZero AI is an AI-powered fit intelligence and delivery assurance layer for D2C e-commerce. It addresses:
1. **Product Uncertainty:** Resolves sizing doubts and bracketing behavior on the product page using Gemini 3.8 Flash multimodal extraction paired with a deterministic sizing engine.
2. **Delivery Uncertainty:** Reduces Cash on Delivery (COD) Return-to-Origin (RTO) using an explainable checkout risk evaluator, a margin-safe dynamic UPI discount solver, and an in-browser WhatsApp delivery assurance simulator.

---

## 2. Key Tech Stack & Libraries
- **Backend:** FastAPI (Python 3.11), Pydantic v2, Google GenAI SDK (`google-genai`), SQLAlchemy 2.0 (Async), `aiosqlite`.
- **Frontend:** Next.js 14 (App Router), React 19, Tailwind CSS, Framer Motion, Lucide React, Zustand.
- **Design Tokens:** KartAI Lavender (`#F5F0FF`), Electric Purple (`#7938F5`), Bento grid layouts, glassmorphic cards.
- **AI Models:** Google Gemini 3.8 Flash (`gemini-3.8-flash`) for multimodal catalog extraction and address normalisation.

---

## 3. Four Core Demo Modules
1. **Storefront Fit Intelligence:** D2C Product Detail Page (PDP) featuring "Check My Fit-Twin" slide-over drawer with brand conversion selector (Zara/H&M/Uniqlo) and visual tension breakdown.
2. **Dynamic Checkout Shield:** Transparent order risk evaluation and algorithmic UPI incentive calculator offering margin-safe discounts (e.g. ₹40 UPI discount leaving ₹8 headroom). COD remains available.
3. **Delivery Assurance Simulator:** On-screen iPhone WhatsApp simulator with conversational landmark clarification and pre-dispatch delivery window confirmation.
4. **Merchant Command Center:** Real-time analytics dashboard with live "Rupees Saved Ticker", separate metrics for RTO vs Customer Returns, and SKU fit anomaly alerts.

---

## 4. Key Engineering Guardrails
- **Generative Perception + Deterministic Computation:** Gemini extracts data; pure Python calculates sizing and discount headroom.
- **Zero Hallucination:** Missing catalog measurements are flagged as `unknown` / `null` instead of being guessed.
- **Fairness:** COD is never forcibly disabled; shoppers are incentivized, not penalized.
- **Resilience:** Three-tier fallback engine for VLM; in-browser simulation for WhatsApp.
