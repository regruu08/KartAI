"use client";

import React from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  title?: string;
  fallbackDescription?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string | null;
}

/**
 * Module-scoped Error Boundary so a single panel failure never triggers a white screen.
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, errorMessage: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: error.message || "Unexpected rendering error.",
    };
  }

  handleReset = () => {
    this.setState({ hasError: false, errorMessage: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          className="rounded-2xl border border-danger/20 bg-danger-soft p-5 text-ink space-y-3"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-danger shrink-0 mt-0.5" aria-hidden="true" />
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-ink">
                {this.props.title ?? "This section encountered a display error"}
              </h3>
              <p className="text-xs text-ink-muted">
                {this.props.fallbackDescription ??
                  this.state.errorMessage ??
                  "Please retry rendering this module."}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={this.handleReset}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface border border-line-strong text-xs font-semibold text-ink hover:border-brand transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
            Retry section
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
