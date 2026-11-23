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

from pydantic import BaseModel, ConfigDict, Field

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
    rto_rate_pct: float = Field(description="RTO failure rate (RTO orders / total orders)")
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
