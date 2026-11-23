import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import HomePage from "../app/page";

describe("Frontend Scaffolding Smoke Test", () => {
  it("renders the home page hero and title", () => {
    render(<HomePage />);
    expect(screen.getByText("ReturnZero")).toBeInTheDocument();
    expect(screen.getByText("AI")).toBeInTheDocument();
  });

  it("renders all four core pillar bento cards", () => {
    render(<HomePage />);
    expect(screen.getByText("1. Fit Intelligence")).toBeInTheDocument();
    expect(screen.getByText("2. Checkout Shield")).toBeInTheDocument();
    expect(screen.getByText("3. Delivery Assurance")).toBeInTheDocument();
    expect(screen.getByText("4. Merchant Command Center")).toBeInTheDocument();
  });
});
