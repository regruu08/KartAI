"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, ShoppingBag, X } from "lucide-react";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/cn";

const NAV_ITEMS = [
  { label: "Storefront", href: "/" },
  { label: "Delivery Simulator", href: "/simulator" },
  { label: "Merchant Command", href: "/dashboard" },
] as const;

export function Navbar() {
  const pathname = usePathname() ?? "/";
  const cart = useStore((s) => s.cart);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const totalCartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const isActive = (href: string): boolean => {
    if (href === "/") return pathname === "/" || pathname.startsWith("/products");
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-40 bg-canvas/95 backdrop-blur-md border-b border-line">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-6">
        <Link
          href="/"
          className="font-display text-xl sm:text-2xl tracking-tight text-ink whitespace-nowrap shrink-0 rounded-md px-1 -ml-1 focus-visible:ring-2 focus-visible:ring-brand"
        >
          ReturnZero <span className="text-brand font-semibold">AI</span>
        </Link>

        <nav aria-label="Primary navigation" className="hidden md:flex items-center gap-8">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "relative inline-flex items-center py-2 text-sm font-medium whitespace-nowrap shrink-0 transition-colors duration-200",
                  active ? "text-ink" : "text-ink-muted hover:text-ink",
                )}
              >
                <span>{item.label}</span>
                {active && (
                  <motion.span
                    layoutId="nav-active-underline"
                    transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                    className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-brand"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2.5 shrink-0">
          <Link
            href="/checkout"
            aria-label={totalCartCount > 0 ? `Cart, ${totalCartCount} item` : "Cart, empty"}
            className="relative inline-flex items-center justify-center gap-2 min-h-[42px] min-w-[42px] px-4 rounded-full border border-line-strong bg-surface text-ink hover:border-brand/60 hover:bg-subtle transition-colors duration-200 whitespace-nowrap shrink-0"
          >
            <ShoppingBag className="w-4 h-4 text-brand" aria-hidden="true" />
            <span className="text-xs font-semibold tabular-nums">
              {totalCartCount > 0 ? `Bag (${totalCartCount})` : "Bag"}
            </span>
          </Link>

          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-nav-panel"
            aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
            className="md:hidden inline-flex items-center justify-center min-h-[42px] min-w-[42px] rounded-full border border-line-strong bg-surface text-ink hover:bg-subtle cursor-pointer"
          >
            {mobileMenuOpen ? (
              <X className="w-5 h-5" aria-hidden="true" />
            ) : (
              <Menu className="w-5 h-5" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.nav
            id="mobile-nav-panel"
            aria-label="Mobile navigation"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            className="md:hidden border-t border-line bg-surface px-4 py-3 space-y-1 shadow-card"
          >
            {NAV_ITEMS.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center justify-between min-h-[44px] px-3.5 rounded-xl text-sm font-medium transition-colors",
                    active ? "bg-brand-soft text-brand" : "text-ink hover:bg-subtle",
                  )}
                >
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
