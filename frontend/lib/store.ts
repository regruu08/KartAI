/** Zustand client state store for ReturnZero AI. */

import { create } from "zustand";
import type {
  SkuResponse,
  FitRecommendationResponse,
  FitPreference,
  BrandName,
  SizeLabel,
  OrderResponse,
} from "./api/types";

export interface CartItem {
  sku: SkuResponse;
  size: string;
  quantity: number;
  fitVerified: boolean;
  knownBrand?: string;
  knownSize?: string;
  fitPreference?: string;
}

interface StoreState {
  /* Catalog */
  selectedSku: SkuResponse | null;
  setSelectedSku: (sku: SkuResponse | null) => void;

  /* Fit Twin */
  fitDrawerOpen: boolean;
  openFitDrawer: () => void;
  closeFitDrawer: () => void;
  selectedBrand: BrandName;
  setSelectedBrand: (brand: BrandName) => void;
  selectedSize: SizeLabel;
  setSelectedSize: (size: SizeLabel) => void;
  fitPreference: FitPreference;
  setFitPreference: (pref: FitPreference) => void;
  heightCm: number;
  setHeightCm: (h: number) => void;
  fitResult: FitRecommendationResponse | null;
  setFitResult: (result: FitRecommendationResponse | null) => void;

  /* Cart */
  cart: CartItem[];
  addToCart: (item: CartItem) => void;
  removeFromCart: (index: number) => void;
  clearCart: () => void;

  /* Order & Checkout */
  customerName: string;
  setCustomerName: (name: string) => void;
  customerPhone: string;
  setCustomerPhone: (phone: string) => void;
  streetAddress: string;
  setStreetAddress: (addr: string) => void;
  city: string;
  setCity: (city: string) => void;
  state: string;
  setState: (state: string) => void;
  pinCode: string;
  setPinCode: (pin: string) => void;
  landmark: string;
  setLandmark: (lm: string) => void;
  paymentMethod: "COD" | "Prepaid";
  setPaymentMethod: (pm: "COD" | "Prepaid") => void;

  placedOrder: OrderResponse | null;
  setPlacedOrder: (order: OrderResponse | null) => void;
}

export const useStore = create<StoreState>((set) => ({
  selectedSku: null,
  setSelectedSku: (sku) => set({ selectedSku: sku }),

  fitDrawerOpen: false,
  openFitDrawer: () => set({ fitDrawerOpen: true }),
  closeFitDrawer: () => set({ fitDrawerOpen: false }),
  selectedBrand: "Zara",
  setSelectedBrand: (brand) => set({ selectedBrand: brand }),
  selectedSize: "M",
  setSelectedSize: (size) => set({ selectedSize: size }),
  fitPreference: "tailored",
  setFitPreference: (pref) => set({ fitPreference: pref }),
  heightCm: 165,
  setHeightCm: (h) => set({ heightCm: h }),
  fitResult: null,
  setFitResult: (result) => set({ fitResult: result }),

  cart: [],
  addToCart: (item) =>
    set((state) => ({
      cart: [...state.cart, item],
    })),
  removeFromCart: (index) =>
    set((state) => ({
      cart: state.cart.filter((_, i) => i !== index),
    })),
  clearCart: () => set({ cart: [] }),

  customerName: "Priya Sharma",
  setCustomerName: (name) => set({ customerName: name }),
  customerPhone: "9876543210",
  setCustomerPhone: (phone) => set({ customerPhone: phone }),
  streetAddress: "Flat 402, Sunshine Heights, Near Sector 15 Market",
  setStreetAddress: (addr) => set({ streetAddress: addr }),
  city: "Delhi",
  setCity: (city) => set({ city }),
  state: "Delhi",
  setState: (state) => set({ state }),
  pinCode: "110001",
  setPinCode: (pin) => set({ pinCode: pin }),
  landmark: "Near Metro Pillar 120",
  setLandmark: (lm) => set({ landmark: lm }),
  paymentMethod: "COD",
  setPaymentMethod: (pm) => set({ paymentMethod: pm }),

  placedOrder: null,
  setPlacedOrder: (order) => set({ placedOrder: order }),
}));
