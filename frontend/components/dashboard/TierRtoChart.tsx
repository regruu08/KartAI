"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { TierRtoStat } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export interface TierRtoChartProps {
  data: TierRtoStat[];
  className?: string;
}

export function TierRtoChart({ data, className }: TierRtoChartProps) {
  const chartData = data.map((d) => ({
    tier: d.tier,
    rtoRate: Number(d.rto_rate_pct.toFixed(1)),
    rtoCount: d.rto_count,
    totalOrders: d.total_orders,
  }));

  return (
    <Card className={cn("p-5 space-y-4 shadow-sm", className)}>
      <div>
        <h3 className="text-sm font-bold text-ink">Geographic Courier RTO Rates</h3>
        <p className="text-xs text-inkMuted">Delivery failure rate broken down across city tiers</p>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5D9FD" vertical={false} />
            <XAxis dataKey="tier" tick={{ fontSize: 11, fill: "#6B6280" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#6B6280" }} axisLine={false} tickLine={false} unit="%" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#FFFFFF",
                borderRadius: "8px",
                borderColor: "#D4C2FC",
                fontSize: "11px",
              }}
              formatter={(value: number) => [`${value}%`, "RTO Rate"]}
            />
            <Bar dataKey="rtoRate" fill="#7938F5" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
