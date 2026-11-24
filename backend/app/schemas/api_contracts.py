r"""Pydantic v2 API Request and Response Schemas for ReturnZero AI.

Follows strict boundary validation rules:
- extra="forbid" on request models
- Exact Indian PIN code validation (^\d{6}$)
- Decimal for financial fields
- StrEnums for categorical statuses
- Clear OpenAPI documentation examples
Reference: ADR-005, ADR-007, AGENTS.md §6.2 & §7.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Status Enums ---


class OrderOutcomeStatus(StrEnum):
    """Canonical order outcome and lifecycle statuses."""

    PLACED = "Placed"
    SAFE_FOR_DISPATCH = "Safe_For_Dispatch"
    ADDRESS_UPDATED = "Address_Updated"
    DELIVERY_RESCHEDULED = "Delivery_Rescheduled"
    CANCELLED_PRE_DISPATCH = "Cancelled_Pre_Dispatch"
    DELIVERED_KEPT = "Delivered (Kept)"
    CUSTOMER_RETURNED_FIT = "Customer Returned (Fit Issue)"
    CUSTOMER_RETURNED_DEFECT = "Customer Returned (Defect)"
    COD_RTO_DOORSTEP_REFUSAL = "COD RTO (Doorstep Refusal)"
    COD_RTO_ADDRESS_INCOMPLETE = "COD RTO (Address Incomplete)"
    PREPAID_RTO_RELOCATED = "Prepaid RTO (Customer Relocated)"
    NDR = "NDR"
    NDR_RESOLVED = "NDR_Resolved"


class PaymentMethodEnum(StrEnum):
    """Permitted payment methods."""

    COD = "COD"
    PREPAID = "Prepaid"


class AddressQualityStatus(StrEnum):
    """Address evaluation classifications."""

    COMPLETE = "Complete"
    NEEDS_LANDMARK = "NeedsLandmark"
    POOR = "Poor"


class ConfidenceBand(StrEnum):
    """Categorical confidence bands for sizing recommendation."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low (Insufficient Data)"


class ProvenanceEnum(StrEnum):
    """Extraction provenance tags for catalog attributes."""

    LIVE_GEMINI = "live_gemini"
    CACHE = "cached"
    FIXTURE = "manual_fixture"


# --- Catalog Schemas ---


class SkuResponse(BaseModel):
    """Product catalog SKU response."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Unique SKU identifier (e.g. SKU-01)")
    name: str = Field(description="Garment display title")
    category: str = Field(description="Apparel category")
    price_inr: Decimal = Field(description="Retail price in INR")
    fabric_composition: str = Field(description="Detailed fabric composition and GSM")
    fabric_stretch: str = Field(description="Stretch classification")
    has_shoulder: bool = Field(description="Whether garment requires shoulder fitting")
    has_sleeve: bool = Field(description="Whether sleeve measurement is specified")
    length_inches: float | None = Field(default=None, description="Garment length in inches")
    sizes_json: dict[str, Any] = Field(description="Size measurement specifications")
    care_instructions: str | None = Field(default=None, description="Garment care instructions")
    provenance: str = Field(default="manual_fixture", description="Extraction provenance")
    extracted_at: datetime | None = Field(default=None, description="UTC extraction timestamp")
    prompt_version: str | None = Field(default=None, description="VLM prompt version")
    image_sha256: str | None = Field(default=None, description="Product image digest")


class SkuListResponse(BaseModel):
    """Catalog SKU list response."""

    model_config = ConfigDict(extra="forbid")

    skus: list[SkuResponse] = Field(description="List of available catalog items")
    total: int = Field(description="Total SKU count")


class GarmentMeasurements(BaseModel):
    """Garment dimensions for a specific size label."""

    model_config = ConfigDict(extra="forbid")

    size_label: str = Field(description="Size label, e.g. S, M, L, XL, 32, 34")
    chest_inches: float | None = Field(
        default=None, description="Chest/bust circumference in inches"
    )
    waist_inches: float | None = Field(default=None, description="Waist circumference in inches")
    hip_inches: float | None = Field(default=None, description="Hip circumference in inches")
    shoulder_inches: float | None = Field(default=None, description="Shoulder width in inches")
    length_inches: float | None = Field(
        default=None, description="Garment vertical length in inches"
    )


class ExtractedCatalogAttributes(BaseModel):
    """Multimodal extracted catalog intelligence from Gemini VLM or benchmark fixture."""

    model_config = ConfigDict(extra="forbid")

    garment_type: str = Field(description="e.g. Kurta, Shirt, Trucker Jacket, Maxi Dress")
    silhouette: Literal[
        "structured_fitted", "regular_straight", "relaxed_boxy", "fluid_oversized"
    ] = Field(description="Garment structural silhouette")
    stretch_category: Literal[
        "non_stretch", "slight_stretch", "medium_stretch", "high_stretch", "unknown"
    ] = Field(description="Fabric stretch classification")
    stated_fabric: str | None = Field(
        default=None, description="Fabric stated in listing text, e.g. 100% Chanderi Silk"
    )
    visible_closure: str | None = Field(
        default=None, description="e.g. Button placket, side zipper, smocked elastic"
    )
    measurements_table: list[GarmentMeasurements] = Field(
        default_factory=list, description="Array of size-wise garment dimensions"
    )
    missing_critical_data: list[str] = Field(
        default_factory=list,
        description="List of unstated physical attributes, e.g. ['sleeve_length']",
    )
    drape_notes: str = Field(
        description="Objective observation of garment fall, stiffness, and drape"
    )
    provenance: str = Field(
        default="live_gemini",
        description="Extraction provenance: live_gemini | cached | manual_fixture",
    )
    extracted_at: datetime | None = Field(
        default=None, description="UTC timestamp of extraction execution"
    )
    prompt_version: str | None = Field(
        default=None, description="Version of extraction prompt used"
    )


class ExtractCatalogRequest(BaseModel):
    """Optional payload for on-demand SKU attribute extraction."""

    model_config = ConfigDict(extra="forbid")

    listing_text: str | None = Field(
        default=None, description="Optional override listing title and description"
    )
    image_path: str | None = Field(
        default=None, description="Optional local file path to product photo"
    )
    force_refresh: bool = Field(
        default=False, description="Whether to bypass cache and force re-extraction"
    )


# --- Address Normalization Schemas ---


class NormalizedAddressResult(BaseModel):
    """Cleaned address, isolated landmark, and rider delivery instructions."""

    model_config = ConfigDict(extra="forbid")

    sanitized_address: str = Field(description="Standardized title-cased address string")
    landmark: str | None = Field(default=None, description="Extracted and formatted landmark")
    delivery_instructions: str = Field(
        description="Actionable last-mile instructions for delivery rider"
    )
    confidence: str = Field(default="high", description="Normalization confidence: high | medium")
    provenance: str = Field(
        default="live_gemini",
        description="Source provenance: live_gemini | deterministic_rule",
    )


class NormalizeAddressRequest(BaseModel):
    """Request payload for conversational address cleansing."""

    model_config = ConfigDict(extra="forbid")

    raw_address: str = Field(min_length=3, description="Raw customer address text")
    landmark: str | None = Field(default=None, description="Optional customer-provided landmark")


# --- Analytics Schemas ---


class TierRtoStat(BaseModel):
    """Delivery and RTO metrics for a geographical tier."""

    model_config = ConfigDict(extra="forbid")

    tier: str = Field(description="Geographical Tier (Tier-1, Tier-2, Tier-3)")
    total_orders: int = Field(description="Total orders dispatched to this tier")
    rto_count: int = Field(description="Number of courier delivery failures (RTO)")
    rto_rate_pct: float = Field(description="RTO percentage rate for this tier")


class SkuMetricStat(BaseModel):
    """Actionable merchant intelligence per apparel SKU."""

    model_config = ConfigDict(extra="forbid")

    sku_id: str = Field(description="SKU identifier")
    sku_name: str = Field(description="Display title")
    total_orders: int = Field(description="Total orders for this SKU")
    rto_count: int = Field(description="Courier failed deliveries")
    rto_rate_pct: float = Field(description="RTO failure rate percentage")
    fit_return_count: int = Field(description="Post-delivery fit-issue returns")
    fit_return_rate_pct: float = Field(description="Customer fit return percentage")
    defect_return_count: int = Field(description="Post-delivery defect returns")
    defect_return_rate_pct: float = Field(description="Customer defect return percentage")
    bracketing_count: int = Field(description="Number of multi-size cart orders")
    has_missing_measurements: bool = Field(
        description="Whether catalog lacks critical measurements"
    )
    alert_message: str | None = Field(default=None, description="Actionable merchant alert")


class AnalyticsOverviewResponse(BaseModel):
    """Live telemetry aggregated dynamically from database rows."""

    model_config = ConfigDict(extra="forbid")

    total_orders: int = Field(description="Total seeded and placed orders")
    cod_orders_count: int = Field(description="Number of Cash on Delivery orders")
    prepaid_orders_count: int = Field(description="Number of Prepaid / UPI orders")
    cod_share_pct: float = Field(description="COD percentage share of total orders")
    rto_count: int = Field(description="Total courier RTO delivery failures")
    rto_rate_pct: float = Field(description="Blended RTO failure rate (RTO orders / total orders)")
    cod_rto_count: int = Field(default=0, description="COD courier RTO failures")
    cod_rto_rate_pct: float = Field(
        default=0.0, description="COD RTO failure rate (COD RTO / COD orders)"
    )
    prepaid_rto_count: int = Field(default=0, description="Prepaid courier RTO failures")
    prepaid_rto_rate_pct: float = Field(
        default=0.0, description="Prepaid RTO failure rate (Prepaid RTO / Prepaid orders)"
    )
    customer_return_count: int = Field(description="Post-delivery customer returns (fit + defect)")
    customer_return_rate_pct: float = Field(description="Customer return rate percentage")
    delivered_kept_count: int = Field(description="Orders successfully delivered and retained")
    delivered_kept_rate_pct: float = Field(description="Delivery success and retention percentage")
    active_orders_count: int = Field(description="Orders currently in transit or verification")
    converted_to_upi_count: int = Field(description="COD orders converted to UPI via incentive")
    estimated_direct_savings_inr: Decimal = Field(
        description="Estimated direct savings from converted COD orders"
    )
    total_incentives_disbursed_inr: Decimal = Field(
        description="Cumulative UPI conversion discounts disbursed"
    )
    tier_breakdown: list[TierRtoStat] = Field(description="RTO statistics grouped by city tier")
    sku_breakdown: list[SkuMetricStat] = Field(description="Performance breakdown per SKU")
    disclaimer: str = Field(
        default=(
            "modelled direct operating savings after incentives, before fees — "
            "excluding tax, overhead, and other non-delivery costs."
        ),
        description="Binding claims compliance attribution per ADR-005 and AGENTS.md §10",
    )


class ScenarioCalculationRequest(BaseModel):
    """Input parameters for 10,000-shipment financial scenario model."""

    model_config = ConfigDict(extra="forbid")

    monthly_shipments: int = Field(
        default=10000, ge=1, le=1000000, description="Monthly shipment volume"
    )
    cod_share_pct: float = Field(default=65.0, ge=0.0, le=100.0, description="COD volume share %")
    cod_rto_pct: float = Field(default=26.0, ge=0.0, le=100.0, description="Baseline COD RTO %")
    prepaid_rto_pct: float = Field(default=2.0, ge=0.0, le=100.0, description="Prepaid RTO %")
    cost_per_rto_inr: Decimal = Field(
        default=Decimal("200.00"), ge=Decimal("0.00"), description="Cost per RTO in INR"
    )
    incentive_offer_inr: Decimal = Field(
        default=Decimal("40.00"), ge=Decimal("0.00"), description="Incentive offer in INR"
    )
    cod_conversion_pct: float = Field(
        default=10.0, ge=0.0, le=100.0, description="COD to UPI conversion rate %"
    )
    residual_cod_rto_reduction_pp: float = Field(
        default=2.0, ge=0.0, le=100.0, description="Residual COD RTO reduction percentage points"
    )
    upi_gateway_fee_pct: float = Field(
        default=0.0, ge=0.0, le=10.0, description="Payment gateway fee %"
    )


class ScenarioOutputsSchema(BaseModel):
    """Outputs generated by the scenario model."""

    model_config = ConfigDict(extra="forbid")

    baseline_cod_shipments: int
    baseline_prepaid_shipments: int
    baseline_cod_rto_shipments: int
    baseline_prepaid_rto_shipments: int
    baseline_total_rto_shipments: int
    baseline_rto_rate_pct: float
    converted_shipments: int
    new_cod_shipments: int
    new_prepaid_shipments: int
    new_cod_rto_shipments: int
    new_prepaid_rto_shipments: int
    new_total_rto_shipments: int
    new_rto_rate_pct: float
    avoided_rto_shipments: int
    gross_avoided_loss_inr: Decimal
    total_incentives_paid_inr: Decimal
    total_payment_fees_inr: Decimal
    net_operating_savings_monthly_inr: Decimal
    net_operating_savings_annual_inr: Decimal


class ScenarioCalculationResponse(BaseModel):
    """Scenario calculator API response."""

    model_config = ConfigDict(extra="forbid")

    combined_case: ScenarioOutputsSchema
    conservative_conversion_only_case: ScenarioOutputsSchema
    disclaimer: str = Field(
        default=(
            "modelled direct operating savings after incentives, before fees — "
            "excluding tax, overhead, and other non-delivery costs."
        ),
        description="Binding claims compliance attribution",
    )


# --- Demo Reset Schemas ---


class DemoResetResponse(BaseModel):
    """Response returned upon database reset."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(description="Execution status")
    message: str = Field(description="Confirmation message")
    seeded_orders: int = Field(description="Count of seeded historical orders")
    seeded_skus: int = Field(description="Count of seeded product SKUs")


# --- Sizing & Fit Schemas ---


class FitRecommendRequest(BaseModel):
    """Request payload for deterministic size recommendation."""

    model_config = ConfigDict(extra="forbid")

    sku_id: str = Field(default="", description="Target catalog SKU identifier, e.g. SKU-01")
    known_brand: str = Field(
        min_length=1, description="Shopper reference brand: Zara | H&M | Uniqlo"
    )
    known_size: str = Field(
        min_length=1, description="Shopper reference size: XS, S, M, L, XL, XXL, 32, 34..."
    )
    fit_preference: str = Field(
        default="tailored",
        description="Fit preference: tight | tailored | regular | relaxed | oversized",
    )
    height_cm: float | None = Field(
        default=None, ge=100.0, le=250.0, description="Shopper height in cm"
    )
    chest_inches: float | None = Field(
        default=None, ge=20.0, le=70.0, description="Shopper chest circumference in inches"
    )
    waist_inches: float | None = Field(
        default=None, ge=15.0, le=70.0, description="Shopper waist circumference in inches"
    )

    @field_validator("known_brand", "known_size", mode="after")
    @classmethod
    def validate_non_blank_strings(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field must not be empty or whitespace only.")
        return stripped


class FitRecommendationResponse(BaseModel):
    """Deterministic size recommendation response with transparent breakdown and gap warnings."""

    model_config = ConfigDict(extra="forbid")

    sku_id: str = Field(description="Target SKU identifier")
    recommended_size: str = Field(description="Recommended size code")
    confidence_level: str = Field(
        description="Categorical confidence band: High | Medium | Low (Insufficient Data)"
    )
    fit_score: int = Field(description="Heuristic explainability index (0-100)")
    fit_zone_breakdown: dict[str, Any] = Field(description="Breakdown per body zone")
    explanation_text: str = Field(description="Human-readable transparent fit rationale")
    missing_data_warnings: list[str] = Field(
        default_factory=list, description="Missing measurement warnings"
    )


# --- Risk & Order Review Schemas ---


class OrderReviewCheckItem(BaseModel):
    """Single item in the 3-point order review checklist."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Check identifier")
    label: str = Field(description="Human readable check label")
    status: str = Field(description="PASS | REVIEW | FAIL")


class RiskEvaluateRequest(BaseModel):
    """Request payload for order operational risk evaluation."""

    model_config = ConfigDict(extra="forbid")

    street_address: str = Field(min_length=3, description="Street address")
    pin_code: str = Field(pattern=r"^\d{6}$", description="6-digit Indian PIN code")
    payment_method: str = Field(default="COD", description="COD | Prepaid")
    has_used_fit_twin: bool = Field(
        default=True, description="Whether shopper completed fit sizing check"
    )
    is_bracketing: bool = Field(
        default=False, description="Whether cart has multiple sizes of identical SKU"
    )


class RiskEvaluateResponse(BaseModel):
    """Explainable risk evaluation result with 3-point checklist and guaranteed COD."""

    model_config = ConfigDict(extra="forbid")

    risk_score_index: int = Field(ge=0, le=100, description="Composite risk index [0, 100]")
    risk_level: str = Field(description="Low | Review | Elevated")
    contributing_factors: list[str] = Field(description="Explainable factor details")
    checks: list[OrderReviewCheckItem] = Field(description="3-point order review checklist")
    cod_remains_available: bool = Field(
        default=True, description="Guaranteed COD availability mandate"
    )


# --- Incentive Schemas ---


class IncentiveQuoteRequest(BaseModel):
    """Request payload for closed-form dynamic incentive quote."""

    model_config = ConfigDict(extra="forbid")

    cart_total_inr: Decimal = Field(ge=Decimal("0.00"), description="Cart total in INR")
    risk_score_index: int = Field(ge=0, le=100, description="Risk index from risk evaluator")
    current_payment: str = Field(default="COD", description="COD | Prepaid")
    has_used_fit_twin: bool = Field(default=True, description="Whether shopper completed fit check")
    applied_coupon_discount_inr: Decimal = Field(
        default=Decimal("0.00"), ge=Decimal("0.00"), description="Existing coupon discount"
    )
    doorstep_refusal_count: int = Field(default=0, ge=0, description="Past doorstep refusal count")
    upi_gateway_fee_pct: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        le=Decimal("10.00"),
        description="Gateway fee %",
    )


class IncentiveQuoteResponse(BaseModel):
    """Closed-form margin-safe incentive quote with guaranteed COD."""

    model_config = ConfigDict(extra="forbid")

    eligible_for_incentive: bool = Field(
        description="Whether order qualifies for instant UPI discount"
    )
    recommended_discount_inr: Decimal = Field(description="Margin-safe discount amount in INR")
    expected_savings_inr: Decimal = Field(description="Expected merchant loss avoided")
    headroom_inr: Decimal = Field(description="Retained margin headroom after discount")
    reason_code: str = Field(description="Decision reason code")
    nudge_copy: str = Field(description="State-conditioned shopper nudge copy")
    cod_remains_available: bool = Field(
        default=True, description="Guaranteed COD availability mandate"
    )


# --- Order Transaction Schemas ---


class OrderCreateRequest(BaseModel):
    """Request payload for customer order creation."""

    model_config = ConfigDict(extra="forbid")

    sku_id: str = Field(description="SKU identifier")
    size: str = Field(description="Selected garment size")
    quantity: int = Field(default=1, ge=1, le=10, description="Order quantity")
    customer_name: str = Field(min_length=2, max_length=120, description="Customer name")
    customer_phone: str = Field(min_length=10, max_length=20, description="Customer phone number")
    street_address: str = Field(min_length=3, description="Delivery address")
    city: str = Field(min_length=2, max_length=100, description="City")
    state: str = Field(min_length=2, max_length=100, description="State")
    pin_code: str = Field(pattern=r"^\d{6}$", description="6-digit Indian PIN code")
    payment_method: str = Field(default="COD", description="COD | Prepaid")
    applied_discount_inr: Decimal = Field(
        default=Decimal("0.00"), ge=Decimal("0.00"), description="Discount applied"
    )
    incentive_reason_code: str | None = Field(default=None, description="Incentive reason code")
    has_used_fit_twin: bool = Field(default=True, description="Fit check participation")
    is_bracketing: bool = Field(default=False, description="Multiple sizes in cart flag")
    known_brand: str | None = Field(default=None, description="Shopper reference brand")
    known_size: str | None = Field(default=None, description="Shopper reference size")
    fit_preference: str | None = Field(default=None, description="Shopper preference")


class OrderResponse(BaseModel):
    """Customer order details response."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Unique internal order ID")
    order_number: str = Field(description="Merchant order reference")
    customer_name: str = Field(description="Customer full name")
    street_address: str = Field(description="Delivery address")
    pin_code: str = Field(description="PIN code")
    city: str = Field(description="City")
    state: str = Field(description="State")
    tier: str = Field(description="Geographic tier (Tier-1, Tier-2, Tier-3)")
    payment_method: str = Field(description="COD or Prepaid")
    total_inr: Decimal = Field(description="Total order value in INR")
    discount_applied_inr: Decimal = Field(description="Applied discount in INR")
    selected_size: str = Field(description="Purchased garment size")
    sku_id: str = Field(description="SKU ID")
    cod_risk_score: int = Field(description="Risk score index")
    order_status: str = Field(description="Order lifecycle status")
    address_status: str = Field(description="Address quality classification")
    used_fit_check: bool = Field(description="Whether fit twin was used")
    consent_status: str = Field(
        description="WhatsApp delivery assurance consent status: opted_in | opted_out"
    )
    dispatch_priority: str = Field(description="Dispatch priority: standard | priority")
    is_synthetic: bool = Field(description="Whether order is synthetic seeded data")
    created_at: datetime = Field(description="Order creation timestamp")


class OrderListResponse(BaseModel):
    """Order listing response."""

    model_config = ConfigDict(extra="forbid")

    orders: list[OrderResponse] = Field(description="List of orders")
    total: int = Field(description="Total count of orders")


class OrderVerifyRequest(BaseModel):
    """Request payload for delivery assurance address/landmark verification."""

    model_config = ConfigDict(extra="forbid")

    landmark: str | None = Field(default=None, description="Optional landmark provided by customer")
    delivery_slot: str | None = Field(default=None, description="Preferred delivery time slot")
    opt_in_whatsapp: bool = Field(default=True, description="WhatsApp delivery assurance opt-in")


class OrderNdrRequest(BaseModel):
    """Request payload for NDR delivery reschedule."""

    model_config = ConfigDict(extra="forbid")

    reschedule_date: str = Field(description="Preferred reschedule date")
    reschedule_slot: str = Field(description="Preferred reschedule delivery slot")
