"""Gemini VLM Adapter, Resilient Client Abstraction & Circuit Breaker.

BINDING ARCHITECTURAL RULE (ADR-001 / E1):
This is the ONLY file in the entire repository permitted to import the Google GenAI
SDK (`google.genai`). Direct imports anywhere else are strictly prohibited and flagged.

Features:
- Dual-key failover (PRIMARY_GEMINI_API_KEY -> BACKUP_GEMINI_API_KEY)
- Strict hard timeout (GEMINI_TIMEOUT_S = 4.0s) enforced via asyncio.wait_for
- In-memory circuit breaker: trips for 60s after 3 consecutive failures
- Protocol interfaces: CatalogExtractorProtocol and AddressNormalizerProtocol
- Structured logging of tier and latency without leaking API keys or PII
Reference: ADR-001, ADR-016 (E16), tech_docs/01_GEMINI_VLM_PIPELINE.md.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Protocol, runtime_checkable

# Sole authorized Google GenAI SDK imports (ADR-001)
import google.genai as genai
from google.genai import types
from starlette.concurrency import run_in_threadpool

from app.config import Settings, get_settings
from app.schemas.api_contracts import (
    ExtractedCatalogAttributes,
    NormalizedAddressResult,
)

logger = logging.getLogger("returnzero.integrations.gemini")


class CircuitBreakerOpenException(Exception):
    """Raised when an API call is attempted while the circuit breaker is OPEN."""


class GeminiAPIException(Exception):
    """Raised when Gemini API invocations fail across configured tiers."""


class CircuitBreaker:
    """In-memory 3-failure / 60-second recovery circuit breaker for external AI APIs."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_s: float = 60.0,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.consecutive_failures = 0
        self.last_failure_time: float = 0.0

    @property
    def is_open(self) -> bool:
        """Return True if circuit breaker is currently open (blocking network calls)."""
        if self.consecutive_failures >= self.failure_threshold:
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed < self.recovery_timeout_s:
                return True
            # Recovery timeout elapsed: allow trial request (half-open)
        return False

    def record_success(self) -> None:
        """Reset consecutive failures upon successful API transaction."""
        self.consecutive_failures = 0
        self.last_failure_time = 0.0

    def record_failure(self) -> None:
        """Register a failure and record wall-clock failure timestamp."""
        self.consecutive_failures += 1
        self.last_failure_time = time.monotonic()

    def reset(self) -> None:
        """Explicitly reset circuit breaker state (useful for test resets)."""
        self.consecutive_failures = 0
        self.last_failure_time = 0.0


@runtime_checkable
class CatalogExtractorProtocol(Protocol):
    """Protocol defining multimodal garment catalog attribute extraction."""

    async def extract(
        self,
        sku_id: str,
        listing_text: str,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        force_refresh: bool = False,
    ) -> ExtractedCatalogAttributes:
        """Extract garment measurements, silhouette, stretch, and drape notes."""
        ...


@runtime_checkable
class AddressNormalizerProtocol(Protocol):
    """Protocol defining conversational address & landmark cleansing."""

    async def normalize(
        self,
        raw_address: str,
        landmark: str | None = None,
    ) -> NormalizedAddressResult:
        """Standardize raw address into clean format and rider instructions."""
        ...


class GeminiAdapter:
    """Resilient async adapter for Google Gemini 3.8 Flash.

    Handles non-blocking async execution, hard 4.0s timeout, dual-key failover,
    and 60s circuit breaker tripping per ADR-001 and ADR-016.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        primary_client: genai.Client | None = None,
        backup_client: genai.Client | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.model_id = self.settings.GEMINI_MODEL_ID
        self.timeout_s = self.settings.GEMINI_TIMEOUT_S
        self._primary_client = primary_client
        self._backup_client = backup_client

    def _get_primary_client(self) -> genai.Client | None:
        """Lazily initialize primary Google GenAI client."""
        if self._primary_client is None and self.settings.PRIMARY_GEMINI_API_KEY:
            self._primary_client = genai.Client(
                api_key=self.settings.PRIMARY_GEMINI_API_KEY.get_secret_value()
            )
        return self._primary_client

    def _get_backup_client(self) -> genai.Client | None:
        """Lazily initialize secondary fallback Google GenAI client."""
        if self._backup_client is None and self.settings.BACKUP_GEMINI_API_KEY:
            self._backup_client = genai.Client(
                api_key=self.settings.BACKUP_GEMINI_API_KEY.get_secret_value()
            )
        return self._backup_client

    async def _execute_sdk_call(
        self,
        client: genai.Client,
        contents: list[Any],
        config: types.GenerateContentConfig | None = None,
    ) -> str:
        """Invoke SDK models.generate_content using native async or threadpool."""
        if hasattr(client, "aio") and hasattr(client.aio, "models"):
            response = await client.aio.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=config,
            )
        else:
            # Synchronous client wrapper (ADR-016)
            response = await run_in_threadpool(
                client.models.generate_content,
                model=self.model_id,
                contents=contents,
                config=config,
            )

        text_content: str | None = getattr(response, "text", None)
        if text_content is None:
            # Check candidate parts if text property is empty
            candidates = getattr(response, "candidates", [])
            if candidates and hasattr(candidates[0], "content") and candidates[0].content.parts:
                text_content = str(candidates[0].content.parts[0].text)
            else:
                text_content = ""
        return text_content

    async def generate_content(
        self,
        contents: list[Any],
        system_instruction: str | None = None,
        response_schema: type[Any] | None = None,
        temperature: float = 0.1,
    ) -> tuple[str, str]:
        """Execute Gemini request with hard timeout, dual-key rotation, and circuit breaker.

        Returns tuple of: (response_text, key_tier_used).
        Raises CircuitBreakerOpenException if breaker is tripped.
        Raises GeminiAPIException if both keys fail or no keys configured.
        """
        # Step 1: In-memory circuit breaker inspection
        if self.circuit_breaker.is_open:
            logger.warning(
                "[CIRCUIT BREAKER OPEN] Bypassing Gemini call. Failures=%d, Recovery=%ds",
                self.circuit_breaker.consecutive_failures,
                int(self.circuit_breaker.recovery_timeout_s),
            )
            raise CircuitBreakerOpenException(
                f"Gemini circuit breaker is OPEN ({self.circuit_breaker.consecutive_failures} consecutive failures)"
            )

        primary_client = self._get_primary_client()
        backup_client = self._get_backup_client()

        if not primary_client and not backup_client:
            logger.info("[GEMINI UNCONFIGURED] No API keys available for live calls.")
            raise GeminiAPIException("No Google GenAI API keys configured in environment")

        # Build GenerateContentConfig
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            system_instruction=system_instruction,
            response_schema=response_schema,
        )

        # Step 2: Attempt Primary Key with Dynamic Timeout Budgeting
        overall_t0 = time.monotonic()
        if primary_client:
            t0 = time.monotonic()
            try:
                response_text = await asyncio.wait_for(
                    self._execute_sdk_call(primary_client, contents, config),
                    timeout=self.timeout_s,
                )
                latency_ms = (time.monotonic() - t0) * 1000
                self.circuit_breaker.record_success()
                logger.info(
                    "[GEMINI LIVE SUCCESS] tier=primary, model=%s, latency_ms=%.1f",
                    self.model_id,
                    latency_ms,
                )
                return response_text, "primary"

            except Exception as exc:
                latency_ms = (time.monotonic() - t0) * 1000
                logger.warning(
                    "[GEMINI PRIMARY FAILED] model=%s, error=%s, latency_ms=%.1f. Failing over to backup key.",
                    self.model_id,
                    type(exc).__name__,
                    latency_ms,
                )

        # Step 3: Attempt Backup Key Failover with Remaining Time Budget
        if backup_client:
            elapsed = time.monotonic() - overall_t0
            remaining_budget = self.timeout_s - elapsed
            if remaining_budget > 0.2:
                t0 = time.monotonic()
                try:
                    response_text = await asyncio.wait_for(
                        self._execute_sdk_call(backup_client, contents, config),
                        timeout=remaining_budget,
                    )
                    latency_ms = (time.monotonic() - t0) * 1000
                    self.circuit_breaker.record_success()
                    logger.info(
                        "[GEMINI LIVE SUCCESS] tier=backup, model=%s, latency_ms=%.1f",
                        self.model_id,
                        latency_ms,
                    )
                    return response_text, "backup"

                except Exception as exc:
                    latency_ms = (time.monotonic() - t0) * 1000
                    self.circuit_breaker.record_failure()
                    logger.warning(
                        "[GEMINI BACKUP FAILED] model=%s, error=%s, latency_ms=%.1f. Breaker status: %d/%d.",
                        self.model_id,
                        type(exc).__name__,
                        latency_ms,
                        self.circuit_breaker.consecutive_failures,
                        self.circuit_breaker.failure_threshold,
                    )
                    raise GeminiAPIException(
                        f"Gemini primary and backup keys failed (latest error: {type(exc).__name__})"
                    ) from exc
            else:
                logger.warning(
                    "[GEMINI BACKUP SKIPPED] Timeout budget exhausted (elapsed=%.2fs >= %.2fs)",
                    elapsed,
                    self.timeout_s,
                )
                self.circuit_breaker.record_failure()
                raise GeminiAPIException(
                    f"Gemini timeout budget ({self.timeout_s}s) exhausted before backup attempt"
                )

        # If primary failed and no backup was configured
        self.circuit_breaker.record_failure()
        raise GeminiAPIException("Gemini primary call failed and no backup key configured")
