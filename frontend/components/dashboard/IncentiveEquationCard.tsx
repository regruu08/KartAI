"use client";

import React, { useState } from "react";
import { Calculator, AlertCircle, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export function IncentiveEquationCard({ className }: { className?: string }) {
  const [cartValue, setCartValue] = useState(1899);
  const [feePct, setFeePct] = useState(0.0);

  // Math calculation
  const codRto = 0.26;
  const prepaidRto = 0.02;
  const costPerRto = 200;
  const marginFloor = 8.0;

  const rtoDiff = codRto - prepaidRto; // 0.24
  const avoidedLoss = rtoDiff * costPerRto; // 48.00
  const gatewayFee = (cartValue * feePct) / 100; // e.g. 1899 * 0.015 = 28.485
  const rawHeadroom = avoidedLoss - gatewayFee - marginFloor; // 48 - fee - 8

  // Floor to 5-step, cap at 40
  const eligible = rawHeadroom >= 25.0;
  const floored = Math.floor(rawHeadroom / 5) * 5;
  const finalDiscount = eligible ? Math.min(40, Math.max(0, floored)) : 0;
  const retainedMargin = avoidedLoss - finalDiscount - gatewayFee;

  return (
    <Card className={cn("p-5 space-y-4 shadow-sm", className)}>
      <div className="flex items-center justify-between pb-3 border-b border-borderLight">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
            <Calculator className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-ink">Closed-Form Incentive Optimizer ($D_{`max`}$)</h3>
            <p className="text-xs text-inkMuted">Mathematical derivation of margin-safe prepaid cash discount</p>
          </div>
        </div>
        <span
          className={cn(
            "text-xs font-bold px-2.5 py-1 rounded-full border",
            eligible
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-rose-50 text-rose-700 border-rose-200",
          )}
        >
          {eligible ? `₹${finalDiscount} Max Offer` : "Offer Ineligible"}
        </span>
      </div>

      {/* Formula Display */}
      <div className="p-3 rounded-lg bg-canvas border border-border text-center font-mono text-xs text-ink">
        <span className="font-bold text-brand">D_max</span> = (P_COD - P_prepaid) × Cost_RTO - GatewayFee - MarginFloor
      </div>

      {/* Interactive Controls */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1">
            <span>Cart Total (GMV)</span>
            <span className="text-ink">₹{cartValue}</span>
          </div>
          <input
            type="range"
            min="500"
            max="5000"
            step="100"
            value={cartValue}
            onChange={(e) => setCartValue(Number(e.target.value))}
            className="w-full accent-brand cursor-pointer"
          />
        </div>

        <div>
          <div className="flex justify-between text-inkMuted font-bold mb-1">
            <span>Payment Gateway Fee</span>
            <span className={cn("font-bold", feePct > 0 ? "text-rose-700" : "text-emerald-700")}>
              {feePct.toFixed(1)}% (₹{gatewayFee.toFixed(1)})
            </span>
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

      {/* Step by step derivation */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] pt-2 border-t border-borderLight">
        <div className="p-2.5 rounded bg-surface border border-borderLight">
          <span className="text-inkMuted block text-[10px]">Avoided RTO Loss</span>
          <span className="font-bold text-ink">₹{avoidedLoss.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded bg-surface border border-borderLight">
          <span className="text-inkMuted block text-[10px]">Payment Fee</span>
          <span className="font-bold text-rose-700">-₹{gatewayFee.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded bg-surface border border-borderLight">
          <span className="text-inkMuted block text-[10px]">Margin Floor</span>
          <span className="font-bold text-inkMuted">-₹{marginFloor.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded bg-surface border border-borderLight">
          <span className="text-inkMuted block text-[10px]">Retained Margin</span>
          <span className="font-bold text-accentEmerald">+₹{retainedMargin.toFixed(2)}</span>
        </div>
      </div>

      {feePct >= 1.5 && (
        <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-accentAmber shrink-0" />
          <span>
            <strong>Headroom Guard Triggered:</strong> Elevated gateway fee ({feePct}%) erodes consumer discount margin. Offer safely withdrawn per ADR-002.
          </span>
        </div>
      )}
    </Card>
  );
}
