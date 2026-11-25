import React from "react";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-line bg-surface mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-14">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-8">
          <div className="space-y-3">
            <Link href="/" className="font-display text-xl text-ink inline-block">
              ReturnZero <span className="text-brand font-semibold">AI</span>
            </Link>
            <h2 className="text-xs font-semibold text-ink">Brand Philosophy</h2>
            <p className="text-sm text-ink-muted leading-relaxed">
              Crafted apparel deserves to arrive once and fit right the first time. We pair Indian
              handlooms and natural fibres with deterministic sizing physics so shoppers never
              resort to multi-size bracketing.
            </p>
          </div>

          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-ink">Sizing Architecture</h2>
            <p className="text-sm text-ink-muted leading-relaxed">
              Every garment is audited for weave stretch, GSM weight, and zone ease tolerances
              before dispatch—no body scans required.
            </p>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/products/SKU-01"
                  className="text-ink hover:text-brand transition-colors"
                >
                  Explore Chanderi Silk Fit Engine
                </Link>
              </li>
              <li>
                <Link
                  href="/products/SKU-03"
                  className="text-ink hover:text-brand transition-colors"
                >
                  Inspect Catalog Data-Gap Handling
                </Link>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-ink">Shipping &amp; RTO Policy</h2>
            <p className="text-sm text-ink-muted leading-relaxed">
              Every order runs a 3-point address, PIN serviceability, and courier RTO check.
              Eligible COD orders receive a transparent, margin-safe UPI savings offer without
              dark patterns.
            </p>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/checkout" className="text-ink hover:text-brand transition-colors">
                  Checkout Shield Preview
                </Link>
              </li>
              <li>
                <Link href="/simulator" className="text-ink hover:text-brand transition-colors">
                  WhatsApp Delivery Assurance
                </Link>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h2 className="text-xs font-semibold text-ink">Team BioXtreme</h2>
            <p className="text-sm text-ink-muted leading-relaxed">
              Built for Code to Cart Hackathon. Unifying deterministic fit verification, checkout
              risk clarity, and pre-dispatch WhatsApp confirmation.
            </p>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/dashboard" className="text-ink hover:text-brand transition-colors">
                  Merchant Command Center
                </Link>
              </li>
              <li>
                <Link href="/" className="text-ink hover:text-brand transition-colors">
                  Browse the Curated Edit
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-line flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs text-ink-muted">
          <p>ReturnZero AI — Team BioXtreme</p>
          <p>Deterministic Fit Physics, Transparent Checkout Shield &amp; Synthetic Demo Telemetry</p>
        </div>
      </div>
    </footer>
  );
}
