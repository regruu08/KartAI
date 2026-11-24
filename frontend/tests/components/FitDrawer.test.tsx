import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { FitDrawer } from "../../components/fit-twin/FitDrawer";
import { useStore } from "../../lib/store";
import { api } from "../../lib/api/client";
import type { SkuResponse, FitRecommendationResponse } from "../../lib/api/types";

vi.mock("../../lib/api/client", () => ({
  api: {
    computeFit: vi.fn(),
  },
}));

const mockSku: SkuResponse = {
  id: "SKU-01",
  name: "Handcrafted Chanderi Silk Anarkali Kurta",
  category: "Women's Ethnic",
  price_inr: 1899,
  fabric_composition: "100% Chanderi Silk, zero-stretch",
  fabric_stretch: "non_stretch",
  has_shoulder: true,
  has_sleeve: true,
  length_inches: 48,
  sizes_json: {
    S: { chest: 36, waist: 32, hip: 38, shoulder: 14.5, length: 48 },
    M: { chest: 38, waist: 34, hip: 40, shoulder: 15.5, length: 48 },
    L: { chest: 42, waist: 38, hip: 44, shoulder: 17.5, length: 49 },
  },
  care_instructions: "Dry clean only",
  provenance: "manual_fixture",
  extracted_at: null,
  prompt_version: null,
  image_sha256: null,
};

const mockFitResponse: FitRecommendationResponse = {
  sku_id: "SKU-01",
  recommended_size: "L",
  confidence_level: "High",
  fit_score: 95,
  fit_zone_breakdown: {
    chest: { shopper_inches: 38.0, garment_inches: 42.0, ease_inches: 4.0, status: "Comfortable" },
    shoulder: { shopper_inches: 17.0, garment_inches: 17.5, ease_inches: 0.5, status: "Ideal Fit" },
    shoulders: { note: 'Size M eliminated: shoulder ease -1.5" is below the 0.0" minimum for non-stretch fabric.' },
  },
  explanation_text:
    'Size M eliminated: shoulder ease -1.5" is below the 0.0" minimum for non-stretch fabric. Size L recommended with +4.0" chest ease and +0.5" shoulder ease.',
  missing_data_warnings: [],
};

describe("FitDrawer Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useStore.setState({
      fitDrawerOpen: false,
      fitResult: null,
      selectedBrand: "Zara",
      selectedSize: "M",
      fitPreference: "tailored",
      heightCm: 165,
      cart: [],
    });
  });

  it("does not render when fitDrawerOpen is false", () => {
    const { container } = render(<FitDrawer sku={mockSku} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders brands, sizes, preferences and triggers calculation when open", async () => {
    useStore.setState({ fitDrawerOpen: true });
    vi.mocked(api.computeFit).mockResolvedValueOnce(mockFitResponse);

    render(<FitDrawer sku={mockSku} />);

    expect(screen.getByText("Check My Fit")).toBeInTheDocument();
    expect(screen.getByText("Analyze Sizing for This Garment")).toBeInTheDocument();

    // Select Zara and Size M
    fireEvent.click(screen.getByText("Zara"));
    fireEvent.click(screen.getByText("M"));

    // Click Analyze Sizing
    fireEvent.click(screen.getByText("Analyze Sizing for This Garment"));

    await waitFor(() => {
      expect(api.computeFit).toHaveBeenCalledWith("SKU-01", {
        known_brand: "Zara",
        known_size: "M",
        fit_preference: "tailored",
        height_cm: 165,
      });
    });

    // Check recommended Size L and explanation
    await waitFor(() => {
      expect(screen.getByText("Size L")).toBeInTheDocument();
      expect(screen.getByText("High Confidence")).toBeInTheDocument();
      expect(
        screen.getByText(/Size M eliminated: shoulder ease -1.5" is below the 0.0" minimum/)
      ).toBeInTheDocument();
    });

    // Apply size and add to cart
    const addBtn = screen.getByText(/Apply Size L/i);
    expect(addBtn).toBeInTheDocument();
    fireEvent.click(addBtn);

    // Verify item in cart and drawer closed
    const cart = useStore.getState().cart;
    expect(cart.length).toBe(1);
    expect(cart[0]?.size).toBe("L");
    expect(cart[0]?.fitVerified).toBe(true);
    expect(useStore.getState().fitDrawerOpen).toBe(false);
  });

  it("handles and displays error when calculation fails", async () => {
    useStore.setState({ fitDrawerOpen: true });
    vi.mocked(api.computeFit).mockRejectedValueOnce(new Error("Fit engine unreachable"));

    render(<FitDrawer sku={mockSku} />);

    fireEvent.click(screen.getByText("Analyze Sizing for This Garment"));

    await waitFor(() => {
      expect(screen.getByText("Fit engine unreachable")).toBeInTheDocument();
    });
  });
});
