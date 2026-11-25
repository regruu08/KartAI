"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  CreditCard,
  Lock,
  ShieldCheck,
  Truck,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api/client";
import type { IncentiveQuoteResponse, RiskEvaluateResponse } from "@/lib/api/types";
import { FALLBACK_CATALOG_SKUS, getSkuDisplayMeta } from "@/lib/catalog";
import { formatInr } from "@/lib/format";
import { composeStreetAddress, isValidIndianPin, type CityTier } from "@/lib/pin";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/cn";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";
import { Button } from "@/components/ui/Button";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { GarmentImage } from "@/components/ui/GarmentImage";
import { OrderReviewModal } from "@/components/checkout/OrderReviewModal";
import { ShieldReviewPanel } from "@/components/checkout/ShieldReviewPanel";

const DEMO_TIER_PINS: Record<CityTier, { pin: string; city: string; state: string }> = {
  1: { pin: "110001", city: "Delhi", state: "Delhi" },
  2: { pin: "302001", city: "Jaipur", state: "Rajasthan" },
  3: { pin: "151001", city: "Bhatinda", state: "Punjab" },
};

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

  const [tierOverride, setTierOverride] = useState<CityTier | null>(null);
  const [liveRisk, setLiveRisk] = useState<RiskEvaluateResponse | null>(null);
  const [isRechecking, setIsRechecking] = useState(false);

  const [isEvaluating, setIsEvaluating] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [riskData, setRiskData] = useState<RiskEvaluateResponse | null>(null);
  const [incentiveData, setIncentiveData] = useState<IncentiveQuoteResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const defaultDemoSku = FALLBACK_CATALOG_SKUS[0]!;
  const subtotal = cart.reduce(
    (sum, item) => sum + Number(item.sku.price_inr) * item.quantity,
    0,
  );
  const effectiveSubtotal = subtotal > 0 ? subtotal : Number(defaultDemoSku.price_inr);
  const hasFitVerification = cart.length > 0 ? cart.some((i) => i.fitVerified) : false;

  const skuIds = cart.map((i) => i.sku.id);
  const hasBracketing = new Set(skuIds).size < skuIds.length;

  // Debounced live risk preview for 3-Check Shield panel
  useEffect(() => {
    const cleanPin = pinCode.trim();
    if (!isValidIndianPin(cleanPin) || streetAddress.trim().length < 3) {
      setLiveRisk(null);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setIsRechecking(true);
      try {
        const res = await api.evaluateRisk(
          {
            street_address: composeStreetAddress({ street: streetAddress, landmark }),
            pin_code: cleanPin,
            payment_method: paymentMethod,
            has_used_fit_twin: hasFitVerification,
            is_bracketing: hasBracketing,
          },
          controller.signal,
        );
        if (!controller.signal.aborted) {
          setLiveRisk(res);
        }
      } catch {
        // Non-blocking live preview; primary review button evaluates explicitly
      } finally {
        if (!controller.signal.aborted) {
          setIsRechecking(false);
        }
      }
    }, 350);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [streetAddress, landmark, pinCode, paymentMethod, hasFitVerification, hasBracketing]);

  const handleTierOverride = (tier: CityTier | null) => {
    setTierOverride(tier);
    if (tier !== null) {
      const preset = DEMO_TIER_PINS[tier];
      setPinCode(preset.pin);
      setCity(preset.city);
      setState(preset.state);
    }
  };

  const handleProceedToReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!/^\d{6}$/.test(pinCode.trim())) {
      setErrorMessage("Please enter a valid 6-digit Indian PIN code.");
      return;
    }

    setIsEvaluating(true);

    try {
      if (paymentMethod === "COD") {
        const riskRes = await api.evaluateRisk({
          street_address: composeStreetAddress({ street: streetAddress, landmark }),
          pin_code: pinCode.trim(),
          payment_method: "COD",
          has_used_fit_twin: hasFitVerification,
          is_bracketing: hasBracketing,
        });

        const incRes = await api.getIncentiveQuote({
          cart_total_inr: effectiveSubtotal,
          risk_score_index: riskRes.risk_score_index,
          current_payment: "COD",
          has_used_fit_twin: hasFitVerification,
        });

        setRiskData(riskRes);
        setLiveRisk(riskRes);
        setIncentiveData(incRes);
        setModalOpen(true);
      } else {
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
      const skuId = activeItem?.sku.id ?? defaultDemoSku.id;
      const size = activeItem?.size ?? "L";

      const order = await api.createOrder({
        sku_id: skuId,
        size,
        quantity: activeItem?.quantity ?? 1,
        customer_name: customerName,
        customer_phone: customerPhone,
        street_address: composeStreetAddress({ street: streetAddress, landmark }),
        city,
        state,
        pin_code: pinCode.trim(),
        payment_method: confirmedPaymentMethod,
        applied_discount_inr: appliedDiscount,
        incentive_reason_code:
          appliedDiscount > 0
            ? (incentiveData?.reason_code ?? "REASON_ELEVATED_RISK_CONVERTIBLE")
            : undefined,
        has_used_fit_twin: hasFitVerification,
        is_bracketing: hasBracketing,
        known_brand: activeItem?.knownBrand,
        known_size: activeItem?.knownSize,
        fit_preference: activeItem?.fitPreference,
      });

      setPlacedOrder(order);
      clearCart();
      setModalOpen(false);
      toast.success(`Order ${order.order_number} confirmed`);
      router.push(`/confirmation/${order.id}`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : "Order creation failed.");
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />

      <main
        id="main-content"
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 flex-1 w-full"
      >
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-muted hover:text-brand transition-colors"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            <span>Continue Shopping</span>
          </Link>
        </div>

        <div className="mb-8 space-y-1">
          <p className="text-xs font-medium text-ink-muted">ReturnZero Checkout Shield</p>
          <h1 className="font-display text-3xl sm:text-4xl text-ink">
            Checkout &amp; Delivery Assurance
          </h1>
        </div>

        {errorMessage && (
          <div
            role="alert"
            className="p-4 mb-6 rounded-2xl bg-danger-soft border border-danger/25 text-danger text-xs font-semibold"
          >
            {errorMessage}
          </div>
        )}

        {hasBracketing && (
          <div className="p-4 mb-6 rounded-2xl bg-warn-soft border border-warn/35 text-warn-text text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-warn shrink-0 mt-0.5" aria-hidden="true" />
            <div>
              <strong className="block font-semibold">Multi-Size Cart Detected (Bracketing)</strong>
              Your cart contains multiple sizes of identical items. Confirming one verified size
              protects your priority dispatch score.
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Form: Delivery Address + Payment Selection */}
          <form onSubmit={handleProceedToReview} className="lg:col-span-7 space-y-6">
            <section className="rounded-2xl border border-line bg-surface p-6 sm:p-7 space-y-4 shadow-card">
              <h2 className="font-display text-xl text-ink flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-brand" aria-hidden="true" />
                <span>Delivery Address Information</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label htmlFor="customerName" className="block text-ink font-semibold mb-1.5">
                    Customer Full Name
                  </label>
                  <input
                    id="customerName"
                    type="text"
                    required
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink focus:bg-surface focus:border-brand"
                  />
                </div>
                <div>
                  <label htmlFor="customerPhone" className="block text-ink font-semibold mb-1.5">
                    Mobile Phone (WhatsApp)
                  </label>
                  <input
                    id="customerPhone"
                    type="tel"
                    required
                    value={customerPhone}
                    onChange={(e) => setCustomerPhone(e.target.value)}
                    className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink tabular-nums focus:bg-surface focus:border-brand"
                  />
                </div>
              </div>

              <div className="text-xs">
                <label htmlFor="streetAddress" className="block text-ink font-semibold mb-1.5">
                  Street Address / House No.
                </label>
                <textarea
                  id="streetAddress"
                  required
                  rows={2}
                  value={streetAddress}
                  onChange={(e) => setStreetAddress(e.target.value)}
                  className="w-full p-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink focus:bg-surface focus:border-brand"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <label htmlFor="pinCode" className="block text-ink font-semibold mb-1.5">
                    PIN Code (6 Digits)
                  </label>
                  <input
                    id="pinCode"
                    type="text"
                    required
                    maxLength={6}
                    value={pinCode}
                    onChange={(e) => {
                      setTierOverride(null);
                      setPinCode(e.target.value.replace(/\D/g, ""));
                    }}
                    className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink tabular-nums focus:bg-surface focus:border-brand"
                  />
                </div>
                <div>
                  <label htmlFor="city" className="block text-ink font-semibold mb-1.5">
                    City
                  </label>
                  <input
                    id="city"
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink focus:bg-surface focus:border-brand"
                  />
                </div>
                <div>
                  <label htmlFor="state" className="block text-ink font-semibold mb-1.5">
                    State
                  </label>
                  <input
                    id="state"
                    type="text"
                    required
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink focus:bg-surface focus:border-brand"
                  />
                </div>
              </div>

              <div className="text-xs">
                <label htmlFor="landmark" className="block text-ink font-semibold mb-1.5">
                  Landmark (Optional — helps riders locate entrance)
                </label>
                <input
                  id="landmark"
                  type="text"
                  placeholder="e.g. Near Metro Pillar 120"
                  value={landmark}
                  onChange={(e) => setLandmark(e.target.value)}
                  className="w-full min-h-[44px] px-3.5 rounded-xl border border-line-strong bg-canvas/50 text-sm text-ink focus:bg-surface focus:border-brand"
                />
              </div>
            </section>

            {/* Payment Method */}
            <section className="rounded-2xl border border-line bg-surface p-6 sm:p-7 space-y-4 shadow-card">
              <div>
                <h2 className="font-display text-xl text-ink">Payment Method</h2>
                <p className="text-xs text-ink-muted mt-0.5">
                  Cash on Delivery is always available. Select your preferred option below.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <label
                  className={cn(
                    "p-4 rounded-2xl border flex items-center justify-between cursor-pointer transition-all",
                    paymentMethod === "COD"
                      ? "border-brand bg-brand-soft/45 font-semibold shadow-sm"
                      : "border-line-strong bg-surface text-ink-muted hover:bg-subtle",
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === "COD"}
                      onChange={() => setPaymentMethod("COD")}
                      className="accent-brand"
                    />
                    <Truck className="w-4 h-4 text-ink" aria-hidden="true" />
                    <span className="text-ink">Cash on Delivery (COD)</span>
                  </div>
                  <span className="text-[11px] font-medium text-ink-muted">Guaranteed</span>
                </label>

                <label
                  className={cn(
                    "p-4 rounded-2xl border flex items-center justify-between cursor-pointer transition-all",
                    paymentMethod === "Prepaid"
                      ? "border-brand bg-brand-soft/45 font-semibold shadow-sm"
                      : "border-line-strong bg-surface text-ink-muted hover:bg-subtle",
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === "Prepaid"}
                      onChange={() => setPaymentMethod("Prepaid")}
                      className="accent-brand"
                    />
                    <CreditCard className="w-4 h-4 text-brand" aria-hidden="true" />
                    <span className="text-ink">Instant UPI / Prepaid</span>
                  </div>
                  <span className="text-[11px] text-trust-text font-semibold">Priority</span>
                </label>
              </div>
            </section>

            <Button type="submit" isLoading={isEvaluating} fullWidth size="lg">
              <Lock className="w-4 h-4" aria-hidden="true" />
              <span>
                {paymentMethod === "COD"
                  ? "Review Order Safety & Place"
                  : "Confirm & Pay via UPI"}
              </span>
            </Button>
          </form>

          {/* Right Summary + 3-Check Shield Review */}
          <aside className="lg:col-span-5 lg:sticky lg:top-24 space-y-5">
            <section className="rounded-2xl border border-line bg-surface p-5 space-y-4 shadow-card">
              <h2 className="font-display text-xl text-ink">Order Summary</h2>

              {cart.length === 0 ? (
                <div className="flex items-start gap-3.5 p-3.5 rounded-xl bg-subtle border border-line text-xs">
                  <GarmentImage
                    src={getSkuDisplayMeta(defaultDemoSku).image}
                    alt={defaultDemoSku.name}
                    garmentName={defaultDemoSku.name}
                    className="w-14 h-16 rounded-lg border border-line shrink-0"
                  />
                  <div className="space-y-1">
                    <p className="font-semibold text-ink">{defaultDemoSku.name}</p>
                    <p className="text-ink-muted">
                      Demo Checkout Fallback (Size L, 1 item — {formatInr(effectiveSubtotal)})
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {cart.map((item, idx) => (
                    <div
                      key={`${item.sku.id}-${item.size}-${idx}`}
                      className="flex items-start justify-between gap-3 text-xs pb-3 border-b border-line last:border-b-0"
                    >
                      <div className="flex items-start gap-3">
                        <GarmentImage
                          src={getSkuDisplayMeta(item.sku).image}
                          alt={item.sku.name}
                          garmentName={item.sku.name}
                          className="w-12 h-14 rounded-lg border border-line shrink-0"
                        />
                        <div>
                          <div className="font-semibold text-ink">{item.sku.name}</div>
                          <div className="text-ink-muted mt-0.5">
                            Size <span className="font-semibold text-brand">{item.size}</span>, Qty{" "}
                            {item.quantity}
                          </div>
                          {item.fitVerified && (
                            <span className="inline-flex items-center gap-1 text-[11px] text-trust-text font-medium mt-1">
                              <CheckCircle2 className="w-3 h-3" aria-hidden="true" />
                              Fit-Twin Verified
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="font-semibold text-ink tabular-nums">
                        {formatInr(Number(item.sku.price_inr) * item.quantity)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <dl className="pt-3 border-t border-line space-y-2 text-xs tabular-nums">
                <div className="flex justify-between text-ink-muted">
                  <dt>Subtotal</dt>
                  <dd className="text-ink">{formatInr(effectiveSubtotal)}</dd>
                </div>
                <div className="flex justify-between text-ink-muted">
                  <dt>Delivery Assurance</dt>
                  <dd className="text-trust-text font-semibold">Complimentary</dd>
                </div>
                <div className="flex justify-between text-sm font-bold text-ink pt-2 border-t border-line">
                  <dt>Estimated Total</dt>
                  <dd className="text-brand">{formatInr(effectiveSubtotal)}</dd>
                </div>
              </dl>
            </section>

            <ErrorBoundary title="Shield risk panel unavailable">
              <ShieldReviewPanel
                streetAddress={streetAddress}
                landmark={landmark}
                pinCode={pinCode}
                risk={liveRisk}
                isRechecking={isRechecking}
                tierOverride={tierOverride}
                onTierOverrideChange={handleTierOverride}
              />
            </ErrorBoundary>
          </aside>
        </div>
      </main>

      <Footer />

      <ErrorBoundary title="Order review modal unavailable">
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
      </ErrorBoundary>
    </div>
  );
}
