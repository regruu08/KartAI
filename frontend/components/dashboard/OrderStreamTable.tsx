import React from "react";
import Link from "next/link";
import { MessageSquare, Zap } from "lucide-react";
import type { OrderResponse } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

export interface OrderStreamTableProps {
  orders: OrderResponse[];
  className?: string;
}

export function OrderStreamTable({ orders, className }: OrderStreamTableProps) {
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
    <Card className={cn("p-0 overflow-hidden shadow-sm", className)}>
      <div className="p-4 border-b border-borderLight flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-ink">Real-Time Order Stream</h3>
          <p className="text-xs text-inkMuted">Live feed of orders with automated delivery assurance &amp; risk status</p>
        </div>
        <span className="text-xs font-bold text-brand bg-canvas px-2.5 py-1 rounded-md border border-border">
          {orders.length} Active Records
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-canvas border-b border-borderLight text-inkMuted uppercase font-bold text-[10px]">
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
          <tbody className="divide-y divide-borderLight">
            {orders.map((o) => (
              <tr key={o.id} className="hover:bg-canvas/40 transition-colors">
                <td className="p-3 font-mono font-bold text-ink truncate max-w-[120px]">
                  {o.order_number}
                </td>
                <td className="p-3">
                  <div className="font-bold text-ink">{o.customer_name}</div>
                  <div className="text-[10px] text-inkMuted truncate max-w-[150px]">{o.street_address}</div>
                </td>
                <td className="p-3">
                  <span className="font-bold text-ink">{o.sku_id}</span>
                  <span className="text-brand font-extrabold ml-1.5 px-1.5 py-0.2 bg-brand/10 rounded">
                    {o.selected_size}
                  </span>
                </td>
                <td className="p-3">
                  <div className="font-semibold text-ink">{o.city}</div>
                  <span className="text-[10px] text-inkMuted font-bold">{o.tier}</span>
                </td>
                <td className="p-3 font-bold">
                  <span className="inline-flex items-center gap-1">
                    {o.payment_method}
                    {o.payment_method === "PREPAID" && (
                      <Zap className="w-3 h-3 text-accentAmber" />
                    )}
                  </span>
                </td>
                <td className="p-3">
                  <span
                    className={cn(
                      "text-[10px] font-bold px-2 py-0.5 rounded border",
                      getRiskBadge(o.cod_risk_score),
                    )}
                  >
                    {o.cod_risk_score}/100
                  </span>
                </td>
                <td className="p-3">
                  <span
                    className={cn(
                      "text-[10px] font-bold px-2.5 py-0.5 rounded-full border inline-block whitespace-nowrap",
                      getStatusBadge(o.order_status),
                    )}
                  >
                    {o.order_status}
                  </span>
                </td>
                <td className="p-3 text-right">
                  <Link
                    href={`/simulator?order=${o.id}`}
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-brand hover:underline"
                  >
                    <MessageSquare className="w-3 h-3" />
                    Simulate
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
