"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  LayoutDashboard,
  MessageSquare,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api/client";
import type { OrderResponse } from "@/lib/api/types";
import { formatInr } from "@/lib/format";
import { useStore } from "@/lib/store";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";

export default function OrderConfirmationPage() {
  const params = useParams();
  const orderId = (params?.orderId as string) ?? "RZ-1042";

  const { placedOrder } = useStore();
  const matchingCached = placedOrder?.id === orderId ? placedOrder : null;
  const [order, setOrder] = useState<OrderResponse | null>(matchingCached);
  const [isLoading, setIsLoading] = useState(!matchingCached);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (matchingCached) {
      setOrder(matchingCached);
      setIsLoading(false);
      setIsError(false);
      return;
    }

    if (!orderId) return;
    let active = true;
    setIsLoading(true);
    setIsError(false);

    api
      .getOrder(orderId)
      .then((data) => {
        if (!active) return;
        setOrder(data);
        setIsError(false);
      })
      .catch(() => {
        if (!active) return;
        setIsError(true);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [matchingCached, orderId]);

  const isPrepaid = order?.payment_method?.toUpperCase() === "PREPAID";

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />

      <main
        id="main-content"
        className="max-w-2xl mx-auto px-4 sm:px-6 py-12 lg:py-16 flex-1 w-full space-y-6"
      >
        <div className="text-center space-y-3">
          <div className="w-16 h-16 rounded-full bg-trust-soft text-trust flex items-center justify-center mx-auto shadow-sm">
            {isError ? (
              <AlertCircle className="w-8 h-8 text-warn" aria-hidden="true" />
            ) : (
              <CheckCircle2 className="w-9 h-9" aria-hidden="true" />
            )}
          </div>
          <p className="text-xs font-semibold text-trust-text">
            {isError ? "Order Lookup" : "Order Successfully Placed"}
          </p>
          <h1 className="font-display text-3xl sm:text-4xl text-ink">
            {isError
              ? "Order reference not found in current session"
              : "Thank you for shopping with ReturnZero"}
          </h1>
          <p className="text-xs sm:text-sm text-ink-muted font-mono">
            Order Reference: <strong className="text-ink">{order?.order_number || orderId}</strong>
          </p>
        </div>

        <section className="rounded-2xl border border-line bg-surface p-6 space-y-4 shadow-card text-xs">
          <div className="flex items-center justify-between pb-3 border-b border-line">
            <span className="font-semibold text-ink">Delivery Status</span>
            <span className="px-3 py-1 rounded-full text-[11px] font-semibold bg-brand-soft text-brand border border-brand/20">
              {order?.order_status ?? (isLoading ? "Syncing..." : isError ? "Not Found" : "Placed")}
            </span>
          </div>

          {isError && (
            <div className="rounded-xl border border-warn/35 bg-warn-soft p-3 text-warn-text">
              We could not locate order <span className="font-mono font-semibold">{orderId}</span> in
              the database. If you just reset demo data, pick any order from the Merchant Command
              Center.
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <span className="text-[11px] text-ink-muted block">Recipient</span>
              <span className="font-semibold text-ink mt-0.5 block">
                {order?.customer_name ?? (isLoading ? "Loading..." : "Unavailable")}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-ink-muted block">Payment Method</span>
              <span className="font-semibold text-ink flex items-center gap-1 mt-0.5">
                {order?.payment_method ?? (isLoading ? "Loading..." : "COD")}
                {isPrepaid && <Zap className="w-3.5 h-3.5 text-warn" aria-hidden="true" />}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-ink-muted block">Total Payable</span>
              <span className="font-semibold text-ink tabular-nums mt-0.5 block">
                {order ? formatInr(order.total_inr) : isLoading ? "Loading..." : "—"}
              </span>
            </div>
            <div className="sm:col-span-3 pt-2 border-t border-line">
              <span className="text-[11px] text-ink-muted block">Destination Address</span>
              <span className="font-medium text-ink mt-0.5 block">
                {order
                  ? [order.street_address, order.city, order.state, order.pin_code]
                      .filter(Boolean)
                      .join(", ")
                  : isLoading
                    ? "Loading..."
                    : "Address unavailable"}
              </span>
            </div>
          </div>
        </section>

        <section className="p-6 rounded-2xl border border-brand/30 bg-surface shadow-card space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-trust-soft text-trust flex items-center justify-center shrink-0">
              <MessageSquare className="w-5 h-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="font-display text-lg text-ink">
                Complete Delivery Assurance (Simulated)
              </h2>
              <p className="text-xs text-ink-muted mt-1 leading-relaxed">
                Confirm your landmark and delivery slot in our in-browser WhatsApp simulator to
                promote your shipment to <strong className="text-ink">Safe_For_Dispatch</strong>.
              </p>
            </div>
          </div>

          <Link
            href={`/simulator?order=${encodeURIComponent(order?.id || orderId)}`}
            className="w-full inline-flex items-center justify-center gap-2 min-h-[48px] px-6 rounded-full text-sm font-semibold bg-[#075E54] hover:bg-[#054a42] text-white shadow-sm transition-colors"
          >
            <span>Open WhatsApp Simulator</span>
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </Link>
        </section>

        <div className="flex flex-wrap items-center justify-center gap-5 text-xs font-semibold pt-2">
          <Link href="/" className="text-ink-muted hover:text-ink transition-colors">
            Back to Storefront
          </Link>
          <Link
            href="/dashboard"
            className="text-brand hover:text-brandHover inline-flex items-center gap-1.5"
          >
            <LayoutDashboard className="w-3.5 h-3.5" aria-hidden="true" />
            <span>View Merchant Command Center</span>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
