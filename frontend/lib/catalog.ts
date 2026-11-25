import type { SkuResponse } from "./api/types";

export type SizeLabel = "XS" | "S" | "M" | "L" | "XL" | "XXL";
export const ALL_SIZES: readonly SizeLabel[] = ["XS", "S", "M", "L", "XL", "XXL"] as const;
export const STOCKED_SIZES: readonly SizeLabel[] = ["S", "M", "L", "XL"] as const;

export type FabricFilter = "all" | "non_stretch" | "slight_stretch";
export type CatalogSort = "featured" | "price_asc" | "price_desc";

export interface SkuDisplayMeta {
  image: string;
  detailImage: string;
  imageAlt: string;
  detailAlt: string;
  weightLabel: string;
  stretchNote: string;
  fitNote?: string;
}

export const SKU_DISPLAY_META: Record<string, SkuDisplayMeta> = {
  "SKU-01": {
    image: "/images/sku-01-main.jpg",
    detailImage: "/images/sku-01-detail.jpg",
    imageAlt:
      "Handcrafted Chanderi Silk Anarkali Kurta in ivory champagne with woven antique gold zari trim along neckline, cuffs, and flared hem",
    detailAlt:
      "Macro detail of Chanderi Silk handloom warp-weft slub grain and woven antique gold zari neckline trim",
    weightLabel: "180 GSM (Handloom silk)",
    stretchNote: "0% Elastane, Rigid",
    fitNote:
      'Rigid fabric needs +2.5" regular ease. Zara Size M shoppers are recommended Size L for shoulder and bust ease.',
  },
  "SKU-02": {
    image: "/images/sku-02-main.jpg",
    detailImage: "/images/sku-02-detail.jpg",
    imageAlt:
      "Relaxed Mandarin Collar Linen Shirt in natural oatmeal-flax cotton-linen blend with tailored placket",
    detailAlt:
      "Macro close-up of oatmeal cotton-linen Mandarin collar band, topstitched placket, and mottled horn buttons",
    weightLabel: "160 GSM (Breathable weave)",
    stretchNote: "Slight natural give",
  },
  "SKU-03": {
    image: "/images/sku-03-main.jpg",
    detailImage: "/images/sku-03-detail.jpg",
    imageAlt:
      "Raw Indigo Denim Trucker Jacket in heavyweight cotton twill with copper contrast topstitching and chest flap pockets",
    detailAlt:
      "Macro view of 320 GSM raw indigo denim twill weave, amber bar-tack stitching, and matte brass shank button",
    weightLabel: "320 GSM (Rigid denim twill)",
    stretchNote: "Rigid armholes",
  },
  "SKU-04": {
    image: "/images/sku-04-main.jpg",
    detailImage: "/images/sku-04-detail.jpg",
    imageAlt:
      "Flowy Floral Rayon Tiered Maxi Dress in ivory botanical lilac print with smocked bodice and softly gathered skirt",
    detailAlt:
      "Close-up editorial drape of smocked floral viscose rayon bodice and softly pleated tiered waist",
    weightLabel: "110 GSM (Fluid draped crepe)",
    stretchNote: "Smocked waist, forgiving drape",
  },
};

/** Offline deterministic catalog matching backend/app/db/seed.py exactly. */
export const FALLBACK_CATALOG_SKUS: SkuResponse[] = [
  {
    id: "SKU-01",
    name: "Handcrafted Chanderi Silk Anarkali Kurta",
    category: "Women's Ethnic",
    price_inr: 1899,
    fabric_composition:
      "100% Chanderi Silk, zero-stretch (0% elastane), structured bodice, 180 GSM",
    fabric_stretch: "non_stretch",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 48.0,
    sizes_json: {
      S: { chest: 36, waist: 32, shoulder: 14.5, length: 46 },
      M: { chest: 38, waist: 34, shoulder: 15.5, length: 47 },
      L: { chest: 40, waist: 36, shoulder: 17.0, length: 48 },
      XL: { chest: 42, waist: 38, shoulder: 18.0, length: 49 },
    },
    care_instructions: "Dry clean only",
    provenance: "manual_fixture",
    extracted_at: null,
    prompt_version: "v1.0",
    image_sha256: null,
  },
  {
    id: "SKU-02",
    name: "Relaxed Mandarin Collar Linen Shirt",
    category: "Men's Casual",
    price_inr: 1499,
    fabric_composition:
      "70% Cotton / 30% Linen, slight natural give, relaxed drape, 160 GSM",
    fabric_stretch: "slight_stretch",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 29.0,
    sizes_json: {
      S: { chest: 38, waist: 36, shoulder: 16.5, length: 28 },
      M: { chest: 40, waist: 38, shoulder: 17.5, length: 29 },
      L: { chest: 42, waist: 40, shoulder: 18.5, length: 30 },
      XL: { chest: 44, waist: 42, shoulder: 19.5, length: 31 },
    },
    care_instructions: "Machine wash cold, tumble dry low",
    provenance: "manual_fixture",
    extracted_at: null,
    prompt_version: "v1.0",
    image_sha256: null,
  },
  {
    id: "SKU-03",
    name: "Raw Indigo Denim Trucker Jacket",
    category: "Outerwear",
    price_inr: 2499,
    fabric_composition: "99% Cotton / 1% Spandex, 320 GSM, rigid armholes",
    fabric_stretch: "non_stretch",
    has_shoulder: true,
    has_sleeve: false,
    length_inches: 26.0,
    sizes_json: {
      S: { chest: 40, waist: 38, shoulder: 17.0, length: 25 },
      M: { chest: 42, waist: 40, shoulder: 18.0, length: 26 },
      L: { chest: 44, waist: 42, shoulder: 19.0, length: 27 },
      XL: { chest: 46, waist: 44, shoulder: 20.0, length: 28 },
    },
    care_instructions: "Spot clean or cold wash separately",
    provenance: "manual_fixture",
    extracted_at: null,
    prompt_version: "v1.0",
    image_sha256: null,
  },
  {
    id: "SKU-04",
    name: "Flowy Floral Rayon Tiered Maxi Dress",
    category: "Women's Western",
    price_inr: 1999,
    fabric_composition:
      "100% Viscose Rayon, highly fluid drape, elasticated smocked waist",
    fabric_stretch: "slight_stretch",
    has_shoulder: true,
    has_sleeve: true,
    length_inches: 53.0,
    sizes_json: {
      S: { chest: 34, waist: 26, shoulder: 14.0, length: 52 },
      M: { chest: 36, waist: 28, shoulder: 15.0, length: 53 },
      L: { chest: 38, waist: 30, shoulder: 16.0, length: 54 },
      XL: { chest: 40, waist: 32, shoulder: 17.0, length: 55 },
    },
    care_instructions: "Gentle hand wash",
    provenance: "manual_fixture",
    extracted_at: null,
    prompt_version: "v1.0",
    image_sha256: null,
  },
];

export function getSkuDisplayMeta(sku: SkuResponse): SkuDisplayMeta {
  return (
    SKU_DISPLAY_META[sku.id] ?? {
      image: "/images/sku-01-main.jpg",
      detailImage: "/images/sku-01-detail.jpg",
      imageAlt: sku.name,
      detailAlt: `${sku.name} textile detail`,
      weightLabel: sku.fabric_stretch === "non_stretch" ? "Structured weave" : "Relaxed weave",
      stretchNote: sku.fabric_stretch === "non_stretch" ? "Non-stretch" : "Slight stretch",
    }
  );
}

export function isSizeStocked(sku: SkuResponse, size: SizeLabel): boolean {
  return Boolean(sku.sizes_json && sku.sizes_json[size]);
}

export interface CatalogFilterOptions {
  search: string;
  category: string;
  fabric: FabricFilter;
  sort: CatalogSort;
}

export function filterAndSortCatalog(
  items: readonly SkuResponse[],
  options: CatalogFilterOptions,
): SkuResponse[] {
  const tokens = options.search
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);

  const filtered = items.filter((sku) => {
    if (options.category !== "All" && sku.category !== options.category) {
      return false;
    }
    if (options.fabric !== "all" && sku.fabric_stretch !== options.fabric) {
      return false;
    }
    if (tokens.length > 0) {
      const haystack =
        `${sku.id} ${sku.name} ${sku.fabric_composition} ${sku.category}`.toLowerCase();
      for (const token of tokens) {
        if (!haystack.includes(token)) {
          return false;
        }
      }
    }
    return true;
  });

  if (options.sort === "price_asc") {
    return [...filtered].sort((a, b) => Number(a.price_inr) - Number(b.price_inr));
  }
  if (options.sort === "price_desc") {
    return [...filtered].sort((a, b) => Number(b.price_inr) - Number(a.price_inr));
  }
  return filtered;
}
