/** TypeScript types matching backend Pydantic v2 API contracts for ReturnZero AI. */

export interface GarmentMeasurements {
  size_label: string;
  chest_inches: number | null;
  waist_inches: number | null;
  hip_inches: number | null;
  shoulder_inches: number | null;
  length_inches: number | null;
}

export interface SkuResponse {
  id: string;
  name: string;
  category: string;
  price_inr: number | string;
  fabric_composition: string;
  fabric_stretch: string;
  has_shoulder: boolean;
  has_sleeve: boolean;
  length_inches: number | null;
  sizes_json: Record<string, Record<string, number>>;
  care_instructions: string | null;
  provenance: string;
  extracted_at: string | null;
  prompt_version: string | null;
  image_sha256: string | null;
}

export interface SkuListResponse {
  skus: SkuResponse[];
  total: number;
}

export interface FitZoneDetail {
  shopper_inches: number;
  garment_inches: number;
  ease_inches: number;
  status: string;
}

export interface FitRecommendRequest {
  sku_id?: string;
  known_brand: string;
  known_size: string;
  fit_preference?: string;
  height_cm?: number | null;
  chest_inches?: number | null;
  waist_inches?: number | null;
}

export interface FitRecommendationResponse {
  sku_id: string;
  recommended_size: string;
  confidence_level: "High" | "Medium" | "Low (Insufficient Data)" | string;
  fit_score: number;
  fit_zone_breakdown: Record<string, FitZoneDetail | { note: string }>;
  explanation_text: string;
  missing_data_warnings: string[];
}

export interface ExtractedCatalogAttributes {
  garment_type: string;
  silhouette: string;
  stretch_category: string;
  stated_fabric: string | null;
  visible_closure: string | null;
  measurements_table: GarmentMeasurements[];
  missing_critical_data: string[];
  drape_notes: string;
  provenance: string;
  extracted_at: string | null;
  prompt_version: string | null;
}

export interface TierRtoStat {
  tier: string;
  total_orders: number;
  rto_count: number;
  rto_rate_pct: number;
}

export interface SkuMetricStat {
  sku_id: string;
  sku_name: string;
  total_orders: number;
  rto_count: number;
  rto_rate_pct: number;
  fit_return_count: number;
  fit_return_rate_pct: number;
  defect_return_count: number;
  defect_return_rate_pct: number;
  bracketing_count: number;
  has_missing_measurements: boolean;
  alert_message: string | null;
}

export interface AnalyticsOverviewResponse {
  total_orders: number;
  cod_orders_count: number;
  prepaid_orders_count: number;
  cod_share_pct: number;
  rto_count: number;
  rto_rate_pct: number;
  cod_rto_count?: number;
  cod_rto_rate_pct?: number;
  prepaid_rto_count?: number;
  prepaid_rto_rate_pct?: number;
  customer_return_count: number;
  customer_return_rate_pct: number;
  delivered_kept_count: number;
  delivered_kept_rate_pct: number;
  active_orders_count: number;
  converted_to_upi_count: number;
  estimated_direct_savings_inr: number | string;
  net_direct_savings_inr?: number | string;
  total_incentives_disbursed_inr: number | string;
  tier_breakdown: TierRtoStat[];
  sku_breakdown: SkuMetricStat[];
  disclaimer: string;
}

export interface OrderReviewCheckItem {
  id: string;
  label: string;
  status: "PASS" | "REVIEW" | "FAIL";
}

export interface RiskEvaluateRequest {
  street_address: string;
  pin_code: string;
  payment_method?: string;
  has_used_fit_twin?: boolean;
  is_bracketing?: boolean;
}

export interface RiskEvaluateResponse {
  risk_score_index: number;
  risk_level: "Low" | "Review" | "Elevated";
  contributing_factors: string[];
  checks: OrderReviewCheckItem[];
  cod_remains_available: boolean;
}

export interface IncentiveQuoteRequest {
  cart_total_inr: number | string;
  risk_score_index: number;
  current_payment?: string;
  has_used_fit_twin?: boolean;
  applied_coupon_discount_inr?: number | string;
  doorstep_refusal_count?: number;
  upi_gateway_fee_pct?: number | string;
}

export interface IncentiveQuoteResponse {
  eligible_for_incentive: boolean;
  recommended_discount_inr: number | string;
  expected_avoided_loss_inr?: number | string;
  expected_savings_inr: number | string;
  headroom_inr: number | string;
  reason_code: string;
  nudge_copy: string;
  cod_remains_available: boolean;
}

export interface OrderCreateRequest {
  sku_id: string;
  size: string;
  quantity?: number;
  customer_name: string;
  customer_phone: string;
  street_address: string;
  city: string;
  state: string;
  pin_code: string;
  payment_method: "COD" | "Prepaid";
  applied_discount_inr?: number | string;
  incentive_reason_code?: string | null;
  has_used_fit_twin?: boolean;
  is_bracketing?: boolean;
  known_brand?: string | null;
  known_size?: string | null;
  fit_preference?: string | null;
}

export interface OrderResponse {
  id: string;
  order_number: string;
  customer_name: string;
  street_address: string;
  pin_code: string;
  city: string;
  state: string;
  tier: string;
  payment_method: string;
  total_inr: number | string;
  discount_applied_inr: number | string;
  selected_size: string;
  sku_id: string;
  cod_risk_score: number;
  order_status: string;
  address_status: string;
  used_fit_check: boolean;
  consent_status: string;
  dispatch_priority: string;
  is_synthetic: boolean;
  created_at: string;
}

export interface OrderListResponse {
  orders: OrderResponse[];
  total: number;
}

export interface OrderVerifyRequest {
  landmark?: string | null;
  delivery_slot?: string | null;
  opt_in_whatsapp: boolean;
}

export interface OrderNdrRequest {
  reschedule_date: string;
  reschedule_slot: string;
}

export interface ScenarioOutputsSchema {
  baseline_cod_shipments: number;
  baseline_prepaid_shipments: number;
  baseline_cod_rto_shipments: number;
  baseline_prepaid_rto_shipments: number;
  baseline_total_rto_shipments: number;
  baseline_rto_rate_pct: number;
  converted_shipments: number;
  new_cod_shipments: number;
  new_prepaid_shipments: number;
  new_cod_rto_shipments: number;
  new_prepaid_rto_shipments: number;
  new_total_rto_shipments: number;
  new_rto_rate_pct: number;
  avoided_rto_shipments: number;
  gross_avoided_loss_inr: number | string;
  total_incentives_paid_inr: number | string;
  total_payment_fees_inr: number | string;
  net_operating_savings_monthly_inr: number | string;
  net_operating_savings_annual_inr: number | string;
}

export interface ScenarioCalculationResponse {
  combined_case: ScenarioOutputsSchema;
  conservative_conversion_only_case: ScenarioOutputsSchema;
  disclaimer: string;
}

export type FitPreference = "tight" | "tailored" | "relaxed" | "oversized";
export type BrandName = "Zara" | "H&M" | "Uniqlo" | "Levi's" | "Marks & Spencer";
export type SizeLabel = "XS" | "S" | "M" | "L" | "XL" | "XXL";
