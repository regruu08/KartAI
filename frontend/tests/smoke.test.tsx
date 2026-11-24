import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import StorefrontHome from "../app/page";
import ProductDetailPage from "../app/products/[skuId]/page";

// Mock next/navigation for ProductDetailPage
let mockSkuId = "SKU-01";
vi.mock("next/navigation", () => ({
  useParams: () => ({ skuId: mockSkuId }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
  useRouter: () => ({ push: vi.fn() }),
}));

describe("Frontend Storefront Smoke Test", () => {
  it("renders the home page hero and title", () => {
    render(<StorefrontHome />);
    expect(screen.getAllByText(/ReturnZero/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/D2C Fashion Storefront/i)).toBeInTheDocument();
  });

  it("renders the 4 curated fashion apparel SKUs", () => {
    render(<StorefrontHome />);
    expect(screen.getByText(/Chanderi Silk/i)).toBeInTheDocument();
    expect(screen.getByText(/Mandarin Collar Linen Shirt/i)).toBeInTheDocument();
    expect(screen.getByText(/Denim Trucker Jacket/i)).toBeInTheDocument();
    expect(screen.getByText(/Floral Rayon/i)).toBeInTheDocument();
  });

  it("renders Product Not Found for non-existent SKU", async () => {
    mockSkuId = "SKU-999";
    render(<ProductDetailPage />);
    await waitFor(() => {
      expect(screen.getByText(/Product Not Found/i)).toBeInTheDocument();
      expect(screen.getByText(/Back to Storefront/i)).toBeInTheDocument();
    });
  });
});
