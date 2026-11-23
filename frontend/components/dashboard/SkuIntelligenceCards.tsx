import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { SkuMetricStat } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export interface SkuIntelligenceCardsProps {
  skus: SkuMetricStat[];
  className?: string;
}

export function SkuIntelligenceCards({ skus, className }: SkuIntelligenceCardsProps) {
  return (
    <div className={cn("space-y-3", className)}>
      <div>
        <h3 className="text-sm font-bold text-ink">SKU Performance &amp; Pattern Audit</h3>
        <p className="text-xs text-inkMuted">Return rates and merchant measurement gap notifications per garment</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {skus.map((sku) => (
          <Card key={sku.sku_id} className="p-4 space-y-3 shadow-sm flex flex-col justify-between">
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-brand uppercase bg-canvas px-2 py-0.5 rounded border border-border">
                  {sku.sku_id}
                </span>
                <span className="text-xs font-semibold text-inkMuted">{sku.total_orders} Orders</span>
              </div>
              <h4 className="text-xs font-bold text-ink line-clamp-1">{sku.sku_name}</h4>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-borderLight">
              <div>
                <span className="text-[10px] text-inkMuted block">Courier RTO</span>
                <span className="font-extrabold text-rose-700">{sku.rto_rate_pct.toFixed(1)}%</span>
              </div>
              <div>
                <span className="text-[10px] text-inkMuted block">Fit Returns</span>
                <span className="font-extrabold text-purple-700">{sku.fit_return_rate_pct.toFixed(1)}%</span>
              </div>
            </div>

            {/* Gap Warning or Verified Indicator */}
            {sku.has_missing_measurements ? (
              <div className="p-2 rounded bg-amber-50 border border-amber-200 text-amber-900 text-[10px] flex items-center gap-1.5 font-bold">
                <AlertTriangle className="w-3.5 h-3.5 text-accentAmber shrink-0" />
                <span>Data Gap: Missing sleeve dimensions</span>
              </div>
            ) : (
              <div className="p-2 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 text-[10px] flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5 text-accentEmerald shrink-0" />
                <span>Verified pattern table</span>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
