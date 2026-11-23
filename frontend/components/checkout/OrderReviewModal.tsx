"use client";

import React from "react";
import { CheckCircle2, AlertCircle, XCircle, Zap, ShieldCheck } from "lucide-react";
import type { RiskEvaluateResponse, IncentiveQuoteResponse } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";

export interface OrderReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  riskData: RiskEvaluateResponse | null;
  incentiveData: IncentiveQuoteResponse | null;
  cartTotal: number;
  onConfirmCod: () => void;
  onAcceptUpi: () => void;
  isSubmitting?: boolean;
}

export function OrderReviewModal({
  isOpen,
  onClose,
  riskData,
  incentiveData,
  cartTotal,
  onConfirmCod,
  onAcceptUpi,
  isSubmitting = false,
}: OrderReviewModalProps) {
  if (!isOpen) return null;

  const discountAmount = incentiveData?.eligible_for_incentive
    ? Number(incentiveData.recommended_discount_inr)
    : 0;
  const upiPayable = Math.max(0, cartTotal - discountAmount);

  const getCheckIcon = (status: "PASS" | "REVIEW" | "FAIL") => {
    switch (status) {
      case "PASS":
        return <CheckCircle2 className="w-4 h-4 text-accentEmerald shrink-0" />;
      case "REVIEW":
        return <AlertCircle className="w-4 h-4 text-accentAmber shrink-0" />;
      case "FAIL":
        return <XCircle className="w-4 h-4 text-accentRose shrink-0" />;
    }
  };

  const getCheckBadge = (status: "PASS" | "REVIEW" | "FAIL") => {
    switch (status) {
      case "PASS":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "REVIEW":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "FAIL":
        return "bg-rose-50 text-rose-700 border-rose-200";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-ink/50 backdrop-blur-sm" onClick={onClose} />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-lg bg-surface rounded-bento border border-border shadow-2xl p-6 space-y-5 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center gap-2.5 border-b border-borderLight pb-4">
          <div className="w-10 h-10 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-ink">Order Safety Review</h3>
            <p className="text-xs text-inkMuted">Automated logistics &amp; delivery assurance checks</p>
          </div>
        </div>

        {/* 3-Point Checklist */}
        <div className="space-y-2.5">
          <span className="text-xs font-bold uppercase tracking-wider text-inkMuted">
            Pre-Dispatch Verification Checklist
          </span>
          <div className="space-y-2">
            {riskData?.checks.map((c) => (
              <div
                key={c.id}
                className="p-3 rounded-lg border border-border bg-canvas/40 flex items-center justify-between"
              >
                <div className="flex items-center gap-2.5">
                  {getCheckIcon(c.status)}
                  <span className="text-xs font-bold text-ink">{c.label}</span>
                </div>
                <span
                  className={cn(
                    "text-[10px] font-bold px-2 py-0.5 rounded border uppercase",
                    getCheckBadge(c.status),
                  )}
                >
                  {c.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Dynamic UPI Conversion Offer (ADR-002, ADR-014) */}
        {incentiveData?.eligible_for_incentive && discountAmount > 0 && (
          <div className="rounded-bento border-2 border-brand bg-brand/5 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-brand text-white">
                <Zap className="w-3 h-3" />
                Instant Prepaid Nudge
              </span>
              <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Save ₹{discountAmount}
              </span>
            </div>
            <p className="text-xs text-ink font-medium leading-relaxed">
              {incentiveData.nudge_copy ||
                `Convert to instant UPI to save ₹${discountAmount} and receive priority dispatch.`}
            </p>
            <div className="text-xs text-inkMuted flex justify-between items-center pt-1 border-t border-brand/20">
              <span>Payable via UPI:</span>
              <span className="text-base font-extrabold text-brand">₹{upiPayable}</span>
            </div>
          </div>
        )}

        {/* Action Buttons: Equal visibility COD vs UPI per ADR-002 */}
        <div className="space-y-2 pt-2">
          {incentiveData?.eligible_for_incentive && discountAmount > 0 && (
            <Button
              type="button"
              onClick={onAcceptUpi}
              isLoading={isSubmitting}
              className="w-full bg-brand hover:bg-brandHover text-white"
              size="lg"
            >
              <Zap className="w-4 h-4 mr-1.5" />
              Pay ₹{upiPayable} via Instant UPI (Simulated)
            </Button>
          )}

          <Button
            type="button"
            variant="outline"
            onClick={onConfirmCod}
            isLoading={isSubmitting}
            className="w-full border-border text-ink hover:bg-canvas"
            size="md"
          >
            Continue with Cash on Delivery (₹{cartTotal})
          </Button>
        </div>

        <p className="text-[10px] text-center text-inkMuted italic">
          Fairness Guarantee: Cash on Delivery is 100% available without restrictions.
        </p>
      </div>
    </div>
  );
}
