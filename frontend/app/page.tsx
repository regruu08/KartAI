import React from "react";
import { AnnouncementBar } from "@/components/layout/AnnouncementBar";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/ui/Navbar";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { HeroSection } from "@/components/home/HeroSection";
import { LiveFitPreview } from "@/components/home/LiveFitPreview";
import { CatalogBrowser } from "@/components/home/CatalogBrowser";
import { TrustBento } from "@/components/home/TrustBento";

export default function StorefrontHome() {
  return (
    <div className="min-h-screen bg-canvas text-ink flex flex-col">
      <AnnouncementBar />
      <Navbar />

      <main id="main-content" className="flex-1">
        <ErrorBoundary title="Storefront hero failed to render">
          <HeroSection />
        </ErrorBoundary>

        <ErrorBoundary title="Interactive fit preview failed to render">
          <LiveFitPreview />
        </ErrorBoundary>

        <ErrorBoundary title="Product catalog failed to render">
          <CatalogBrowser />
        </ErrorBoundary>

        <TrustBento />
      </main>

      <Footer />
    </div>
  );
}
