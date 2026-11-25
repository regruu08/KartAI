"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  AnalyticsOverviewResponse,
  OrderListResponse,
  ScenarioCalculationResponse,
  SkuListResponse,
  SkuResponse,
} from "./types";

export const queryKeys = {
  skus: ["catalog", "skus"] as const,
  sku: (id: string) => ["catalog", "sku", id] as const,
  overview: ["analytics", "overview"] as const,
  scenario: (params?: Record<string, string | number>) =>
    ["analytics", "scenario", params ?? {}] as const,
  orders: (limit: number, offset: number) => ["orders", { limit, offset }] as const,
};

export function useCatalogSkus() {
  return useQuery<SkuListResponse>({
    queryKey: queryKeys.skus,
    queryFn: ({ signal }) => api.listSkus(signal),
    staleTime: 30_000,
  });
}

export function useSku(skuId: string) {
  return useQuery<SkuResponse>({
    queryKey: queryKeys.sku(skuId),
    queryFn: ({ signal }) => api.getSku(skuId, signal),
    enabled: Boolean(skuId),
  });
}

export function useExtractSku(skuId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (forceRefresh: boolean = false) =>
      api.extractAttributes(skuId, forceRefresh),
    onSuccess: (updatedSku) => {
      queryClient.setQueryData(queryKeys.sku(skuId), updatedSku);
      void queryClient.invalidateQueries({ queryKey: queryKeys.skus });
    },
  });
}

export function useAnalyticsOverview(pollIntervalMs: number = 5_000) {
  return useQuery<AnalyticsOverviewResponse>({
    queryKey: queryKeys.overview,
    queryFn: () => api.getAnalyticsOverview(),
    refetchInterval: pollIntervalMs,
  });
}

export function useOrders(limit: number = 50, offset: number = 0, pollIntervalMs: number = 5_000) {
  return useQuery<OrderListResponse>({
    queryKey: queryKeys.orders(limit, offset),
    queryFn: () => api.listOrders(limit, offset),
    refetchInterval: pollIntervalMs,
  });
}

export function useScenario(params?: Record<string, string | number>) {
  return useQuery<ScenarioCalculationResponse>({
    queryKey: queryKeys.scenario(params),
    queryFn: () => api.getScenario(params),
    staleTime: 15_000,
  });
}

export function useDemoReset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => api.resetDemo(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["analytics"] });
      void queryClient.invalidateQueries({ queryKey: ["orders"] });
      void queryClient.invalidateQueries({ queryKey: ["catalog"] });
    },
  });
}
