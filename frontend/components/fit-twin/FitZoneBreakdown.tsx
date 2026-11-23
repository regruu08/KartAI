import React from "react";
import type { FitZoneDetail } from "@/lib/api/types";
import { cn } from "@/lib/cn";

export interface FitZoneBreakdownProps {
  breakdown: Record<string, FitZoneDetail | { note: string }>;
  className?: string;
}

export function FitZoneBreakdown({ breakdown, className }: FitZoneBreakdownProps) {
  const zones = ["bust", "waist", "shoulder"] as const;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "comfortable":
      case "relaxed":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "fitted":
      case "snug":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "restrictive":
        return "bg-rose-50 text-rose-700 border-rose-200";
      case "roomy":
        return "bg-purple-50 text-purple-700 border-purple-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
  };

  return (
    <div className={cn("space-y-2.5", className)}>
      <h4 className="text-xs font-bold uppercase tracking-wider text-inkMuted">
        Zone-by-Zone Ease Breakdown
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {zones.map((zoneKey) => {
          const detail = breakdown[zoneKey];
          if (!detail || "note" in detail) return null;

          const easeSign = detail.ease_inches >= 0 ? "+" : "";
          const easeDisplay = `${easeSign}${detail.ease_inches.toFixed(1)}"`;

          return (
            <div
              key={zoneKey}
              className="p-3 rounded-lg border border-border bg-canvas/40 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="capitalize font-bold text-ink">{zoneKey}</span>
                <span
                  className={cn(
                    "text-[10px] font-bold px-1.5 py-0.5 rounded border capitalize",
                    getStatusColor(detail.status),
                  )}
                >
                  {detail.status}
                </span>
              </div>
              <div className="text-sm font-extrabold text-brand">
                {easeDisplay} <span className="text-[10px] font-normal text-inkMuted">ease</span>
              </div>
              <div className="text-[10px] text-inkMuted mt-1">
                Garment: {detail.garment_inches.toFixed(1)}&quot; · Body: {detail.shopper_inches.toFixed(1)}&quot;
              </div>
            </div>
          );
        })}
      </div>

      {breakdown.length && "note" in breakdown.length && (
        <div className="p-2.5 rounded-lg border border-borderLight bg-surface text-xs text-inkMuted">
          <span className="font-semibold text-ink">Vertical Fall:</span> {breakdown.length.note}
        </div>
      )}
    </div>
  );
}
