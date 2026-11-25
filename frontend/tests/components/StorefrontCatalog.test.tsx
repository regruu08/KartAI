import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { CatalogBrowser } from "../../components/home/CatalogBrowser";
import { LiveFitPreview } from "../../components/home/LiveFitPreview";
import { ErrorBoundary } from "../../components/ui/ErrorBoundary";
import { api } from "../../lib/api/client";

vi.mock("../../lib/api/client", () => ({
  api: {
    listSkus: vi.fn().mockRejectedValue(new Error("offline fallback test")),
    computeFit: vi.fn().mockResolvedValue({
      sku_id: "SKU-03",
      recommended_size: "L",
      confidence_level: "Medium",
      fit_score: 68,
      explanation_text: "Mocked live preview denim ease calculation.",
      missing_data_warnings: ["Sleeve length omitted in merchant catalog"],
    }),
  },
}));

describe("CatalogBrowser & ErrorBoundary", () => {
  it("filters curated SKUs by search, fabric stretch, and category with reset", () => {
    render(<CatalogBrowser />);

    expect(screen.getByText("Showing 4 of 4 pieces")).toBeInTheDocument();

    // Search filter
    const searchInput = screen.getByLabelText(/Search garments by name/i);
    fireEvent.change(searchInput, { target: { value: "Denim" } });
    expect(screen.getByText("Showing 1 of 4 pieces")).toBeInTheDocument();
    expect(screen.getByText(/Raw Indigo Denim Trucker Jacket/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Gap: Missing Sleeve Dimensions/i)).toBeInTheDocument();

    // Clear all filters returns all 4
    fireEvent.click(screen.getByText(/Clear all filters/i));
    expect(screen.getByText("Showing 4 of 4 pieces")).toBeInTheDocument();

    // Fabric stretch filter
    fireEvent.click(screen.getByRole("button", { name: "Rigid Non-Stretch" }));
    expect(screen.getByText("Showing 2 of 4 pieces")).toBeInTheDocument();
  });

  it("renders ErrorBoundary recovery UI when a child throws", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    const Broken = () => {
      throw new Error("Simulated component crash");
    };

    render(
      <ErrorBoundary title="Catalog crashed">
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Catalog crashed")).toBeInTheDocument();
    expect(screen.getByText("Simulated component crash")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Retry section/i })).toBeInTheDocument();
    spy.mockRestore();
  });

  it("renders interactive LiveFitPreview and displays SKU-03 missing sleeve notice", async () => {
    render(<LiveFitPreview />);
    fireEvent.click(screen.getByRole("button", { name: /SKU-03/i }));

    await waitFor(() => {
      expect(api.computeFit).toHaveBeenCalledWith(
        "SKU-03",
        expect.objectContaining({ known_brand: "Zara", known_size: "M" }),
      );
      expect(screen.getByText(/Sleeve length omitted in merchant catalog/i)).toBeInTheDocument();
    });
  });
});
