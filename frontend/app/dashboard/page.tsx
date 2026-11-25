"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Activity, ArrowLeft, RotateCw, Sliders } from "lucide-react";
import { api } from "@/lib/api/client";
import type { AnalyticsOverviewResponse, OrderResponse } from "@/lib/api/types";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { OverviewKPIs } from "@/components/dashboard/OverviewKPIs";
import { OrderStreamTable } from "@/components/dashboard/OrderStreamTable";
import { TierRtoChart } from "@/components/dashboard/TierRtoChart";
import { SkuIntelligenceCards } from "@/components/dashboard/SkuIntelligenceCards";
import { ScenarioModelPanel } from "@/components/dashboard/ScenarioModelPanel";
import { IncentiveEquationCard } from "@/components/dashboard/IncentiveEquationCard";
import { DemoResetButton } from "@/components/dashboard/DemoResetButton";
import { cn } from "@/lib/cn";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<"telemetry" | "scenario">("telemetry");
  const [overview, setOverview] = useState<AnalyticsOverviewResponse | null>(null);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const refreshData = async () => {
    try {
      const [ovRes, ordRes] = await Promise.all([
        api.getAnalyticsOverview(),
        api.listOrders(50, 0),
      ]);
      setOverview(ovRes);
      setOrders(ordRes.orders);
      setLastRefreshed(
        new Date().toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
      );
    } catch {
      // Keep last known snapshot gracefully
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void refreshData();
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        void refreshData();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />

      <main
        id="main-content"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 flex-1 w-full space-y-6"
      >
        {/* Top Control Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-line">
          <div className="space-y-1.5">
            <Link
              href="/"
              className="text-xs font-semibold text-ink-muted hover:text-ink inline-flex items-center gap-1"
            >
              <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
              <span>Storefront</span>
            </Link>
            <h1 className="font-display text-3xl sm:text-4xl text-ink">
              Merchant Command Center
            </h1>
            <p className="text-xs text-ink-muted">
              Live synthetic database telemetry separated from 10,000-order financial scenario
              modeling (ADR-005)
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            {lastRefreshed && (
              <span className="inline-flex items-center gap-2 rounded-full border border-trust/30 bg-trust-soft px-3.5 py-1.5 text-xs font-medium text-trust-text tabular-nums">
                <span
                  className="h-2 w-2 rounded-full bg-trust animate-pulse motion-reduce:animate-none"
                  aria-hidden="true"
                />
                <span>Live · {lastRefreshed}</span>
              </span>
            )}

            <button
              type="button"
              onClick={() => void refreshData()}
              className="min-h-[38px] px-3.5 py-1.5 rounded-full border border-line-strong bg-surface hover:bg-subtle text-ink-muted hover:text-ink transition-colors text-xs font-semibold inline-flex items-center gap-1.5 cursor-pointer"
            >
              <RotateCw className={cn("w-3.5 h-3.5", isLoading && "animate-spin")} aria-hidden="true" />
              <span>Refresh</span>
            </button>

            <DemoResetButton onResetComplete={() => void refreshData()} />
          </div>
        </div>

        {/* Animated Tab Toggle */}
        <div role="tablist" aria-label="Dashboard sections" className="flex border-b border-line space-x-6">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "telemetry"}
            onClick={() => setActiveTab("telemetry")}
            className={cn(
              "relative pb-3 text-xs sm:text-sm font-semibold flex items-center gap-2 transition-colors cursor-pointer",
              activeTab === "telemetry" ? "text-brand" : "text-ink-muted hover:text-ink",
            )}
          >
            <Activity className="w-4 h-4" aria-hidden="true" />
            <span>Live Database Telemetry ({overview?.total_orders ?? 150} Orders)</span>
            {activeTab === "telemetry" && (
              <motion.span
                layoutId="dashboard-tab-indicator"
                transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand"
              />
            )}
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "scenario"}
            onClick={() => setActiveTab("scenario")}
            className={cn(
              "relative pb-3 text-xs sm:text-sm font-semibold flex items-center gap-2 transition-colors cursor-pointer",
              activeTab === "scenario" ? "text-brand" : "text-ink-muted hover:text-ink",
            )}
          >
            <Sliders className="w-4 h-4" aria-hidden="true" />
            <span>10,000-Shipment Financial Scenario Modeler</span>
            {activeTab === "scenario" && (
              <motion.span
                layoutId="dashboard-tab-indicator"
                transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand"
              />
            )}
          </button>
        </div>

        {activeTab === "telemetry" ? (
          <motion.div
            key="telemetry"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-6"
          >
            <ErrorBoundary title="KPI strip failed to render">
              {overview ? (
                <OverviewKPIs data={overview} />
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3.5" aria-hidden="true">
                  {Array.from({ length: 7 }).map((_, idx) => (
                    <div
                      key={idx}
                      className="h-24 rounded-2xl border border-line bg-surface p-4 animate-pulse"
                    />
                  ))}
                </div>
              )}
            </ErrorBoundary>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-5">
                <ErrorBoundary title="Tier RTO chart failed to render">
                  {overview ? (
                    <TierRtoChart data={overview.tier_breakdown} />
                  ) : (
                    <div className="h-72 rounded-2xl border border-line bg-surface animate-pulse" aria-hidden="true" />
                  )}
                </ErrorBoundary>
              </div>
              <div className="lg:col-span-7">
                <ErrorBoundary title="Incentive equation widget failed to render">
                  <IncentiveEquationCard />
                </ErrorBoundary>
              </div>
            </div>

            <ErrorBoundary title="SKU audit cards failed to render">
              {overview && <SkuIntelligenceCards skus={overview.sku_breakdown} />}
            </ErrorBoundary>

            <ErrorBoundary title="Order stream table failed to render">
              <OrderStreamTable orders={orders} />
            </ErrorBoundary>

            {overview && (
              <p className="text-[11px] text-center text-ink-muted">
                {overview.disclaimer}
              </p>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="scenario"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-6"
          >
            <ErrorBoundary title="Scenario modeler failed to render">
              <ScenarioModelPanel />
            </ErrorBoundary>
            <ErrorBoundary title="Incentive equation widget failed to render">
              <IncentiveEquationCard />
            </ErrorBoundary>
          </motion.div>
        )}
      </main>

      <Footer />
    </div>
  );
}
