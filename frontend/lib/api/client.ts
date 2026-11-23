/** Typed API client wrapper for ReturnZero AI backend. */

import type {
  SkuListResponse,
  SkuResponse,
  FitRecommendRequest,
  FitRecommendationResponse,
  ExtractedCatalogAttributes,
  AnalyticsOverviewResponse,
  RiskEvaluateRequest,
  RiskEvaluateResponse,
  IncentiveQuoteRequest,
  IncentiveQuoteResponse,
  OrderCreateRequest,
  OrderResponse,
  OrderListResponse,
  OrderVerifyRequest,
  OrderNdrRequest,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    public readonly body: unknown,
  ) {
    super(`API ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, res.statusText, body);
  }
  return res.json() as Promise<T>;
}

export const api = {
  /** GET /v1/catalog/skus */
  listSkus(): Promise<SkuListResponse> {
    return request<SkuListResponse>("/v1/catalog/skus");
  },

  /** GET /v1/catalog/skus/:id */
  getSku(skuId: string): Promise<SkuResponse> {
    return request<SkuResponse>(`/v1/catalog/skus/${skuId}`);
  },

  /** POST /v1/catalog/skus/:id/extract */
  extractAttributes(skuId: string): Promise<ExtractedCatalogAttributes> {
    return request<ExtractedCatalogAttributes>(
      `/v1/catalog/skus/${skuId}/extract`,
      { method: "POST", body: JSON.stringify({}) },
    );
  },

  /** POST /v1/catalog/skus/:id/fit */
  computeFit(
    skuId: string,
    payload: FitRecommendRequest,
  ): Promise<FitRecommendationResponse> {
    return request<FitRecommendationResponse>(`/v1/catalog/skus/${skuId}/fit`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** POST /v1/risk/evaluate */
  evaluateRisk(payload: RiskEvaluateRequest): Promise<RiskEvaluateResponse> {
    return request<RiskEvaluateResponse>("/v1/risk/evaluate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** POST /v1/incentive/quote */
  getIncentiveQuote(
    payload: IncentiveQuoteRequest,
  ): Promise<IncentiveQuoteResponse> {
    return request<IncentiveQuoteResponse>("/v1/incentive/quote", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** POST /v1/orders */
  createOrder(payload: OrderCreateRequest): Promise<OrderResponse> {
    return request<OrderResponse>("/v1/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** GET /v1/orders */
  listOrders(limit: number = 50, offset: number = 0): Promise<OrderListResponse> {
    return request<OrderListResponse>(`/v1/orders?limit=${limit}&offset=${offset}`);
  },

  /** GET /v1/orders/:id */
  getOrder(orderId: string): Promise<OrderResponse> {
    return request<OrderResponse>(`/v1/orders/${orderId}`);
  },

  /** POST /v1/orders/:id/verify */
  verifyOrder(
    orderId: string,
    payload: OrderVerifyRequest,
  ): Promise<OrderResponse> {
    return request<OrderResponse>(`/v1/orders/${orderId}/verify`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** POST /v1/orders/:id/ndr */
  rescheduleNdr(
    orderId: string,
    payload: OrderNdrRequest,
  ): Promise<OrderResponse> {
    return request<OrderResponse>(`/v1/orders/${orderId}/ndr`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** GET /v1/analytics/overview */
  getAnalyticsOverview(): Promise<AnalyticsOverviewResponse> {
    return request<AnalyticsOverviewResponse>("/v1/analytics/overview");
  },

  /** POST /v1/demo/reset */
  resetDemo(token: string = "secret-demo-token-2026"): Promise<{ status: string; message: string }> {
    return request("/v1/demo/reset", {
      method: "POST",
      headers: { "X-Demo-Token": token },
    });
  },
} as const;
