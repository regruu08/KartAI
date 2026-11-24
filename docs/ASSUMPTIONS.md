# Sources, Definitions & Assumptions

**Review date:** 18 November 2026  
**Purpose:** keep every external claim and modelled result traceable for the pitch and judge Q&A.

---

## A. External sources used

### 1. Shipway — ShipNotes FY25 RTO findings

- **Public coverage:** [Shipway launches ShipNotes and reports nearly 26% COD RTO](https://mediabrief.com/shipnotes-reveals-26-rto-rate-on-cod-orders-across-india/), and [Textile Value Chain report coverage](https://textilevaluechain.in/shipway-report-reveals-key-trends-behind-e-commerce-returns).
- **What we use:** approximate 26% RTO for COD / non-prepaid shipments and under 2% for prepaid shipments in Shipway's FY25 platform data; the report is described as covering millions of shipments. The city cohort coverage cited in the report uses a minimum shipment threshold.
- **Limitations:** a logistics provider's shipment cohort, not an official national census; product category and seller mix can affect rates; the detailed raw dataset and full statistical methodology are not published in the public coverage.
- **Pitch-safe wording:** “Shipway's FY25 shipment data reported around 26% COD RTO and under 2% prepaid RTO.” Do not say “India's national RTO rate is 26%”.

### 2. Meesho — IPO disclosures / prospectus

- **Official company page:** [Meesho IPO disclosures](https://investor.meesho.com/ipo-disclosures).
- **Regulatory filing page:** [SEBI — Meesho Limited Prospectus](https://www.sebi.gov.in/filings/public-issues/dec-2025/meesho-limited-prospectus_98226.html); the filing is dated 8 December 2025.
- **Accessible document containing the metric table:** [Meesho offer-document extract](https://indiaipo.jpmorgan.com/content/dam/jpmorgan/documents/india-private-limited/meesho-basis-of-allotment.pdf). Use the official company / SEBI filings as the authoritative document route when presenting the figure.
- **What we use:** six months ended 30 September 2025: COD was 72.00% of shipped orders; COD successful delivery rate was 75.85%; prepaid successful delivery rate was 96.39%.
- **Definition:** the filing says successful delivery counts orders delivered to consumers regardless of whether the product was subsequently returned.
- **Limitations:** platform-specific; delivery-success rate is not itself RTO rate and says nothing about whether an item was later returned.
- **Pitch-safe wording:** “In Meesho's disclosed marketplace data, the COD delivery-success rate was 75.85% versus 96.39% for prepaid for the six months ended September 2025.”

### 3. GS1 India and Kanvic Consulting — product data quality report (February 2026)

- **Report:** [Uncovering the Hidden Cost of Poor Product Data in Indian E-Commerce](https://admin.gs1india.org/uploads/Report_E_Commerce_3_3e63b6caab_df4e2396a3.pdf).
- **What we use:** estimated ₹5,000 crore annual revenue loss, ₹2,000 crore gross-margin impact and ₹1,900 crore direct return costs attributable to poor product data across Indian e-commerce and Q-commerce.
- **Method note:** the report describes population-level analysis across marketplaces, D2C and Q-commerce and a trigger-based approach linking data-quality failures to operational outcomes. The report gives examples of inconsistent size, fit and material attributes in apparel listings.
- **Limitations:** these are report estimates. ₹1,900 crore is not all return costs in India and not all RTO losses. The estimate is linked specifically to poor product data; it is not a measure of ReturnZero's addressable savings.
- **Pitch-safe wording:** “GS1 India and Kanvic estimate ₹1,900 crore in annual return costs attributable to poor product data.”

### 4. Amazon Shipping India — direct cost of failed delivery (May 2026)

- **Article:** [What Is Last-Mile Delivery? A Plain-English Guide for Indian SMBs](https://shipping.amazon.in/blog/last-mile-delivery-india-smb-guide).
- **What we use:** the article itemises forward freight (₹40–₹120), reverse freight (₹60–₹150), repackaging / quality checks (₹30–₹80) and COD handling (₹25–₹50) as direct components of failed-delivery cost, and attributes the underlying analysis to Pragma's work on 142 Indian D2C brands (2024).
- **Limitations:** the same article gives differing total-cost ranges in its narrative and itemised table; we therefore do not present a single published total as a settled benchmark. It is a logistics provider guide citing external analysis, not a merchant invoice. The ₹200 in our model is a scenario input, not the sum of a published average.
- **Pitch-safe wording:** “For illustration, the model assumes ₹200 in direct cost per failed delivery. That is a scenario input, not an India-wide average; replace it with actual carrier and handling costs.”

### 5. Shiprocket — existing RTO capability

- **Official support article:** [How can I reduce my RTO shipments?](https://support.shiprocket.in/support/solutions/articles/152000000948-how-can-i-reduce-my-rto-shipments-what-are-the-tools-offered-by-shiprocket-).
- **What it establishes:** Shiprocket lists RTO scoring, COD-to-prepaid discounts, address verification, WhatsApp tracking and NDR / delivery recovery tools.
- **Use in the pitch:** evidence that these operational features already exist; ReturnZero must differentiate through the fit-data-to-order-outcome connection, not claim these features are new.

### 6. GoKwik and ClickPost — competitive context

- **GoKwik RTO API document:** [RTO Prediction API](https://cdn.gokwik.co/rto-doc/rto-predict-api.pdf).
- **GoKwik product page:** [GoKwik RTO Protection](https://rto-assets.gokwik.co/).
- **ClickPost platform:** [ClickPost](https://www.clickpost.ai/).
- **What these establish:** RTO probability / risk intelligence, address intelligence, COD interventions, order confirmation, prepaid incentives and failed-delivery workflows are already offered by established providers.
- **Limitations:** vendor descriptions and case studies are not independent efficacy evaluations. Do not repeat vendor reduction claims as universal benchmarks.

### 7. Google — Gemini API model status

- **Current model documentation:** [Gemini 3.8 Flash](https://aistudio.google.com/docs/models/gemini-3.8-flash).
- **Release notes:** [Gemini API release notes](https://aistudio.google.com/docs/changelog).
- **What we use:** as reviewed on 18 November 2026, `gemini-3.8-flash` is listed as a stable model; the model documentation lists image input and structured output support. Google release notes list Gemini 2.0 Flash as shut down on 1 June 2026.
- **Limitations:** model IDs, access, quota, pricing and capabilities can change. Check again immediately before the event. Keep the model ID configurable.

### 8. WhatsApp Business messaging policy

- **Policy:** [WhatsApp Business Messaging Policy](https://whatsappbusiness.com/policy/).
- **What we use:** obtain appropriate opt-in, respect opt-outs, use approved message templates for business-initiated conversations where required, and make communications expected and relevant.
- **Use in the product:** the MVP uses an in-browser simulator. Do not claim real WhatsApp delivery unless the business account, consent flow, template and API integration are active.

### 9. Central Consumer Protection Authority — dark patterns

- **Official guidelines index:** [CCPA Guidelines and Advisories](https://ccpa.doca.gov.in/guidelines), which lists the Guidelines for Prevention and Regulation of Dark Patterns, 2023 and a 2025 self-audit advisory.
- **Use in the product:** no fake urgency, hidden fees, confusing default selections or coercive prepaid prompts. The prepaid offer must be optional and clear.

---

## B. Definitions that must remain consistent

| Term | Definition used in this project |
|---|---|
| RTO | A shipped parcel that is not delivered to the customer and is returned to the seller |
| Customer return | A delivered product that the customer later sends back / exchanges |
| NDR | A failed delivery attempt / non-delivery report that may still be resolved |
| Delivery success | An order delivered to the shopper; some source definitions count success regardless of subsequent customer return |
| COD-to-prepaid conversion | A customer voluntarily changes payment method before the shipment is processed |

## C. Financial model: complete assumptions

| Variable | Value | Type |
|---|---:|---|
| Monthly shipments | 10,000 | Illustrative scale input |
| COD mix | 65% | Illustrative merchant input; not a market benchmark |
| Prepaid mix | 35% | Illustrative merchant input |
| COD RTO | 26% | Shipway FY25 cohort benchmark |
| Prepaid RTO | 2% | Conservative model input using reported “under 2%” |
| Direct cost per RTO | ₹200 | Illustrative model input only; replace with merchant invoices |
| COD orders shifted to prepaid | 10% of COD orders (650) | Scenario assumption, not measured conversion |
| Discount per shifted order | ₹40 | Scenario assumption |
| Residual COD RTO improvement | 2 percentage points (26% to 24%) | Scenario assumption, not proven efficacy |

### Reproducible calculation

**Baseline**

- COD RTO = 6,500 × 26% = 1,690
- Prepaid RTO = 3,500 × 2% = 70
- Total RTO = 1,760

**Combined scenario**

- Remaining COD = 6,500 − 650 = 5,850
- Prepaid = 3,500 + 650 = 4,150
- COD RTO = 5,850 × 24% = 1,404
- Prepaid RTO = 4,150 × 2% = 83
- Total RTO = 1,487
- Avoided RTO = 1,760 − 1,487 = 273
- Gross direct cost avoided = 273 × ₹200 = ₹54,600
- Incentives = 650 × ₹40 = ₹26,000
- Direct operating savings after incentives = ₹28,600/month
- Annualised direct operating savings = ₹3,43,200 ≈ ₹3.43 lakh

**Excluded:** incremental payment gateway / processing charges, ReturnZero subscription, implementation, staffing, tax, overhead, marketing CAC, inventory opportunity cost, contribution margin from recovered sales and fit-related customer-return savings. Therefore, call this **“modelled direct operating savings after incentives, before fees”**, not net profit.

## D. Claims deliberately removed

The revised project files do not use the following prior assertions because the exact claims were not sufficiently substantiated in this review:

- ₹18,000 crore / $2.2B annual Indian RTO losses;
- 30–35% national overall RTO;
- 53% fit uncertainty / 32% COD remorse / 15% address split;
- 67% cart abandonment due to fit uncertainty;
- 85% of shoppers do not use tape measures;
- 2.4 million tonnes CO₂ from reverse logistics;
- 420 grams CO₂ avoided per RTO;
- 44% fit-return reduction;
- 58% reduction in blended RTO;
- ₹54.1 lakh annual net profit;
- 100% fit accuracy / guaranteed drape or sub-800ms end-to-end vision response.

These may be reintroduced only if the team locates a credible source or obtains measured pilot results and updates the source register.
