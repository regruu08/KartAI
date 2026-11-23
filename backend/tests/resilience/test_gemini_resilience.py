"""Resilience and Chaos Tests for Gemini VLM Pipeline.

Verifies:
1. Simulated 429 quota exhaustion -> backup key switch
2. Simulated >4.0s timeout -> verified fixture fallback (zero 500 errors)
3. Circuit breaker tripping after 3 consecutive failures
4. Cache hits making zero network calls
5. Image preprocessing downscales images > 1024px to <= 1024px JPEG q85
6. Offline address normalizer deterministic fallback with expanded abbreviations
7. Honest garment uncertainty reporting on SKU-03 (missing sleeve length)

Reference: ADR-001, ADR-004, ADR-013, ADR-016.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from PIL import Image
from pydantic import SecretStr

from app.config import Settings
from app.integrations.gemini.adapter import (
    CircuitBreaker,
    GeminiAdapter,
)
from app.integrations.gemini.cache import CatalogCache
from app.integrations.gemini.extractor import (
    CatalogExtractor,
    preprocess_image,
)
from app.integrations.gemini.normalizer import (
    deterministic_fallback_normalize,
)
from app.schemas.api_contracts import (
    ExtractedCatalogAttributes,
    GarmentMeasurements,
    ProvenanceEnum,
)


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


def make_mock_client(
    response_text: str = '{"status": "ok"}', error: Exception | None = None
) -> MagicMock:
    client = MagicMock()
    mock_gen = AsyncMock()
    if error:
        mock_gen.side_effect = error
    else:
        mock_gen.return_value = FakeResponse(response_text)
    client.aio.models.generate_content = mock_gen
    return client


@pytest.mark.asyncio
async def test_extractor_quota_exhaustion_failover() -> None:
    """Simulate HTTP 429 quota exhaustion on primary key triggering backup key switch."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-exhausted"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-available"),
        GEMINI_TIMEOUT_S=4.0,
    )
    # Primary fails with 429
    mock_primary = make_mock_client(error=RuntimeError("ResourceExhausted: 429 Quota exceeded"))

    # Valid extracted JSON returned by backup
    valid_extracted = ExtractedCatalogAttributes(
        garment_type="Handcrafted Chanderi Silk Anarkali Kurta",
        silhouette="structured_fitted",
        stretch_category="non_stretch",
        stated_fabric="100% Chanderi Silk",
        measurements_table=[
            GarmentMeasurements(size_label="M", chest_inches=38.0, waist_inches=34.0)
        ],
        missing_critical_data=[],
        drape_notes="Structured bodice",
        provenance="live_gemini",
    )
    mock_backup = make_mock_client(valid_extracted.model_dump_json())

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    result = await extractor.extract("SKU-01", listing_text="Handcrafted silk kurta")

    assert result.provenance == ProvenanceEnum.LIVE_GEMINI.value
    assert result.garment_type == "Handcrafted Chanderi Silk Anarkali Kurta"
    assert mock_primary.aio.models.generate_content.called
    assert mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_extractor_timeout_fixture_fallback_zero_500() -> None:
    """Simulate >4.0s timeout on all live keys triggering verified benchmark fixture fallback."""
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-slow"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-slow"),
        GEMINI_TIMEOUT_S=0.05,  # 50ms timeout to simulate deadline exceeded
    )

    async def slow_call(*args: object, **kwargs: object) -> FakeResponse:
        await asyncio.sleep(0.3)
        return FakeResponse("{}")

    mock_primary = MagicMock()
    mock_primary.aio.models.generate_content = slow_call
    mock_backup = MagicMock()
    mock_backup.aio.models.generate_content = slow_call

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    # Must NOT raise exception / 500 error: returns verified fixture
    result = await extractor.extract("SKU-01", listing_text="Handcrafted silk kurta")

    assert result.provenance == ProvenanceEnum.FIXTURE.value
    assert result.garment_type == "Handcrafted Chanderi Silk Anarkali Kurta"
    assert result.silhouette == "structured_fitted"
    assert result.stretch_category == "non_stretch"
    assert len(result.measurements_table) == 4


@pytest.mark.asyncio
async def test_dual_key_dynamic_timeout_budgeting_prevents_latency_overrun() -> None:
    """Verify that when both primary and backup keys simulate network latency (> timeout_s),
    dynamic timeout budgeting prevents latency overrun: CatalogExtractor.extract finishes in
    under timeout_s + 0.5s and cleanly falls back to the verified benchmark fixture (provenance='manual_fixture').
    """
    timeout_s = 0.5
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-hanging-key"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-hanging-key"),
        GEMINI_TIMEOUT_S=timeout_s,
    )

    async def hanging_call(*args: object, **kwargs: object) -> FakeResponse:
        # Both keys simulate network delay greater than timeout_s
        await asyncio.sleep(timeout_s + 2.0)
        return FakeResponse("{}")

    mock_primary = MagicMock()
    mock_primary.aio.models.generate_content = AsyncMock(side_effect=hanging_call)
    mock_backup = MagicMock()
    mock_backup.aio.models.generate_content = AsyncMock(side_effect=hanging_call)

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    t0 = time.monotonic()
    result = await extractor.extract("SKU-01", listing_text="Handcrafted silk kurta")
    elapsed = time.monotonic() - t0

    # Under dynamic timeout budgeting, total wall-clock time must strictly be < timeout_s + 0.5s
    # (Without timeout budgeting, sequential 2 x timeout would take ~1.0s+ and exceed timeout_s + 0.5s)
    assert elapsed < (timeout_s + 0.5), (
        f"Elapsed {elapsed:.3f}s exceeded deadline {timeout_s + 0.5:.3f}s"
    )
    assert result.provenance == ProvenanceEnum.FIXTURE.value
    assert result.provenance == "manual_fixture"
    assert result.garment_type == "Handcrafted Chanderi Silk Anarkali Kurta"
    # Verify backup client was not called because primary exhausted the operation timeout budget
    assert not mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_dual_key_backup_hanging_respects_remaining_budget() -> None:
    """Verify that when primary fails quickly (e.g. 429) but backup hangs,
    backup timeout is budgeted to remaining time and finishes under timeout_s + 0.5s.
    """
    timeout_s = 0.5
    settings = Settings(
        PRIMARY_GEMINI_API_KEY=SecretStr("primary-429-key"),
        BACKUP_GEMINI_API_KEY=SecretStr("backup-hanging-key"),
        GEMINI_TIMEOUT_S=timeout_s,
    )

    # Primary fails fast with 429
    mock_primary = make_mock_client(error=RuntimeError("ResourceExhausted: 429"))

    # Backup hangs
    async def hanging_backup(*args: object, **kwargs: object) -> FakeResponse:
        await asyncio.sleep(timeout_s + 2.0)
        return FakeResponse("{}")

    mock_backup = MagicMock()
    mock_backup.aio.models.generate_content = AsyncMock(side_effect=hanging_backup)

    adapter = GeminiAdapter(
        settings=settings,
        primary_client=mock_primary,
        backup_client=mock_backup,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    t0 = time.monotonic()
    result = await extractor.extract("SKU-01", listing_text="Handcrafted silk kurta")
    elapsed = time.monotonic() - t0

    assert elapsed < (timeout_s + 0.5), (
        f"Elapsed {elapsed:.3f}s exceeded deadline {timeout_s + 0.5:.3f}s"
    )
    assert result.provenance == ProvenanceEnum.FIXTURE.value
    assert result.provenance == "manual_fixture"
    assert mock_backup.aio.models.generate_content.called


@pytest.mark.asyncio
async def test_circuit_breaker_tripping_bypasses_network_calls() -> None:
    """Verify circuit breaker trips after 3 failures and immediately serves fixture without latency."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_s=60.0)
    mock_client = make_mock_client(error=RuntimeError("Google Cloud outage"))

    adapter = GeminiAdapter(
        settings=Settings(PRIMARY_GEMINI_API_KEY=SecretStr("test-key")),
        circuit_breaker=breaker,
        primary_client=mock_client,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    # Call 1, 2, 3 fail on live API and fall back to fixture
    for _ in range(3):
        res = await extractor.extract("SKU-02", force_refresh=True)
        assert res.provenance == ProvenanceEnum.FIXTURE.value

    assert breaker.is_open is True
    assert mock_client.aio.models.generate_content.call_count == 3

    # Call 4: Circuit breaker is OPEN. Must immediately return fixture without calling live API!
    call_count_before = mock_client.aio.models.generate_content.call_count
    res_open = await extractor.extract("SKU-02", force_refresh=True)

    assert res_open.provenance == ProvenanceEnum.FIXTURE.value
    # Exactly 0 new network calls attempted!
    assert mock_client.aio.models.generate_content.call_count == call_count_before


@pytest.mark.asyncio
async def test_cache_hit_makes_zero_network_calls() -> None:
    """Verify Tier 1 cache hit serves result with provenance='cached' and zero network calls."""
    mock_client = make_mock_client()
    adapter = GeminiAdapter(
        settings=Settings(PRIMARY_GEMINI_API_KEY=SecretStr("test-key")),
        primary_client=mock_client,
    )
    cache = CatalogCache()
    extractor = CatalogExtractor(adapter=adapter, cache=cache)

    # First call loads fixture into cache (since mock returns empty JSON)
    first_result = await extractor.extract("SKU-01")
    call_count_after_first = mock_client.aio.models.generate_content.call_count

    # Second call for the same SKU should hit in-memory TTL cache
    second_result = await extractor.extract("SKU-01")

    assert second_result.provenance == ProvenanceEnum.CACHE.value
    assert second_result.garment_type == first_result.garment_type
    # Assert zero additional network calls made
    assert mock_client.aio.models.generate_content.call_count == call_count_after_first


def test_image_preprocessing_downscaling() -> None:
    """Verify high-resolution images are downscaled to <= 1024px JPEG at quality 85."""
    # Create a 2400 x 1800 test image in memory
    orig_img = Image.new("RGB", (2400, 1800), color=(120, 50, 200))

    jpeg_bytes, sha256_hash, sdk_img = preprocess_image(
        orig_img, max_dimension=1024, jpeg_quality=85
    )

    assert len(jpeg_bytes) > 0
    assert len(sha256_hash) == 64
    assert sdk_img.width <= 1024
    assert sdk_img.height <= 1024
    # Check aspect ratio preservation: 2400/1800 = 4/3 -> 1024 / 768
    assert sdk_img.width == 1024
    assert sdk_img.height == 768


def test_offline_address_normalizer_abbreviation_expansion() -> None:
    """Verify deterministic address cleansing expands Indian logistics abbreviations offline."""
    raw = "flat 402, sai res, opp. sbi atm, nr. metro station, amritsar 143001"
    landmark = "behind hanuman mandir"

    result = deterministic_fallback_normalize(raw, landmark=landmark)

    assert result.provenance == "deterministic_rule"
    assert "Opposite" in result.sanitized_address
    assert "Near" in result.sanitized_address
    assert "Behind Hanuman Mandir" in result.sanitized_address
    assert "Landmark: Behind Hanuman Mandir" in result.delivery_instructions


def test_sku_03_missing_sleeve_uncertainty_reporting() -> None:
    """Verify SKU-03 fixture represents honest missing sleeve measurement per ADR-004 & ADR-013."""
    extractor = CatalogExtractor()
    sku_03 = extractor.load_fixture("SKU-03")

    assert "sleeve_length" in sku_03.missing_critical_data
    assert "Sleeve length not specified by merchant" in sku_03.drape_notes
    # Sizing measurements for SKU-03 have chest and shoulder but no sleeve
    for m in sku_03.measurements_table:
        assert m.chest_inches is not None
        assert m.shoulder_inches is not None
