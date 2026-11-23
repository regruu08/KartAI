"use client";

import React, { useState, useEffect } from "react";
import { Sliders, TrendingUp, Sparkles, AlertCircle } from "lucide-react";
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
    api
      .getScenario({
        monthly_shipments: shipments,
        cod_share_pct: codShare,
        cod_rto_pct: codRto,
        cost_per_rto_inr: costPerRto,
        cod_conversion_pct: conversionRate,
        upi_gateway_fee_pct: feePct,
      })
      .then(setData)
      .catch(() => null);
  }, [shipments, codShare, codRto, costPerRto, conversionRate, feePct]);

  const combined = data?.combined_case;
  const conservative = data?.conservative_conversion_only_case;

  return (
    <Card className={cn("p-6 space-y-6 border-2 border-brand/40 bg-surface shadow-bento", className)}>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-4 border-b border-borderLight">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-brand text-white flex items-center justify-center">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-extrabold text-ink">
              10,000-Shipment Financial Scenario Modeler
            </h3>
            <p className="text-xs text-inkMuted">
              Interactive financial projections strictly segregated from live database telemetry (ADR-005)
            </p>
          </div>
        </div>
        <span className="text-[10px] uppercase font-bold text-brand bg-canvas px-2.5 py-1 rounded-full border border-border">
          Interactive Projections
        </span>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 text-xs">
        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1.5">
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
            className="w-full accent-brand cursor-pointer"
          />
        </div>
      </div>

      {/* Projection Outcomes Bento Row */}
      {combined && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-borderLight">
          <div className="p-3.5 rounded-lg bg-canvas border border-border">
            <span className="text-[10px] font-bold text-inkMuted uppercase block">Avoided RTO Orders</span>
            <div className="text-2xl font-extrabold text-brand mt-1">
              {combined.avoided_rto_shipments.toLocaleString("en-IN")}
            </div>
            <span className="text-[10px] text-inkMuted mt-0.5 block">
              Baseline: {combined.baseline_total_rto_shipments} → New: {combined.new_total_rto_shipments}
            </span>
          </div>

          <div className="p-3.5 rounded-lg bg-canvas border border-border">
            <span className="text-[10px] font-bold text-inkMuted uppercase block">Gross Loss Avoided</span>
            <div className="text-2xl font-extrabold text-ink mt-1">
              ₹{Number(combined.gross_avoided_loss_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[10px] text-inkMuted mt-0.5 block">Pre-incentive savings</span>
          </div>

          <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200">
            <span className="text-[10px] font-bold text-emerald-800 uppercase block">Net Monthly Savings</span>
            <div className="text-2xl font-extrabold text-emerald-700 mt-1">
              ₹{Number(combined.net_operating_savings_monthly_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[10px] text-emerald-800 mt-0.5 block">After incentive payouts</span>
          </div>

          <div className="p-3.5 rounded-lg bg-brand/10 border border-brand/20">
            <span className="text-[10px] font-bold text-brand uppercase block">Annualized Net Impact</span>
            <div className="text-2xl font-extrabold text-brand mt-1">
              ₹{Number(combined.net_operating_savings_annual_inr).toLocaleString("en-IN")}
            </div>
            <span className="text-[10px] text-inkMuted mt-0.5 block">12-month projected ROI</span>
          </div>
        </div>
      )}

      {/* Conservative Case callout */}
      {conservative && (
        <div className="p-3 rounded-lg bg-surface border border-borderLight flex items-center justify-between text-xs text-inkMuted">
          <span>
            <strong className="text-ink">Conservative Conversion-Only Floor:</strong> ₹
            {Number(conservative.net_operating_savings_monthly_inr).toLocaleString("en-IN")}/mo (
            {conservative.avoided_rto_shipments} avoided RTOs from 10% COD conversion alone)
          </span>
          <span className="text-[10px] font-bold text-brand bg-canvas px-2 py-0.5 rounded border border-border">
            Robust Margin
          </span>
        </div>
      )}

      {/* Mandatory Claims Compliance Attribution Disclaimer (AGENTS.md §10) */}
      <p className="text-[10px] text-inkMuted leading-relaxed italic border-t border-borderLight pt-3">
        * Disclaimer: {data?.disclaimer || "modelled direct operating savings after incentives, before fees — excluding tax, overhead, and other non-delivery costs."}
      </p>
    </Card>
  );
}
