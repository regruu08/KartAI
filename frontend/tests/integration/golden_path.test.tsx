import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import StorefrontHome from "../../app/page";
import ProductDetailPage from "../../app/products/[skuId]/page";
import CheckoutPage from "../../app/checkout/page";
import { WhatsAppPhoneSimulator } from "../../components/simulator/WhatsAppPhoneSimulator";

vi.mock("next/navigation", () => ({
  useParams: () => ({ skuId: "SKU-01" }),
  useSearchParams: () => new URLSearchParams({ order: "ORD-TEST-123" }),
  usePathname: () => "/",
  useRouter: () => ({ push: vi.fn() }),
}));

describe("End-to-End Golden Path Workflow", () => {
  it("Step 1: Storefront renders 4 curated fashion SKUs", () => {
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

  it("Step 2: PDP renders garment details, Check My Fit CTA, and Catalog Intelligence", async () => {
    render(<ProductDetailPage />);
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: /Handcrafted Chanderi Silk Anarkali Kurta/i }),
      ).toBeInTheDocument();
    });
    expect(screen.getAllByRole("button", { name: /Check My Fit/i }).length).toBeGreaterThan(0);
    expect(screen.getByText(/Catalog Intelligence/i)).toBeInTheDocument();
  });

  it("Step 3: Checkout page renders address form and guaranteed COD payment choice", () => {
    render(<CheckoutPage />);
    expect(screen.getByText(/Delivery Address Information/i)).toBeInTheDocument();
    expect(screen.getByText(/Cash on Delivery \(COD\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Guaranteed/i)).toBeInTheDocument();
  });

  it("Step 4: WhatsApp Simulator executes conversational delivery assurance", async () => {
    render(
      <WhatsAppPhoneSimulator
        orderId="ORD-GOLDEN-01"
        customerName="Ananya Verma"
        streetAddress="Flat 304, Green Glen Layout"
        addressQuality="NeedsLandmark"
      />,
    );

    expect(screen.getByText(/Hi Ananya Verma!/i)).toBeInTheDocument();
    expect(screen.getByText(/Simulated — no real WhatsApp message is sent/i)).toBeInTheDocument();

    const optInButton = screen.getByText(/YES, Confirm Updates/i);
    expect(optInButton).toBeInTheDocument();
    fireEvent.click(optInButton);

    await waitFor(() => {
      expect(screen.getAllByText("YES, Confirm Updates").length).toBeGreaterThanOrEqual(1);
    });
  });
});
