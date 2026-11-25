/**
 * Documented demo heuristic matching Indian 3-digit PIN prefixes to city tiers
 * and evaluating 3-cue address completeness for Checkout Shield UI feedback.
 */
const TIER_1_PREFIXES = new Set(["110", "400", "560", "600", "700", "500", "411", "380"]);
const TIER_2_PREFIXES = new Set([
  "226",
  "302",
  "462",
  "440",
  "160",
  "641",
  "682",
  "530",
  "751",
  "800",
]);

export type CityTier = 1 | 2 | 3;

export function getCityTierFromPin(pinCode: string): CityTier {
  const digits = pinCode.replace(/\D/g, "");
  if (digits.length < 3) return 3;
  const prefix = digits.slice(0, 3);
  if (TIER_1_PREFIXES.has(prefix)) return 1;
  if (TIER_2_PREFIXES.has(prefix)) return 2;
  return 3;
}

export function isValidIndianPin(pinCode: string): boolean {
  return /^[1-9][0-9]{5}$/.test(pinCode.trim());
}

export function isValidIndianPhone(phone: string): boolean {
  return /^[6-9][0-9]{9}$/.test(phone.trim());
}

export interface AddressCompleteness {
  hasFlat: boolean;
  hasStreet: boolean;
  hasLandmark: boolean;
  score: number;
}

export function evaluateAddressCompleteness(input: {
  flat: string;
  street: string;
  landmark: string;
}): AddressCompleteness {
  const hasFlat = input.flat.trim().length >= 1;
  const hasStreet = input.street.trim().length >= 5;
  const hasLandmark = input.landmark.trim().length >= 3;
  const score = (hasFlat ? 1 : 0) + (hasStreet ? 1 : 0) + (hasLandmark ? 1 : 0);
  return { hasFlat, hasStreet, hasLandmark, score };
}

export function composeStreetAddress(input: {
  flat?: string;
  street: string;
  landmark?: string;
}): string {
  const parts = [input.flat?.trim(), input.street.trim()].filter(
    (part): part is string => Boolean(part),
  );
  const base = parts.join(", ");
  const landmark = input.landmark?.trim();
  if (landmark && !base.toLowerCase().includes(landmark.toLowerCase())) {
    return `${base}, ${landmark}`;
  }
  return base;
}
