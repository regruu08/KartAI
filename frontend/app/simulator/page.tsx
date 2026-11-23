"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, LayoutDashboard, ShieldCheck, CheckCircle2 } from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { Card } from "@/components/ui/Card";
import { WhatsAppPhoneSimulator } from "@/components/simulator/WhatsAppPhoneSimulator";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import type { OrderResponse } from "@/lib/api/types";

function SimulatorContent() {
  const searchParams = useSearchParams();
  const orderParam = searchParams.get("order") ?? "";

  const { placedOrder } = useStore();
  const [order, setOrder] = useState<OrderResponse | null>(placedOrder);

  useEffect(() => {
    const targetId = orderParam || placedOrder?.id;
    if (targetId) {
      api.getOrder(targetId).then(setOrder).catch(() => null);
    }
  }, [orderParam, placedOrder]);

  const fetchLatestOrder = () => {
    const targetId = orderParam || placedOrder?.id;
    if (targetId) {
      api.getOrder(targetId).then(setOrder).catch(() => null);
    }
  };

  const activeOrderId = order?.id || orderParam || "ORD-DEMO-001";
  const customerName = order?.customer_name || "Priya Sharma";
  const streetAddress = order?.street_address || "House 12, Sector 15, Near City Market";
  const addressQuality = (order?.address_status as "Complete" | "NeedsLandmark" | "Poor") || "NeedsLandmark";

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
      <div className="mb-6 flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-inkMuted hover:text-brand transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Storefront
        </Link>

        <Link
          href="/dashboard"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-brand bg-surface px-3 py-1.5 rounded-lg border border-border shadow-xs hover:bg-canvas transition-colors"
        >
          <LayoutDashboard className="w-3.5 h-3.5" />
          Merchant Command Center
        </Link>
      </div>

      <div className="text-center max-w-xl mx-auto mb-8 space-y-2">
        <span className="text-[10px] font-extrabold uppercase tracking-wider text-brand px-2.5 py-0.5 rounded-full bg-brand/10 border border-brand/20">
          Delivery Assurance Module
        </span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-ink">
          Interactive WhatsApp Simulator
        </h1>
        <p className="text-xs text-inkMuted leading-relaxed">
          Simulating real-time conversational address enrichment, landmark capture, and delivery slot confirmation without external Meta API delays.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Order Context Card */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-borderLight">
              <span className="text-xs font-bold uppercase tracking-wider text-inkMuted">
                Target Order Context
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-canvas text-brand border border-border">
                {order?.order_status || "Safe_For_Dispatch"}
              </span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div>
                <span className="text-[10px] font-semibold text-inkMuted block">Order Reference</span>
                <span className="font-bold text-ink">{order?.order_number || activeOrderId}</span>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-inkMuted block">Recipient Name</span>
                <span className="font-bold text-ink">{customerName}</span>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-inkMuted block">Delivery Address</span>
                <span className="font-medium text-ink">{streetAddress}</span>
              </div>
              <div>
                <span className="text-[10px] font-semibold text-inkMuted block">Address Status</span>
                <span className="font-bold capitalize text-accentEmerald">
                  {order?.address_status || addressQuality}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-canvas border border-borderLight text-xs text-inkMuted space-y-1">
              <div className="font-bold text-ink flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-brand" />
                Live State Synchronization
              </div>
              <p className="text-[11px] leading-relaxed">
                When you interact in the phone simulator, actions execute live calls to backend <code className="text-brand">/v1/orders/{activeOrderId}/verify</code> and immediately update database state.
              </p>
            </div>
          </Card>
        </div>

        {/* Right Column: Phone Simulator */}
        <div className="lg:col-span-7 flex justify-center">
          <WhatsAppPhoneSimulator
            orderId={activeOrderId}
            customerName={customerName}
            streetAddress={streetAddress}
            addressQuality={addressQuality}
            onOrderUpdated={fetchLatestOrder}
          />
        </div>
      </div>
    </div>
  );
}

export default function SimulatorPage() {
  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />
      <Suspense fallback={<div className="p-10 text-center">Loading simulator...</div>}>
        <SimulatorContent />
      </Suspense>
    </div>
  );
}
