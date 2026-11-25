import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Canonical ReturnZero Atelier design tokens (ADR-023)
        canvas: "#FAF8FD",
        surface: "#FFFFFF",
        subtle: "#F9F6FE",
        line: "#F0EAF8",
        "line-strong": "#DFD5EE",
        brand: "#6D28D9",
        brandHover: "#5B21B6",
        "brand-hover": "#5B21B6",
        "brand-soft": "#F3E8FF",
        ink: "#171321",
        inkMuted: "#585266",
        "ink-muted": "#585266",
        trust: "#059669",
        "trust-soft": "#ECFDF5",
        "trust-text": "#047857",
        warn: "#D97706",
        "warn-soft": "#FFFBEB",
        "warn-text": "#92400E",
        danger: "#B42318",
        "danger-soft": "#FEF3F2",
        border: "#EAE3F5",
        borderLight: "#F0EAF8",
        // Semantic aliases that do NOT clobber Tailwind's built-in 50-950 scales
        accentEmerald: "#059669",
        accentRose: "#E11D48",
        accentAmber: "#D97706",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "-apple-system", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        bento: "1rem",
      },
      boxShadow: {
        bento: "0 1px 2px rgba(23, 19, 33, 0.04), 0 8px 30px rgba(109, 40, 217, 0.06)",
        card: "0 1px 2px rgba(23, 19, 33, 0.04), 0 8px 30px rgba(109, 40, 217, 0.06)",
        lift: "0 12px 40px rgba(109, 40, 217, 0.14)",
      },
    },
  },
  plugins: [],
};

export default config;
