"use client";

import React, { useEffect, useState } from "react";
import { Sliders } from "lucide-react";
import type { ScenarioCalculationResponse } from "@/lib/api/types";
import { api } from "@/lib/api/client";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export function ScenarioModelPanel({ className }: { className?: string }) {
  const [shipments, setShipments] = useState(10000);
  const [codShare, setCodShare] = useState(65.0);
  const [codRto, setCodRto] = useState(26.0);
  const [costPerRto, setCostPerRto] = useState(200);
  const [conversionRate, setConversionRate] = useState(10.0);
  const [feePct, setFeePct] = useState(0.0);
  const [data, setData] = useState<ScenarioCalculationResponse | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      api
        .getScenario(
          {
            monthly_shipments: shipments,
            cod_share_pct: codShare,
            cod_rto_pct: codRto,
            cost_per_rto_inr: costPerRto,
            cod_conversion_pct: conversionRate,
            upi_gateway_fee_pct: feePct,
          },
          controller.signal,
        )
        .then(setData)
        .catch(() => null);
    }, 120);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [shipments, codShare, codRto, costPerRto, conversionRate, feePct]);

  const combined = data?.combined_case;
  const conservative = data?.conservative_conversion_only_case;

  return (
    <Card className={cn("p-6 space-y-6 border border-brand/30 bg-surface shadow-card", className)}>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-4 border-b border-line">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-brand-soft text-brand flex items-center justify-center shrink-0">
            <Sliders className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <h3 className="font-display text-xl text-ink">
              10,000-Shipment Financial Scenario Modeler
            </h3>
            <p className="text-xs text-ink-muted">
              Interactive financial projections strictly segregated from live database telemetry (ADR-005)
            </p>
          </div>
        </div>
        <span className="text-xs font-semibold text-brand bg-subtle px-3 py-1 rounded-full border border-line">
          Interactive Projections
        </span>
      </div>

      {/* Interactive Sliders */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-xs tabular-nums">
        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>Monthly Shipments</span>
            <span className="text-ink">{shipments.toLocaleString("en-IN")}</span>
          </div>
          <input
            type="range"
            min="2000"
            max="30000"
            step="1000"
            value={shipments}
            onChange={(e) => setShipments(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>COD Volume Share</span>
            <span className="text-ink">{codShare.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="30"
            max="90"
            step="5"
            value={codShare}
            onChange={(e) => setCodShare(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>Direct Cost per RTO</span>
            <span className="text-ink">₹{costPerRto}</span>
          </div>
          <input
            type="range"
            min="100"
            max="350"
            step="10"
            value={costPerRto}
            onChange={(e) => setCostPerRto(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>Baseline COD RTO Rate</span>
            <span className="text-ink">{codRto.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="15"
            max="40"
            step="1"
            value={codRto}
            onChange={(e) => setCodRto(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>COD → UPI Conversion Rate</span>
            <span className="text-ink">{conversionRate.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="5"
            max="25"
            step="1"
            value={conversionRate}
            onChange={(e) => setConversionRate(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>UPI Gateway Fee</span>
            <span className="text-ink">{feePct.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="3"
            step="0.5"
            value={feePct}
            onChange={(e) => setFeePct(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>
      </div>

      {/* Outcomes Row */}
      {combined && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 pt-3 border-t border-line tabular-nums">
          <div className="p-4 rounded-xl bg-subtle border border-line">
            <span className="text-xs font-medium text-ink-muted block">Avoided RTO Orders</span>
            <div className="text-2xl font-bold text-brand mt-1">
              {combined.avoided_rto_shipments.toLocaleString("en-IN")}
            </div>
            <span className="text-[11px] text-ink-muted mt-0.5 block">
              Baseline: {combined.baseline_total_rto_shipments} to New: {combined.new_total_rto_shipments}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-subtle border border-line">
            <span className="text-xs font-medium text-ink-muted block">Gross Loss Avoided</span>
            <div className="text-2xl font-bold text-ink mt-1">
              ₹{Number(combined.gross_avoided_loss_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[11px] text-ink-muted mt-0.5 block">
              Fees deducted: ₹{Number(combined.total_payment_fees_inr).toLocaleString("en-IN")}
            </span>
          </div>

          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
            <span className="text-xs font-medium text-emerald-800 block">Net Monthly Savings</span>
            <div className="text-2xl font-bold text-emerald-700 mt-1">
              ₹{Number(combined.net_operating_savings_monthly_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[11px] text-emerald-800 mt-0.5 block">
              After incentives &amp; fees
            </span>
          </div>

          <div className="p-4 rounded-xl bg-brand-soft/60 border border-brand/25">
            <span className="text-xs font-medium text-brand block">Annualized Net Impact</span>
            <div className="text-2xl font-bold text-brand mt-1">
              ₹{Number(combined.net_operating_savings_annual_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[11px] text-ink-muted mt-0.5 block">12-month projection</span>
          </div>
        </div>
      )}

      {conservative && (
        <div className="p-3.5 rounded-xl bg-subtle border border-line flex flex-wrap items-center justify-between gap-2 text-xs text-ink-muted">
          <span>
            <strong className="text-ink">Conservative Conversion-Only Floor:</strong> ₹
            {Number(conservative.net_operating_savings_monthly_inr).toLocaleString("en-IN")}/mo (
            {conservative.avoided_rto_shipments} avoided RTOs from {conversionRate.toFixed(0)}% COD
            conversion alone)
          </span>
          <span className="text-[11px] font-semibold text-brand bg-surface px-2.5 py-0.5 rounded-full border border-line">
            Robust Margin
          </span>
        </div>
      )}

      <p className="text-[11px] text-ink-muted leading-relaxed border-t border-line pt-3">
        {data?.disclaimer ||
          "modelled direct operating savings after incentives, before fees — excluding tax, overhead, and other non-delivery costs."}
      </p>
    </Card>
  );
}
