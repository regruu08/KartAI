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
        canvas: "#F5F0FF",
        surface: "#FFFFFF",
        brand: "#7938F5",
        brandHover: "#6525E5",
        ink: "#171321",
        inkMuted: "#6B6280",
        border: "#D4C2FC",
        borderLight: "#E5D9FD",
        // Semantic status tokens (supporting both naming conventions)
        emerald: "#059669",
        rose: "#E11D48",
        amber: "#F59E0B",
        accentEmerald: "#059669",
        accentRose: "#E11D48",
        accentAmber: "#F59E0B",
      },
      borderRadius: {
        bento: "1rem",
      },
      boxShadow: {
        bento: "0 4px 20px -2px rgba(121, 56, 245, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
