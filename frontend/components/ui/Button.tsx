import React from "react";
import { cn } from "@/lib/cn";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "subtle" | "danger";
  size?: "sm" | "md" | "lg";
  fullWidth?: boolean;
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      fullWidth = false,
      isLoading = false,
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-semibold rounded-full whitespace-nowrap transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer";

    const variantStyles = {
      primary:
        "bg-brand text-white hover:bg-brandHover shadow-sm active:scale-[0.99]",
      secondary:
        "bg-brand-soft text-brand hover:bg-brand-soft/80 border border-brand/20",
      outline:
        "border border-line-strong bg-surface text-ink hover:border-brand/50 hover:bg-subtle active:bg-brand-soft/40",
      subtle:
        "border border-line bg-subtle text-ink hover:bg-line/50",
      ghost: "text-ink hover:bg-subtle",
      danger: "bg-danger text-white hover:bg-rose-800 shadow-sm",
    };

    const sizeStyles = {
      sm: "min-h-[38px] px-4 py-1.5 text-xs gap-1.5",
      md: "min-h-[44px] px-5 py-2.5 text-sm gap-2",
      lg: "min-h-[48px] px-6 py-3 text-sm sm:text-base gap-2",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          fullWidth && "w-full",
          className,
        )}
        {...props}
      >
        {isLoading && (
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" />
        )}
        {children}
      </button>
    );
  },
);

Button.displayName = "Button";
