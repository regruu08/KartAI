"""Lightweight per-IP sliding-window rate limiter for Gemini-backed endpoints.

Protects external LLM API quota on public deployments without requiring Redis.
Reference: AGENTS.md §6.2.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """In-memory per-IP sliding-window request rate limiter."""

    def __init__(self, max_requests: int = 30, window_seconds: float = 60.0) -> None:
        self.max_requests = max(1, max_requests)
        self.window_seconds = max(1.0, window_seconds)
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, client_key: str) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds) for a given client identifier."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        bucket = self._buckets[client_key]

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            oldest = bucket[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest)) + 1)
            return False, retry_after

        bucket.append(now)
        return True, 0

    def reset(self) -> None:
        """Clear all rate-limit tracking buckets."""
        self._buckets.clear()


def get_client_ip(request: Request) -> str:
    """Extract client IP safely, respecting X-Forwarded-For when behind a proxy."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_hop = forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


async def enforce_extract_rate_limit(request: Request) -> None:
    """FastAPI dependency enforcing per-IP limits on /v1/catalog/skus/{id}/extract."""
    limiter: SlidingWindowRateLimiter | None = getattr(
        request.app.state, "extract_rate_limiter", None
    )
    if limiter is None:
        return

    client_ip = get_client_ip(request)
    allowed, retry_after = limiter.allow(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for catalog attribute extraction. Please retry shortly.",
            headers={"Retry-After": str(retry_after)},
        )
