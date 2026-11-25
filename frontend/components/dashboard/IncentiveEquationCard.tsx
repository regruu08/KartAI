"use client";

import React, { useEffect, useState } from "react";
import { Calculator, AlertCircle } from "lucide-react";
import { api } from "@/lib/api/client";
import type { IncentiveQuoteResponse } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export function IncentiveEquationCard({ className }: { className?: string }) {
  const [cartValue, setCartValue] = useState(1899);
  const [feePct, setFeePct] = useState(0.0);
  const [liveQuote, setLiveQuote] = useState<IncentiveQuoteResponse | null>(null);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      api
        .getIncentiveQuote({
          cart_total_inr: cartValue,
          risk_score_index: 55,
          current_payment: "COD",
          upi_gateway_fee_pct: feePct,
        })
        .then(setLiveQuote)
        .catch(() => null);
    }, 150);
    return () => window.clearTimeout(timer);
  }, [cartValue, feePct]);

  // Deterministic preview fallback matching backend closed-form equation exactly
  const avoidedLoss = Number(liveQuote?.expected_avoided_loss_inr ?? 48.0);
  const marginFloor = 8.0;
  const gatewayFee = (cartValue * feePct) / 100;
  const rawHeadroom = avoidedLoss - gatewayFee - marginFloor;
  const eligible = liveQuote ? liveQuote.eligible_for_incentive : rawHeadroom >= 25.0;
  const finalDiscount = liveQuote
    ? Number(liveQuote.recommended_discount_inr)
    : eligible
      ? Math.min(40, Math.max(0, Math.floor(rawHeadroom / 5) * 5))
      : 0;
  const retainedMargin = liveQuote
    ? Number(liveQuote.headroom_inr)
    : avoidedLoss - finalDiscount - gatewayFee;

  return (
    <Card className={cn("p-5 space-y-4 shadow-card", className)}>
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-line">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-brand-soft text-brand flex items-center justify-center shrink-0">
            <Calculator className="w-4 h-4" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink">
              Closed-Form Incentive Optimizer (D_max)
            </h3>
            <p className="text-xs text-ink-muted">
              Live margin-safe prepaid discount derivation with floor protection
            </p>
          </div>
        </div>
        <span
          className={cn(
            "text-xs font-semibold px-3 py-1 rounded-full border tabular-nums",
            eligible
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-rose-50 text-rose-700 border-rose-200",
          )}
        >
          {eligible ? `₹${finalDiscount} Max Offer` : "Offer Ineligible"}
        </span>
      </div>

      <div className="p-3 rounded-xl bg-subtle border border-line text-center font-mono text-xs text-ink">
        <span className="font-semibold text-brand">D_max</span> = (P_COD − P_prepaid) × Cost_RTO −
        GatewayFee − MarginFloor
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>Cart Total (GMV)</span>
            <span className="text-ink tabular-nums">₹{cartValue}</span>
          </div>
          <input
            type="range"
            aria-label="Cart Total GMV"
            min="500"
            max="5000"
            step="100"
            value={cartValue}
            onChange={(e) => setCartValue(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>

        <div>
          <div className="flex justify-between text-ink-muted font-semibold mb-1.5">
            <span>UPI Gateway Fee (%)</span>
            <span
              className={cn(
                "font-semibold tabular-nums",
                feePct > 0 ? "text-rose-700" : "text-emerald-700",
              )}
            >
              {feePct.toFixed(1)}% (₹{gatewayFee.toFixed(1)})
            </span>
          </div>
          <input
            type="range"
            aria-label="UPI Gateway Fee Percentage"
            min="0"
            max="3"
            step="0.5"
            value={feePct}
            onChange={(e) => setFeePct(Number(e.target.value))}
            className="rz-slider w-full"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs pt-2 border-t border-line tabular-nums">
        <div className="p-2.5 rounded-xl bg-subtle border border-line">
          <span className="text-ink-muted block text-[11px]">Avoided RTO Loss</span>
          <span className="font-semibold text-ink">₹{avoidedLoss.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-subtle border border-line">
          <span className="text-ink-muted block text-[11px]">Payment Fee</span>
          <span className="font-semibold text-rose-700">-₹{gatewayFee.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-subtle border border-line">
          <span className="text-ink-muted block text-[11px]">Margin Floor</span>
          <span className="font-semibold text-ink-muted">-₹{marginFloor.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-subtle border border-line">
          <span className="text-ink-muted block text-[11px]">Retained Headroom</span>
          <span className="font-semibold text-trust-text">+₹{retainedMargin.toFixed(2)}</span>
        </div>
      </div>

      {!eligible && (
        <div className="p-3 rounded-xl bg-warn-soft border border-warn/35 text-warn-text text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-warn shrink-0" aria-hidden="true" />
          <span>
            <strong>Margin Guard Triggered ({liveQuote?.reason_code ?? "REASON_INSUFFICIENT_MARGIN"}):</strong>{" "}
            Gateway fee ({feePct.toFixed(1)}%) drops allowable discount below ₹25 minimum. Offer
            safely withdrawn.
          </span>
        </div>
      )}
    </Card>
  );
}
