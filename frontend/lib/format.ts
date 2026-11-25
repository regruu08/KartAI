const inrFormatter = new Intl.NumberFormat("en-IN", {
  maximumFractionDigits: 0,
});

export function formatInr(amount: number | string): string {
  const numeric = typeof amount === "string" ? Number(amount) : amount;
  if (Number.isNaN(numeric)) return "₹0";
  const rounded = Math.round(numeric);
  const prefix = rounded < 0 ? "-₹" : "₹";
  return `${prefix}${inrFormatter.format(Math.abs(rounded))}`;
}

export function formatIndianNumber(value: number): string {
  if (Number.isNaN(value)) return "0";
  return inrFormatter.format(Math.round(value));
}

export function formatSignedInches(inches: number): string {
  const fixed = Math.abs(inches).toFixed(1);
  if (inches > 0) return `+${fixed}"`;
  if (inches < 0) return `-${fixed}"`;
  return `0.0"`;
}

export function cmToFeetInches(cm: number): string {
  const totalInches = Math.round(cm / 2.54);
  const feet = Math.floor(totalInches / 12);
  const inches = totalInches % 12;
  return `${feet}' ${inches}"`;
}
