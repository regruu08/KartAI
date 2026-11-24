"""Unit tests for Gemini VLM Client Adapter, Protocols & Circuit Breaker.

Tests mocked SDK responses, protocol compliance, timeout enforcement, dual-key rotation,
circuit breaker state transitions, and secret-safe logging per ADR-001, ADR-016.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from app.config import Settings
from app.integrations.gemini.adapter import (
    AddressNormalizerProtocol,
    CatalogExtractorProtocol,
    CircuitBreaker,
    CircuitBreakerOpenException,
    GeminiAdapter,
    GeminiAPIException,
)
from app.integrations.gemini.cache import CatalogCache
from app.integrations.gemini.extractor import CatalogExtractor
from app.integrations.gemini.normalizer import AddressNormalizer, clean_address_text
from app.schemas.api_contracts import (
    ExtractedCatalogAttributes,
    NormalizedAddressResult,
)


class FakeCandidate:
    def __init__(self, text: str) -> None:
        part = MagicMock()
        part.text = text
        self.content = MagicMock()
        self.content.parts = [part]


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text
        self.candidates = [FakeCandidate(text)]


def make_mock_client(
    response_text: str = '{"status": "ok"}', error: Exception | None = None
) -> MagicMock:
    """Create a mock genai.Client with native async aio.models.generate_content."""
    client = MagicMock()
    mock_generate = AsyncMock()
    if error:
        mock_generate.side_effect = error
    else:
        mock_generate.return_value = FakeResponse(response_text)
    client.aio.models.generate_content = mock_generate
    return client


def test_protocol_compliance() -> None:
    """Verify that concrete extractor and normalizer satisfy runtime-checkable Protocols."""
    extractor = CatalogExtractor()
    normalizer = AddressNormalizer()

    assert isinstance(extractor, CatalogExtractorProtocol)
    assert isinstance(normalizer, AddressNormalizerProtocol)


@pytest.mark.asyncio
async def test_primary_client_success() -> None:
    """Verify standard happy path execution using primary API key."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-key-123"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-key-456"),
        GEMINI_TIMEOUT_S=4.0,
    )
    mock_primary = make_mock_client('{"extracted": true}')
    mock_backup = make_mock_client('{"extracted": "backup"}')

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )

    text, tier = await adapter.generate_content(contents=["Extract catalog"])
    assert text == '{"extracted": true}'
    assert tier == "primary"
    assert mock_primary.aio.models.generate_content.called
    assert not mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_dual_key_failover_on_primary_error() -> None:
    """Verify immediate failover to backup key when primary key returns 429 or 5xx."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-key-123"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-key-456"),
        GEMINI_TIMEOUT_S=4.0,
    )
    # Primary fails with simulated 429 quota exhaustion
    mock_primary = make_mock_client(error=RuntimeError("HTTP 429: Resource exhausted"))
    # Backup succeeds
    mock_backup = make_mock_client('{"backup_success": true}')

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )

    text, tier = await adapter.generate_content(contents=["Extract catalog"])
    assert text == '{"backup_success": true}'
    assert tier == "backup"
    assert mock_primary.aio.models.generate_content.called
    assert mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_dual_key_budget_exhaustion_on_primary_timeout() -> None:
    """Verify backup call is skipped and GeminiAPIException raised when primary exhausts timeout budget."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-key-123"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-key-456"),
        GEMINI_TIMEOUT_S=0.1,  # Short timeout for test
    )

    async def slow_primary(*args: object, **kwargs: object) -> FakeResponse:
        await asyncio.sleep(0.5)
        return FakeResponse('{"too_late": true}')

    mock_primary = MagicMock()
    mock_primary.aio.models.generate_content = slow_primary

    mock_backup = make_mock_client('{"recovered_by_backup": true}')

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )

    with pytest.raises(GeminiAPIException) as exc_info:
        await adapter.generate_content(contents=["Extract catalog"])

    assert "exhausted before backup attempt" in str(exc_info.value)
    assert not mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_both_keys_failing_raises_gemini_api_exception() -> None:
    """Verify GeminiAPIException is raised when both primary and backup keys fail."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-key-123"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-key-456"),
        GEMINI_TIMEOUT_S=4.0,
    )
    mock_primary = make_mock_client(error=RuntimeError("Primary HTTP 500"))
    mock_backup = make_mock_client(error=RuntimeError("Backup HTTP 503"))

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )

    with pytest.raises(GeminiAPIException) as exc_info:
        await adapter.generate_content(contents=["Extract catalog"])

    assert "Gemini primary and backup keys failed" in str(exc_info.value)
    assert adapter.circuit_breaker.consecutive_failures == 1


@pytest.mark.asyncio
async def test_circuit_breaker_trips_after_three_failures() -> None:
    """Verify in-memory circuit breaker trips for 60s after 3 consecutive failures."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60.0)
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-key-123"),
        GEMINI_TIMEOUT_S=4.0,
    )
    mock_client = make_mock_client(error=RuntimeError("Provider outage"))

    adapter = GeminiAdapter(
        settings=settings,
        circuit_breaker=breaker,
        primary_client=mock_client,
    )

    # Induce 3 consecutive failures
    for i in range(1, 4):
        with pytest.raises(GeminiAPIException):
            await adapter.generate_content(contents=["ping"])
        assert breaker.consecutive_failures == i

    is_open_tripped = breaker.is_open
    assert is_open_tripped is True

    # 4th call should immediately raise CircuitBreakerOpenException without invoking client
    call_count_before = mock_client.aio.models.generate_content.call_count
    with pytest.raises(CircuitBreakerOpenException) as exc_info:
        await adapter.generate_content(contents=["ping"])

    assert "circuit breaker is OPEN" in str(exc_info.value)
    # Zero network calls attempted while circuit breaker is open
    assert mock_client.aio.models.generate_content.call_count == call_count_before

    # Verify manual reset works
    breaker.reset()
    is_open_after_reset = breaker.is_open
    assert is_open_after_reset is False
    assert breaker.consecutive_failures == 0


@pytest.mark.asyncio
async def test_unconfigured_keys_raises_gemini_api_exception() -> None:
    """Verify that invoking adapter without API keys cleanly raises GeminiAPIException."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=None,
        BACKUP_GEMINI_API_KEY=None,
    )
    adapter = GeminiAdapter(settings=settings)

    with pytest.raises(GeminiAPIException) as exc_info:
        await adapter.generate_content(contents=["test"])

    assert "No Google GenAI API keys configured" in str(exc_info.value)


def test_cache_key_computation() -> None:
    """Verify deterministic SHA-256 cache key computation."""
    key1 = CatalogCache.compute_cache_key("SKU-01", "abc123sha", "gemini-3.8-flash", "v1.0")
    key2 = CatalogCache.compute_cache_key("sku-01", "abc123sha", "gemini-3.8-flash", "v1.0")
    key_diff = CatalogCache.compute_cache_key("SKU-02", "abc123sha", "gemini-3.8-flash", "v1.0")

    assert key1 == key2  # Case insensitive SKU
    assert key1 != key_diff
    assert len(key1) == 64  # SHA-256 hex digest length


def test_catalog_cache_operations() -> None:
    """Verify in-memory TTL cache operations: set, get, delete, clear, expiration, get_stats."""
    cache = CatalogCache(default_ttl_seconds=0.05)
    attrs = ExtractedCatalogAttributes(
        garment_type="Kurta",
        silhouette="structured_fitted",
        stretch_category="non_stretch",
        drape_notes="Structured",
        provenance="live_gemini",
    )
    cache.set("key1", attrs)
    assert cache.get("key1") is not None
    assert len(cache) == 1

    stats = cache.get_stats()
    assert stats["total_keys"] == 1
    assert stats["active_keys"] == 1

    # Delete
    assert cache.delete("key1") is True
    assert cache.delete("key1") is False
    assert cache.get("key1") is None

    # Expiration
    cache.set("key2", attrs, ttl_seconds=0.01)
    import time

    time.sleep(0.02)
    assert cache.get("key2") is None

    # Clear
    cache.set("key3", attrs)
    cache.clear()
    assert len(cache) == 0


def test_clean_address_text_edge_cases() -> None:
    """Verify clean_address_text handles empty strings and abbreviations."""
    assert clean_address_text("") == ""
    assert clean_address_text("   ") == ""

    # Test abbreviation expansions
    text = "bldg 4, flt 12, hno 55, plt 10, sec 14, nr metro, opp bus stand"
    cleaned = clean_address_text(text)
    assert "Building" in cleaned
    assert "Flat" in cleaned
    assert "House No." in cleaned
    assert "Plot" in cleaned
    assert "Sector" in cleaned
    assert "Near" in cleaned
    assert "Opposite" in cleaned


@pytest.mark.asyncio
async def test_address_normalizer_live_success() -> None:
    """Verify AddressNormalizer uses live Gemini response when valid."""
    live_res = NormalizedAddressResult(
        sanitized_address="Flat 402, Sai Residency, Opposite SBI ATM, Amritsar - 143001",
        landmark="Opposite SBI ATM",
        delivery_instructions="Deliver between 9 AM - 12 PM. Landmark: Opposite SBI ATM",
        confidence="high",
        provenance="live_gemini",
    )
    mock_client = make_mock_client(live_res.model_dump_json())
    adapter = GeminiAdapter(
        settings=Settings(PRIMARY_GEMINI_API_KEY=SecretStr("key")),
        primary_client=mock_client,
    )
    normalizer = AddressNormalizer(adapter=adapter)

    res = await normalizer.normalize(
        raw_address="flat 402, sai res, opp sbi atm",
        landmark="Near ATM",
    )
    assert res.provenance == "live_gemini"
    assert "Opposite SBI ATM" in res.sanitized_address


@pytest.mark.asyncio
async def test_address_normalizer_empty_input_fallback() -> None:
    """Verify AddressNormalizer handles empty input gracefully via fallback."""
    normalizer = AddressNormalizer()
    res = await normalizer.normalize("")
    assert res.provenance == "deterministic_rule"
    assert res.sanitized_address == ""


@pytest.mark.asyncio
async def test_catalog_extractor_json_repair_retry() -> None:
    """Verify CatalogExtractor repairs malformed JSON on first attempt and succeeds."""
    valid_repaired = ExtractedCatalogAttributes(
        garment_type="Chanderi Kurta",
        silhouette="structured_fitted",
        stretch_category="non_stretch",
        drape_notes="Handcrafted silk",
        provenance="live_gemini",
    )
    # First attempt: malformed JSON; Second attempt (repair): valid JSON
    mock_generate = AsyncMock(
        side_effect=[
            FakeResponse("This is not JSON: {broken"),
            FakeResponse(valid_repaired.model_dump_json()),
        ]
    )
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = mock_generate

    adapter = GeminiAdapter(
        settings=Settings(PRIMARY_GEMINI_API_KEY=SecretStr("key")),
        primary_client=mock_client,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    res = await extractor.extract("SKU-01", force_refresh=True)
    assert res.provenance == "live_gemini"
    assert res.garment_type == "Chanderi Kurta"
    assert mock_generate.call_count == 2


def test_preprocess_image_types_and_errors() -> None:
    """Verify preprocess_image handles PIL Image, bytes, and invalid types."""
    import io

    from PIL import Image

    from app.integrations.gemini.extractor import preprocess_image

    # PIL Image
    img = Image.new("RGB", (200, 200), color=(255, 0, 0))
    jpeg_bytes, sha, sdk_img = preprocess_image(img)
    assert len(jpeg_bytes) > 0
    assert len(sha) == 64

    # Bytes input
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    jpeg_bytes2, sha2, _ = preprocess_image(buf.getvalue())
    assert sha == sha2

    # Invalid input
    with pytest.raises(ValueError, match="Unsupported image input type"):
        preprocess_image(12345)  # type: ignore[arg-type]
