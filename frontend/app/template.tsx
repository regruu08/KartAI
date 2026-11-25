"use client";

import React from "react";
import { motion } from "framer-motion";

/**
 * Route-level GPU-composited transition wrapper.
 * Automatically mounts cleanly on every Next.js App Router navigation switch.
 */
export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      className="min-h-screen flex flex-col"
    >
      {children}
    </motion.div>
  );
}
