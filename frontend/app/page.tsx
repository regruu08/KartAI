import React from "react";
import Link from "next/link";
import { Sparkles, ShieldCheck, ArrowRight, AlertTriangle, Layers } from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";

// Curated 4 Fashion SKUs per ADR-013 & BUILD_PLAN Phase 4
const CURATED_SKUS = [
  {
    id: "SKU-01",
    name: "Handcrafted Chanderi Silk Anarkali Kurta",
    category: "Ethnic Apparel",
    price_inr: 2499,
    fabric_stretch: "non_stretch",
    fabric_composition: "100% Chanderi Silk · 70 GSM",
    has_gap: false,
    image_url: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80",
    provenance: "live_gemini",
    description: "Traditional flared silhouette with structured yoke. Rigid handwoven silk requiring exact bust ease.",
  },
  {
    id: "SKU-02",
    name: "Relaxed Mandarin Collar Linen Shirt",
    category: "Men's Casuals",
    price_inr: 1899,
    fabric_stretch: "slight_stretch",
    fabric_composition: "100% European Flax Linen · 140 GSM",
    has_gap: false,
    image_url: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80",
    provenance: "cached",
    description: "Breathable vacation shirt with mandarin collar. Slight natural mechanical stretch for relaxed everyday drape.",
  },
  {
    id: "SKU-03",
    name: "Raw Indigo Denim Trucker Jacket",
    category: "Outerwear",
    price_inr: 3299,
    fabric_stretch: "non_stretch",
    fabric_composition: "100% Heavyweight Cotton Denim · 13.5 oz",
    has_gap: true, // Intentionally missing sleeve measurement (ADR-004, ADR-013)
    image_url: "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=800&q=80",
    provenance: "manual_fixture",
    description: "Classic rigid trucker jacket. Merchant measurements lack sleeve length, automatically audited as data gap.",
  },
  {
    id: "SKU-04",
    name: "Flowy Floral Rayon Tiered Maxi Dress",
    category: "Women's Western",
    price_inr: 2199,
    fabric_stretch: "slight_stretch",
    fabric_composition: "100% Viscose Rayon Crepe · 110 GSM",
    has_gap: false,
    image_url: "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80",
    provenance: "cached",
    description: "Flattering tiered skirt with smocked bodice. Fluid drape with forgiving waist ease across diverse body shapes.",
  },
];

export default function StorefrontHome() {
  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />

      {/* Hero Banner */}
      <section className="bg-surface border-b border-border py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-canvas border border-border text-brand shadow-xs">
            <Sparkles className="w-3.5 h-3.5 text-brand" />
            Code to Cart Hackathon · Team BioXtreme
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-ink">
            D2C Fashion Storefront <span className="text-brand">with Fit Intelligence</span>
          </h1>
          <p className="text-sm sm:text-base text-inkMuted max-w-2xl mx-auto leading-relaxed">
            Eliminating sizing uncertainty and courier RTO delivery failures using deterministic brand conversion matrices,
            multimodal garment extraction, and in-browser delivery assurance.
          </p>
        </div>
      </section>

      {/* Product Catalog Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-xl font-extrabold text-ink">Curated Apparel Collection</h2>
            <p className="text-xs text-inkMuted">Tested across rigid silk, flax linen, raw denim, and fluid rayon fabrics</p>
          </div>
          <span className="text-xs font-bold text-brand bg-canvas px-3 py-1.5 rounded-lg border border-border">
            4 Curated SKUs
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {CURATED_SKUS.map((sku) => (
            <Card key={sku.id} className="p-0 overflow-hidden flex flex-col group hover:shadow-lg transition-all">
              {/* Product Photo */}
              <div className="relative h-64 bg-gray-100 overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={sku.image_url}
                  alt={sku.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute top-2.5 left-2.5">
                  <Badge variant="brand">{sku.id}</Badge>
                </div>
                {sku.has_gap && (
                  <div className="absolute top-2.5 right-2.5">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white shadow-xs">
                      <AlertTriangle className="w-3 h-3" />
                      Data Gap
                    </span>
                  </div>
                )}
              </div>

              {/* Card Details */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-inkMuted uppercase tracking-wider text-[10px] font-bold">
                      {sku.category}
                    </span>
                    <ProvenanceBadge provenance={sku.provenance} />
                  </div>
                  <h3 className="text-sm font-bold text-ink group-hover:text-brand transition-colors line-clamp-1">
                    {sku.name}
                  </h3>
                  <p className="text-xs text-inkMuted line-clamp-2 leading-relaxed">
                    {sku.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-borderLight flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-semibold text-inkMuted block">Retail Price</span>
                    <span className="text-base font-extrabold text-ink">₹{sku.price_inr.toLocaleString("en-IN")}</span>
                  </div>
                  <Link
                    href={`/products/${sku.id}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-canvas hover:bg-brand hover:text-white text-brand border border-border transition-colors"
                  >
                    View &amp; Check Fit
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-borderLight py-6 bg-surface text-center text-xs text-inkMuted">
        <p>ReturnZero AI · Team BioXtreme · Code to Cart Hackathon Round 2 Buildathon</p>
      </footer>
    </div>
  );
}
