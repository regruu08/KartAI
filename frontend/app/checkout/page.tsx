"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ShieldCheck, ArrowLeft, AlertTriangle, CheckCircle2, Lock } from "lucide-react";
import { Navbar } from "@/components/ui/Navbar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { OrderReviewModal } from "@/components/checkout/OrderReviewModal";
import { api } from "@/lib/api/client";
import { useStore } from "@/lib/store";
import type { RiskEvaluateResponse, IncentiveQuoteResponse } from "@/lib/api/types";

export default function CheckoutPage() {
  const router = useRouter();
  const {
    cart,
    clearCart,
    setPlacedOrder,
    customerName,
    setCustomerName,
    customerPhone,
    setCustomerPhone,
    streetAddress,
    setStreetAddress,
    city,
    setCity,
    state,
    setState,
    pinCode,
    setPinCode,
    landmark,
    setLandmark,
    paymentMethod,
    setPaymentMethod,
  } = useStore();

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [riskData, setRiskData] = useState<RiskEvaluateResponse | null>(null);
  const [incentiveData, setIncentiveData] = useState<IncentiveQuoteResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Cart financial totals
  const subtotal = cart.reduce(
    (sum, item) => sum + Number(item.sku.price_inr) * item.quantity,
    0,
  );
  // Default demo fallback if cart empty
  const effectiveSubtotal = subtotal > 0 ? subtotal : 2499;

  // Bracketing check
  const skuIds = cart.map((i) => i.sku.id);
  const hasBracketing = new Set(skuIds).size < skuIds.length;

  const handleProceedToReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    // Validate 6-digit PIN
    if (!/^\d{6}$/.test(pinCode.trim())) {
      setErrorMessage("Please enter a valid 6-digit Indian PIN code.");
      return;
    }

    setIsEvaluating(true);

    try {
      if (paymentMethod === "COD") {
        // Evaluate operational risk and dynamic margin-safe incentive quote
        const [riskRes, incRes] = await Promise.all([
          api.evaluateRisk({
            street_address: streetAddress,
            pin_code: pinCode.trim(),
            payment_method: "COD",
            has_used_fit_twin: cart.some((i) => i.fitVerified),
            is_bracketing: hasBracketing,
          }),
          api.getIncentiveQuote({
            cart_total_inr: effectiveSubtotal,
            risk_score_index: 55, // Estimated baseline
            current_payment: "COD",
            has_used_fit_twin: cart.some((i) => i.fitVerified),
          }),
        ]);

        setRiskData(riskRes);
        setIncentiveData(incRes);
        setModalOpen(true);
      } else {
        // Direct Prepaid checkout creation
        await executeCreateOrder("Prepaid", 0);
      }
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to evaluate order review. Please retry.",
      );
    } finally {
      setIsEvaluating(false);
    }
  };

  const executeCreateOrder = async (
    confirmedPaymentMethod: "COD" | "Prepaid",
    appliedDiscount: number,
  ) => {
    setIsEvaluating(true);
    try {
      const activeItem = cart[0];
      const skuId = activeItem?.sku.id ?? "SKU-01";
      const size = activeItem?.size ?? "M";

      const order = await api.createOrder({
        sku_id: skuId,
        size,
        quantity: activeItem?.quantity ?? 1,
        customer_name: customerName,
        customer_phone: customerPhone,
        street_address: streetAddress,
        city,
        state,
        pin_code: pinCode.trim(),
        payment_method: confirmedPaymentMethod,
        applied_discount_inr: appliedDiscount,
        incentive_reason_code:
          appliedDiscount > 0 ? "REASON_ELEVATED_RISK_CONVERTIBLE" : undefined,
        has_used_fit_twin: cart.some((i) => i.fitVerified),
        is_bracketing: hasBracketing,
        known_brand: activeItem?.knownBrand,
        known_size: activeItem?.knownSize,
        fit_preference: activeItem?.fitPreference,
      });

      setPlacedOrder(order);
      clearCart();
      setModalOpen(false);
      router.push(`/confirmation/${order.id}`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Order creation failed.");
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-inkMuted hover:text-brand transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Continue Shopping
          </Link>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold text-ink mb-6">
          Checkout &amp; Delivery Assurance
        </h1>

        {errorMessage && (
          <div className="p-3.5 mb-6 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
            {errorMessage}
          </div>
        )}

        {/* Bracketing Alert */}
        {hasBracketing && (
          <div className="p-4 mb-6 rounded-bento bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-accentAmber shrink-0 mt-0.5" />
            <div>
              <strong className="block font-bold">Multi-Size Cart Detected (Bracketing)</strong>
              Your cart contains multiple sizes of identical items. Sizing engine recommends confirming one verified size to ensure dispatch priority.
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          {/* Left Form: Delivery Address */}
          <form onSubmit={handleProceedToReview} className="md:col-span-7 space-y-5">
            <Card className="space-y-4">
              <h2 className="text-sm font-bold text-ink flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-brand" />
                Delivery Address Information
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-inkMuted font-bold mb-1">Customer Full Name</label>
                  <input
                    type="text"
                    required
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                  />
                </div>
                <div>
                  <label className="block text-inkMuted font-bold mb-1">Mobile Phone (WhatsApp)</label>
                  <input
                    type="tel"
                    required
                    value={customerPhone}
                    onChange={(e) => setCustomerPhone(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                  />
                </div>
              </div>

              <div className="text-xs">
                <label className="block text-inkMuted font-bold mb-1">Street Address / House No.</label>
                <textarea
                  required
                  rows={2}
                  value={streetAddress}
                  onChange={(e) => setStreetAddress(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div>
                  <label className="block text-inkMuted font-bold mb-1">PIN Code (6 Digits)</label>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={pinCode}
                    onChange={(e) => setPinCode(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                  />
                </div>
                <div>
                  <label className="block text-inkMuted font-bold mb-1">City</label>
                  <input
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                  />
                </div>
                <div>
                  <label className="block text-inkMuted font-bold mb-1">State</label>
                  <input
                    type="text"
                    required
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                  />
                </div>
              </div>

              <div className="text-xs">
                <label className="block text-inkMuted font-bold mb-1">Landmark (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Near Metro Pillar 120"
                  value={landmark}
                  onChange={(e) => setLandmark(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-border bg-surface text-ink focus:outline-none focus:border-brand"
                />
              </div>
            </Card>

            {/* Payment Method Selector */}
            <Card className="space-y-3">
              <h2 className="text-sm font-bold text-ink">Payment Method</h2>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <label
                  className={`p-3.5 rounded-lg border flex items-center justify-between cursor-pointer transition-all ${
                    paymentMethod === "COD"
                      ? "border-brand bg-canvas shadow-xs font-bold"
                      : "border-border bg-surface text-inkMuted hover:bg-canvas"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === "COD"}
                      onChange={() => setPaymentMethod("COD")}
                      className="accent-brand"
                    />
                    <span>Cash on Delivery (COD)</span>
                  </div>
                  <span className="text-[10px] text-inkMuted">Guaranteed</span>
                </label>

                <label
                  className={`p-3.5 rounded-lg border flex items-center justify-between cursor-pointer transition-all ${
                    paymentMethod === "Prepaid"
                      ? "border-brand bg-canvas shadow-xs font-bold"
                      : "border-border bg-surface text-inkMuted hover:bg-canvas"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === "Prepaid"}
                      onChange={() => setPaymentMethod("Prepaid")}
                      className="accent-brand"
                    />
                    <span>Instant UPI / Prepaid</span>
                  </div>
                  <span className="text-[10px] text-emerald-700 font-bold">Priority</span>
                </label>
              </div>
            </Card>

            <Button
              type="submit"
              isLoading={isEvaluating}
              className="w-full"
              size="lg"
            >
              <Lock className="w-4 h-4 mr-2" />
              {paymentMethod === "COD" ? "Review Order Safety & Place" : "Confirm & Pay via UPI"}
            </Button>
          </form>

          {/* Right Summary: Cart Overview */}
          <div className="md:col-span-5 space-y-4">
            <Card className="space-y-4">
              <h2 className="text-sm font-bold text-ink">Order Summary</h2>

              {cart.length === 0 ? (
                <div className="p-3 rounded-lg bg-canvas border border-borderLight text-xs text-inkMuted">
                  <span>Demo Mode: Pre-filled standard order (1 item · ₹2,499)</span>
                </div>
              ) : (
                <div className="space-y-3">
                  {cart.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-start justify-between text-xs pb-3 border-b border-borderLight last:border-b-0"
                    >
                      <div>
                        <div className="font-bold text-ink">{item.sku.name}</div>
                        <div className="text-inkMuted mt-0.5">
                          Size: <span className="font-bold text-brand">{item.size}</span> · Qty: {item.quantity}
                        </div>
                        {item.fitVerified && (
                          <span className="inline-flex items-center gap-1 text-[10px] text-accentEmerald font-semibold mt-1">
                            <CheckCircle2 className="w-3 h-3" />
                            Fit-Twin Verified
                          </span>
                        )}
                      </div>
                      <div className="font-extrabold text-ink">
                        ₹{(Number(item.sku.price_inr) * item.quantity).toLocaleString("en-IN")}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 border-t border-borderLight space-y-2 text-xs">
                <div className="flex justify-between text-inkMuted">
                  <span>Subtotal</span>
                  <span>₹{effectiveSubtotal.toLocaleString("en-IN")}</span>
                </div>
                <div className="flex justify-between text-inkMuted">
                  <span>Delivery Assurance</span>
                  <span className="text-accentEmerald font-bold">FREE</span>
                </div>
                <div className="flex justify-between text-sm font-extrabold text-ink pt-2 border-t border-borderLight">
                  <span>Estimated Total</span>
                  <span className="text-brand">₹{effectiveSubtotal.toLocaleString("en-IN")}</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </main>

      {/* Order Review Modal */}
      <OrderReviewModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        riskData={riskData}
        incentiveData={incentiveData}
        cartTotal={effectiveSubtotal}
        isSubmitting={isEvaluating}
        onConfirmCod={() => executeCreateOrder("COD", 0)}
        onAcceptUpi={() => {
          const discount = incentiveData?.eligible_for_incentive
            ? Number(incentiveData.recommended_discount_inr)
            : 0;
          executeCreateOrder("Prepaid", discount);
        }}
      />
    </div>
  );
}
