/** Typed API client wrapper for ReturnZero AI backend with bounded 10s timeouts. */

import type {
  SkuListResponse,
  SkuResponse,
  FitRecommendRequest,
  FitRecommendationResponse,
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
  ScenarioCalculationResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 10_000;

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly statusText: string,
    public readonly body: unknown,
  ) {
    const detailMessage =
      typeof body === "object" && body !== null && ("detail" in body || "message" in body)
        ? String(
            (body as { detail?: unknown; message?: unknown }).detail ??
              (body as { message?: unknown }).message,
          )
        : null;
    super(detailMessage ? `${detailMessage} (HTTP ${status})` : `API ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init?: RequestInit & { timeoutMs?: number; absoluteUrl?: string },
): Promise<T> {
  const url = init?.absoluteUrl ?? `${API_BASE}${path}`;
  const controller = new AbortController();
  const timeoutMs = init?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const externalSignal = init?.signal;
  const onExternalAbort = () => controller.abort();
  if (externalSignal) {
    if (externalSignal.aborted) {
      controller.abort();
    } else {
      externalSignal.addEventListener("abort", onExternalAbort, { once: true });
    }
  }

  try {
    const { timeoutMs: _t, absoluteUrl: _a, ...fetchInit } = init ?? {};
    const res = await fetch(url, {
      ...fetchInit,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...fetchInit?.headers,
      },
    });
    if (!res.ok) {
      const body = await res.json().catch(() => null);
      throw new ApiError(res.status, res.statusText, body);
    }
    return (await res.json()) as Promise<T>;
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(408, "Request Timeout", {
        message: "The API request timed out. Please verify the backend service is running.",
      });
    }
    throw err;
  } finally {
    clearTimeout(timer);
    if (externalSignal) {
      externalSignal.removeEventListener("abort", onExternalAbort);
    }
  }
}

export const api = {
  /** GET /v1/catalog/skus */
  listSkus(signal?: AbortSignal): Promise<SkuListResponse> {
    return request<SkuListResponse>("/v1/catalog/skus", { signal });
  },

  /** GET /v1/catalog/skus/:id */
  getSku(skuId: string, signal?: AbortSignal): Promise<SkuResponse> {
    return request<SkuResponse>(`/v1/catalog/skus/${encodeURIComponent(skuId)}`, { signal });
  },

  /** POST /v1/catalog/skus/:id/extract */
  extractAttributes(skuId: string, forceRefresh: boolean = false): Promise<SkuResponse> {
    return request<SkuResponse>(`/v1/catalog/skus/${encodeURIComponent(skuId)}/extract`, {
      method: "POST",
      body: JSON.stringify({ force_refresh: forceRefresh }),
    });
  },

  /** POST /v1/fit/recommend (Canonical route per AGENTS.md §7) */
  computeFit(
    skuId: string,
    payload: FitRecommendRequest,
  ): Promise<FitRecommendationResponse> {
    return request<FitRecommendationResponse>("/v1/fit/recommend", {
      method: "POST",
      body: JSON.stringify({ ...payload, sku_id: skuId }),
    });
  },

  /** POST /v1/risk/evaluate */
  evaluateRisk(
    payload: RiskEvaluateRequest,
    signal?: AbortSignal,
  ): Promise<RiskEvaluateResponse> {
    return request<RiskEvaluateResponse>("/v1/risk/evaluate", {
      method: "POST",
      body: JSON.stringify(payload),
      signal,
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
    return request<OrderResponse>(`/v1/orders/${encodeURIComponent(orderId)}`);
  },

  /** POST /v1/orders/:id/verify */
  verifyOrder(
    orderId: string,
    payload: OrderVerifyRequest,
  ): Promise<OrderResponse> {
    return request<OrderResponse>(`/v1/orders/${encodeURIComponent(orderId)}/verify`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** POST /v1/orders/:id/ndr */
  rescheduleNdr(
    orderId: string,
    payload: OrderNdrRequest,
  ): Promise<OrderResponse> {
    return request<OrderResponse>(`/v1/orders/${encodeURIComponent(orderId)}/ndr`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /** GET /v1/analytics/overview */
  getAnalyticsOverview(): Promise<AnalyticsOverviewResponse> {
    return request<AnalyticsOverviewResponse>("/v1/analytics/overview");
  },

  /** GET /v1/analytics/scenario */
  getScenario(
    params?: Record<string, string | number>,
    signal?: AbortSignal,
  ): Promise<ScenarioCalculationResponse> {
    const qs = params ? `?${new URLSearchParams(params as Record<string, string>).toString()}` : "";
    return request<ScenarioCalculationResponse>(`/v1/analytics/scenario${qs}`, { signal });
  },

  /** POST /api/demo/reset (server-side Route Handler keeps DEMO_TOKEN off client JS) */
  resetDemo(): Promise<{ status: string; message: string; seeded_orders?: number }> {
    return request<{ status: string; message: string; seeded_orders?: number }>(
      "/api/demo/reset",
      {
        absoluteUrl: "/api/demo/reset",
        method: "POST",
        body: JSON.stringify({}),
      },
    );
  },
} as const;
