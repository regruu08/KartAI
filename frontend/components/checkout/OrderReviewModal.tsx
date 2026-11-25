"use client";

import React from "react";
import * as Dialog from "@radix-ui/react-dialog";
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
  const avoidedLoss = Number(incentiveData?.expected_avoided_loss_inr ?? 48);
  const headroom = Number(incentiveData?.headroom_inr ?? 8);
  const upiPayable = Math.max(0, cartTotal - discountAmount);

  const getCheckIcon = (status: "PASS" | "REVIEW" | "FAIL") => {
    switch (status) {
      case "PASS":
        return <CheckCircle2 className="w-4 h-4 text-trust shrink-0" aria-hidden="true" />;
      case "REVIEW":
        return <AlertCircle className="w-4 h-4 text-warn shrink-0" aria-hidden="true" />;
      case "FAIL":
        return <XCircle className="w-4 h-4 text-danger shrink-0" aria-hidden="true" />;
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
    <Dialog.Root
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="rz-overlay-in fixed inset-0 z-50 bg-ink/45 backdrop-blur-[2px]" />
        <Dialog.Content
          aria-describedby="order-review-description"
          className="rz-modal-in fixed inset-0 z-50 m-auto h-fit w-[calc(100vw-2rem)] max-w-xl rounded-2xl border border-line bg-surface p-6 sm:p-7 shadow-lift outline-none space-y-5"
        >
          {/* Header */}
          <div className="flex items-start gap-3 border-b border-line pb-4">
            <div className="w-10 h-10 rounded-xl bg-brand-soft text-brand flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5" aria-hidden="true" />
            </div>
            <div>
              <Dialog.Title className="font-display text-xl sm:text-2xl text-ink leading-tight">
                Order Safety Review
              </Dialog.Title>
              <Dialog.Description id="order-review-description" className="text-xs text-ink-muted mt-0.5">
                Automated logistics &amp; delivery assurance checks before dispatch
              </Dialog.Description>
            </div>
          </div>

          {/* 3-Point Checklist */}
          <div className="space-y-2.5">
            <span className="text-xs font-semibold text-ink-muted block">
              Pre-Dispatch Verification Checklist
            </span>
            <div className="space-y-2">
              {riskData?.checks.map((c) => (
                <div
                  key={c.id}
                  className="p-3 rounded-xl border border-line bg-subtle/80 flex items-center justify-between gap-2"
                >
                  <div className="flex items-center gap-2.5">
                    {getCheckIcon(c.status)}
                    <span className="text-xs font-semibold text-ink">{c.label}</span>
                  </div>
                  <span
                    className={cn(
                      "text-[10px] font-bold px-2.5 py-0.5 rounded-full border uppercase",
                      getCheckBadge(c.status),
                    )}
                  >
                    {c.status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Margin-Safe UPI Conversion Offer */}
          {incentiveData?.eligible_for_incentive && discountAmount > 0 && (
            <div className="rounded-2xl border border-brand/35 bg-brand-soft/35 p-4 space-y-2.5">
              <div className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-brand text-white">
                  <Zap className="w-3 h-3" aria-hidden="true" />
                  Transparent Margin-Safe Incentive
                </span>
                <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 tabular-nums">
                  Save ₹{discountAmount}
                </span>
              </div>

              <p className="text-xs text-ink leading-relaxed">
                {incentiveData.nudge_copy ||
                  `Switch to instant UPI to save ₹${discountAmount} and secure priority dispatch.`}
              </p>

              <div className="rounded-xl bg-surface border border-line p-3 text-xs space-y-1 tabular-nums">
                <p className="font-semibold text-brand">
                  Avoided RTO ₹{avoidedLoss.toFixed(0)} - Margin Floor ₹{headroom.toFixed(0)} = ₹
                  {discountAmount} Offer
                </p>
                <div className="flex justify-between items-center text-ink-muted pt-1 border-t border-line">
                  <span>Payable via Instant UPI:</span>
                  <span className="text-sm font-bold text-ink">₹{upiPayable}</span>
                </div>
              </div>
            </div>
          )}

          {/* Equal-Weight Checkout Actions */}
          <div className="space-y-2.5 pt-1">
            {incentiveData?.eligible_for_incentive && discountAmount > 0 && (
              <Button
                type="button"
                onClick={onAcceptUpi}
                isLoading={isSubmitting}
                fullWidth
                size="lg"
              >
                <Zap className="w-4 h-4" aria-hidden="true" />
                <span>Pay ₹{upiPayable} via Instant UPI (Simulated)</span>
              </Button>
            )}

            <Button
              type="button"
              variant="outline"
              onClick={onConfirmCod}
              isLoading={isSubmitting}
              fullWidth
              size="md"
              className="border-2 border-ink text-ink hover:bg-subtle"
            >
              Continue with Cash on Delivery (₹{cartTotal})
            </Button>
          </div>

          <p className="text-[11px] text-center text-ink-muted">
            Fairness Guarantee: Cash on Delivery remains 100% available without restrictions.
          </p>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
