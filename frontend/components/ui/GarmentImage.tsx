"use client";

import React, { useState } from "react";
import { cn } from "@/lib/cn";

interface GarmentImageProps {
  src: string;
  hoverSrc?: string;
  alt: string;
  garmentName: string;
  className?: string;
  imgClassName?: string;
  cropMode?: "full" | "upper" | "lower";
  hoverZoom?: boolean;
  priority?: boolean;
}

/**
 * Responsive fashion photography container with crisp editorial aspect framing,
 * optional hover detail crossfade, and non-blocking typographic fallback.
 */
export function GarmentImage({
  src,
  hoverSrc,
  alt,
  garmentName,
  className,
  imgClassName,
  cropMode = "full",
  hoverZoom = false,
  priority = false,
}: GarmentImageProps) {
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return (
      <div
        role="img"
        aria-label={alt}
        className={cn(
          "flex items-center justify-center bg-subtle border border-line p-6 text-center select-none",
          className,
        )}
      >
        <div className="space-y-2 max-w-[18ch]">
          <span className="block text-xs tracking-wide text-ink-muted">ReturnZero Atelier</span>
          <p className="font-display italic text-lg text-ink leading-snug">{garmentName}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("relative overflow-hidden bg-subtle", className)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        decoding="async"
        referrerPolicy="no-referrer"
        onError={() => setHasError(true)}
        className={cn(
          "h-full w-full object-cover object-top transition-transform duration-700 ease-out",
          cropMode === "upper" && "object-[50%_18%] scale-[1.28]",
          cropMode === "lower" && "object-[50%_72%] scale-[1.25]",
          hoverZoom && cropMode === "full" && !hoverSrc && "group-hover:scale-[1.03]",
          imgClassName,
        )}
      />

      {hoverSrc && cropMode === "full" && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={hoverSrc}
          alt=""
          aria-hidden="true"
          loading="lazy"
          decoding="async"
          className="absolute inset-0 h-full w-full object-cover object-center opacity-0 transition-opacity duration-500 ease-out group-hover:opacity-100 motion-reduce:hidden"
        />
      )}
    </div>
  );
}
