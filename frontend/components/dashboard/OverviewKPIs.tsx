import React from "react";
import { Package, Percent, Truck, RotateCcw, Zap, DollarSign, TrendingUp } from "lucide-react";
import type { AnalyticsOverviewResponse } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export interface OverviewKPIsProps {
  data: AnalyticsOverviewResponse;
  className?: string;
}

export function OverviewKPIs({ data, className }: OverviewKPIsProps) {
  const kpis = [
    {
      title: "Shipped Orders",
      value: data.total_orders.toString(),
      subtitle: `${data.cod_orders_count} COD · ${data.prepaid_orders_count} Prepaid`,
      icon: Package,
      color: "text-brand",
      bg: "bg-brand-soft",
    },
    {
      title: "COD Share",
      value: `${data.cod_share_pct.toFixed(1)}%`,
      subtitle: "COD order share",
      icon: Percent,
      color: "text-amber-700",
      bg: "bg-amber-100",
    },
    {
      title: "Blended RTO Rate",
      value: `${data.rto_rate_pct.toFixed(1)}%`,
      subtitle:
        data.cod_rto_rate_pct != null
          ? `COD: ${data.cod_rto_rate_pct.toFixed(1)}% · Prepaid: ${(data.prepaid_rto_rate_pct ?? 0).toFixed(1)}%`
          : `${data.rto_count} failed deliveries`,
      description: "Courier delivery failure before delivery to customer (SOURCES_AND_ASSUMPTIONS §B)",
      icon: Truck,
      color: "text-rose-700",
      bg: "bg-rose-100",
    },
    {
      title: "Customer Return Rate",
      value: `${data.customer_return_rate_pct.toFixed(1)}%`,
      subtitle: `${data.customer_return_count} post-delivery returns`,
      description: "Delivered product returned post-delivery for fit or defect (SOURCES_AND_ASSUMPTIONS §B)",
      icon: RotateCcw,
      color: "text-purple-700",
      bg: "bg-purple-100",
    },
    {
      title: "COD → UPI Conversions",
      value: data.converted_to_upi_count.toString(),
      subtitle: "Converted via incentive",
      icon: Zap,
      color: "text-emerald-700",
      bg: "bg-emerald-100",
    },
    {
      title: "Incentives Disbursed",
      value: `₹${Number(data.total_incentives_disbursed_inr).toLocaleString("en-IN")}`,
      subtitle: "Margin-safe discounts",
      icon: DollarSign,
      color: "text-blue-700",
      bg: "bg-blue-100",
    },
    {
      title: "Modelled Direct Savings",
      value: `₹${Number(data.estimated_direct_savings_inr).toLocaleString("en-IN")}`,
      subtitle:
        data.net_direct_savings_inr != null
          ? `Net retained: ₹${Number(data.net_direct_savings_inr).toLocaleString("en-IN")}`
          : "Avoided courier loss",
      icon: TrendingUp,
      color: "text-trust-text",
      bg: "bg-emerald-100",
      highlight: true,
    },
  ];

  return (
    <div className={cn("grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3.5", className)}>
      {kpis.map((kpi, idx) => {
        const Icon = kpi.icon;
        return (
          <Card
            key={idx}
            title={kpi.description}
            className={cn(
              "p-4 flex flex-col justify-between space-y-2.5 transition-all",
              kpi.highlight &&
                "col-span-2 sm:col-span-1 border-trust/45 bg-emerald-50/45",
            )}
          >
            <div className="flex items-center justify-between gap-1.5">
              <span className="text-[11px] font-semibold text-ink-muted leading-tight">
                {kpi.title}
              </span>
              <div
                className={cn(
                  "w-7 h-7 rounded-lg flex items-center justify-center shrink-0",
                  kpi.bg,
                  kpi.color,
                )}
              >
                <Icon className="w-3.5 h-3.5" aria-hidden="true" />
              </div>
            </div>

            <div>
              <div className={cn("text-xl font-bold tracking-tight tabular-nums", kpi.color)}>
                {kpi.value}
              </div>
              <p className="text-[10px] text-ink-muted truncate mt-0.5 tabular-nums">
                {kpi.subtitle}
              </p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
