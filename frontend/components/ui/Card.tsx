import React from "react";
import { cn } from "@/lib/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

export function Card({ className, glass = false, children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-bento border border-border p-5 md:p-6 shadow-bento",
        glass ? "bg-surface/80 backdrop-blur-md" : "bg-surface",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
