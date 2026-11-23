"use client";

import React, { useState } from "react";
import { RotateCcw } from "lucide-react";
import { api } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";

export function DemoResetButton({ onResetComplete }: { onResetComplete?: () => void }) {
  const [isLoading, setIsLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const handleReset = async () => {
    setIsLoading(true);
    setToast(null);
    try {
      const res = await api.resetDemo("secret-demo-token-2026");
      setToast(res.message || "Database reset to 150 seeded orders");
      onResetComplete?.();
      setTimeout(() => setToast(null), 4000);
    } catch {
      setToast("Failed to reset database state.");
      setTimeout(() => setToast(null), 4000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative inline-flex items-center">
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleReset}
        isLoading={isLoading}
        className="text-inkMuted hover:text-ink text-xs border-border"
      >
        <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
        Reset Demo Data (150 Orders)
      </Button>

      {toast && (
        <div className="absolute right-0 top-10 whitespace-nowrap z-50 p-2 rounded-lg bg-surface border border-brand text-brand text-xs font-bold shadow-lg animate-in fade-in">
          {toast}
        </div>
      )}
    </div>
  );
}
