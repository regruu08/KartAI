"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
  ShoppingBag,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import type { SkuResponse } from "@/lib/api/types";
import {
  ALL_SIZES,
  FALLBACK_CATALOG_SKUS,
  getSkuDisplayMeta,
  isSizeStocked,
  type SizeLabel,
} from "@/lib/catalog";
import { formatInr } from "@/lib/format";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/cn";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { GarmentImage } from "@/components/ui/GarmentImage";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { RadioChipGroup, type RadioChipOption } from "@/components/ui/RadioChipGroup";
import { FitDrawer } from "@/components/fit-twin/FitDrawer";
import { CatalogIntelligencePanel } from "@/components/fit-twin/CatalogIntelligencePanel";

type GalleryView = "full" | "macro" | "lower";

const GALLERY_VIEWS: readonly { id: GalleryView; label: string }[] = [
  { id: "full", label: "Lookbook" },
  { id: "macro", label: "Textile Macro" },
  { id: "lower", label: "Silhouette & Hem" },
];

export default function ProductDetailPage() {
  const params = useParams();
  const rawId = (params?.skuId as string) ?? "SKU-01";
  const skuId = rawId.toUpperCase();

  const [sku, setSku] = useState<SkuResponse | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [selectedSize, setSelectedSize] = useState<SizeLabel>("M");
  const [activeView, setActiveView] = useState<GalleryView>("full");
  const [addedToast, setAddedToast] = useState(false);
  const [bracketingWarning, setBracketingWarning] = useState(false);

  const { openFitDrawer, fitBySku, fitInputsBySku, cart, addToCart } = useStore();
  const scopedFit = fitBySku[skuId];
  const scopedInput = fitInputsBySku[skuId];

  useEffect(() => {
    setNotFound(false);
    setActiveView("full");
    setAddedToast(false);

    const controller = new AbortController();
    api
      .getSku(skuId, controller.signal)
      .then((data) => {
        setSku(data);
        setNotFound(false);
      })
      .catch(() => {
        if (controller.signal.aborted) return;
        const fallback = FALLBACK_CATALOG_SKUS.find((s) => s.id === skuId);
        if (fallback) {
          setSku(fallback);
          setNotFound(false);
        } else {
          setNotFound(true);
          setSku(null);
        }
      });

    return () => controller.abort();
  }, [skuId]);

  useEffect(() => {
    if (scopedFit?.recommended_size) {
      setSelectedSize(scopedFit.recommended_size as SizeLabel);
    }
  }, [scopedFit]);

  if (notFound) {
    return (
      <div className="min-h-screen bg-canvas text-ink flex flex-col">
        <AnnouncementBar />
        <Navbar />
        <main
          id="main-content"
          className="max-w-3xl mx-auto px-4 py-20 flex-1 flex flex-col items-center justify-center text-center"
        >
          <div className="p-4 bg-brand-soft text-brand rounded-full mb-4">
            <AlertCircle className="w-8 h-8" aria-hidden="true" />
          </div>
          <h1 className="font-display text-3xl text-ink mb-2">Product Not Found</h1>
          <p className="text-sm text-ink-muted max-w-md mb-6 leading-relaxed">
            We could not find the garment catalog entry for{" "}
            <span className="font-mono font-semibold text-ink">{skuId}</span>. It may have been
            retired or does not exist.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-brand text-white text-sm font-semibold hover:bg-brandHover transition-colors shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            <span>Back to Storefront</span>
          </Link>
        </main>
        <Footer />
      </div>
    );
  }

  if (!sku) {
    return (
      <div className="min-h-screen bg-canvas text-ink flex flex-col">
        <AnnouncementBar />
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  const meta = getSkuDisplayMeta(sku);
  const sizeOptions: RadioChipOption<SizeLabel>[] = ALL_SIZES.map((size) => {
    const stocked = isSizeStocked(sku, size);
    return {
      value: size,
      label: size,
      disabled: !stocked,
      tooltip: stocked ? `Select size ${size}` : "Not stocked for this garment",
    };
  });

  const isFitMatch = Boolean(scopedFit && selectedSize === scopedFit.recommended_size);
  const isFitMismatch = Boolean(scopedFit && selectedSize !== scopedFit.recommended_size);

  const handleAddToCart = () => {
    const existingSameSkuOtherSize = cart.some(
      (item) => item.sku.id === sku.id && item.size !== selectedSize,
    );
    setBracketingWarning(existingSameSkuOtherSize);

    addToCart({
      sku,
      size: selectedSize,
      quantity: 1,
      fitVerified: Boolean(scopedFit),
      knownBrand: scopedInput?.brand,
      knownSize: scopedInput?.size,
      fitPreference: scopedInput?.preference,
    });
    setAddedToast(true);
    toast.success(`Added ${sku.name} (Size ${selectedSize}) to bag`);
    setTimeout(() => setAddedToast(false), 4000);
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />

      <main
        id="main-content"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 pb-28 lg:pb-16 flex-1 w-full"
      >
        {/* Editorial Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex flex-wrap items-center gap-1.5 text-xs text-ink-muted">
            <li>
              <Link href="/" className="hover:text-ink transition-colors">
                Storefront
              </Link>
            </li>
            <li aria-hidden="true">
              <ChevronRight className="w-3.5 h-3.5" />
            </li>
            <li>{sku.category}</li>
            <li aria-hidden="true">
              <ChevronRight className="w-3.5 h-3.5" />
            </li>
            <li
              aria-current="page"
              className="text-ink font-medium truncate max-w-[240px] sm:max-w-none"
            >
              {sku.name}
            </li>
          </ol>
        </nav>

        {/* Editorial Split (7/5 across md+ and lg+) */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12 items-start">
          {/* Left: Garment Plate + 3 Detail Thumbnails */}
          <div className="md:col-span-7 space-y-4">
            <div className="group relative rounded-2xl border border-line bg-surface overflow-hidden shadow-card">
              <GarmentImage
                src={activeView === "macro" ? meta.detailImage : meta.image}
                alt={
                  activeView === "macro"
                    ? meta.detailAlt
                    : `${meta.imageAlt} — ${GALLERY_VIEWS.find((v) => v.id === activeView)?.label ?? "Lookbook"}`
                }
                garmentName={sku.name}
                cropMode={activeView === "lower" ? "lower" : "full"}
                hoverZoom={activeView === "full"}
                priority
                className="aspect-[3/4] w-full"
              />
              <div className="absolute top-4 left-4">
                <Badge variant="brand">{sku.id}</Badge>
              </div>
              <div className="absolute top-4 right-4">
                <ProvenanceBadge provenance={sku.provenance} className="bg-surface/95 backdrop-blur-md" />
              </div>
            </div>

            <div
              role="group"
              aria-label="Garment angle views"
              className="grid grid-cols-3 gap-3 sm:gap-4"
            >
              {GALLERY_VIEWS.map((view) => {
                const active = activeView === view.id;
                return (
                  <button
                    key={view.id}
                    type="button"
                    aria-pressed={active}
                    onClick={() => setActiveView(view.id)}
                    className={cn(
                      "rounded-xl overflow-hidden border bg-surface text-left transition-all cursor-pointer",
                      active ? "border-brand ring-1 ring-brand/40 shadow-sm" : "border-line hover:border-line-strong",
                    )}
                  >
                    <GarmentImage
                      src={view.id === "macro" ? meta.detailImage : meta.image}
                      alt={`${sku.name} — ${view.label}`}
                      garmentName={sku.name}
                      cropMode={view.id === "lower" ? "lower" : "full"}
                      className="aspect-[4/3] w-full"
                    />
                    <span
                      className={cn(
                        "block px-3 py-2 text-xs font-medium text-center",
                        active ? "text-brand bg-brand-soft/40" : "text-ink-muted",
                      )}
                    >
                      {view.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right: Sticky Purchase Module */}
          <div className="md:col-span-5 md:sticky md:top-24 space-y-6">
            <div className="space-y-2.5">
              <p className="text-xs font-medium text-ink-muted">{sku.category}</p>
              <h1 className="font-display text-3xl sm:text-4xl text-ink leading-tight">
                {sku.name}
              </h1>
              <p className="text-2xl font-semibold text-ink tabular-nums">
                {formatInr(sku.price_inr)}
                <span className="ml-2 text-xs font-normal text-ink-muted">
                  Inclusive of all taxes
                </span>
              </p>

              <div className="flex flex-wrap items-center gap-2 pt-1">
                <span className="inline-flex items-center rounded-lg border border-line-strong bg-subtle px-2.5 py-1 text-xs font-medium text-ink">
                  {sku.fabric_composition}
                </span>
                <span
                  className={cn(
                    "inline-flex items-center rounded-lg border px-2.5 py-1 text-xs font-medium",
                    sku.fabric_stretch === "non_stretch"
                      ? "bg-warn-soft border-warn/35 text-warn-text"
                      : "bg-trust-soft border-trust/25 text-trust-text",
                  )}
                >
                  {meta.stretchNote}
                </span>
              </div>
            </div>

            {/* Scoped Fit-Twin Verification Banner */}
            <div aria-live="polite">
              {isFitMatch && scopedFit && (
                <div className="rounded-2xl border border-trust/35 bg-trust-soft px-4 py-3.5 flex items-center justify-between gap-3">
                  <div className="flex items-start gap-2.5 min-w-0">
                    <CheckCircle2 className="w-4 h-4 text-trust shrink-0 mt-0.5" aria-hidden="true" />
                    <p className="text-xs sm:text-sm font-medium text-trust-text leading-snug">
                      Fit-Twin Verified: <strong>Size {scopedFit.recommended_size}</strong> (
                      {scopedFit.confidence_level} Confidence)
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={openFitDrawer}
                    className="text-xs font-semibold text-trust-text underline underline-offset-4 whitespace-nowrap shrink-0 cursor-pointer"
                  >
                    Adjust
                  </button>
                </div>
              )}

              {isFitMismatch && scopedFit && (
                <div className="rounded-2xl border border-warn/40 bg-warn-soft px-4 py-3.5 flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-start gap-2.5">
                    <AlertTriangle className="w-4 h-4 text-warn shrink-0 mt-0.5" aria-hidden="true" />
                    <p className="text-xs sm:text-sm font-medium text-warn-text leading-snug">
                      Fit-Twin recommended Size {scopedFit.recommended_size}; you selected Size{" "}
                      {selectedSize}.
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedSize(scopedFit.recommended_size as SizeLabel)}
                  >
                    Switch to {scopedFit.recommended_size}
                  </Button>
                </div>
              )}
            </div>

            {/* Size Selection */}
            <div className="rounded-2xl border border-line bg-surface p-5 space-y-4 shadow-card">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-sm font-semibold text-ink">Select Garment Size</span>
                {!sku.has_sleeve && (
                  <span className="inline-flex items-center gap-1.5 rounded-lg border border-warn/35 bg-warn-soft px-2.5 py-1 text-xs font-medium text-warn-text">
                    <AlertTriangle className="w-3.5 h-3.5 text-warn shrink-0" aria-hidden="true" />
                    Data Gap: Missing Sleeve Dimensions
                  </span>
                )}
              </div>

              <RadioChipGroup
                ariaLabel="Select Garment Size"
                options={sizeOptions}
                value={selectedSize}
                onChange={(size) => {
                  setSelectedSize(size);
                  setAddedToast(false);
                }}
                layout="grid-6"
              />

              <div className="flex flex-col sm:flex-row gap-3 pt-1">
                <Button
                  type="button"
                  variant={isFitMatch ? "outline" : "primary"}
                  size="lg"
                  onClick={openFitDrawer}
                  className="flex-1"
                >
                  <Sparkles className="w-4 h-4" aria-hidden="true" />
                  <span>{isFitMatch ? "Re-check Fit" : "Check My Fit"}</span>
                </Button>

                <Button
                  type="button"
                  variant={isFitMatch ? "primary" : "outline"}
                  size="lg"
                  onClick={handleAddToCart}
                  className="flex-1"
                >
                  <ShoppingBag className="w-4 h-4" aria-hidden="true" />
                  <span>
                    {isFitMatch
                      ? `Add Size ${selectedSize} (Fit Verified)`
                      : `Add Size ${selectedSize} to Cart`}
                  </span>
                </Button>
              </div>

              {addedToast && (
                <Link
                  href="/checkout"
                  className="w-full inline-flex items-center justify-center gap-2 min-h-[46px] px-6 rounded-full bg-trust text-white text-sm font-semibold hover:bg-trust-text transition-colors"
                >
                  <span>Proceed to Checkout</span>
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </Link>
              )}

              {bracketingWarning && (
                <div className="p-3 rounded-xl bg-warn-soft border border-warn/35 text-warn-text text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-warn shrink-0 mt-0.5" aria-hidden="true" />
                  <div>
                    <strong className="block">Multi-Size Cart Detected (Bracketing)</strong>
                    You have multiple sizes of this garment in your bag. Selecting one verified
                    size helps keep return rates near zero.
                  </div>
                </div>
              )}
            </div>

            {/* Catalog Intelligence Accordion */}
            <ErrorBoundary title="Catalog Intelligence panel unavailable">
              <CatalogIntelligencePanel
                sku={sku}
                selectedSize={selectedSize}
                recommendedSize={scopedFit?.recommended_size ?? null}
                onSkuUpdated={setSku}
              />
            </ErrorBoundary>
          </div>
        </div>
      </main>

      {/* Mobile Sticky Purchase Bar */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-30 border-t border-line bg-surface/95 backdrop-blur-md px-4 py-2.5 shadow-lift">
        <div className="flex items-center gap-2.5 max-w-lg mx-auto">
          <Button type="button" variant="outline" size="sm" onClick={openFitDrawer}>
            Check My Fit
          </Button>
          <Button type="button" variant="primary" size="sm" fullWidth onClick={handleAddToCart}>
            Add Size {selectedSize} ({formatInr(sku.price_inr)})
          </Button>
        </div>
      </div>

      <Footer />

      <ErrorBoundary title="Fit drawer encountered an error">
        <FitDrawer sku={sku} />
      </ErrorBoundary>
    </div>
  );
}
