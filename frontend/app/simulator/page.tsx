"use client";

import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  LayoutDashboard,
  ShieldCheck,
} from "lucide-react";
import { api } from "@/lib/api/client";
import type { OrderResponse } from "@/lib/api/types";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/cn";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import {
  WhatsAppPhoneSimulator,
  type WhatsAppSyncActivity,
} from "@/components/simulator/WhatsAppPhoneSimulator";

const TIMELINE_STEPS = [
  { id: "Placed", label: "Placed" },
  { id: "Opt-in", label: "Opt-in" },
  { id: "AWAITING_LANDMARK", label: "Landmark" },
  { id: "SLOT_SELECTION", label: "Slot" },
  { id: "Safe_For_Dispatch", label: "Safe_For_Dispatch" },
] as const;

function SimulatorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const orderParam = searchParams.get("order") ?? "";

  const { placedOrder } = useStore();
  const initialMatched =
    placedOrder && (!orderParam || placedOrder.id === orderParam) ? placedOrder : null;
  const [order, setOrder] = useState<OrderResponse | null>(initialMatched);
  const [isOrderLoading, setIsOrderLoading] = useState(!initialMatched);
  const [recentOrders, setRecentOrders] = useState<OrderResponse[]>([]);
  const [syncActivity, setSyncActivity] = useState<WhatsAppSyncActivity | null>(null);

  useEffect(() => {
    api
      .listOrders(10, 0)
      .then((res) => {
        if (res.orders) setRecentOrders(res.orders);
      })
      .catch(() => null);
  }, []);

  useEffect(() => {
    let active = true;
    setIsOrderLoading(true);
    const targetId = orderParam || placedOrder?.id;
    const load = targetId
      ? api.getOrder(targetId)
      : api.listOrders(1, 0).then((res) => {
          if (res.orders && res.orders.length > 0 && res.orders[0]) {
            return res.orders[0];
          }
          return api.getOrder("RZ-1042");
        });

    load
      .then((resolved) => {
        if (active) setOrder(resolved);
      })
      .catch(() => {
        if (!targetId) {
          api
            .getOrder("RZ-1042")
            .then((resolved) => {
              if (active) setOrder(resolved);
            })
            .catch(() => null);
        }
      })
      .finally(() => {
        if (active) setIsOrderLoading(false);
      });

    return () => {
      active = false;
    };
  }, [orderParam, placedOrder]);

  const fetchLatestOrder = () => {
    const targetId = order?.id || orderParam || placedOrder?.id || "RZ-1042";
    api.getOrder(targetId).then(setOrder).catch(() => null);
  };

  const activeOrderId = order?.id || orderParam || "RZ-1042";
  const customerName = order?.customer_name || (isOrderLoading ? "Loading recipient…" : "Guest Shopper");
  const streetAddress =
    order?.street_address || (isOrderLoading ? "Fetching persisted destination…" : "Address pending");
  const addressQuality =
    (order?.address_status as "Complete" | "NeedsLandmark" | "Poor") || "NeedsLandmark";

  const completedStages = (() => {
    if (order?.order_status === "Safe_For_Dispatch" || syncActivity?.step === "SAFE_FOR_DISPATCH") {
      return 5;
    }
    if (syncActivity?.step === "SLOT_SELECTION") return 3;
    if (syncActivity?.step === "AWAITING_LANDMARK") return 2;
    if (syncActivity?.step === "NDR_RESCHEDULED") return 5;
    return 1;
  })();

  return (
    <main
      id="main-content"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 flex-1 w-full"
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted hover:text-brand transition-colors"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>Back to Storefront</span>
        </Link>

        <Link
          href="/dashboard"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand bg-surface px-4 py-2 rounded-full border border-line-strong hover:border-brand/50 hover:bg-subtle transition-colors"
        >
          <LayoutDashboard className="w-3.5 h-3.5" aria-hidden="true" />
          <span>Merchant Command Center</span>
        </Link>
      </div>

      <div className="max-w-2xl mb-8 space-y-1.5">
        <p className="text-xs font-medium text-ink-muted">Pre-Dispatch Delivery Assurance</p>
        <h1 className="font-display text-3xl sm:text-4xl text-ink">
          WhatsApp Delivery Simulator
        </h1>
        <p className="text-sm text-ink-muted leading-relaxed">
          Interactive address enrichment, landmark capture, and delivery slot confirmation synced
          live to the order database.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10 items-start">
        {/* Left Column: Live Sync Badge + WhatsApp Phone Simulator */}
        <div className="lg:col-span-5 flex flex-col items-center space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-trust/30 bg-trust-soft px-4 py-1.5 text-xs font-semibold text-trust-text">
            <span
              className="h-2 w-2 rounded-full bg-trust animate-pulse motion-reduce:animate-none"
              aria-hidden="true"
            />
            <span>
              {isOrderLoading && !order
                ? `Syncing Order (#${activeOrderId})…`
                : `Database Synced (Order: #${order?.order_number || activeOrderId})`}
            </span>
          </div>

          <ErrorBoundary title="Phone simulator failed to render">
            <WhatsAppPhoneSimulator
              orderId={activeOrderId}
              customerName={customerName}
              streetAddress={streetAddress}
              addressQuality={addressQuality}
              onOrderUpdated={fetchLatestOrder}
              onSyncActivity={setSyncActivity}
            />
          </ErrorBoundary>
        </div>

        {/* Right Column: Order Context, Switcher, Timeline, and Live API Inspector */}
        <aside className="lg:col-span-7 space-y-6">
          <section className="rounded-2xl border border-line bg-surface p-6 space-y-5 shadow-card">
            <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-line">
              <div>
                <h2 className="font-display text-xl text-ink">Target Order &amp; Sync State</h2>
                <p className="text-xs text-ink-muted mt-0.5">
                  Actions persist via{" "}
                  <code className="font-mono text-ink">POST /v1/orders/{activeOrderId}/verify</code>
                </p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-brand-soft text-brand border border-brand/20">
                {order?.order_status || "Safe_For_Dispatch"}
              </span>
            </div>

            {recentOrders.length > 0 && (
              <div className="space-y-1.5">
                <label
                  htmlFor="simulator-order-select"
                  className="block text-xs font-semibold text-ink"
                >
                  Switch Simulated Order
                </label>
                <select
                  id="simulator-order-select"
                  value={activeOrderId}
                  onChange={(e) => {
                    router.push(`/simulator?order=${encodeURIComponent(e.target.value)}`);
                  }}
                  className="w-full min-h-[42px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-xs font-medium text-ink cursor-pointer"
                >
                  {!recentOrders.some((r) => r.id === activeOrderId) && (
                    <option value={activeOrderId}>{activeOrderId} (Current)</option>
                  )}
                  {recentOrders.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.order_number} — {r.customer_name} ({r.address_status}, {r.order_status})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="rounded-xl border border-line bg-subtle p-3.5">
                <dt className="text-[11px] text-ink-muted">Recipient</dt>
                <dd className="font-semibold text-ink mt-0.5">{customerName}</dd>
              </div>
              <div className="rounded-xl border border-line bg-subtle p-3.5">
                <dt className="text-[11px] text-ink-muted">Address Evaluation</dt>
                <dd className="font-semibold text-trust-text mt-0.5">
                  {order?.address_status || addressQuality}
                </dd>
              </div>
              <div className="sm:col-span-2 rounded-xl border border-line bg-subtle p-3.5">
                <dt className="text-[11px] text-ink-muted">Persisted Street Address</dt>
                <dd className="font-medium text-ink mt-0.5">{streetAddress}</dd>
              </div>
            </dl>

            {/* 5-Stage Lifecycle Timeline */}
            <ol className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1">
              {TIMELINE_STEPS.map((stage, idx) => {
                const done = idx < completedStages;
                return (
                  <li
                    key={stage.id}
                    className={cn(
                      "rounded-xl border p-2.5 text-center transition-colors",
                      done
                        ? "border-trust/35 bg-trust-soft/65 text-trust-text"
                        : "border-line bg-subtle text-ink-muted",
                    )}
                  >
                    <div className="flex justify-center mb-1">
                      <CheckCircle2
                        className={cn("w-4 h-4", done ? "text-trust" : "text-line-strong")}
                        aria-hidden="true"
                      />
                    </div>
                    <span className="block text-[11px] font-semibold leading-tight break-words">
                      {stage.label}
                    </span>
                  </li>
                );
              })}
            </ol>
          </section>

          {/* Live API Request / Response Inspector */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <section className="rounded-2xl border border-line bg-surface p-5 space-y-2.5 shadow-card">
              <h3 className="text-xs font-semibold text-ink flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-brand" aria-hidden="true" />
                <span>Last API Request Payload</span>
              </h3>
              <pre className="rounded-xl border border-line bg-subtle p-3.5 text-[11px] font-mono text-ink overflow-x-auto leading-relaxed">
                {syncActivity?.requestPayload
                  ? JSON.stringify(syncActivity.requestPayload, null, 2)
                  : "// Waiting for shopper opt-in reply"}
              </pre>
            </section>

            <section className="rounded-2xl border border-line bg-surface p-5 space-y-2.5 shadow-card">
              <h3 className="text-xs font-semibold text-ink">Last Synced Order JSON</h3>
              <pre className="rounded-xl border border-line bg-subtle p-3.5 text-[11px] font-mono text-ink overflow-x-auto leading-relaxed">
                {syncActivity?.responsePayload
                  ? JSON.stringify(syncActivity.responsePayload, null, 2)
                  : order
                    ? JSON.stringify(
                        {
                          id: order.id,
                          order_status: order.order_status,
                          address_status: order.address_status,
                          consent_status: order.consent_status,
                        },
                        null,
                        2,
                      )
                    : "// Database state appears here"}
              </pre>
            </section>
          </div>
        </aside>
      </div>
    </main>
  );
}

export default function SimulatorPage() {
  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />
      <Suspense fallback={<div className="p-12 text-center text-sm text-ink-muted">Loading simulator…</div>}>
        <SimulatorContent />
      </Suspense>
      <Footer />
    </div>
  );
}
