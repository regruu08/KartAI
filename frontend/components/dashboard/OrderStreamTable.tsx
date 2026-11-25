"use client";

import React, { useMemo, useState } from "react";
import Link from "next/link";
import { MessageSquare, Search, Zap } from "lucide-react";
import type { OrderResponse } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export interface OrderStreamTableProps {
  orders: OrderResponse[];
  className?: string;
}

type OrderFilterMode = "all" | "high_risk" | "safe" | "cod_only" | "rto_ndr";

export function OrderStreamTable({ orders, className }: OrderStreamTableProps) {
  const [query, setQuery] = useState("");
  const [filterMode, setFilterMode] = useState<OrderFilterMode>("all");

  const filteredOrders = useMemo(() => {
    const q = query.trim().toLowerCase();
    return orders.filter((o) => {
      if (filterMode === "high_risk" && o.cod_risk_score < 70) return false;
      if (filterMode === "safe" && o.order_status !== "Safe_For_Dispatch") return false;
      if (filterMode === "cod_only" && o.payment_method.toUpperCase() !== "COD") return false;
      if (
        filterMode === "rto_ndr" &&
        !o.order_status.includes("RTO") &&
        !o.order_status.includes("NDR")
      ) {
        return false;
      }
      if (q) {
        const hay = `${o.order_number} ${o.customer_name} ${o.city} ${o.sku_id} ${o.pin_code}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [orders, query, filterMode]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Safe_For_Dispatch":
      case "Delivered (Kept)":
      case "NDR_Resolved":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "Address_Updated":
      case "Delivery_Rescheduled":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "COD RTO (Doorstep Refusal)":
      case "COD RTO (Address Incomplete)":
      case "Prepaid RTO (Customer Relocated)":
        return "bg-rose-50 text-rose-700 border-rose-200";
      case "Customer Returned (Fit Issue)":
      case "Customer Returned (Defect)":
        return "bg-purple-50 text-purple-700 border-purple-200";
      case "Placed":
      case "NDR":
      default:
        return "bg-amber-50 text-amber-700 border-amber-200";
    }
  };

  const getRiskBadge = (score: number) => {
    if (score < 40) return "bg-emerald-50 text-emerald-700 border-emerald-200";
    if (score < 70) return "bg-amber-50 text-amber-700 border-amber-200";
    return "bg-rose-50 text-rose-700 border-rose-200";
  };

  return (
    <Card className={cn("p-0 overflow-hidden shadow-card", className)}>
      <div className="p-4 sm:p-5 border-b border-line space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-display text-lg text-ink">Real-Time Order Stream</h3>
            <p className="text-xs text-ink-muted">
              Live feed of orders with delivery assurance status and risk scores
            </p>
          </div>
          <span className="text-xs font-semibold text-brand bg-subtle px-3 py-1 rounded-full border border-line tabular-nums">
            {filteredOrders.length} of {orders.length} Records
          </span>
        </div>

        {/* Search & Filter Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-1">
          <div className="relative w-full md:max-w-xs">
            <Search
              className="w-3.5 h-3.5 text-ink-muted absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"
              aria-hidden="true"
            />
            <input
              type="search"
              aria-label="Filter order stream"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search order #, customer, city, SKU…"
              className="w-full min-h-[38px] pl-8 pr-3 rounded-xl border border-line-strong bg-canvas/60 text-xs text-ink placeholder:text-ink-muted focus:border-brand focus:bg-surface"
            />
          </div>

          <div role="group" aria-label="Filter orders by risk or status" className="flex flex-wrap gap-1.5">
            {(
              [
                { id: "all", label: "All" },
                { id: "high_risk", label: "High Risk" },
                { id: "safe", label: "Safe for Dispatch" },
                { id: "cod_only", label: "COD Only" },
                { id: "rto_ndr", label: "RTO / NDR" },
              ] as const
            ).map((pill) => {
              const active = filterMode === pill.id;
              return (
                <button
                  key={pill.id}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setFilterMode(pill.id)}
                  className={cn(
                    "min-h-[34px] px-3 py-1 rounded-full border text-xs font-medium transition-colors cursor-pointer",
                    active
                      ? "bg-brand text-white border-brand"
                      : "bg-surface text-ink-muted border-line-strong hover:text-ink hover:bg-subtle",
                  )}
                >
                  {pill.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-subtle border-b border-line text-ink-muted font-semibold text-[11px]">
            <tr>
              <th className="p-3">Order #</th>
              <th className="p-3">Customer</th>
              <th className="p-3">Garment / Size</th>
              <th className="p-3">Destination</th>
              <th className="p-3">Payment</th>
              <th className="p-3">Risk Index</th>
              <th className="p-3">Lifecycle Status</th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {filteredOrders.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-xs text-ink-muted">
                  No orders match your current search or filter pill.
                </td>
              </tr>
            ) : (
              filteredOrders.map((o) => (
                <tr key={o.id} className="hover:bg-subtle/60 transition-colors">
                  <td className="p-3 font-mono font-semibold text-ink truncate max-w-[130px]">
                    {o.order_number}
                  </td>
                  <td className="p-3">
                    <div className="font-semibold text-ink">{o.customer_name}</div>
                    <div className="text-[11px] text-ink-muted truncate max-w-[160px]">
                      {o.street_address}
                    </div>
                  </td>
                  <td className="p-3">
                    <span className="font-semibold text-ink">{o.sku_id}</span>
                    <span className="text-brand font-bold ml-1.5 px-1.5 py-0.5 bg-brand-soft rounded">
                      {o.selected_size}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="font-medium text-ink">{o.city}</div>
                    <span className="text-[11px] text-ink-muted">{o.tier}</span>
                  </td>
                  <td className="p-3 font-semibold">
                    <span className="inline-flex items-center gap-1">
                      {o.payment_method}
                      {o.payment_method.toUpperCase() === "PREPAID" && (
                        <Zap className="w-3 h-3 text-warn" aria-hidden="true" />
                      )}
                    </span>
                  </td>
                  <td className="p-3">
                    <span
                      className={cn(
                        "text-[11px] font-semibold px-2 py-0.5 rounded border tabular-nums",
                        getRiskBadge(o.cod_risk_score),
                      )}
                    >
                      {o.cod_risk_score}/100
                    </span>
                  </td>
                  <td className="p-3">
                    <span
                      className={cn(
                        "text-[11px] font-semibold px-2.5 py-0.5 rounded-full border inline-block whitespace-nowrap",
                        getStatusBadge(o.order_status),
                      )}
                    >
                      {o.order_status}
                    </span>
                  </td>
                  <td className="p-3 text-right">
                    <Link
                      href={`/simulator?order=${encodeURIComponent(o.id)}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-brand hover:underline"
                    >
                      <MessageSquare className="w-3.5 h-3.5" aria-hidden="true" />
                      <span>Simulate</span>
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
