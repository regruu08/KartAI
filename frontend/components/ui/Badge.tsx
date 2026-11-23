import React from "react";
import { cn } from "@/lib/cn";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "brand" | "emerald" | "amber" | "rose" | "neutral" | "outline";
}

export function Badge({
  className,
  variant = "brand",
  children,
  ...props
}: BadgeProps) {
  const variantStyles = {
    brand: "bg-canvas text-brand border border-border",
    emerald: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    amber: "bg-amber-50 text-amber-700 border border-amber-200",
    rose: "bg-rose-50 text-rose-700 border border-rose-200",
    neutral: "bg-gray-100 text-gray-700 border border-gray-200",
    outline: "bg-transparent text-inkMuted border border-borderLight",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide",
        variantStyles[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
