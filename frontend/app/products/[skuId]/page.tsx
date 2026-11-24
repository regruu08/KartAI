"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Sparkles, ShoppingBag, ArrowLeft, Check, AlertCircle } from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { FitDrawer } from "@/components/fit-twin/FitDrawer";
import { CatalogIntelligencePanel } from "@/components/fit-twin/CatalogIntelligencePanel";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import type { SkuResponse } from "@/lib/api/types";

// Curated fallbacks for instant initial render
const CURATED_DETAILS: Record<string, Partial<SkuResponse> & { image_url: string; description: string }> = {
  "SKU-01": {
    id: "SKU-01",
    name: "Handcrafted Chanderi Silk Anarkali Kurta",
    category: "Ethnic Apparel",
    price_inr: 2499,
    fabric_stretch: "non_stretch",
    fabric_composition: "100% Chanderi Silk · 70 GSM",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 48.0,
    sizes_json: {
      S: { chest: 36.0, waist: 32.0, shoulder: 14.5, length: 46.0 },
      M: { chest: 38.0, waist: 34.0, shoulder: 15.5, length: 47.0 },
      L: { chest: 40.0, waist: 36.0, shoulder: 17.0, length: 48.0 },
      XL: { chest: 42.0, waist: 38.0, shoulder: 18.0, length: 49.0 },
    },
    provenance: "live_gemini",
    image_url: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80",
    description: "Handwoven in Madhya Pradesh with gold zari border. Rigid zero-stretch weave requiring exact bust ease calibration.",
  },
  "SKU-02": {
    id: "SKU-02",
    name: "Relaxed Mandarin Collar Linen Shirt",
    category: "Men's Casuals",
    price_inr: 1899,
    fabric_stretch: "slight_stretch",
    fabric_composition: "100% European Flax Linen · 140 GSM",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 29.0,
    sizes_json: {
      S: { chest: 38.0, waist: 36.0, shoulder: 16.5, length: 28.0 },
      M: { chest: 40.0, waist: 38.0, shoulder: 17.5, length: 29.0 },
      L: { chest: 42.0, waist: 40.0, shoulder: 18.5, length: 30.0 },
      XL: { chest: 44.0, waist: 42.0, shoulder: 19.5, length: 31.0 },
    },
    provenance: "cached",
    image_url: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80",
    description: "Tailored from French flax yarn. Breathable weave with 1.5% natural ease stretch for all-day comfort.",
  },
  "SKU-03": {
    id: "SKU-03",
    name: "Raw Indigo Denim Trucker Jacket",
    category: "Outerwear",
    price_inr: 3299,
    fabric_stretch: "non_stretch",
    fabric_composition: "100% Heavyweight Cotton Denim · 13.5 oz",
    has_shoulder: true,
    has_sleeve: false, // Intentionally missing sleeve measurement (ADR-004, ADR-013)
    length_inches: 26.0,
    sizes_json: {
      S: { chest: 40.0, waist: 38.0, shoulder: 17.0, length: 25.0 },
      M: { chest: 42.0, waist: 40.0, shoulder: 18.0, length: 26.0 },
      L: { chest: 44.0, waist: 42.0, shoulder: 19.0, length: 27.0 },
      XL: { chest: 46.0, waist: 44.0, shoulder: 20.0, length: 28.0 },
    },
    provenance: "manual_fixture",
    image_url: "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80",
    description: "Rugged sanforized raw denim. Sizing engine flags missing sleeve length and safely alerts shoppers.",
  },
  "SKU-04": {
    id: "SKU-04",
    name: "Flowy Floral Rayon Tiered Maxi Dress",
    category: "Women's Western",
    price_inr: 2199,
    fabric_stretch: "slight_stretch",
    fabric_composition: "100% Viscose Rayon Crepe · 110 GSM",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 53.0,
    sizes_json: {
      S: { chest: 34.0, waist: 26.0, shoulder: 14.0, length: 52.0 },
      M: { chest: 36.0, waist: 28.0, shoulder: 15.0, length: 53.0 },
      L: { chest: 38.0, waist: 30.0, shoulder: 16.0, length: 54.0 },
      XL: { chest: 40.0, waist: 32.0, shoulder: 17.0, length: 55.0 },
    },
    provenance: "cached",
    image_url: "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80",
    description: "Floor-length silhouette with smocked bodice and tiered hem. Lightweight drape with generous hip allowance.",
  },
};

export default function ProductDetailPage() {
  const params = useParams();
  const rawId = (params?.skuId as string) ?? "SKU-01";
  const skuId = rawId.toUpperCase();

  const [sku, setSku] = useState<SkuResponse | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [selectedSize, setSelectedSize] = useState<string>("M");
  const [addedToast, setAddedToast] = useState(false);
  const [bracketingWarning, setBracketingWarning] = useState(false);

  const { openFitDrawer, fitResult, cart, addToCart } = useStore();

  useEffect(() => {
    setNotFound(false);
    api
      .getSku(skuId)
      .then((data) => {
        setSku(data);
        setNotFound(false);
      })
      .catch(() => {
        // Only fall back if it is one of the known curated SKUs
        if (CURATED_DETAILS[skuId]) {
          setSku(CURATED_DETAILS[skuId] as SkuResponse);
          setNotFound(false);
        } else {
          setNotFound(true);
          setSku(null);
        }
      });
  }, [skuId]);

  // Synchronize recommended size if user computed fit
  useEffect(() => {
    if (fitResult?.recommended_size) {
      setSelectedSize(fitResult.recommended_size);
    }
  }, [fitResult]);

  if (notFound) {
    return (
      <div className="min-h-screen bg-canvas text-ink flex flex-col">
        <Navbar />
        <main className="max-w-4xl mx-auto px-4 py-16 flex-1 flex flex-col items-center justify-center text-center">
          <div className="p-4 bg-brand/10 text-brand rounded-full mb-4">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-ink mb-2">Product Not Found</h1>
          <p className="text-sm text-inkMuted max-w-md mb-6">
            We could not find the garment catalog entry for{" "}
            <span className="font-mono font-bold text-ink">{skuId}</span>. It may
            have been retired or does not exist.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-brand text-white text-sm font-semibold hover:bg-brandHover transition-colors shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Storefront
          </Link>
        </main>
      </div>
    );
  }

  if (!sku) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-brand border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const fallbackMeta = CURATED_DETAILS[sku.id] ?? CURATED_DETAILS["SKU-01"]!;
  const availableSizes = sku.sizes_json ? Object.keys(sku.sizes_json) : ["S", "M", "L", "XL"];

  const handleAddToCart = () => {
    // Check bracketing suppression per BUILD_PLAN Phase 4 (E12):
    // Alert if shopper has already added a different size of the same SKU
    const existingSameSkuOtherSize = cart.some(
      (item) => item.sku.id === sku.id && item.size !== selectedSize,
    );

    if (existingSameSkuOtherSize) {
      setBracketingWarning(true);
    } else {
      setBracketingWarning(false);
    }

    addToCart({
      sku,
      size: selectedSize,
      quantity: 1,
      fitVerified: !!fitResult,
    });
    setAddedToast(true);
    setTimeout(() => setAddedToast(false), 3500);
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1">
        {/* Breadcrumb Back */}
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-inkMuted hover:text-brand transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Apparel Collection
          </Link>
        </div>

        {/* PDP Layout Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Product Gallery */}
          <div className="lg:col-span-6 space-y-4">
            <div className="rounded-bento border border-border bg-surface overflow-hidden shadow-bento aspect-square relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={fallbackMeta.image_url}
                alt={sku.name}
                className="w-full h-full object-cover"
              />
              <div className="absolute top-4 left-4">
                <Badge variant="brand">{sku.id}</Badge>
              </div>
              <div className="absolute top-4 right-4">
                <ProvenanceBadge provenance={sku.provenance} />
              </div>
            </div>
          </div>

          {/* Right Column: Garment Specs, Size Selector & Fit Action */}
          <div className="lg:col-span-6 space-y-6">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-inkMuted block">
                {sku.category}
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-ink mt-1">
                {sku.name}
              </h1>
              <div className="text-2xl font-extrabold text-brand mt-2">
                ₹{Number(sku.price_inr).toLocaleString("en-IN")}
                <span className="text-xs font-normal text-inkMuted ml-2">Inclusive of all taxes</span>
              </div>
            </div>

            {/* Fabric Badges */}
            <div className="p-4 rounded-bento border border-border bg-surface space-y-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-inkMuted block">
                Fabric &amp; Silhouette Architecture
              </span>
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="px-2.5 py-1 rounded-md bg-canvas border border-border font-semibold">
                  {sku.fabric_composition}
                </span>
                <span className="px-2.5 py-1 rounded-md bg-canvas border border-border font-semibold capitalize">
                  Stretch: {sku.fabric_stretch.replace("_", " ")}
                </span>
                {sku.length_inches && (
                  <span className="px-2.5 py-1 rounded-md bg-canvas border border-border font-semibold">
                    Length: {sku.length_inches}&quot;
                  </span>
                )}
              </div>
            </div>

            {/* Sizing & Check My Fit Hero Section */}
            <div className="p-5 rounded-bento border-2 border-border bg-surface space-y-4 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-ink">Select Garment Size</h3>
                  <p className="text-xs text-inkMuted">Based on body measurements or brand conversion</p>
                </div>

                {/* Sizing Button CTA */}
                <Button
                  type="button"
                  onClick={openFitDrawer}
                  className="bg-brand text-white hover:bg-brandHover shadow-sm"
                  size="sm"
                >
                  <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                  Check My Fit
                </Button>
              </div>

              {/* Size Buttons */}
              <div className="grid grid-cols-4 gap-2">
                {availableSizes.map((size) => {
                  const isSelected = selectedSize === size;
                  const isRecommended = fitResult?.recommended_size === size;
                  return (
                    <button
                      key={size}
                      type="button"
                      onClick={() => setSelectedSize(size)}
                      className={`relative py-3 rounded-lg font-bold text-xs border text-center transition-all ${
                        isSelected
                          ? "bg-brand text-white border-brand shadow-sm scale-102"
                          : "bg-surface border-border text-ink hover:bg-canvas"
                      }`}
                    >
                      {size}
                      {isRecommended && (
                        <span className="absolute -top-2 right-1 px-1.5 py-0.2 bg-accentEmerald text-white text-[9px] rounded-full font-extrabold shadow-xs">
                          Fit-Twin
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Fit Result pill if available */}
              {fitResult && (
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-accentEmerald" />
                    <span>
                      Fit-Twin Verified: <strong>Size {fitResult.recommended_size}</strong> ({fitResult.confidence_level} Confidence)
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={openFitDrawer}
                    className="text-[11px] underline font-bold text-emerald-800"
                  >
                    Adjust
                  </button>
                </div>
              )}

              {/* Add to Cart CTA */}
              <div className="space-y-2 pt-2">
                <Button
                  type="button"
                  onClick={handleAddToCart}
                  className="w-full bg-ink hover:bg-ink/90 text-white"
                  size="lg"
                >
                  <ShoppingBag className="w-4 h-4 mr-2" />
                  Add Size {selectedSize} to Cart
                </Button>

                {addedToast && (
                  <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold text-center animate-in fade-in">
                    ✓ Added to cart! Proceed to checkout to review delivery assurance.
                  </div>
                )}

                {/* Bracketing Warning per BUILD_PLAN Phase 4 */}
                {bracketingWarning && (
                  <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-accentAmber shrink-0 mt-0.5" />
                    <div>
                      <strong className="block">Multi-Size Cart Detected (Bracketing)</strong>
                      You have added multiple sizes of this garment to your cart. Sizing engine recommends selecting one verified size to ensure dispatch priority.
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Catalog Intelligence Panel (ADR-004) */}
            <CatalogIntelligencePanel sku={sku} />
          </div>
        </div>
      </main>

      {/* Check My Fit Slide-over Drawer */}
      <FitDrawer sku={sku} />
    </div>
  );
}
