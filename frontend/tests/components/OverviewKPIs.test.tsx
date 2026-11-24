import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { OverviewKPIs } from "../../components/dashboard/OverviewKPIs";
import type { AnalyticsOverviewResponse } from "../../lib/api/types";

describe("OverviewKPIs Component", () => {
  const mockData: AnalyticsOverviewResponse = {
    total_orders: 150,
    cod_orders_count: 98,
    prepaid_orders_count: 52,
    cod_share_pct: 65.3,
    rto_count: 24,
    rto_rate_pct: 16.0,
    customer_return_count: 12,
    customer_return_rate_pct: 8.0,
    delivered_kept_count: 114,
    delivered_kept_rate_pct: 76.0,
    active_orders_count: 0,
    converted_to_upi_count: 14,
    estimated_direct_savings_inr: 728,
    total_incentives_disbursed_inr: 560,
    tier_breakdown: [],
    sku_breakdown: [],
    disclaimer: "modelled direct operating savings after incentives, before fees",
  };

  it("renders all 7 key metrics with isolated RTO vs customer return separation", () => {
    render(<OverviewKPIs data={mockData} />);

    expect(screen.getByText("Shipped Orders")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();

    expect(screen.getByText("COD Share")).toBeInTheDocument();
    expect(screen.getByText("65.3%")).toBeInTheDocument();

    expect(screen.getByText("Blended RTO Rate")).toBeInTheDocument();
    expect(screen.getByText("16.0%")).toBeInTheDocument();

    expect(screen.getByText("Customer Return Rate")).toBeInTheDocument();
    expect(screen.getByText("8.0%")).toBeInTheDocument();

    expect(screen.getByText("COD → UPI Conversions")).toBeInTheDocument();
    expect(screen.getByText("14")).toBeInTheDocument();

    expect(screen.getByText("Modelled Direct Savings")).toBeInTheDocument();
    expect(screen.getByText("₹728")).toBeInTheDocument();
  });

  it("renders explicit COD and Prepaid RTO subtitles when provided", () => {
    const dataWithBreakdown: AnalyticsOverviewResponse = {
      ...mockData,
      cod_rto_rate_pct: 40.8,
      prepaid_rto_rate_pct: 5.8,
    };
    render(<OverviewKPIs data={dataWithBreakdown} />);

    expect(screen.getByText(/COD: 40.8% · Prepaid: 5.8%/)).toBeInTheDocument();
  });

  it("renders clean zeros in empty state without division by zero errors", () => {
    const emptyData: AnalyticsOverviewResponse = {
      total_orders: 0,
      cod_orders_count: 0,
      prepaid_orders_count: 0,
      cod_share_pct: 0.0,
      rto_count: 0,
      rto_rate_pct: 0.0,
      cod_rto_count: 0,
      cod_rto_rate_pct: 0.0,
      prepaid_rto_count: 0,
      prepaid_rto_rate_pct: 0.0,
      customer_return_count: 0,
      customer_return_rate_pct: 0.0,
      delivered_kept_count: 0,
      delivered_kept_rate_pct: 0.0,
      active_orders_count: 0,
      converted_to_upi_count: 0,
      estimated_direct_savings_inr: 0,
      total_incentives_disbursed_inr: 0,
      tier_breakdown: [],
      sku_breakdown: [],
      disclaimer: "modelled direct operating savings",
    };
    render(<OverviewKPIs data={emptyData} />);

    expect(screen.getByText("Shipped Orders")).toBeInTheDocument();
    expect(screen.getAllByText("0").length).toBeGreaterThan(0);
    expect(screen.getAllByText("0.0%").length).toBeGreaterThan(0);
  });
});
