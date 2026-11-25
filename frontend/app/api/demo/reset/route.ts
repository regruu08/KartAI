import { NextResponse } from "next/server";

const API_BASE =
  process.env.BACKEND_INTERNAL_URL ??
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

/**
 * Server-side proxy for POST /v1/demo/reset so DEMO_TOKEN never ships in NEXT_PUBLIC_* bundles.
 */
export async function POST() {
  const token = process.env.DEMO_TOKEN ?? "returnzero-demo-secret-2026";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10_000);

  try {
    const upstream = await fetch(`${API_BASE}/v1/demo/reset`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Demo-Token": token,
      },
      body: JSON.stringify({}),
      signal: controller.signal,
      cache: "no-store",
    });

    const data: unknown = await upstream.json().catch(() => ({
      status: upstream.ok ? "ok" : "error",
      message: upstream.statusText || "Upstream reset response",
    }));

    return NextResponse.json(data, { status: upstream.status });
  } catch (err: unknown) {
    const isAbort = err instanceof Error && err.name === "AbortError";
    return NextResponse.json(
      {
        error: isAbort ? "upstream_timeout" : "upstream_unreachable",
        message: isAbort
          ? "Backend reset request timed out after 10s."
          : "Unable to reach ReturnZero API backend for demo reset.",
      },
      { status: isAbort ? 504 : 502 },
    );
  } finally {
    clearTimeout(timeout);
  }
}
