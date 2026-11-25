"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Ruler } from "lucide-react";
import { formatIndianNumber } from "@/lib/format";
import { Button } from "@/components/ui/Button";
import { GarmentImage } from "@/components/ui/GarmentImage";

function useCountUp(target: number, inView: boolean): number {
  const [value, setValue] = useState(target);

  useEffect(() => {
    if (!inView) return;
    const prefersReduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced || target === 0) {
      setValue(target);
      return;
    }

    let frameId = 0;
    const durationMs = 650;
    const start = performance.now();

    const tick = (now: number): void => {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * eased));
      if (progress < 1) {
        frameId = window.requestAnimationFrame(tick);
      }
    };

    frameId = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(frameId);
  }, [target, inView]);

  return value;
}

export function HeroSection() {
  const metricsRef = useRef<HTMLDivElement | null>(null);
  const [metricsInView, setMetricsInView] = useState(false);

  useEffect(() => {
    const el = metricsRef.current;
    if (!el || typeof IntersectionObserver === "undefined") {
      setMetricsInView(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setMetricsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const avoidedRtos = useCountUp(273, metricsInView);
  const netMonthlySavings = useCountUp(28600, metricsInView);

  const handleScrollToSection = (id: string): void => {
    const target = document.getElementById(id);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-14 lg:pt-14 lg:pb-20">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 items-center">
        {/* Left: Editorial Display Typography + Actions */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
          className="md:col-span-6 space-y-6"
        >
          <p className="text-xs font-medium tracking-wide text-ink-muted">
            Autumn-Winter Craft Edit · Fit &amp; Delivery Assurance
          </p>

          <h1 className="font-display text-4xl sm:text-5xl lg:text-[3.5rem] leading-[1.06] tracking-tight text-ink max-w-[16ch]">
            D2C Fashion Engineered for Perfect First-Time Fit
          </h1>

          <p className="text-base sm:text-[17px] text-ink-muted leading-relaxed max-w-xl">
            Multimodal weave parsing meets deterministic body-zone ease physics, transparent
            margin-safe UPI offers, and pre-dispatch WhatsApp address verification.
          </p>

          <div className="flex flex-wrap items-center gap-3.5 pt-2">
            <Button variant="primary" size="lg" onClick={() => handleScrollToSection("catalog")}>
              Shop the Edit
            </Button>

            <Button
              variant="secondary"
              size="lg"
              onClick={() => handleScrollToSection("live-fit-atelier")}
            >
              <Ruler className="w-4 h-4 text-brand" aria-hidden="true" />
              <span>Test Fit-Twin Live</span>
            </Button>

            <Link
              href="/products/SKU-01"
              className="inline-flex items-center min-h-[44px] px-2 text-sm font-medium text-ink-muted hover:text-brand underline underline-offset-4 transition-colors"
            >
              Inspect Chanderi Kurta
            </Link>
          </div>

          <div ref={metricsRef} className="pt-6 border-t border-line grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="space-y-0.5">
              <p className="text-2xl font-semibold text-ink tabular-nums tracking-tight">
                {formatIndianNumber(avoidedRtos)}
              </p>
              <p className="text-xs font-medium text-brand">RTOs Avoided</p>
              <p className="text-[11px] text-ink-muted leading-snug">
                Monthly scenario (1,760 down to 1,487)
              </p>
            </div>

            <div className="space-y-0.5 sm:border-l sm:border-line sm:pl-5">
              <p className="text-2xl font-semibold text-ink tabular-nums tracking-tight">
                ₹{formatIndianNumber(netMonthlySavings)}
              </p>
              <p className="text-xs font-medium text-brand">Net Monthly Savings</p>
              <p className="text-[11px] text-ink-muted leading-snug">
                ₹54,600 gross less ₹26,000 incentives
              </p>
            </div>

            <div className="space-y-0.5 sm:border-l sm:border-line sm:pl-5">
              <p className="text-2xl font-semibold text-ink tabular-nums tracking-tight">0%</p>
              <p className="text-xs font-medium text-brand">Size Bracketing</p>
              <p className="text-[11px] text-ink-muted leading-snug">
                Single-size confidence, zero bracketing
              </p>
            </div>
          </div>

          <p className="text-[11px] text-ink-muted">
            Figures above model a 10,000-shipment monthly cohort before gateway fees. Live synthetic
            orders are audited separately in Merchant Command.
          </p>
        </motion.div>

        {/* Right: Single Monumental Atelier Campaign Frame */}
        <motion.div
          initial={{ opacity: 0, scale: 0.985 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.55, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
          className="md:col-span-6"
        >
          <div className="relative rounded-2xl overflow-hidden border border-line bg-surface shadow-lift">
            <Link href="/products/SKU-01" className="group block">
              <GarmentImage
                src="/images/hero-editorial.jpg"
                alt="Handcrafted Chanderi Silk Anarkali Kurta with antique gold zari trim photographed in sunlit limestone atelier"
                garmentName="Handcrafted Chanderi Silk Anarkali Kurta"
                priority
                hoverZoom
                className="aspect-[4/5] w-full"
              />
            </Link>

            <div className="absolute inset-x-4 bottom-4 rounded-xl border border-surface/35 bg-ink/85 backdrop-blur-md text-canvas p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-0.5 min-w-0">
                <p className="text-[11px] text-canvas/75">Featured Piece · Rigid 180 GSM Silk</p>
                <p className="font-display text-base text-canvas truncate">
                  Handcrafted Chanderi Silk Anarkali Kurta
                </p>
                <p className="text-xs text-canvas/85">
                  Zara M shoppers match Size L (+0.5&quot; shoulder clearance)
                </p>
              </div>
              <Link
                href="/products/SKU-01"
                className="inline-flex items-center justify-center min-h-[38px] px-4 rounded-full bg-surface text-ink text-xs font-semibold hover:bg-brand-soft transition-colors whitespace-nowrap shrink-0"
              >
                Inspect Piece
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
