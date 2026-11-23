import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import StorefrontHome from "../app/page";

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
});
