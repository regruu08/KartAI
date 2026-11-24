"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { CheckCircle2, MessageSquare, LayoutDashboard, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import type { OrderResponse } from "@/lib/api/types";

export default function OrderConfirmationPage() {
  const params = useParams();
  const orderId = (params?.orderId as string) ?? "ORD-DEMO";

  const { placedOrder } = useStore();
  const [order, setOrder] = useState<OrderResponse | null>(placedOrder);
  const [isLoading, setIsLoading] = useState(!placedOrder);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!order && orderId) {
      setIsLoading(true);
      api
        .getOrder(orderId)
        .then((data) => {
          setOrder(data);
          setIsError(false);
        })
        .catch(() => {
          setIsError(true);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [order, orderId]);

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />

      <main className="max-w-2xl mx-auto px-4 sm:px-6 py-12 flex-1 w-full text-center space-y-6">
        {/* Success Icon */}
        <div className="w-16 h-16 rounded-full bg-emerald-100 text-accentEmerald flex items-center justify-center mx-auto shadow-sm">
          <CheckCircle2 className="w-9 h-9" />
        </div>

        {/* Confirmation Title */}
        <div className="space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-accentEmerald">
            Order Successfully Placed
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-ink">
            Thank you for shopping with ReturnZero!
          </h1>
          <p className="text-xs sm:text-sm text-inkMuted max-w-md mx-auto">
            Order Reference: <strong className="text-ink">{order?.order_number || orderId}</strong>
          </p>
        </div>

        {/* Order Details Bento Card */}
        <Card className="text-left space-y-3.5 text-xs">
          <div className="flex items-center justify-between pb-3 border-b border-borderLight">
            <span className="font-bold text-ink">Delivery Status</span>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-canvas text-brand border border-border">
              {order?.order_status || "Placed"}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <span className="text-[10px] font-semibold text-inkMuted block">Recipient</span>
              <span className="font-bold text-ink">
                {order?.customer_name ?? (isLoading ? "Loading..." : "Verified Customer")}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-semibold text-inkMuted block">Payment Method</span>
              <span className="font-bold text-ink flex items-center gap-1">
                {order?.payment_method || "COD"}
                {order?.payment_method === "PREPAID" && (
                  <Zap className="w-3 h-3 text-accentAmber" />
                )}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-[10px] font-semibold text-inkMuted block">Destination Address</span>
              <span className="font-medium text-ink">
                {order
                  ? [order.street_address, order.city, order.state, order.pin_code].filter(Boolean).join(", ")
                  : (isLoading ? "Loading..." : "Registered delivery address")}
              </span>
            </div>
          </div>
        </Card>

        {/* Big CTA for WhatsApp Delivery Assurance Simulator (ADR-015, BUILD_PLAN Phase 4) */}
        <div className="p-6 rounded-bento border-2 border-brand bg-surface shadow-bento space-y-3 text-left">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-[#25D366]/10 text-[#00A884] flex items-center justify-center shrink-0">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-ink">
                Complete Delivery Assurance (Simulated)
              </h3>
              <p className="text-xs text-inkMuted mt-0.5 leading-relaxed">
                Confirm your landmark and delivery slot in our in-browser WhatsApp simulator to upgrade your shipment to <strong className="text-ink">Safe for Dispatch</strong>.
              </p>
            </div>
          </div>

          <Link
            href={`/simulator?order=${order?.id || orderId}`}
            className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg text-sm font-bold bg-[#00A884] hover:bg-[#008f6f] text-white shadow-sm transition-all"
          >
            Open WhatsApp Simulator
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Secondary Navigation */}
        <div className="flex items-center justify-center gap-4 text-xs font-bold pt-4">
          <Link
            href="/"
            className="text-inkMuted hover:text-ink transition-colors"
          >
            ← Back to Storefront
          </Link>
          <span className="text-border">·</span>
          <Link
            href="/dashboard"
            className="text-brand hover:underline inline-flex items-center gap-1"
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            View Merchant Command Center
          </Link>
        </div>
      </main>
    </div>
  );
}
