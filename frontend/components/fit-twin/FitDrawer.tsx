"use client";

import React, { useState } from "react";
import { X, Sparkles, Shield, AlertTriangle, ArrowRight } from "lucide-react";
import type { SkuResponse, BrandName, SizeLabel, FitPreference } from "@/lib/api/types";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { FitZoneBreakdown } from "./FitZoneBreakdown";
import { cn } from "@/lib/cn";

export interface FitDrawerProps {
  sku: SkuResponse;
}

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
    setFitResult,
    addToCart,
  } = useStore();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!fitDrawerOpen) return null;

  const brands: BrandName[] = ["Zara", "H&M", "Uniqlo"];
  const sizes: SizeLabel[] = ["XS", "S", "M", "L", "XL", "XXL"];
  const preferences: { key: FitPreference; label: string }[] = [
    { key: "tight", label: "Tight" },
    { key: "tailored", label: "Regular" }, // UI label "Regular" per BUILD_PLAN Phase 4
    { key: "relaxed", label: "Relaxed" },
    { key: "oversized", label: "Oversized" },
  ];

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
      setFitResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to calculate fit recommendation");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySizeAndAddToCart = () => {
    if (!fitResult) return;
    addToCart({
      sku,
      size: fitResult.recommended_size,
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
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-ink/40 backdrop-blur-sm transition-opacity"
        onClick={closeFitDrawer}
      />

      {/* Slide-over panel */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-surface border-l border-border shadow-2xl flex flex-col">
          {/* Drawer Header */}
          <div className="p-5 border-b border-borderLight flex items-center justify-between bg-canvas/40">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand text-white flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-ink">Check My Fit</h2>
                <p className="text-xs text-inkMuted">Deterministic Sizing Intelligence</p>
              </div>
            </div>
            <button
              type="button"
              onClick={closeFitDrawer}
              className="p-1.5 rounded-lg text-inkMuted hover:text-ink hover:bg-canvas transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5">
            {/* Privacy Guarantee Banner (ADR-004) */}
            <div className="p-3 rounded-lg bg-canvas border border-borderLight flex items-center gap-2.5 text-xs text-inkMuted">
              <Shield className="w-4 h-4 text-brand shrink-0" />
              <span>
                <strong className="text-ink">No photos required.</strong> We calculate sizing using verified brand measurement tables.
              </span>
            </div>

            {/* Step 1: Known Brand */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-inkMuted mb-2">
                1. Your best-fitting reference brand
              </label>
              <div className="grid grid-cols-3 gap-2">
                {brands.map((b) => (
                  <button
                    key={b}
                    type="button"
                    onClick={() => {
                      setSelectedBrand(b);
                      setFitResult(null);
                    }}
                    className={cn(
                      "py-2.5 px-3 rounded-lg text-xs font-bold border transition-all text-center",
                      selectedBrand === b
                        ? "bg-brand text-white border-brand shadow-sm"
                        : "bg-surface border-border text-ink hover:bg-canvas",
                    )}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            {/* Step 2: Known Size */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-inkMuted mb-2">
                2. Your typical size in {selectedBrand}
              </label>
              <div className="grid grid-cols-6 gap-1.5">
                {sizes.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => {
                      setSelectedSize(s);
                      setFitResult(null);
                    }}
                    className={cn(
                      "py-2 text-xs font-bold rounded-lg border transition-all text-center",
                      selectedSize === s
                        ? "bg-brand text-white border-brand shadow-sm"
                        : "bg-surface border-border text-ink hover:bg-canvas",
                    )}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Step 3: Fit Preference */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-inkMuted mb-2">
                3. Desired fit silhouette
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {preferences.map((p) => (
                  <button
                    key={p.key}
                    type="button"
                    onClick={() => {
                      setFitPreference(p.key);
                      setFitResult(null);
                    }}
                    className={cn(
                      "py-2 px-1 text-xs font-bold rounded-lg border transition-all text-center",
                      fitPreference === p.key
                        ? "bg-brand text-white border-brand shadow-sm"
                        : "bg-surface border-border text-ink hover:bg-canvas",
                    )}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Step 4: Shopper Height (cm) */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-inkMuted">
                  4. Your Height
                </label>
                <span className="text-xs font-bold text-brand">{heightCm} cm</span>
              </div>
              <input
                type="range"
                min="145"
                max="195"
                value={heightCm}
                onChange={(e) => {
                  setHeightCm(Number(e.target.value));
                  setFitResult(null);
                }}
                className="w-full accent-brand cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-inkMuted mt-1">
                <span>145 cm</span>
                <span>170 cm</span>
                <span>195 cm</span>
              </div>
            </div>

            {/* Calculate CTA */}
            <Button
              type="button"
              onClick={handleCalculateFit}
              isLoading={isLoading}
              className="w-full"
              size="lg"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Analyze Sizing for This Garment
            </Button>

            {error && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
                {error}
              </div>
            )}

            {/* Sizing Recommendation Result Card */}
            {fitResult && (
              <div className="rounded-bento border-2 border-brand bg-surface p-4 space-y-4 shadow-bento animate-in fade-in duration-300">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-inkMuted">
                      Recommended Size
                    </span>
                    <div className="text-3xl font-extrabold text-brand mt-0.5">
                      Size {fitResult.recommended_size}
                    </div>
                  </div>
                  <div className="text-right space-y-1">
                    <Badge variant={getConfidenceBadgeVariant(fitResult.confidence_level)}>
                      {fitResult.confidence_level} Confidence
                    </Badge>
                    <div className="text-[10px] text-inkMuted">
                      Score: {fitResult.fit_score}/100
                    </div>
                  </div>
                </div>

                {/* Explanation text */}
                <p className="text-xs text-ink bg-canvas/50 p-2.5 rounded-lg border border-borderLight leading-relaxed">
                  {fitResult.explanation_text}
                </p>

                {/* Missing data warnings if any */}
                {fitResult.missing_data_warnings.length > 0 && (
                  <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
                    <div className="font-bold flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-accentAmber" />
                      Measurement Notices
                    </div>
                    {fitResult.missing_data_warnings.map((w, idx) => (
                      <p key={idx} className="text-[11px] leading-snug">
                        {w}
                      </p>
                    ))}
                  </div>
                )}

                {/* Zone Breakdown */}
                {fitResult.fit_zone_breakdown && (
                  <FitZoneBreakdown breakdown={fitResult.fit_zone_breakdown} />
                )}

                {/* Apply size CTA */}
                <Button
                  type="button"
                  onClick={handleApplySizeAndAddToCart}
                  className="w-full bg-accentEmerald hover:bg-emerald-700 text-white"
                  size="md"
                >
                  Apply Size {fitResult.recommended_size} &amp; Add to Cart
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
