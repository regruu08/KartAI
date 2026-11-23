import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { CatalogIntelligencePanel } from "../../components/fit-twin/CatalogIntelligencePanel";
import type { SkuResponse } from "../../lib/api/types";

describe("CatalogIntelligencePanel Component", () => {
  const mockSkuWithGap: SkuResponse = {
    id: "SKU-03",
    name: "Raw Indigo Denim Trucker Jacket",
    category: "Outerwear",
    price_inr: 3299,
    fabric_stretch: "non_stretch",
    fabric_composition: "100% Cotton Denim",
    has_shoulder: true,
    has_sleeve: false, // Gap intentionally present
    length_inches: 26.0,
    sizes_json: {
      M: { chest: 42.0, waist: 40.0, shoulder: 18.0, length: 26.0 },
    },
    care_instructions: null,
    provenance: "manual_fixture",
    extracted_at: null,
    prompt_version: null,
    image_sha256: null,
  };

  it("renders collapsed panel with title and provenance badge", () => {
    render(<CatalogIntelligencePanel sku={mockSkuWithGap} />);
    expect(screen.getByText("Catalog Intelligence")).toBeInTheDocument();
    expect(screen.getByText("Standard Verified Fixture")).toBeInTheDocument();
  });

  it("expands on click and displays missing sleeve data gap warning", () => {
    render(<CatalogIntelligencePanel sku={mockSkuWithGap} />);
    const button = screen.getByRole("button");
    fireEvent.click(button);

    expect(screen.getByText("Merchant Data Gaps Detected")).toBeInTheDocument();
    expect(screen.getByText(/Sleeve Length/i)).toBeInTheDocument();
    expect(screen.getByText(/100% Cotton Denim/i)).toBeInTheDocument();
  });
});
