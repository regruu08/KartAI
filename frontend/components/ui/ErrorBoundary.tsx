"use client";

import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "./Button";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public override state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in production
    console.error("ErrorBoundary caught an unhandled error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public override render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="p-6 rounded-bento border border-rose-200 bg-rose-50 text-rose-900 max-w-md mx-auto my-8 text-center space-y-3">
          <div className="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center mx-auto text-rose-600">
            <AlertCircle className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold">Something went wrong in this view</h3>
          <p className="text-xs text-rose-700 leading-relaxed">
            {this.state.error?.message || "An unexpected error occurred."}
          </p>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={this.handleReset}
            className="border-rose-300 text-rose-800 hover:bg-rose-100"
          >
            <RotateCcw className="w-3.5 h-3.5 mr-1" />
            Try Again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
