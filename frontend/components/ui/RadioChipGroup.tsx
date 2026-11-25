"use client";

import React, { useRef, type KeyboardEvent } from "react";
import { cn } from "@/lib/cn";

export interface RadioChipOption<T extends string> {
  value: T;
  label: string;
  sublabel?: string;
  disabled?: boolean;
  tooltip?: string;
}

interface RadioChipGroupProps<T extends string> {
  ariaLabel: string;
  options: readonly RadioChipOption<T>[];
  value: T | null;
  onChange: (value: T) => void;
  layout?: "wrap" | "grid-2" | "grid-6";
  className?: string;
}

export function RadioChipGroup<T extends string>({
  ariaLabel,
  options,
  value,
  onChange,
  layout = "wrap",
  className,
}: RadioChipGroupProps<T>) {
  const buttonRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const enabledIndices = options
    .map((opt, idx) => (opt.disabled ? -1 : idx))
    .filter((idx) => idx >= 0);

  const activeIndex = options.findIndex((opt) => opt.value === value && !opt.disabled);
  const firstFocusableIndex = activeIndex >= 0 ? activeIndex : (enabledIndices[0] ?? 0);

  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, currentIndex: number): void => {
    const keys = ["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"];
    if (!keys.includes(event.key) || enabledIndices.length === 0) return;
    event.preventDefault();

    const pos = enabledIndices.indexOf(currentIndex);
    let targetPos = pos;

    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      targetPos = pos >= 0 ? (pos + 1) % enabledIndices.length : 0;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      targetPos = pos >= 0 ? (pos - 1 + enabledIndices.length) % enabledIndices.length : 0;
    } else if (event.key === "Home") {
      targetPos = 0;
    } else if (event.key === "End") {
      targetPos = enabledIndices.length - 1;
    }

    const nextIndex = enabledIndices[targetPos];
    if (nextIndex === undefined) return;
    const nextOption = options[nextIndex];
    if (!nextOption || nextOption.disabled) return;
    onChange(nextOption.value);
    buttonRefs.current[nextIndex]?.focus();
  };

  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className={cn(
        layout === "wrap" && "flex flex-wrap gap-2",
        layout === "grid-2" && "grid grid-cols-1 sm:grid-cols-2 gap-2.5",
        layout === "grid-6" && "grid grid-cols-3 sm:grid-cols-6 gap-2",
        className,
      )}
    >
      {options.map((option, index) => {
        const isChecked = value === option.value && !option.disabled;
        const tabIndex = option.disabled ? -1 : index === firstFocusableIndex ? 0 : -1;

        return (
          <button
            key={option.value}
            ref={(el) => {
              buttonRefs.current[index] = el;
            }}
            type="button"
            role="radio"
            aria-checked={isChecked}
            aria-disabled={option.disabled ? "true" : undefined}
            disabled={option.disabled}
            tabIndex={tabIndex}
            title={option.tooltip}
            onClick={() => {
              if (!option.disabled) {
                onChange(option.value);
              }
            }}
            onKeyDown={(e) => handleKeyDown(e, index)}
            className={cn(
              "min-h-[44px] px-3.5 py-2 rounded-xl border text-sm transition-all duration-200 cursor-pointer focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2",
              layout === "grid-2"
                ? "flex flex-col items-start justify-center text-left px-4 py-3"
                : "inline-flex items-center justify-center whitespace-nowrap",
              option.disabled &&
                "bg-subtle/70 text-ink-muted/60 border-line line-through cursor-not-allowed",
              !option.disabled &&
                !isChecked &&
                "bg-surface text-ink border-line-strong hover:border-brand/50 hover:bg-subtle",
              isChecked &&
                "bg-brand-soft text-brand border-brand font-semibold shadow-sm",
            )}
          >
            <span className="leading-snug">{option.label}</span>
            {option.sublabel && (
              <span
                className={cn(
                  "text-xs mt-0.5 leading-snug",
                  isChecked ? "text-brand-hover" : "text-ink-muted",
                )}
              >
                {option.sublabel}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
