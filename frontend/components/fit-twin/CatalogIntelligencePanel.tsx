"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import type { SkuResponse } from "@/lib/api/types";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { cn } from "@/lib/cn";

export interface CatalogIntelligencePanelProps {
  sku: SkuResponse;
  className?: string;
}

export function CatalogIntelligencePanel({ sku, className }: CatalogIntelligencePanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Missing data detection per ADR-004 and ADR-013
  const missingFields: string[] = [];
  if (!sku.has_sleeve) {
    missingFields.push("Sleeve Length (not measured by merchant)");
  }
  if (!sku.has_shoulder) {
    missingFields.push("Shoulder Width (not specified)");
  }

  return (
    <div className={cn("rounded-bento border border-border bg-surface overflow-hidden shadow-sm", className)}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between text-left hover:bg-canvas/50 transition-colors"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-brand/10 text-brand flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-ink">Catalog Intelligence</h3>
            <p className="text-xs text-inkMuted">VLM pattern extraction &amp; measurement gap audit</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ProvenanceBadge provenance={sku.provenance} />
          {isOpen ? <ChevronUp className="w-4 h-4 text-inkMuted" /> : <ChevronDown className="w-4 h-4 text-inkMuted" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-4 pt-0 border-t border-borderLight space-y-3.5 text-xs">
          {/* Missing data warnings */}
          {missingFields.length > 0 && (
            <div className="p-3 rounded-lg border border-amber-200 bg-amber-50 text-amber-900 space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-accentAmber" />
                Merchant Data Gaps Detected
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-[11px] text-amber-800">
                {missingFields.map((field) => (
                  <li key={field}>{field}</li>
                ))}
              </ul>
              <p className="text-[10px] text-amber-700 italic pt-1">
                Note: Sizing engine penalizes confidence to &apos;Medium&apos; to protect against fit failure.
              </p>
            </div>
          )}

          {/* Specifications Grid */}
          <div className="grid grid-cols-2 gap-2 text-ink">
            <div className="p-2.5 rounded-lg bg-canvas border border-borderLight">
              <span className="text-[10px] font-semibold text-inkMuted uppercase block">Fabric Stretch</span>
              <span className="font-bold capitalize">{sku.fabric_stretch.replace("_", " ")}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-canvas border border-borderLight">
              <span className="text-[10px] font-semibold text-inkMuted uppercase block">Fabric Composition</span>
              <span className="font-bold">{sku.fabric_composition}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-canvas border border-borderLight">
              <span className="text-[10px] font-semibold text-inkMuted uppercase block">Garment Length</span>
              <span className="font-bold">{sku.length_inches ? `${sku.length_inches}"` : "Not specified"}</span>
            </div>
            <div className="p-2.5 rounded-lg bg-canvas border border-borderLight">
              <span className="text-[10px] font-semibold text-inkMuted uppercase block">Extraction Source</span>
              <span className="font-bold capitalize">{sku.provenance.replace("_", " ")}</span>
            </div>
          </div>

          {/* Pattern Size Table */}
          {sku.sizes_json && Object.keys(sku.sizes_json).length > 0 && (
            <div>
              <span className="text-[10px] font-semibold text-inkMuted uppercase block mb-1.5">
                Merchant Measurement Table (Inches)
              </span>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse border border-borderLight rounded-lg overflow-hidden text-[11px]">
                  <thead className="bg-canvas border-b border-borderLight">
                    <tr>
                      <th className="p-1.5 font-bold">Size</th>
                      <th className="p-1.5 font-bold">Chest</th>
                      <th className="p-1.5 font-bold">Waist</th>
                      <th className="p-1.5 font-bold">Shoulder</th>
                      <th className="p-1.5 font-bold">Length</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(sku.sizes_json).map(([size, dims]) => (
                      <tr key={size} className="border-b border-borderLight/60 hover:bg-canvas/30">
                        <td className="p-1.5 font-bold text-brand">{size}</td>
                        <td className="p-1.5">{dims.chest ?? dims.bust ?? "—"}&quot;</td>
                        <td className="p-1.5">{dims.waist ?? "—"}&quot;</td>
                        <td className="p-1.5">{dims.shoulder ?? "—"}&quot;</td>
                        <td className="p-1.5">{dims.length ?? "—"}&quot;</td>
                      </tr>
                    ))}
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
