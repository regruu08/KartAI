"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  LayoutDashboard,
  Activity,
  Sliders,
  RotateCw,
  ArrowLeft,
  Sparkles,
} from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { OverviewKPIs } from "@/components/dashboard/OverviewKPIs";
import { OrderStreamTable } from "@/components/dashboard/OrderStreamTable";
import { TierRtoChart } from "@/components/dashboard/TierRtoChart";
import { SkuIntelligenceCards } from "@/components/dashboard/SkuIntelligenceCards";
import { ScenarioModelPanel } from "@/components/dashboard/ScenarioModelPanel";
import { IncentiveEquationCard } from "@/components/dashboard/IncentiveEquationCard";
import { DemoResetButton } from "@/components/dashboard/DemoResetButton";
import { api } from "@/lib/api/client";
import type { AnalyticsOverviewResponse, OrderResponse } from "@/lib/api/types";

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
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch {
      // Fallback state will be gracefully maintained
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    // Auto-poll every 5 seconds to catch live order submissions
    const interval = setInterval(refreshData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">
        {/* Top Control Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-borderLight">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Link
                href="/"
                className="text-xs font-bold text-inkMuted hover:text-ink inline-flex items-center gap-1"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                Storefront
              </Link>
              <span className="text-border">/</span>
              <span className="text-xs font-bold text-brand uppercase tracking-wider">
                Control Center
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-ink flex items-center gap-2">
              Merchant Command Center
            </h1>
            <p className="text-xs text-inkMuted">
              Live database telemetry separated from financial scenario modeling (ADR-005)
            </p>
          </div>

          {/* Action Toolbar */}
          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={refreshData}
              className="p-2 rounded-lg border border-border bg-surface hover:bg-canvas text-inkMuted hover:text-ink transition-colors text-xs font-semibold flex items-center gap-1.5"
            >
              <RotateCw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <DemoResetButton onResetComplete={refreshData} />
          </div>
        </div>

        {/* Tab Toggle: Live Telemetry vs Financial Scenario */}
        <div className="flex border-b border-borderLight space-x-4">
          <button
            type="button"
            onClick={() => setActiveTab("telemetry")}
            className={`pb-3 text-xs font-bold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === "telemetry"
                ? "border-brand text-brand"
                : "border-transparent text-inkMuted hover:text-ink"
            }`}
          >
            <Activity className="w-4 h-4" />
            Live Database Telemetry (150 Orders)
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("scenario")}
            className={`pb-3 text-xs font-bold flex items-center gap-2 border-b-2 transition-all ${
              activeTab === "scenario"
                ? "border-brand text-brand"
                : "border-transparent text-inkMuted hover:text-ink"
            }`}
          >
            <Sliders className="w-4 h-4" />
            10,000-Shipment Financial Scenario Modeler
          </button>
        </div>

        {/* TAB 1: LIVE TELEMETRY */}
        {activeTab === "telemetry" && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* 7 KPI Tiles Row */}
            {overview && <OverviewKPIs data={overview} />}

            {/* Split Row: Geographic Tier Chart & Incentive Equation */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-5">
                {overview && <TierRtoChart data={overview.tier_breakdown} />}
              </div>
              <div className="lg:col-span-7">
                <IncentiveEquationCard />
              </div>
            </div>

            {/* SKU Pattern Audit & Missing Dimension Alert Cards */}
            {overview && <SkuIntelligenceCards skus={overview.sku_breakdown} />}

            {/* Real-Time Order Stream Table */}
            <OrderStreamTable orders={orders} />

            {/* Telemetry disclaimer */}
            {overview && (
              <p className="text-[10px] text-center text-inkMuted italic">
                * {overview.disclaimer}
              </p>
            )}
          </div>
        )}

        {/* TAB 2: FINANCIAL SCENARIO MODELER */}
        {activeTab === "scenario" && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <ScenarioModelPanel />
            <IncentiveEquationCard />
          </div>
        )}
      </main>
    </div>
  );
}
