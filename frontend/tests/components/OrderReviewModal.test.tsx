import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { OrderReviewModal } from "../../components/checkout/OrderReviewModal";
import type { RiskEvaluateResponse, IncentiveQuoteResponse } from "../../lib/api/types";

describe("OrderReviewModal Component", () => {
  const mockRisk: RiskEvaluateResponse = {
    risk_score_index: 45,
    risk_level: "Review",
    contributing_factors: ["Cash on Delivery", "Missing Landmark"],
    checks: [
      { id: "address_quality", label: "Address complete", status: "REVIEW" },
      { id: "serviceable_pin", label: "Serviceable PIN", status: "PASS" },
      { id: "rto_risk", label: "RTO risk band", status: "PASS" },
    ],
    cod_remains_available: true,
  };

  const mockIncentive: IncentiveQuoteResponse = {
    eligible_for_incentive: true,
    recommended_discount_inr: 40,
    expected_savings_inr: 52,
    headroom_inr: 12,
    reason_code: "REASON_ELEVATED_RISK_CONVERTIBLE",
    nudge_copy: "Pay via UPI & Save ₹40 with instant priority dispatch.",
    cod_remains_available: true,
  };

  it("renders 3 checks and guarantees COD option is available", () => {
    const handleConfirmCod = vi.fn();
    const handleAcceptUpi = vi.fn();

    render(
      <OrderReviewModal
        isOpen={true}
        onClose={vi.fn()}
        riskData={mockRisk}
        incentiveData={mockIncentive}
        cartTotal={1899}
        onConfirmCod={handleConfirmCod}
        onAcceptUpi={handleAcceptUpi}
      />,
    );

    expect(screen.getByText("Order Safety Review")).toBeInTheDocument();
    expect(screen.getByText("Address complete")).toBeInTheDocument();
    expect(screen.getByText("Serviceable PIN")).toBeInTheDocument();
    expect(screen.getByText("RTO risk band")).toBeInTheDocument();

    // Equal-visibility COD button must be present
    const codButton = screen.getByText(/Continue with Cash on Delivery/i);
    expect(codButton).toBeInTheDocument();
    fireEvent.click(codButton);
    expect(handleConfirmCod).toHaveBeenCalled();

    // UPI offer button must be present
    const upiButton = screen.getByText(/Pay ₹1859 via Instant UPI/i);
    expect(upiButton).toBeInTheDocument();
    fireEvent.click(upiButton);
    expect(handleAcceptUpi).toHaveBeenCalled();
  });

  it("returns null when isOpen is false", () => {
    const { container } = render(
      <OrderReviewModal
        isOpen={false}
        onClose={vi.fn()}
        riskData={mockRisk}
        incentiveData={mockIncentive}
        cartTotal={1899}
        onConfirmCod={vi.fn()}
        onAcceptUpi={vi.fn()}
      />,
    );
    expect(container.firstChild).toBeNull();
  });

  it("handles ineligible incentive gracefully with COD remaining available", () => {
    const handleConfirmCod = vi.fn();
    const ineligibleIncentive: IncentiveQuoteResponse = {
      eligible_for_incentive: false,
      recommended_discount_inr: 0,
      expected_savings_inr: 0,
      headroom_inr: 0,
      reason_code: "REASON_INSUFFICIENT_MARGIN",
      nudge_copy: "Order safety verified. Ready for dispatch.",
      cod_remains_available: true,
    };

    render(
      <OrderReviewModal
        isOpen={true}
        onClose={vi.fn()}
        riskData={mockRisk}
        incentiveData={ineligibleIncentive}
        cartTotal={1499}
        onConfirmCod={handleConfirmCod}
        onAcceptUpi={vi.fn()}
      />,
    );

    // No UPI discount button rendered
    expect(screen.queryByText(/via Instant UPI/i)).toBeNull();

    // COD button remains present and clickable
    const codButton = screen.getByText(/Continue with Cash on Delivery/i);
    expect(codButton).toBeInTheDocument();
    fireEvent.click(codButton);
    expect(handleConfirmCod).toHaveBeenCalled();
  });
});
