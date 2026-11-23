import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReturnZero AI — Fit Intelligence & Delivery Assurance",
  description:
    "Next-generation fit intelligence and delivery assurance layer for D2C fashion apparel.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans bg-canvas text-ink antialiased">
        {children}
      </body>
    </html>
  );
}
