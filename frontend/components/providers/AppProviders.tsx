"use client";

import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "framer-motion";
import { Toaster } from "sonner";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 10_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <MotionConfig reducedMotion="user">
        {children}
        <Toaster
          position="bottom-right"
          richColors
          closeButton
          toastOptions={{
            className: "font-sans text-sm rounded-xl border border-line shadow-card",
          }}
        />
      </MotionConfig>
    </QueryClientProvider>
  );
}
