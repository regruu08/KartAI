"use client";

import React, { useState } from "react";
import { Check, ChevronDown, Circle, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/cn";
import {
  evaluateAddressCompleteness,
  getCityTierFromPin,
  type CityTier,
} from "@/lib/pin";
import type { RiskEvaluateResponse } from "@/lib/api/types";

interface ShieldReviewPanelProps {
  streetAddress: string;
  landmark: string;
  pinCode: string;
  risk: RiskEvaluateResponse | null;
  isRechecking: boolean;
  tierOverride: CityTier | null;
  onTierOverrideChange: (tier: CityTier | null) => void;
}

export function ShieldReviewPanel({
  streetAddress,
  landmark,
  pinCode,
  risk,
  isRechecking,
  tierOverride,
  onTierOverrideChange,
}: ShieldReviewPanelProps) {
  const [demoOpen, setDemoOpen] = useState(false);

  const addressCheck = evaluateAddressCompleteness({
    flat: streetAddress.split(",")[0] ?? "",
    street: streetAddress,
    landmark,
  });

  const effectiveTier = tierOverride ?? getCityTierFromPin(pinCode);
  const serviceCheck = risk?.checks.find((c) => c.id === "serviceable_pin");

  const riskTone =
    risk?.risk_level === "Elevated"
      ? "bg-danger-soft text-danger border-danger/25"
      : risk?.risk_level === "Review"
        ? "bg-warn-soft text-warn-text border-warn/30"
        : "bg-trust-soft text-trust-text border-trust/25";

  return (
    <section
      aria-labelledby="shield-heading"
      className="rounded-2xl border border-line bg-surface p-5 space-y-4 shadow-card"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-brand shrink-0" aria-hidden="true" />
          <h2 id="shield-heading" className="text-sm font-semibold text-ink">
            3-Check Order Review
          </h2>
        </div>
        {isRechecking && (
          <span className="text-[11px] font-medium text-ink-muted">Updating checks…</span>
        )}
      </div>

      <div
        aria-live="polite"
        className={cn(
          "space-y-3 transition-opacity duration-200",
          isRechecking && risk ? "opacity-65" : "opacity-100",
        )}
      >
        {/* Check 1: Address Completeness */}
        <div className="rounded-xl border border-line bg-subtle p-3.5 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold text-ink">1. Address Completeness</span>
            <span className="text-xs font-medium text-ink-muted tabular-nums">
              {addressCheck.score}/3 cues
            </span>
          </div>
          <div className="grid grid-cols-3 gap-2 pt-0.5">
            {[
              { label: "Premise", ok: addressCheck.hasFlat },
              { label: "Street", ok: addressCheck.hasStreet },
              { label: "Landmark", ok: addressCheck.hasLandmark },
            ].map((item) => (
              <div
                key={item.label}
                className="flex items-center gap-1.5 text-[11px] text-ink-muted"
              >
                {item.ok ? (
                  <Check className="w-3.5 h-3.5 text-trust shrink-0" aria-hidden="true" />
                ) : (
                  <Circle className="w-3 h-3 text-line-strong shrink-0" aria-hidden="true" />
                )}
                <span className={item.ok ? "text-ink font-medium" : ""}>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Check 2: PIN Serviceability */}
        <div className="rounded-xl border border-line bg-subtle p-3.5 flex items-center justify-between gap-3">
          <div>
            <p className="text-xs font-semibold text-ink">2. PIN Serviceability</p>
            <p className="text-[11px] text-ink-muted mt-0.5 tabular-nums">
              {pinCode.trim().length === 6
                ? `PIN ${pinCode.trim()} (Tier-${effectiveTier})`
                : "Enter a 6-digit Indian PIN code"}
            </p>
          </div>
          {risk ? (
            <span
              className={cn(
                "inline-flex items-center rounded-lg border px-2.5 py-1 text-[11px] font-semibold",
                serviceCheck?.status === "FAIL"
                  ? "bg-danger-soft text-danger border-danger/25"
                  : "bg-trust-soft text-trust-text border-trust/25",
              )}
            >
              {serviceCheck?.status === "FAIL" ? "Out of lane" : "Serviceable"}
            </span>
          ) : (
            <span className="inline-flex items-center rounded-lg border border-line-strong bg-surface px-2.5 py-1 text-[11px] font-medium text-ink-muted">
              Waiting
            </span>
          )}
        </div>

        {/* Check 3: RTO Risk Band */}
        <div className="rounded-xl border border-line bg-subtle p-3.5 space-y-2">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs font-semibold text-ink">3. RTO Risk Band</p>
              <p className="text-[11px] text-ink-muted mt-0.5 tabular-nums">
                {risk ? `Risk index: ${risk.risk_score_index}/100` : "Evaluates live"}
              </p>
            </div>
            {risk ? (
              <span
                className={cn(
                  "inline-flex items-center rounded-lg border px-2.5 py-1 text-[11px] font-semibold",
                  riskTone,
                )}
              >
                {risk.risk_level}
              </span>
            ) : (
              <span className="inline-flex items-center rounded-lg border border-line-strong bg-surface px-2.5 py-1 text-[11px] font-medium text-ink-muted">
                Pending
              </span>
            )}
          </div>

          {risk && risk.contributing_factors.length > 0 && (
            <ul className="space-y-1 pt-1 border-t border-line text-[11px] text-ink-muted list-disc pl-4">
              {risk.contributing_factors.slice(0, 2).map((factor, idx) => (
                <li key={idx}>{factor}</li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Collapsed Demo Lane Controls for Judges */}
      <div className="pt-2 border-t border-line">
        <button
          type="button"
          aria-expanded={demoOpen}
          onClick={() => setDemoOpen((prev) => !prev)}
          className="w-full min-h-[36px] flex items-center justify-between gap-2 text-xs font-medium text-ink-muted hover:text-ink cursor-pointer"
        >
          <span className="inline-flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5" aria-hidden="true" />
            <span>Demo lane controls</span>
          </span>
          <ChevronDown
            className={cn(
              "w-3.5 h-3.5 transition-transform duration-200",
              demoOpen && "rotate-180",
            )}
            aria-hidden="true"
          />
        </button>

        {demoOpen && (
          <div className="mt-2.5 space-y-2 rounded-xl border border-line bg-canvas p-3">
            <p className="text-[11px] text-ink-muted">
              Switch synthetic PIN lanes to inspect Checkout Shield risk tiers:
            </p>
            <div className="grid grid-cols-4 gap-1.5">
              {(
                [
                  { label: "Auto", value: null },
                  { label: "Tier 1", value: 1 },
                  { label: "Tier 2", value: 2 },
                  { label: "Tier 3", value: 3 },
                ] as const
              ).map((opt) => {
                const active = tierOverride === opt.value;
                return (
                  <button
                    key={opt.label}
                    type="button"
                    aria-pressed={active}
                    onClick={() => onTierOverrideChange(opt.value)}
                    className={cn(
                      "min-h-[36px] rounded-lg border text-xs font-medium transition-colors cursor-pointer",
                      active
                        ? "bg-brand text-white border-brand"
                        : "bg-surface text-ink border-line-strong hover:bg-subtle",
                    )}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
