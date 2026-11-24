# ReturnZero AI — 2-Minute Demo Video Script

**Title:** ReturnZero AI: Sizing Intelligence & Delivery Assurance Layer for D2C Fashion  
**Team:** Team BioXtreme  
**Hackathon:** Code to Cart Round 2 Buildathon (KartAI x CodeXcelerate)  
**Total Target Duration:** 120 Seconds (2:00)

---

### Segment 1: The Problem & The Solution (0:00 – 0:20 | 20s)

**Visual:**
Open on the ReturnZero Storefront (`/`). Smooth scroll across the 4 curated fashion SKUs.

**Spoken Audio:**
> "In Indian fashion e-commerce, up to 30% of shipments end in costly returns and RTOs, bleeding merchants ₹150 to ₹250 per failed delivery. Shoppers bracket sizes because size charts lie, and couriers fail because Indian addresses lack landmarks.
> 
> Meet **ReturnZero AI** — the full-stack intelligence layer built for Team BioXtreme that stops returns before dispatch."

---

### Segment 2: Fit-Twin Intelligence & Merchant Data Gaps (0:20 – 0:50 | 30s)

**Visual:**
Click on **SKU-01 (Handcrafted Chanderi Silk Kurta)**. Click **"Check My Fit"**.
Select **Zara → Size M → Regular fit → 165 cm**. Click **"Analyze Sizing"**.
Show the recommended **Size L** (demonstrating how non-stretch silk prevents sizing down to M), **High Confidence**, and the zone-by-zone ease breakdown (+4.0" chest ease, +0.5" shoulder ease, with an explicit note explaining that Size M was eliminated because shoulder ease -1.5" is below the 0.0" minimum for non-stretch fabric).
Click on **SKU-03 (Raw Indigo Denim Trucker)**. Expand the **"Catalog Intelligence"** accordion to reveal the ⚠ **"Merchant Data Gaps Detected (Missing Sleeve Length)"** alert and how the confidence band drops to **Medium**.

**Spoken Audio:**
> "First: **Fit Intelligence**. No invasive body photos. A shopper selects their trusted brand—like Zara Size M. Our pure Ease-Over-Measurement engine compares garment pattern specs against fabric elasticity, recommending Size L with transparent zone-by-zone ease—demonstrating how rigid silk eliminates Size M before dispatch.
> 
> When merchants omit critical measurements—like missing sleeve length on this raw denim trucker—ReturnZero never hallucinates. It explicitly audits the data gap and penalizes confidence to protect the shopper."

---

### Segment 3: Checkout Shield & Closed-Form Incentive (0:50 – 1:15 | 25s)

**Visual:**
Add recommended Size L to cart. Go to **`/checkout`**.
Notice the multi-size bracketing warning if multiple sizes are chosen.
Enter Delhi address with PIN `110001`. Select **Cash on Delivery (COD)**.
Click **"Review Order Safety & Place"**.
The **Order Safety Review** modal pops up:
1. Show the 3-point checklist (`Address complete`, `Serviceable PIN`, `RTO risk band`).
2. Show the **"Pay via UPI & Save ₹40"** nudge.
3. Emphasize that **"Continue with Cash on Delivery"** is 100% available with equal visibility.
Click **"Pay ₹2459 via Instant UPI"**. Redirect to Confirmation page.

**Spoken Audio:**
> "Second: **Checkout Shield**. Our explainable risk engine evaluates address quality and lane risk, generating an instant 3-point review checklist.
> 
> Instead of dark patterns or blocking COD, our closed-form margin solver calculates the exact mathematically allowable discount—here, ₹40—funded entirely by avoided courier losses. COD remains 100% available, but shoppers willingly convert to prepaid."

---

### Segment 4: In-Browser WhatsApp Delivery Assurance (1:15 – 1:40 | 25s)

**Visual:**
From Confirmation, click **"Open WhatsApp Simulator"** (`/simulator`).
Show the iPhone 15 frame with the sticky ribbon: *"Simulated — no real WhatsApp message is sent"*.
1. Bot greets shopper. Shopper clicks **"YES, Confirm Updates"**.
2. Address lacks landmark. Shopper clicks **"Near Metro Pillar 120"**.
3. Shopper selects **"Morning (9 AM - 1 PM)"** delivery slot.
4. Toast flashes: **`[Database Synced] Order #... marked 'Safe_For_Dispatch'`**.
5. Click **"Simulate Courier NDR Failure"** → Bot immediately prompts reschedule → Click **"Reschedule Tomorrow Afternoon"**.

**Spoken Audio:**
> "Third: **Delivery Assurance**. Zero telecom blockers or SMS gateway drops. Our in-browser WhatsApp simulator requests explicit consent, detects missing landmarks, and captures delivery instructions.
> 
> One click confirms the slot, synchronizing directly with our database to mark the order 'Safe for Dispatch'. And if a delivery ever fails, our automated NDR flow recovers the reattempt instantly."

---

### Segment 5: Merchant Command Center & Auditable Economics (1:40 – 2:00 | 20s)

**Visual:**
Click over to **`/dashboard`**.
Show the **7 KPI cards** aggregating live data across the 150 seeded orders:
- Isolated RTO % vs Customer Return %
- Rupees Saved Ticker
- City Tier RTO bar chart (Recharts)
- Order Stream Table showing the newly placed order updated to `Safe_For_Dispatch`.
Switch to the **"10,000-Shipment Financial Scenario Modeler"** tab.
Show the deck economics: **273 avoided RTOs**, **₹28,600 monthly net savings**, and the mandatory claims attribution disclaimer.

**Spoken Audio:**
> "Finally: the **Merchant Command Center**. Live database telemetry is strictly separated from financial projections. Merchants monitor real-time orders, city-tier RTO rates, and direct rupees saved.
> 
> On a 10,000-shipment scale, ReturnZero delivers 273 avoided RTOs and ₹28,600 in net monthly operating savings—mathematically verified and auditable.
> 
> ReturnZero AI: Zero sizing doubt. Zero wasted freight. Thank you!"
