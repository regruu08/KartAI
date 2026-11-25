"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Ruler, TriangleAlert } from "lucide-react";
import { api } from "@/lib/api/client";
import type {
  BrandName,
  FitPreference,
  FitRecommendationResponse,
  FitZoneDetail,
  SizeLabel,
} from "@/lib/api/types";
import { FALLBACK_CATALOG_SKUS, getSkuDisplayMeta } from "@/lib/catalog";
import { cn } from "@/lib/cn";
import { GarmentImage } from "@/components/ui/GarmentImage";

const PREVIEW_SKUS = ["SKU-01", "SKU-02", "SKU-03"] as const;
const BRANDS: readonly BrandName[] = ["Zara", "H&M", "Uniqlo", "Levi's", "Marks & Spencer"];
const SIZES: readonly SizeLabel[] = ["S", "M", "L", "XL"];
const DRAPES: readonly { value: FitPreference; label: string }[] = [
  { value: "tight", label: "Close Cut" },
  { value: "tailored", label: "Regular" },
  { value: "relaxed", label: "Relaxed" },
];

function isFitZoneDetail(value: FitZoneDetail | { note: string } | undefined): value is FitZoneDetail {
  return Boolean(value && "ease_inches" in value && "status" in value);
}

const FALLBACK_SANDBOX_RESULT: Record<string, FitRecommendationResponse> = {
  "SKU-01": {
    sku_id: "SKU-01",
    recommended_size: "L",
    confidence_level: "Medium",
    fit_score: 71,
    explanation_text:
      "Size M eliminated due to rigid 0% elastane shoulder constraint (-1.5\" ease). Size L delivers tailored +2.0\" chest ease and +0.5\" shoulder clearance.",
    missing_data_warnings: [],
    fit_zone_breakdown: {
      chest: { shopper_inches: 38.0, garment_inches: 40.0, ease_inches: 2.0, status: "Tailored" },
      shoulder: { shopper_inches: 16.5, garment_inches: 17.0, ease_inches: 0.5, status: "Meets minimum" },
    },
  },
  "SKU-02": {
    sku_id: "SKU-02",
    recommended_size: "M",
    confidence_level: "High",
    fit_score: 88,
    explanation_text:
      "Cotton-linen weave has slight natural give. Size M delivers +2.0\" chest ease and +1.0\" shoulder comfort.",
    missing_data_warnings: [],
    fit_zone_breakdown: {
      chest: { shopper_inches: 38.0, garment_inches: 40.0, ease_inches: 2.0, status: "Ideal" },
      shoulder: { shopper_inches: 16.5, garment_inches: 17.5, ease_inches: 1.0, status: "Comfortable" },
    },
  },
  "SKU-03": {
    sku_id: "SKU-03",
    recommended_size: "L",
    confidence_level: "Medium",
    fit_score: 68,
    explanation_text:
      "Size L prevents armhole restriction in rigid 320 GSM denim. Confidence capped at Medium because merchant sleeve length is missing.",
    missing_data_warnings: ["Sleeve length omitted in merchant catalog"],
    fit_zone_breakdown: {
      chest: { shopper_inches: 38.0, garment_inches: 42.0, ease_inches: 4.0, status: "Layering ease" },
      shoulder: { shopper_inches: 16.5, garment_inches: 18.0, ease_inches: 1.5, status: "Structured" },
    },
  },
};

export function LiveFitPreview() {
  const [selectedSkuId, setSelectedSkuId] = useState<(typeof PREVIEW_SKUS)[number]>("SKU-01");
  const [brand, setBrand] = useState<BrandName>("Zara");
  const [size, setSize] = useState<SizeLabel>("M");
  const [preference, setPreference] = useState<FitPreference>("tailored");
  const [result, setResult] = useState<FitRecommendationResponse>(
    FALLBACK_SANDBOX_RESULT["SKU-01"]!,
  );
  const [isSyncing, setIsSyncing] = useState(false);

  const sku =
    FALLBACK_CATALOG_SKUS.find((item) => item.id === selectedSkuId) ?? FALLBACK_CATALOG_SKUS[0]!;
  const meta = getSkuDisplayMeta(sku);

  useEffect(() => {
    let active = true;
    setIsSyncing(true);
    api
      .computeFit(selectedSkuId, {
        known_brand: brand,
        known_size: size,
        fit_preference: preference,
        height_cm: 168,
      })
      .then((res) => {
        if (active) setResult(res);
      })
      .catch(() => {
        if (active) {
          setResult(FALLBACK_SANDBOX_RESULT[selectedSkuId] ?? FALLBACK_SANDBOX_RESULT["SKU-01"]!);
        }
      })
      .finally(() => {
        if (active) setIsSyncing(false);
      });

    return () => {
      active = false;
    };
  }, [selectedSkuId, brand, size, preference]);

  const rawChest = result.fit_zone_breakdown?.chest;
  const rawShoulder = result.fit_zone_breakdown?.shoulder;
  const chest = isFitZoneDetail(rawChest) ? rawChest : null;
  const shoulder = isFitZoneDetail(rawShoulder) ? rawShoulder : null;

  return (
    <section
      id="live-fit-atelier"
      aria-labelledby="live-fit-heading"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 lg:py-20 border-t border-line"
    >
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div className="space-y-1.5 max-w-2xl">
          <p className="text-xs font-medium text-brand">Interactive Fit Physics</p>
          <h2 id="live-fit-heading" className="font-display text-3xl sm:text-4xl text-ink">
            Test Ease Math Before You Click Add to Bag
          </h2>
        </div>
        <p className="text-xs text-ink-muted max-w-sm">
          Switch garment weave or reference brand below to inspect how deterministic tolerances
          prevent shoulder restriction and bracketing.
        </p>
      </div>

      <div className="rounded-2xl border border-line bg-surface shadow-card overflow-hidden grid grid-cols-1 lg:grid-cols-12">
        {/* Left: Controls & Garment Selector */}
        <div className="lg:col-span-7 p-6 sm:p-8 space-y-6 border-b lg:border-b-0 lg:border-r border-line">
          <div className="space-y-2.5">
            <span className="block text-xs font-semibold text-ink">1. Choose a Garment Weave</span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {PREVIEW_SKUS.map((id) => {
                const item = FALLBACK_CATALOG_SKUS.find((s) => s.id === id)!;
                const active = selectedSkuId === id;
                return (
                  <button
                    key={id}
                    type="button"
                    aria-pressed={active}
                    onClick={() => setSelectedSkuId(id)}
                    className={cn(
                      "text-left p-3 rounded-xl border transition-colors cursor-pointer",
                      active
                        ? "border-brand bg-brand-soft/65 text-ink"
                        : "border-line bg-subtle/60 text-ink-muted hover:border-line-strong hover:text-ink",
                    )}
                  >
                    <p className="text-[11px] font-mono text-brand">{id}</p>
                    <p className="text-xs font-semibold text-ink line-clamp-1 mt-0.5">{item.name}</p>
                    <p className="text-[11px] text-ink-muted mt-0.5">
                      {item.fabric_stretch === "non_stretch" ? "Rigid 0% stretch" : "Slight stretch"}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            <div className="space-y-2">
              <span className="block text-xs font-semibold text-ink">2. Known Brand</span>
              <div className="flex flex-wrap gap-1.5">
                {BRANDS.map((b) => (
                  <button
                    key={b}
                    type="button"
                    aria-pressed={brand === b}
                    onClick={() => setBrand(b)}
                    className={cn(
                      "min-h-[36px] px-3 rounded-lg text-xs font-medium border transition-colors cursor-pointer",
                      brand === b
                        ? "border-brand bg-brand text-white"
                        : "border-line-strong bg-surface text-ink hover:bg-subtle",
                    )}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <span className="block text-xs font-semibold text-ink">
                3. Your Size in {brand} &amp; Drape
              </span>
              <div className="flex flex-wrap gap-1.5">
                {SIZES.map((s) => (
                  <button
                    key={s}
                    type="button"
                    aria-pressed={size === s}
                    onClick={() => setSize(s)}
                    className={cn(
                      "min-h-[36px] min-w-[40px] px-2.5 rounded-lg text-xs font-semibold border transition-colors cursor-pointer tabular-nums",
                      size === s
                        ? "border-brand bg-brand text-white"
                        : "border-line-strong bg-surface text-ink hover:bg-subtle",
                    )}
                  >
                    {s}
                  </button>
                ))}
                <span className="w-px h-6 bg-line self-center mx-1" aria-hidden="true" />
                {DRAPES.map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    aria-pressed={preference === d.value}
                    onClick={() => setPreference(d.value)}
                    className={cn(
                      "min-h-[36px] px-2.5 rounded-lg text-xs font-medium border transition-colors cursor-pointer",
                      preference === d.value
                        ? "border-ink bg-ink text-canvas"
                        : "border-line-strong bg-surface text-ink hover:bg-subtle",
                    )}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Real-time Verdict Readout */}
          <div className="rounded-xl border border-line bg-subtle p-4 sm:p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-brand text-white font-display text-xl flex items-center justify-center shrink-0">
                  {result.recommended_size}
                </div>
                <div>
                  <p className="text-[11px] text-ink-muted">
                    {isSyncing ? "Evaluating pattern ease…" : `Recommended Size for ${brand} ${size}`}
                  </p>
                  <p className="text-sm font-semibold text-ink">
                    {result.confidence_level} Confidence · Heuristic Fit Score {result.fit_score}/100
                  </p>
                </div>
              </div>

              <Link
                href={`/products/${sku.id}`}
                className="inline-flex items-center gap-1.5 min-h-[38px] px-4 rounded-full border border-line-strong bg-surface text-xs font-semibold text-ink hover:border-brand/60 transition-colors"
              >
                <Ruler className="w-3.5 h-3.5 text-brand" aria-hidden="true" />
                <span>Open Full Fitting Room</span>
              </Link>
            </div>

            <p className="text-xs text-ink leading-relaxed">{result.explanation_text}</p>

            {(chest || shoulder) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {chest && (
                  <div className="rounded-lg bg-surface border border-line p-3 space-y-1.5">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-ink-muted">Chest Ease</span>
                      <span className="font-semibold text-trust-text tabular-nums">
                        +{Number(chest.ease_inches).toFixed(1)}&quot; ({chest.status})
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-line overflow-hidden">
                      <div
                        className="h-full rounded-full bg-trust transition-all duration-300"
                        style={{
                          width: `${Math.min(100, Math.max(15, Number(chest.ease_inches) * 18))}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
                {shoulder && (
                  <div className="rounded-lg bg-surface border border-line p-3 space-y-1.5">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-ink-muted">Shoulder Clearance</span>
                      <span className="font-semibold text-brand tabular-nums">
                        {Number(shoulder.ease_inches) >= 0 ? "+" : ""}
                        {Number(shoulder.ease_inches).toFixed(1)}&quot; ({shoulder.status})
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-line overflow-hidden">
                      <div
                        className="h-full rounded-full bg-brand transition-all duration-300"
                        style={{
                          width: `${Math.min(100, Math.max(12, (Number(shoulder.ease_inches) + 1) * 32))}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {result.missing_data_warnings.length > 0 && (
              <div className="flex items-start gap-2 rounded-lg border border-warn/35 bg-warn-soft px-3 py-2 text-[11px] text-warn-text">
                <TriangleAlert className="w-3.5 h-3.5 text-warn shrink-0 mt-0.5" aria-hidden="true" />
                <span>{result.missing_data_warnings[0]}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right: Garment Visual + Macro Preview */}
        <div className="lg:col-span-5 bg-subtle/60 p-6 flex flex-col justify-between gap-4">
          <div className="grid grid-cols-2 gap-3">
            <GarmentImage
              src={meta.image}
              alt={meta.imageAlt}
              garmentName={sku.name}
              className="aspect-[3/4] rounded-xl border border-line"
            />
            <GarmentImage
              src={meta.detailImage}
              alt={meta.detailAlt}
              garmentName={sku.name}
              className="aspect-[3/4] rounded-xl border border-line"
            />
          </div>

          <div className="rounded-xl border border-line bg-surface p-3.5 flex items-center justify-between gap-3 text-xs">
            <div className="min-w-0">
              <p className="font-semibold text-ink truncate">{sku.name}</p>
              <p className="text-[11px] text-ink-muted truncate">{meta.weightLabel}</p>
            </div>
            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-trust-text shrink-0">
              <CheckCircle2 className="w-3.5 h-3.5 text-trust" aria-hidden="true" />
              S–XL Stocked
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
