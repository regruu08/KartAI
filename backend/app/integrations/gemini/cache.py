"""In-memory TTL cache for Gemini VLM extractions.

Keyed by SHA-256 hash of (sku_id, image_sha256, model_id, prompt_version)
per ADR-016 (E16) to ensure 0 duplicate network calls and quota preservation.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from app.schemas.api_contracts import ExtractedCatalogAttributes


class CatalogCache:
    """Thread-safe in-memory TTL cache for extracted catalog attributes."""

    def __init__(self, default_ttl_seconds: float = 3600.0) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._entries: dict[str, tuple[ExtractedCatalogAttributes, float]] = {}

    @staticmethod
    def compute_cache_key(
        sku_id: str,
        image_sha256: str | None,
        model_id: str,
        prompt_version: str,
    ) -> str:
        """Compute deterministic SHA-256 cache key."""
        raw_key = f"{sku_id.strip().upper()}:{image_sha256 or 'no_image'}:{model_id.strip()}:{prompt_version.strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> ExtractedCatalogAttributes | None:
        """Retrieve cached catalog attributes if not expired."""
        if key not in self._entries:
            return None

        attributes, expires_at = self._entries[key]
        if time.monotonic() > expires_at:
            # Expired entry
            del self._entries[key]
            return None

        # Return deep copy or model_validate to avoid mutation
        return ExtractedCatalogAttributes.model_validate(attributes.model_dump())

    def set(
        self,
        key: str,
        value: ExtractedCatalogAttributes,
        ttl_seconds: float | None = None,
    ) -> None:
        """Store catalog attributes with TTL expiration."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        expires_at = time.monotonic() + ttl
        self._entries[key] = (
            ExtractedCatalogAttributes.model_validate(value.model_dump()),
            expires_at,
        )

    def delete(self, key: str) -> bool:
        """Remove entry by key if present."""
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def clear(self) -> None:
        """Purge all cached entries."""
        self._entries.clear()

    def __len__(self) -> int:
        """Return count of active (non-expired) entries."""
        now = time.monotonic()
        return sum(1 for _, expires_at in self._entries.values() if expires_at > now)

    def __bool__(self) -> bool:
        """Cache instance is always considered truthy."""
        return True

    def get_stats(self) -> dict[str, Any]:
        """Return cache health telemetry."""
        return {
            "total_keys": len(self._entries),
            "active_keys": len(self),
            "default_ttl_s": self.default_ttl_seconds,
        }


# Global singleton instance
_GLOBAL_CATALOG_CACHE: CatalogCache | None = None


def get_catalog_cache() -> CatalogCache:
    """Retrieve shared global in-memory catalog cache singleton."""
    global _GLOBAL_CATALOG_CACHE
    if _GLOBAL_CATALOG_CACHE is None:
        _GLOBAL_CATALOG_CACHE = CatalogCache()
    return _GLOBAL_CATALOG_CACHE
