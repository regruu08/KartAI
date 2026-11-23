"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShoppingBag, LayoutDashboard, MessageSquare } from "lucide-react";
import { useStore } from "@/lib/store";
import { cn } from "@/lib/cn";

export function Navbar() {
  const pathname = usePathname();
  const cart = useStore((s) => s.cart);
  const totalCartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const navItems = [
    { label: "Storefront", href: "/", icon: null },
    {
      label: "WhatsApp Simulator",
      href: "/simulator",
      icon: MessageSquare,
      badge: "Simulated",
    },
    {
      label: "Merchant Command Center",
      href: "/dashboard",
      icon: LayoutDashboard,
      badge: null,
    },
  ];

  return (
    <header className="sticky top-0 z-40 bg-surface/90 backdrop-blur-md border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-9 h-9 rounded-lg bg-brand flex items-center justify-center text-white font-bold text-lg shadow-sm group-hover:scale-105 transition-transform">
            RZ
          </div>
          <div>
            <div className="text-base font-extrabold tracking-tight text-ink flex items-center gap-1.5">
              ReturnZero <span className="text-brand">AI</span>
            </div>
            <p className="text-[10px] text-inkMuted uppercase tracking-wider font-semibold">
              Fit &amp; Delivery Assurance
            </p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors",
                  active
                    ? "bg-canvas text-brand border border-border"
                    : "text-inkMuted hover:text-ink hover:bg-canvas/60",
                )}
              >
                {Icon && <Icon className="w-3.5 h-3.5" />}
                {item.label}
                {item.badge && (
                  <span className="text-[9px] uppercase px-1.5 py-0.2 bg-brand/10 text-brand rounded font-bold">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right Action: Cart */}
        <div className="flex items-center gap-3">
          <Link
            href="/checkout"
            className="relative p-2 rounded-lg border border-border bg-surface hover:bg-canvas transition-colors text-ink flex items-center gap-2"
          >
            <ShoppingBag className="w-4 h-4 text-brand" />
            <span className="text-xs font-semibold hidden sm:inline">Cart</span>
            {totalCartCount > 0 && (
              <span className="w-5 h-5 rounded-full bg-brand text-white text-[10px] font-bold flex items-center justify-center">
                {totalCartCount}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
