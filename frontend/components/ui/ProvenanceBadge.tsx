import React from "react";
import { Sparkles, Database, FileText } from "lucide-react";
import { Badge } from "./Badge";

export interface ProvenanceBadgeProps {
  provenance: string;
  className?: string;
}

export function ProvenanceBadge({ provenance, className }: ProvenanceBadgeProps) {
  switch (provenance) {
    case "live_gemini":
      return (
        <Badge variant="emerald" className={className}>
          <Sparkles className="w-3 h-3 text-accentEmerald" />
          Live Gemini 3.8 Flash VLM
        </Badge>
      );
    case "cached":
      return (
        <Badge variant="brand" className={className}>
          <Database className="w-3 h-3 text-brand" />
          Verified Extraction Cache
        </Badge>
      );
    case "manual_fixture":
    default:
      return (
        <Badge variant="neutral" className={className}>
          <FileText className="w-3 h-3 text-gray-500" />
          Standard Verified Fixture
        </Badge>
      );
  }
}
