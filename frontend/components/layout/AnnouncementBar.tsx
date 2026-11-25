import React from "react";

const ANNOUNCEMENT_COPY =
  "Zero-Return Guarantee — Deterministic Fit-Twin sizing and ₹40 UPI Cashback on eligible orders";

export function AnnouncementBar() {
  return (
    <div
      role="region"
      aria-label="Storefront guarantee"
      className="bg-ink text-white text-[11px] sm:text-xs tracking-wide border-b border-ink/90"
    >
      <div className="flex items-center justify-center max-w-7xl mx-auto px-4 sm:px-6 py-2 text-center leading-snug">
        <p className="font-medium text-white/95">{ANNOUNCEMENT_COPY}</p>
      </div>
    </div>
  );
}
