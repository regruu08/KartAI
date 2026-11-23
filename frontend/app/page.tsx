import React from "react";
import { Sparkles, ShieldCheck, MessageSquare, BarChart3, CheckCircle2 } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-canvas text-ink px-4 py-12 md:py-20 flex flex-col items-center justify-center">
      <div className="max-w-4xl w-full mx-auto space-y-8">
        {/* Header Badge */}
        <div className="flex items-center justify-center">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-surface border border-border text-brand shadow-sm">
            <CheckCircle2 className="w-3.5 h-3.5 text-accentEmerald" />
            Phase 0 Operational · Monorepo Scaffolding
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-ink">
            ReturnZero <span className="text-brand">AI</span>
          </h1>
          <p className="text-base md:text-lg text-inkMuted max-w-2xl mx-auto">
            Fit Intelligence &amp; Delivery Assurance Layer for D2C Fashion Apparel.
            Built for KartAI x CodeXcelerate Buildathon 2026.
          </p>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-surface rounded-bento border border-border p-6 shadow-bento space-y-3">
            <div className="w-10 h-10 rounded-lg bg-canvas flex items-center justify-center text-brand">
              <Sparkles className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-ink">1. Fit Intelligence</h2>
            <p className="text-sm text-inkMuted">
              Deterministic size recommendation from brand conversion matrices with
              transparent confidence bands and merchant data gap reporting.
            </p>
          </div>

          <div className="bg-surface rounded-bento border border-border p-6 shadow-bento space-y-3">
            <div className="w-10 h-10 rounded-lg bg-canvas flex items-center justify-center text-brand">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-ink">2. Checkout Shield</h2>
            <p className="text-sm text-inkMuted">
              Explainable risk evaluation and closed-form margin-safe UPI incentive solver.
              Cash on Delivery remains 100% available without dark patterns.
            </p>
          </div>

          <div className="bg-surface rounded-bento border border-border p-6 shadow-bento space-y-3">
            <div className="w-10 h-10 rounded-lg bg-canvas flex items-center justify-center text-brand">
              <MessageSquare className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-ink">3. Delivery Assurance</h2>
            <p className="text-sm text-inkMuted">
              In-browser delivery simulator for address clarification, landmark enrichment,
              and non-delivery reschedule recovery.
            </p>
          </div>

          <div className="bg-surface rounded-bento border border-border p-6 shadow-bento space-y-3">
            <div className="w-10 h-10 rounded-lg bg-canvas flex items-center justify-center text-brand">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-ink">4. Merchant Command Center</h2>
            <p className="text-sm text-inkMuted">
              Dual-panel merchant dashboard separating live synthetic telemetry from an
              interactive 10,000-shipment financial scenario modeler.
            </p>
          </div>
        </div>

        {/* Footer info */}
        <div className="text-center text-xs text-inkMuted pt-4 border-t border-borderLight">
          Team BioXtreme · Code to Cart Round 2 Buildathon · November 2026
        </div>
      </div>
    </main>
  );
}
