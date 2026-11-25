"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle, Sparkles } from "lucide-react";
import type { SkuResponse } from "@/lib/api/types";
import { api } from "@/lib/api/client";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { cn } from "@/lib/cn";

export interface CatalogIntelligencePanelProps {
  sku: SkuResponse;
  selectedSize?: string | null;
  recommendedSize?: string | null;
  onSkuUpdated?: (updated: SkuResponse) => void;
  className?: string;
}

export function CatalogIntelligencePanel({
  sku,
  selectedSize,
  recommendedSize,
  onSkuUpdated,
  className,
}: CatalogIntelligencePanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [extractNote, setExtractNote] = useState<string | null>(null);

  const missingFields: string[] = [];
  if (!sku.has_sleeve) {
    missingFields.push("Sleeve Length (not measured by merchant)");
  }
  if (!sku.has_shoulder) {
    missingFields.push("Shoulder Width (not specified)");
  }

  const handleRunExtraction = async () => {
    setExtracting(true);
    setExtractNote(null);
    try {
      const updated = await api.extractAttributes(sku.id, true);
      onSkuUpdated?.(updated);
      setExtractNote(`Updated via ${updated.provenance.replace(/_/g, " ")}`);
    } catch (err: unknown) {
      setExtractNote(
        err instanceof Error ? err.message : "Extraction fell back to verified benchmark.",
      );
    } finally {
      setExtracting(false);
    }
  };

  return (
    <div
      className={cn(
        "rounded-2xl border border-line bg-surface overflow-hidden shadow-card",
        className,
      )}
    >
      <button
        type="button"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 sm:p-5 flex items-center justify-between text-left hover:bg-subtle/70 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-brand-soft text-brand flex items-center justify-center shrink-0">
            <Sparkles className="w-4 h-4" aria-hidden="true" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink">Catalog Intelligence</h3>
            <p className="text-xs text-ink-muted">
              VLM pattern extraction &amp; measurement gap audit
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ProvenanceBadge provenance={sku.provenance} />
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-ink-muted" aria-hidden="true" />
          ) : (
            <ChevronDown className="w-4 h-4 text-ink-muted" aria-hidden="true" />
          )}
        </div>
      </button>

      {isOpen && (
        <div className="px-5 pb-5 pt-3 border-t border-line space-y-4 text-xs">
          {missingFields.length > 0 && (
            <div className="p-3.5 rounded-xl border border-warn/35 bg-warn-soft text-warn-text space-y-1">
              <div className="font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-warn shrink-0" aria-hidden="true" />
                <span>Merchant Data Gaps Detected</span>
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                {missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
              <p className="text-[11px] pt-1 opacity-90">
                Sizing engine caps confidence at Medium whenever critical garment specs are unstated.
              </p>
            </div>
          )}

          {/* Specifications Grid */}
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-ink">
            <div className="p-3 rounded-xl bg-subtle border border-line">
              <dt className="text-[11px] font-medium text-ink-muted">Fabric Stretch</dt>
              <dd className="font-semibold capitalize mt-0.5">
                {sku.fabric_stretch.replace("_", " ")}
              </dd>
            </div>
            <div className="p-3 rounded-xl bg-subtle border border-line">
              <dt className="text-[11px] font-medium text-ink-muted">Fabric Composition</dt>
              <dd className="font-semibold mt-0.5">{sku.fabric_composition}</dd>
            </div>
            <div className="p-3 rounded-xl bg-subtle border border-line">
              <dt className="text-[11px] font-medium text-ink-muted">Garment Length</dt>
              <dd className="font-semibold tabular-nums mt-0.5">
                {sku.length_inches ? `${sku.length_inches}"` : "Not specified"}
              </dd>
            </div>
            <div className="p-3 rounded-xl bg-subtle border border-line">
              <dt className="text-[11px] font-medium text-ink-muted">Extraction Source</dt>
              <dd className="font-semibold capitalize mt-0.5">
                {sku.provenance.replace(/_/g, " ")}
              </dd>
            </div>
          </dl>

          {/* Optional live Gemini Extraction action when PDP passes updater */}
          {onSkuUpdated && (
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <button
                type="button"
                disabled={extracting}
                onClick={() => void handleRunExtraction()}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full border border-line-strong bg-surface text-xs font-semibold text-brand hover:border-brand/60 hover:bg-subtle transition-colors cursor-pointer disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
                <span>{extracting ? "Extracting with Gemini…" : "Refresh VLM Extraction"}</span>
              </button>
              {extractNote && (
                <span className="text-[11px] text-ink-muted font-medium">{extractNote}</span>
              )}
            </div>
          )}

          {/* Pattern Measurement Table */}
          {sku.sizes_json && Object.keys(sku.sizes_json).length > 0 && (
            <div>
              <span className="text-[11px] font-semibold text-ink block mb-2">
                Merchant Measurement Table (Inches)
              </span>
              <div className="overflow-x-auto rounded-xl border border-line">
                <table className="w-full text-left border-collapse text-xs tabular-nums">
                  <thead className="bg-subtle border-b border-line text-ink-muted">
                    <tr>
                      <th className="py-2 px-3 font-semibold">Size</th>
                      <th className="py-2 px-3 font-semibold text-right">Chest</th>
                      <th className="py-2 px-3 font-semibold text-right">Waist</th>
                      <th className="py-2 px-3 font-semibold text-right">Shoulder</th>
                      <th className="py-2 px-3 font-semibold text-right">Length</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {Object.entries(sku.sizes_json).map(([size, dims]) => {
                      const highlighted = size === selectedSize || size === recommendedSize;
                      return (
                        <tr
                          key={size}
                          className={cn(
                            "transition-colors",
                            highlighted ? "bg-brand-soft/60 font-semibold" : "hover:bg-subtle/40",
                          )}
                        >
                          <td className="py-2 px-3 font-semibold text-brand whitespace-nowrap">
                            {size}
                            {size === recommendedSize && (
                              <span className="ml-1.5 text-[10px] font-semibold text-trust-text">
                                (Fit-Twin)
                              </span>
                            )}
                          </td>
                          <td className="py-2 px-3 text-right">
                            {dims.chest ?? dims.bust ?? "—"}&quot;
                          </td>
                          <td className="py-2 px-3 text-right">{dims.waist ?? "—"}&quot;</td>
                          <td className="py-2 px-3 text-right">{dims.shoulder ?? "—"}&quot;</td>
                          <td className="py-2 px-3 text-right">{dims.length ?? "—"}&quot;</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
