import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { OrderStreamTable } from "../../components/dashboard/OrderStreamTable";
import type { OrderResponse } from "../../lib/api/types";

describe("OrderStreamTable Component", () => {
  const mockOrders: OrderResponse[] = [
    {
      id: "ord_001",
      order_number: "ORD-20261128-AA11BB",
      customer_name: "Sneha Rao",
      street_address: "123 Indiranagar, Bengaluru",
      pin_code: "560034",
      city: "Bengaluru",
      state: "Karnataka",
      tier: "Tier-1",
      payment_method: "COD",
      total_inr: 2499,
      discount_applied_inr: 0,
      selected_size: "M",
      sku_id: "SKU-01",
      cod_risk_score: 35,
      order_status: "Safe_For_Dispatch",
      address_status: "Complete",
      used_fit_check: true,
      consent_status: "opted_in",
      dispatch_priority: "standard",
      is_synthetic: true,
      created_at: "2026-11-28T10:00:00Z",
    },
  ];

  it("renders order stream table with status badges and details", () => {
    render(<OrderStreamTable orders={mockOrders} />);

    expect(screen.getByText("Real-Time Order Stream")).toBeInTheDocument();
    expect(screen.getByText("ORD-20261128-AA11BB")).toBeInTheDocument();
    expect(screen.getByText("Sneha Rao")).toBeInTheDocument();
    expect(screen.getByText("SKU-01")).toBeInTheDocument();
    expect(screen.getByText("Bengaluru")).toBeInTheDocument();
    expect(screen.getByText("Safe_For_Dispatch")).toBeInTheDocument();
    expect(screen.getByText("35/100")).toBeInTheDocument();
  });
});
