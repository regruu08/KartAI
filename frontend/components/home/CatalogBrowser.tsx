"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Search, TriangleAlert, X } from "lucide-react";
import { api } from "@/lib/api/client";
import type { SkuResponse } from "@/lib/api/types";
import {
  FALLBACK_CATALOG_SKUS,
  STOCKED_SIZES,
  filterAndSortCatalog,
  getSkuDisplayMeta,
  isSizeStocked,
  type CatalogSort,
  type FabricFilter,
} from "@/lib/catalog";
import { formatInr } from "@/lib/format";
import { cn } from "@/lib/cn";
import { ProvenanceBadge } from "@/components/ui/ProvenanceBadge";
import { GarmentImage } from "@/components/ui/GarmentImage";

const FABRIC_OPTIONS: readonly { value: FabricFilter; label: string }[] = [
  { value: "all", label: "All Fabrics" },
  { value: "non_stretch", label: "Rigid Non-Stretch" },
  { value: "slight_stretch", label: "Slight Stretch" },
];

export function CatalogBrowser() {
  const [skus, setSkus] = useState<SkuResponse[]>(FALLBACK_CATALOG_SKUS);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>("All");
  const [fabric, setFabric] = useState<FabricFilter>("all");
  const [sort, setSort] = useState<CatalogSort>("featured");

  useEffect(() => {
    const controller = new AbortController();
    api
      .listSkus(controller.signal)
      .then((res) => {
        if (res.skus && res.skus.length > 0) {
          setSkus(res.skus);
        }
      })
      .catch(() => {
        // Offline deterministic fallback stays active without blocking UI
      });
    return () => controller.abort();
  }, []);

  const categories = useMemo(() => {
    const unique = Array.from(new Set(skus.map((s) => s.category)));
    return ["All", ...unique];
  }, [skus]);

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { All: skus.length };
    for (const sku of skus) {
      counts[sku.category] = (counts[sku.category] ?? 0) + 1;
    }
    return counts;
  }, [skus]);

  const filteredSkus = useMemo(
    () => filterAndSortCatalog(skus, { search, category, fabric, sort }),
    [skus, search, category, fabric, sort],
  );

  const hasActiveFilters =
    search.trim().length > 0 || category !== "All" || fabric !== "all" || sort !== "featured";

  const clearAllFilters = (): void => {
    setSearch("");
    setCategory("All");
    setFabric("all");
    setSort("featured");
  };

  return (
    <section
      id="catalog"
      aria-labelledby="catalog-heading"
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 lg:py-20 border-t border-line"
    >
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-ink-muted">Curated Collection · Stocked S–XL</p>
          <h2 id="catalog-heading" className="font-display text-3xl sm:text-4xl text-ink">
            The Verified Edit
          </h2>
        </div>

        <p aria-live="polite" className="text-sm text-ink-muted tabular-nums">
          Showing {filteredSkus.length} of {skus.length} pieces
        </p>
      </div>

      {/* Combinable Search, Fabric Stretch, Sort & Category Controls */}
      <div className="rounded-2xl border border-line bg-surface p-4 sm:p-5 space-y-4 shadow-card mb-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-center">
          <div className="lg:col-span-5 relative">
            <label htmlFor="catalog-search" className="sr-only">
              Search garments by name, fabric, or category
            </label>
            <Search
              className="w-4 h-4 text-ink-muted absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none"
              aria-hidden="true"
            />
            <input
              id="catalog-search"
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search Chanderi silk, linen, denim, outerwear…"
              className="w-full min-h-[44px] pl-10 pr-10 rounded-xl border border-line-strong bg-canvas/60 text-sm text-ink placeholder:text-ink-muted/80 focus:border-brand focus:bg-surface transition-colors"
            />
            {search.length > 0 && (
              <button
                type="button"
                onClick={() => setSearch("")}
                aria-label="Clear search query"
                className="absolute right-1.5 top-1/2 -translate-y-1/2 min-h-[36px] min-w-[36px] inline-flex items-center justify-center rounded-lg text-ink-muted hover:text-ink hover:bg-subtle cursor-pointer"
              >
                <X className="w-4 h-4" aria-hidden="true" />
              </button>
            )}
          </div>

          <div
            role="group"
            aria-label="Filter by fabric stretch"
            className="lg:col-span-4 inline-flex flex-wrap sm:flex-nowrap items-center gap-1 p-1 rounded-xl bg-subtle border border-line"
          >
            {FABRIC_OPTIONS.map((opt) => {
              const active = fabric === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setFabric(opt.value)}
                  className={cn(
                    "flex-1 min-h-[38px] px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap cursor-pointer",
                    active
                      ? "bg-surface text-ink shadow-sm border border-line-strong"
                      : "text-ink-muted hover:text-ink border border-transparent",
                  )}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>

          <div className="lg:col-span-3 flex items-center gap-2">
            <label htmlFor="catalog-sort" className="text-xs font-medium text-ink-muted shrink-0">
              Sort
            </label>
            <select
              id="catalog-sort"
              value={sort}
              onChange={(e) => setSort(e.target.value as CatalogSort)}
              className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-surface text-sm text-ink cursor-pointer"
            >
              <option value="featured">Curated Order</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-line">
          <div role="group" aria-label="Filter by category" className="flex flex-wrap gap-2">
            {categories.map((cat) => {
              const active = category === cat;
              const count = categoryCounts[cat] ?? 0;
              return (
                <button
                  key={cat}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setCategory(cat)}
                  className={cn(
                    "min-h-[40px] px-3.5 py-1.5 rounded-full text-xs font-medium border transition-colors whitespace-nowrap shrink-0 cursor-pointer",
                    active
                      ? "bg-brand text-white border-brand"
                      : "bg-surface text-ink border-line-strong hover:border-brand/50 hover:bg-subtle",
                  )}
                >
                  {cat} <span className="tabular-nums opacity-85">({count})</span>
                </button>
              );
            })}
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={clearAllFilters}
              className="min-h-[40px] px-3 text-xs font-medium text-brand hover:text-brand-hover underline underline-offset-4 cursor-pointer whitespace-nowrap"
            >
              Clear all filters
            </button>
          )}
        </div>
      </div>

      {/* Lookbook Product Grid */}
      {filteredSkus.length === 0 ? (
        <div className="rounded-2xl border border-line bg-surface px-6 py-12 text-center flex flex-col items-center justify-center gap-3">
          <h3 className="font-display text-xl text-ink">No pieces match your filters</h3>
          <p className="text-sm text-ink-muted max-w-md leading-relaxed">
            Try broadening your search terms or switching back to all fabrics and categories.
          </p>
          <button
            type="button"
            onClick={clearAllFilters}
            className="mt-2 inline-flex items-center justify-center min-h-[44px] px-5 rounded-full border border-line-strong bg-surface text-sm font-semibold text-ink hover:bg-subtle cursor-pointer"
          >
            Clear all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-7">
          {filteredSkus.map((sku) => {
            const meta = getSkuDisplayMeta(sku);
            const hasSleeveGap = !sku.has_sleeve;
            return (
              <Link
                key={sku.id}
                href={`/products/${sku.id}`}
                className="group flex flex-col rounded-2xl border border-line bg-surface overflow-hidden transition-shadow duration-300 hover:shadow-lift focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2"
              >
                <div className="relative aspect-[3/4] w-full overflow-hidden bg-subtle border-b border-line">
                  <GarmentImage
                    src={meta.image}
                    hoverSrc={meta.detailImage}
                    alt={meta.imageAlt}
                    garmentName={sku.name}
                    className="h-full w-full"
                  />

                  <div className="absolute top-3 left-3">
                    <ProvenanceBadge provenance={sku.provenance} className="bg-surface/95 backdrop-blur-md" />
                  </div>

                  {/* Quick-Stocked Size Strip */}
                  <div className="absolute inset-x-3 bottom-3 flex items-center justify-between rounded-lg bg-surface/95 backdrop-blur-md border border-line px-2.5 py-1.5 text-[11px] shadow-sm opacity-95 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-200">
                    <span className="text-ink-muted font-medium">Stocked Sizes</span>
                    <span className="font-semibold text-ink tracking-wider tabular-nums">
                      {STOCKED_SIZES.filter((s) => isSizeStocked(sku, s)).join(" · ")}
                    </span>
                  </div>
                </div>

                <div className="p-5 flex-1 flex flex-col justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2 text-[11px] text-ink-muted">
                      <span>{sku.category}</span>
                      <span>{meta.stretchNote}</span>
                    </div>
                    <h3 className="font-display text-lg text-ink leading-snug group-hover:text-brand transition-colors">
                      {sku.name}
                    </h3>
                    <p className="text-xs text-ink-muted leading-relaxed line-clamp-2">
                      {sku.fabric_composition}
                    </p>

                    {hasSleeveGap && (
                      <div className="pt-1.5">
                        <span className="inline-flex items-center gap-1.5 rounded-lg border border-warn/35 bg-warn-soft px-2.5 py-1 text-[11px] font-medium text-warn-text leading-snug">
                          <TriangleAlert className="w-3.5 h-3.5 text-warn shrink-0" aria-hidden="true" />
                          Data Gap: Missing Sleeve Dimensions
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="pt-3 border-t border-line flex items-center justify-between gap-2">
                    <span className="text-base font-semibold text-ink tabular-nums">
                      {formatInr(sku.price_inr)}
                    </span>
                    <span className="text-xs font-semibold text-brand group-hover:underline underline-offset-4 whitespace-nowrap">
                      Inspect &amp; Fit Check
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </section>
  );
}
