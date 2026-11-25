import React from "react";
import Link from "next/link";
import { MessageCircle, ShieldCheck } from "lucide-react";

export function TrustBento() {
  return (
    <section
      aria-labelledby="architecture-heading"
      className="bg-ink text-canvas mt-8 border-t border-line"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24 space-y-12">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 border-b border-surface/15 pb-8">
          <div className="space-y-2 max-w-2xl">
            <p className="text-xs font-medium text-brand-soft">Commerce Risk &amp; Delivery Backbone</p>
            <h2 id="architecture-heading" className="font-display text-3xl sm:text-4xl text-canvas">
              Engineered from Weave to Doorstep
            </h2>
          </div>
          <p className="text-sm text-canvas/75 max-w-md leading-relaxed">
            Fit verification solves sizing returns. Our checkout shield and pre-dispatch WhatsApp
            assurance eliminate courier RTO losses before parcels leave the warehouse.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
          {/* Obsidian Panel 1: Checkout Shield */}
          <article className="lg:col-span-6 rounded-2xl border border-surface/15 bg-surface/5 p-6 sm:p-8 flex flex-col justify-between gap-6">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-trust/20 text-trust-soft flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" aria-hidden="true" />
              </div>
              <h3 className="font-display text-2xl text-canvas">Transparent Checkout Shield</h3>
              <p className="text-sm text-canvas/75 leading-relaxed">
                Every order undergoes a 3-point PIN serviceability, landmark density, and risk-tier
                audit. Cash on Delivery always remains accessible—zero forced blocks or countdown
                dark patterns.
              </p>
            </div>

            <div className="rounded-xl border border-surface/15 bg-ink/70 p-4 space-y-2.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-canvas/70">Avoided Courier RTO Delta</span>
                <span className="font-mono font-semibold text-canvas tabular-nums">₹48.00</span>
              </div>
              <div className="flex items-center justify-between border-t border-surface/10 pt-2">
                <span className="text-canvas/70">Protected Margin Floor</span>
                <span className="font-mono font-semibold text-canvas tabular-nums">−₹8.00</span>
              </div>
              <div className="flex items-center justify-between border-t border-surface/10 pt-2">
                <span className="text-canvas/85 font-medium">Margin-Safe UPI Savings Cap</span>
                <span className="font-mono font-semibold text-trust-soft tabular-nums">
                  ₹40.00 Eligible
                </span>
              </div>
            </div>

            <div>
              <Link
                href="/checkout"
                className="inline-flex items-center min-h-[40px] px-5 rounded-full bg-surface text-ink text-xs font-semibold hover:bg-brand-soft transition-colors"
              >
                Inspect Checkout Shield
              </Link>
            </div>
          </article>

          {/* Obsidian Panel 2: Pre-Dispatch Delivery Assurance */}
          <article className="lg:col-span-6 rounded-2xl border border-surface/15 bg-surface/5 p-6 sm:p-8 flex flex-col justify-between gap-6">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-brand/30 text-brand-soft flex items-center justify-center">
                <MessageCircle className="w-5 h-5" aria-hidden="true" />
              </div>
              <h3 className="font-display text-2xl text-canvas">Consent-Based Delivery Assurance</h3>
              <p className="text-sm text-canvas/75 leading-relaxed">
                Incomplete addresses trigger an opt-in WhatsApp clarification flow that captures exact
                gate landmarks and buyer time-windows before courier handoff.
              </p>
            </div>

            <div className="rounded-xl border border-surface/15 bg-ink/70 p-4 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-canvas/70">1. Shopper Opt-In Consent</span>
                <span className="text-trust-soft font-semibold">YES_CONFIRMED</span>
              </div>
              <div className="flex items-center justify-between border-t border-surface/10 pt-2">
                <span className="text-canvas/70">2. Address Normalisation</span>
                <span className="text-canvas font-mono">Near Metro Pillar 120</span>
              </div>
              <div className="flex items-center justify-between border-t border-surface/10 pt-2">
                <span className="text-canvas/70">3. Dispatch Readiness</span>
                <span className="px-2 py-0.5 rounded-md bg-trust/25 text-trust-soft font-mono font-semibold">
                  Safe_For_Dispatch
                </span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/simulator"
                className="inline-flex items-center min-h-[40px] px-5 rounded-full bg-brand text-white text-xs font-semibold hover:bg-brand-hover transition-colors"
              >
                Launch Delivery Simulator
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center min-h-[40px] px-4 rounded-full border border-surface/25 text-canvas/90 text-xs font-medium hover:bg-surface/10 transition-colors"
              >
                View Live Analytics
              </Link>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
