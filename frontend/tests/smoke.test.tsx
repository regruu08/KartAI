import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import StorefrontHome from "../app/page";
import ProductDetailPage from "../app/products/[skuId]/page";

let mockSkuId = "SKU-01";
vi.mock("next/navigation", () => ({
  useParams: () => ({ skuId: mockSkuId }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
  useRouter: () => ({ push: vi.fn() }),
}));

describe("Frontend Storefront Smoke Test", () => {
  it("renders the home page editorial hero and guarantee banner", () => {
    render(<StorefrontHome />);
    expect(screen.getAllByText(/ReturnZero/i).length).toBeGreaterThan(0);
    expect(
      screen.getByRole("heading", {
        name: /D2C Fashion Engineered for Perfect First-Time Fit/i,
      }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Net Monthly Savings/i)).toBeInTheDocument();
  });

  it("renders the 4 curated fashion apparel SKUs", () => {
    render(<StorefrontHome />);
    expect(
      screen.getByRole("heading", { name: /Handcrafted Chanderi Silk Anarkali Kurta/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Relaxed Mandarin Collar Linen Shirt/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Raw Indigo Denim Trucker Jacket/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Flowy Floral Rayon Tiered Maxi Dress/i }),
    ).toBeInTheDocument();
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
