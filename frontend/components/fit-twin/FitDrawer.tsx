"use client";

import React, { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X, Sparkles, Shield, AlertTriangle, ArrowRight, CheckCircle2 } from "lucide-react";
import type { SkuResponse, BrandName, SizeLabel, FitPreference } from "@/lib/api/types";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import { cmToFeetInches } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { RadioChipGroup, type RadioChipOption } from "@/components/ui/RadioChipGroup";
import { FitZoneBreakdown } from "./FitZoneBreakdown";

export interface FitDrawerProps {
  sku: SkuResponse;
}

const BRAND_OPTIONS: readonly RadioChipOption<BrandName>[] = [
  { value: "Zara", label: "Zara" },
  { value: "H&M", label: "H&M" },
  { value: "Uniqlo", label: "Uniqlo" },
  { value: "Levi's", label: "Levi's" },
  { value: "Marks & Spencer", label: "Marks & Spencer" },
];

const SIZE_OPTIONS: readonly RadioChipOption<SizeLabel>[] = (
  ["XS", "S", "M", "L", "XL", "XXL"] as const
).map((s) => ({ value: s, label: s }));

const FIT_PREF_OPTIONS: readonly RadioChipOption<FitPreference>[] = [
  { value: "tight", label: "Tight", sublabel: '+1.0" close cut' },
  { value: "tailored", label: "Regular", sublabel: '+2.5" tailored' },
  { value: "relaxed", label: "Relaxed", sublabel: '+4.0" easy drape' },
  { value: "oversized", label: "Oversized", sublabel: '+6.0" generous' },
];

export function FitDrawer({ sku }: FitDrawerProps) {
  const {
    fitDrawerOpen,
    closeFitDrawer,
    selectedBrand,
    setSelectedBrand,
    selectedSize,
    setSelectedSize,
    fitPreference,
    setFitPreference,
    heightCm,
    setHeightCm,
    fitResult,
    fitBySku,
    setFitForSku,
    addToCart,
  } = useStore();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!fitDrawerOpen) return null;

  const activeFitResult =
    fitBySku[sku.id] ?? (fitResult?.sku_id === sku.id ? fitResult : null);

  const handleCalculateFit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.computeFit(sku.id, {
        known_brand: selectedBrand,
        known_size: selectedSize,
        fit_preference: fitPreference,
        height_cm: heightCm,
      });
      setFitForSku(sku.id, res, {
        brand: selectedBrand,
        size: selectedSize,
        preference: fitPreference,
        heightCm,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to calculate fit recommendation");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySizeAndAddToCart = () => {
    if (!activeFitResult) return;
    addToCart({
      sku,
      size: activeFitResult.recommended_size,
      quantity: 1,
      fitVerified: true,
      knownBrand: selectedBrand,
      knownSize: selectedSize,
      fitPreference,
    });
    closeFitDrawer();
  };

  const getConfidenceBadgeVariant = (band: string) => {
    if (band.startsWith("High")) return "emerald";
    if (band.startsWith("Medium")) return "amber";
    return "rose";
  };

  return (
    <Dialog.Root
      open={fitDrawerOpen}
      onOpenChange={(open) => {
        if (!open) closeFitDrawer();
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="rz-overlay-in fixed inset-0 z-50 bg-ink/40 backdrop-blur-[2px]" />
        <Dialog.Content
          aria-describedby="fit-drawer-description"
          className="rz-drawer-in fixed right-0 top-0 bottom-0 z-50 w-full sm:w-[480px] bg-surface border-l border-line shadow-lift flex flex-col outline-none"
        >
          {/* Drawer Header */}
          <div className="px-6 py-5 border-b border-line flex items-start justify-between gap-4 bg-subtle/60">
            <div className="space-y-1">
              <p className="text-xs font-semibold text-brand">Deterministic Sizing Engine</p>
              <Dialog.Title className="font-display text-2xl text-ink leading-tight">
                Check My Fit
              </Dialog.Title>
              <Dialog.Description id="fit-drawer-description" className="text-xs text-ink-muted">
                {sku.name} — {sku.fabric_stretch.replace("_", " ")}
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <button
                type="button"
                onClick={closeFitDrawer}
                aria-label="Close Check My Fit drawer"
                className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-full border border-line-strong text-ink-muted hover:text-ink hover:bg-surface transition-colors cursor-pointer shrink-0"
              >
                <X className="w-4 h-4" aria-hidden="true" />
              </button>
            </Dialog.Close>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
            <div className="p-3.5 rounded-2xl bg-subtle border border-line flex items-center gap-2.5 text-xs text-ink-muted">
              <Shield className="w-4 h-4 text-brand shrink-0" aria-hidden="true" />
              <span>
                <strong className="text-ink">No photos required.</strong> Calculated from verified
                brand size matrices and weave ease rules.
              </span>
            </div>

            <fieldset className="space-y-2">
              <legend className="text-xs font-semibold text-ink">
                1. Reference brand you know your size in
              </legend>
              <RadioChipGroup
                ariaLabel="Known Brand"
                options={BRAND_OPTIONS}
                value={selectedBrand}
                onChange={(b) => {
                  setSelectedBrand(b);
                  setFitForSku(sku.id, null);
                }}
                layout="wrap"
              />
            </fieldset>

            <fieldset className="space-y-2">
              <legend className="text-xs font-semibold text-ink">
                2. Your usual size in {selectedBrand}
              </legend>
              <RadioChipGroup
                ariaLabel="Known Size"
                options={SIZE_OPTIONS}
                value={selectedSize}
                onChange={(s) => {
                  setSelectedSize(s);
                  setFitForSku(sku.id, null);
                }}
                layout="grid-6"
              />
            </fieldset>

            <fieldset className="space-y-2">
              <legend className="text-xs font-semibold text-ink">
                3. Desired silhouette ease
              </legend>
              <RadioChipGroup
                ariaLabel="Fit Preference"
                options={FIT_PREF_OPTIONS}
                value={fitPreference}
                onChange={(p) => {
                  setFitPreference(p);
                  setFitForSku(sku.id, null);
                }}
                layout="grid-2"
              />
            </fieldset>

            <div className="space-y-2.5 rounded-2xl border border-line bg-subtle p-4">
              <div className="flex items-baseline justify-between gap-2">
                <label htmlFor="fit-height-slider" className="text-xs font-semibold text-ink">
                  4. Your Height
                </label>
                <span className="text-sm font-semibold text-brand tabular-nums">
                  {heightCm} cm ({cmToFeetInches(heightCm)})
                </span>
              </div>
              <input
                id="fit-height-slider"
                type="range"
                min={145}
                max={195}
                step={1}
                value={heightCm}
                onChange={(e) => {
                  setHeightCm(Number(e.target.value));
                  setFitForSku(sku.id, null);
                }}
                className="rz-slider w-full"
              />
              <div className="flex justify-between text-[11px] text-ink-muted tabular-nums">
                <span>145 cm</span>
                <span>170 cm</span>
                <span>195 cm</span>
              </div>
            </div>

            <Button
              type="button"
              onClick={handleCalculateFit}
              isLoading={isLoading}
              fullWidth
              size="lg"
            >
              <Sparkles className="w-4 h-4" aria-hidden="true" />
              <span>Analyze Sizing for This Garment</span>
            </Button>

            {error && (
              <div
                role="alert"
                className="p-3.5 rounded-xl bg-danger-soft border border-danger/25 text-danger text-xs font-medium"
              >
                {error}
              </div>
            )}

            {activeFitResult && (
              <div
                aria-live="polite"
                className="rounded-2xl border border-brand/35 bg-surface p-5 space-y-4 shadow-card"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="text-[11px] font-medium text-ink-muted">
                      Recommended Size
                    </span>
                    <div className="font-display text-4xl text-brand mt-0.5">
                      Size {activeFitResult.recommended_size}
                    </div>
                    <div className="mt-1.5 flex flex-wrap items-center gap-2">
                      <Badge variant={getConfidenceBadgeVariant(activeFitResult.confidence_level)}>
                        {activeFitResult.confidence_level} Confidence
                      </Badge>
                      <span className="text-[11px] text-ink-muted inline-flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-trust" aria-hidden="true" />
                        Stocked
                      </span>
                    </div>
                  </div>

                  {/* Circular Heuristic Fit Score */}
                  <div className="flex flex-col items-center shrink-0">
                    <div className="relative h-14 w-14 flex items-center justify-center">
                      <svg viewBox="0 0 36 36" className="h-14 w-14 -rotate-90" aria-hidden="true">
                        <circle
                          cx="18"
                          cy="18"
                          r="15.5"
                          fill="none"
                          stroke="#E8DFF5"
                          strokeWidth="3"
                        />
                        <circle
                          cx="18"
                          cy="18"
                          r="15.5"
                          fill="none"
                          stroke="#6D28D9"
                          strokeWidth="3"
                          strokeDasharray={`${Math.min(100, activeFitResult.fit_score)} 100`}
                          strokeLinecap="round"
                        />
                      </svg>
                      <span className="absolute text-xs font-bold text-ink tabular-nums">
                        {activeFitResult.fit_score}
                      </span>
                    </div>
                    <span className="text-[10px] text-ink-muted tabular-nums mt-0.5">
                      Score: {activeFitResult.fit_score}/100
                    </span>
                  </div>
                </div>

                <p className="text-xs text-ink bg-subtle p-3 rounded-xl border border-line leading-relaxed">
                  {activeFitResult.explanation_text}
                </p>

                {activeFitResult.missing_data_warnings.length > 0 && (
                  <div className="p-3 rounded-xl bg-warn-soft border border-warn/35 text-warn-text text-xs space-y-1">
                    <div className="font-semibold flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-warn shrink-0" aria-hidden="true" />
                      <span>Measurement Notices</span>
                    </div>
                    {activeFitResult.missing_data_warnings.map((w, idx) => (
                      <p key={idx} className="text-[11px] leading-snug">
                        {w}
                      </p>
                    ))}
                  </div>
                )}

                {activeFitResult.fit_zone_breakdown && (
                  <FitZoneBreakdown breakdown={activeFitResult.fit_zone_breakdown} />
                )}

                <Button
                  type="button"
                  onClick={handleApplySizeAndAddToCart}
                  fullWidth
                  size="md"
                  className="bg-trust hover:bg-trust-text text-white"
                >
                  <span>Apply Size {activeFitResult.recommended_size} &amp; Add to Cart</span>
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </Button>
              </div>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
