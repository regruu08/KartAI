# ReturnZero AI — Frontend Master Specification & AI Studio Prompt Kit
> **Purpose:** Use this document to prompt Google AI Studio, Claude, Lovable, or v0 to generate a world-class, production-ready, luxury D2C fashion frontend for ReturnZero AI.
> Every component generated from this specification will plug directly into this repository (`frontend/`) and talk to the running FastAPI backend (`http://127.0.0.1:8000`) with zero modifications.

---

## 1. Master System Prompt for AI Studio (Copy-Paste Ready)

```markdown
You are a Principal Frontend Architect & Luxury D2C UI Designer specializing in Next.js 14 (App Router), React 18, TypeScript, and Tailwind CSS.

### Project Mission:
Build the production frontend for **ReturnZero AI** — an AI-powered fit-intelligence and delivery-assurance layer for high-end D2C fashion brands (Team BioXtreme, Code to Cart Hackathon).
The brand aesthetic should rival luxury fashion tech leaders like **Aarke, FabIndia, Nicobar, and Zara**, combined with the crisp fintech trust of **Stripe / Apple Pay**.

### Core Pillars:
1. **Fit Intelligence ("Check My Fit"):** Solves size uncertainty using deterministic ease physics and brand matrix conversions (e.g., Zara M -> Size L on 0% stretch Chanderi Silk).
2. **Checkout Shield:** Real-time 3-check order risk review + margin-safe ₹40 instant UPI incentive modal (COD is never blocked; zero dark patterns).
3. **Delivery Assurance:** In-browser WhatsApp simulator capturing landmark clarifications, delivery time slots, and NDR recoveries.
4. **Merchant Command Center:** Real-time telemetry separating Blended RTO vs Customer Returns, financial scenario modeling, and live order streams.

### Technical Stack & Dependencies:
- Framework: Next.js 14.2.x (App Router), React 18.3, TypeScript (Strict).
- Styling: Tailwind CSS with semantic tokens (Canvas: #FAF8FD, Surface: #FFFFFF, Brand: #6D28D9, Accent Emerald: #059669, Border: #F0EAF8).
- Icons: Lucide React.
- State & Sync: Zustand for cart & fit state; TanStack React Query for live telemetry polling.
- Data Integration: Talks directly to FastAPI backend on `http://127.0.0.1:8000`.

Generate modular, fully typed, responsive, accessible, and clean React components based on the page-by-page specifications provided below.
```

---

## 2. Design Tokens & Typography Architecture

### Typography
- **Headings & Fashion Editorial Accents:** `Playfair Display` or `Instrument Serif` (Italic accents for categories, e.g., *"Handcrafted Silk"*, *"Zero Returns"*).
- **Body & Numerical UI (Sizes, Prices, Metrics):** `Plus Jakarta Sans` or `Inter` (crisp, modern geometric grotesque).
- **Line Length:** Maintain max prose width `< 65ch` for readability.

### Tailwind Color Palette (`tailwind.config.ts`)
```typescript
colors: {
  canvas: "#FAF8FD",        // Subtle warm violet-tinted white background
  surface: "#FFFFFF",       // Pure white cards & modals
  surfaceSubtle: "#F9F6FE", // Flat secondary tinted surface
  brand: "#6D28D9",         // Deep royal violet (WCAG AA accessible)
  brandHover: "#5B21B6",    // Darker violet on hover
  brandMuted: "#F3E8FF",    // Soft lilac badge background
  border: "#F0EAF8",        // Ultra-fine card borders
  borderHover: "#DCCDF6",   // Hover state border
  ink: "#171321",           // Deep charcoal/ink for high contrast text
  inkMuted: "#6B7280",      // Slate gray for secondary metadata
  accentGreen: "#059669",   // Fintech trust emerald for UPI savings
  accentGreenBg: "#ECFDF5", // Light emerald tint for discount pills
  accentAmber: "#D97706",   // Warning amber for data gaps & missing sleeve alerts
  accentAmberBg: "#FFFBEB", // Light amber tint
}
```

---

## 3. Page-by-Page Specifications & Features

### A. Storefront Homepage (`/`) — *Mandatory Modernization*
1. **Announcement & Reassurance Bar (Top):**
   - Text: *"✦ Zero-Return Guarantee · Smart Fit-Twin Verified · ₹40 Instant UPI Cashback Available"*
2. **Hero Section:**
   - Badge: `Code to Cart AI x E-Commerce Hackathon · Team BioXtreme`
   - Editorial Headline: *"D2C Fashion Engineered for Perfect First-Time Fit."*
   - Subhead: *"Eliminating sizing confusion and courier RTO delivery failures using deterministic ease physics, multimodal garment extraction, and in-browser delivery assurance."*
   - Stats Pill: `1,487 Avoided RTOs · ₹54,600 Direct Monthly Savings · 0% Bracketing`
3. **Live Search & Filter Control Bar (New Feature):**
   - **Search Input:** Real-time search across product name, fabric description, and category.
   - **Category Pills:** `All (4)`, `Ethnic Apparel`, `Men's Casuals`, `Outerwear`, `Women's Western`.
   - **Fabric Stretch Filter:** `All Fabrics`, `0% Non-Stretch (Rigid)`, `Slight Stretch (Mechanical)`.
   - **Sort Dropdown:** `Featured`, `Price: Low to High`, `Price: High to Low`.
4. **Curated 4-SKU Collection Grid:**
   - Card displays: High-res garment photo, Provenance pill (`Live Gemini 3.8 Flash` / `Verified Benchmark`), Fabric composition, Price in INR, and quick "Check Fit & View" CTA.
   - **Data Gap Badge:** SKU-03 proactively displays `⚠ Missing Sleeve Length (Data Gap Audit)` warning badge.
5. **Why ReturnZero Reassurance Bento Strip:**
   - Card 1: *Deterministic Ease Engine* — No body scans, no guessing. Pure mechanical ease calculation.
   - Card 2: *Checkout Shield* — 3-point address verification and margin-safe ₹40 UPI incentive.
   - Card 3: *Delivery Assurance* — WhatsApp-based landmark clarification and delivery slot scheduling.
6. **Luxury Footer:**
   - Columns: Brand Narrative, Fit Guide Architecture, Shipping & Delivery Policy, Tech Stack Specs.

---

### B. Product Detail Page (`/products/[skuId]`)
1. **Above-the-Fold Layout:**
   - Left (55%): 2-image interactive gallery with zoom hover and fabric close-up thumbnail.
   - Right (45%): Title, category, price, fabric composition pill, size selector chips (`XS, S, M, L, XL, XXL`), and **Prominent "Check My Fit" Drawer Button**.
2. **Catalog Intelligence Panel (Collapsible Accordion):**
   - Extracted attributes from Gemini: Fabric stretch class, GSM weight, and merchant size measurements table (Chest, Waist, Shoulder, Length).
   - Provenance badge with extraction date and model ID (`gemini-3.8-flash`).
3. **Fit-Twin Recommendation Banner (Dynamic State):**
   - When a fit is calculated in the drawer, the PDP updates dynamically:
     - Badge: `✓ Fit-Twin Verified: Size L Recommended for Zara M`
     - Auto-selects Size L on the garment chips.
     - CTA becomes: `Add Size L to Cart (Fit Verified)`.

---

### C. "Check My Fit" Interactive Drawer (`components/fit-twin/FitDrawer.tsx`)
1. **Input Step:**
   - **Known Brand Selector:** Zara, H&M, Levi's, Marks & Spencer.
   - **Known Size Selector:** XS, S, M, L, XL, XXL.
   - **Fit Preference Selector:** Tight (+1.0" ease), Regular/Tailored (+2.5" ease), Relaxed (+4.0" ease), Oversized (+6.0" ease).
   - **Height Slider:** 140 cm to 200 cm (used for garment length/ankle notes).
2. **Calculation State & Visual Feedback:**
   - Instant calculation (calls `POST /v1/fit/recommend`).
   - **Recommendation Card:**
     - Recommended Size (e.g., **Size L**).
     - Fit Score Index (e.g., `71/100 · Confidence: Medium`).
     - Plain-English explanation citing brand delta and garment ease.
   - **Visual Ease Bar:**
     - Shows garment chest (42") vs estimated body chest (38") = +4.0" ease.
   - **Fabric Alert:**
     - If non-stretch silk: *"Rigid fabric with 0% spandex. Size M eliminated due to negative shoulder ease (-1.5"). Size L selected for comfortable drape."*
   - **Data Gap Alert (SKU-03):**
     - *"Merchant listing lacks sleeve length measurement. Confidence capped at Medium."*

---

### D. Checkout & Checkout Shield (`/checkout`)
1. **Shipping Details Form:**
   - Full Name, Street Address, Flat/House Number, City, 6-digit PIN code.
2. **Payment Method Selector:**
   - COD (Cash on Delivery) vs UPI / Card.
3. **3-Check Order Review Panel (Real-Time):**
   - Check 1: `Address Completeness` (Checks house #, street, landmark).
   - Check 2: `Serviceable PIN Code` (Verifies against serviceable lane list).
   - Check 3: `RTO Risk Band` (Calculated risk score 0–100, Tier classification).
4. **Margin-Safe ₹40 UPI Incentive Modal:**
   - Triggered when user selects COD on an elevated-risk order.
   - Header: *"Save ₹40 via Instant UPI + Priority Dispatch"*.
   - Value Prop: *"Pay via UPI now to lock in an instant ₹40 discount and get prioritized warehouse dispatch."*
   - Honest Transparency: Equation breakdown shown (`Avoided RTO ₹48 - Margin Floor ₹8 = ₹40 Offer`).
   - **Non-Negotiable:** "Continue with COD (₹2,499)" button is **always fully visible and enabled** (Zero dark patterns).

---

### E. In-Browser WhatsApp Delivery Simulator (`/simulator`)
1. **Smartphone Frame Container:**
   - Realistic iPhone/Android border with top speaker notch and 9:41 status bar.
   - Authentic WhatsApp green bar (`#075E54`) with verified merchant badge (`ReturnZero Store ✓`).
2. **Live Synchronization Badge:**
   - Header badge: `● Database Synced (Order: #ord_seed_150)` with quick-switch dropdown to load any recent order.
3. **Conversational Flow (State Machine):**
   - **Message 1 (Opt-in Consent):** Bot asks permission to send dispatch updates. Quick reply chip: `[YES, Confirm Updates]`.
   - **Message 2 (Address & Landmark):** Bot flags missing landmark. User quick-reply chips: `[Near Metro Pillar 120]`, `[Opposite City Hospital]`, or custom input.
   - **Message 3 (Time Slot):** Bot asks preferred delivery slot: `[Tomorrow Morning (9 AM - 1 PM)]`, `[Tomorrow Evening (4 PM - 8 PM)]`.
   - **Message 4 (Confirmation):** Status transitions to `Safe_For_Dispatch`.
4. **NDR Recovery Edge-Case Toggle:**
   - Button: `Simulate Courier NDR (Customer Unavailable)`.
   - Bot sends proactive reschedule message with 1-click reattempt request.

---

### F. Merchant Intelligence Command Center (`/dashboard`)
1. **7 Core KPI Bento Cards (ADR-020 Compliant):**
   - Total Orders Shipped: `150`
   - COD Share: `65.3%`
   - **Blended RTO Rate:** `28.7%` *(Explicitly separated from customer returns)*
   - **Customer Return Rate:** `8.0%` *(Fit/quality returns)*
   - COD to UPI Conversions: `23 orders`
   - Total Incentives Disbursed: `₹920`
   - **Estimated Direct Savings (Modelled):** `₹1,104`
2. **10,000-Shipment Financial Scenario Modeler (Deck Parity):**
   - Baseline RTO: `1,760 orders` (₹3,52,000 loss)
   - With ReturnZero: `1,487 orders` (Avoided: 273 orders)
   - Gross Savings: `₹54,600/month`
   - Incentives Paid: `₹26,000/month`
   - **Net Direct Savings:** `₹28,600/month (₹3,43,200/year)`
   - Interactive sliders to test "What-if" scenarios (Courier RTO cost, Payment gateway fee, Conversion rate).
3. **Real-Time Order Stream Table:**
   - Columns: Order ID, Timestamp, Customer Name, SKU / Size, Delivery PIN / City Tier, Risk Score Index, Lifecycle Status, Actions (Deep link to simulate in WhatsApp).
   - Filter pills: `All`, `High Risk`, `Safe for Dispatch`, `NDR Pending`, `Delivered`.

---

## 4. Complete Backend API Contracts & TypeScript Schemas

All components can consume these exact types. The backend runs at `http://127.0.0.1:8000`.

```typescript
// 1. Catalog SKU Schema
export interface CatalogSku {
  id: string; // e.g. "SKU-01"
  name: string;
  category: string;
  price_inr: number;
  fabric_stretch: "non_stretch" | "slight_stretch" | "stretch";
  fabric_composition: string;
  has_gap: boolean;
  image_url: string;
  provenance: "live_gemini" | "cached" | "manual_fixture";
  description: string;
  measurements_inches: {
    chest: number;
    waist?: number;
    shoulder?: number;
    length?: number;
    sleeve_length?: number; // Missing in SKU-03
  };
}

// 2. Fit Recommendation Contract
// POST /v1/fit/recommend
export interface FitRecommendRequest {
  sku_id: string;
  known_brand: "Zara" | "H&M" | "Levi's" | "Marks & Spencer";
  known_size: "XS" | "S" | "M" | "L" | "XL" | "XXL";
  fit_preference: "tight" | "tailored" | "relaxed" | "oversized"; // "tailored" renders as "Regular"
  height_cm?: number;
}

export interface FitRecommendResponse {
  recommended_size: string;
  confidence_level: "High" | "Medium" | "Low (Insufficient Data)";
  fit_score_index: number; // 0-100 heuristic
  explanation: string;
  ease_breakdown: {
    bust_ease_inches: number;
    waist_ease_inches?: number;
    shoulder_ease_inches?: number;
  };
  warnings: string[];
  missing_data_notes: string[];
}

// 3. Risk Evaluation Contract
// POST /v1/risk/evaluate
export interface RiskEvaluateRequest {
  order_id?: string;
  cart_value_inr: number;
  payment_method: "COD" | "PREPAID";
  pin_code: string;
  street_address: string;
  city_tier: 1 | 2 | 3;
  is_fit_verified: boolean;
}

export interface RiskEvaluateResponse {
  risk_score_index: number; // 0-100
  risk_tier: "LOW" | "ELEVATED" | "CRITICAL";
  is_elevated_risk: boolean;
  order_review_checks: Array<{
    id: "address_completeness" | "pin_serviceability" | "rto_risk_band";
    label: string;
    status: "PASS" | "WARNING" | "FAIL";
    detail: string;
  }>;
}

// 4. Incentive Quote Contract
// POST /v1/incentive/quote
export interface IncentiveQuoteRequest {
  cart_value_inr: number;
  risk_score_index: number;
  payment_method: "COD" | "PREPAID";
  gateway_fee_pct?: number; // default 0.0
}

export interface IncentiveQuoteResponse {
  is_eligible: boolean;
  offered_discount_inr: number; // e.g. 40
  headroom_inr: number; // e.g. 8
  reason_code: string;
  cod_remains_available: true; // Always true
  formula_breakdown: {
    avoided_rto_loss_inr: number;
    margin_floor_inr: number;
    net_benefit_inr: number;
  };
}

// 5. Order Creation & Verification Contract
// POST /v1/orders
export interface CreateOrderRequest {
  sku_id: string;
  selected_size: string;
  customer_name: string;
  phone_number: string;
  street_address: string;
  pin_code: string;
  payment_method: "COD" | "PREPAID";
  discount_applied_inr?: number;
  is_fit_verified: boolean;
}

// POST /v1/orders/{order_id}/verify
export interface VerifyOrderRequest {
  landmark?: string;
  preferred_slot?: string;
  confirm_opt_in?: boolean;
}

export interface OrderRecord {
  id: string; // e.g. "ord_seed_150"
  created_at: string;
  customer_name: string;
  street_address: string;
  pin_code: string;
  sku_id: string;
  selected_size: string;
  cart_value_inr: number;
  payment_method: "COD" | "PREPAID";
  order_status: "PLACED" | "PENDING_VERIFICATION" | "SAFE_FOR_DISPATCH" | "IN_TRANSIT" | "DELIVERED" | "RTO_RETURNED";
  risk_score_index: number;
  is_fit_verified: boolean;
}

// 6. Analytics Overview Contract
// GET /v1/analytics/overview
export interface AnalyticsOverviewResponse {
  total_orders_shipped: number;
  cod_order_count: number;
  prepaid_order_count: number;
  cod_share_pct: number;
  blended_rto_rate_pct: number;
  customer_return_rate_pct: number;
  cod_to_upi_conversions: number;
  total_incentives_disbursed_inr: number;
  modelled_direct_savings_inr: number;
}
```

---

## 5. Instructions for Applying AI Studio Outputs to this Repository

When you generate code using AI Studio, provide the components back to this agent by:
1. Saving files into the designated paths:
   - Storefront Home: `frontend/app/page.tsx`
   - Navigation: `frontend/components/ui/Navbar.tsx`
   - Storefront Filter & Search Bar: `frontend/components/storefront/ProductFilterBar.tsx`
   - PDP: `frontend/app/products/[skuId]/page.tsx`
   - Fit Drawer: `frontend/components/fit-twin/FitDrawer.tsx`
   - Checkout Modal: `frontend/components/checkout/OrderReviewModal.tsx`
   - Simulator: `frontend/app/simulator/page.tsx`
   - Dashboard: `frontend/app/dashboard/page.tsx`
2. Every component will automatically connect to `http://127.0.0.1:8000` via `frontend/lib/api.ts`.
3. Run `npm test` and `npx tsc --noEmit` to verify 100% build pass.
