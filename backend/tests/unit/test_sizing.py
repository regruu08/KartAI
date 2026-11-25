"""Unit tests for deterministic sizing recommendation engine in app.domain.sizing.

Verifies golden fit conversions for all curated SKUs, EOM rules, preference-based ease,
missing sleeve notes, and dynamic confidence bands per ADR-004 and AGENTS.md §6.4.
"""

import pytest

from app.domain.sizing import (
    recommend_size,
)


class TestSizingGoldenCases:
    """Verifies mandatory golden tests defined in AGENTS.md §6.4."""

    def test_zara_m_chanderi_non_stretch_tailored_recommends_size_l(self) -> None:
        """Zara M (Chest 38.0, Shoulder 17.0) on Chanderi Kurta (non-stretch) must yield Size L.

        Size M has shoulder 15.5" (negative shoulder ease -1.5"), which is eliminated for non-stretch.
        Size L has shoulder 17.0" (0.0" ease) and chest 40.0" (+2.0" ease), matching EOM rules.
        """
        rec = recommend_size(
            sku_id="SKU-01",
            known_brand="Zara",
            known_size="M",
            fit_preference="tailored",
        )
        assert rec.recommended_size == "L"
        assert rec.confidence_level in ("High", "Medium")
        assert rec.fit_score >= 70
        assert "L" in rec.explanation_text
        assert rec.fit_zone_breakdown["bust"]["garment_inches"] == 40.0
        assert rec.fit_zone_breakdown["bust"]["shopper_inches"] == 38.0
        assert rec.fit_zone_breakdown["shoulder"]["garment_inches"] == 17.0
        assert rec.fit_zone_breakdown["shoulder"]["shopper_inches"] == 17.0

        # Rigid fabric elimination note from data (A3)
        expected_note = 'Size M eliminated: shoulder ease -1.5" is below the 0.0" minimum for non-stretch fabric.'
        assert expected_note in rec.explanation_text
        assert "shoulders" in rec.fit_zone_breakdown
        assert rec.fit_zone_breakdown["shoulders"]["note"] == expected_note

    def test_hm_m_linen_shirt_slight_stretch_recommends_size_m(self) -> None:
        """H&M M (Chest 38.0, Shoulder 16.8) on Linen Shirt (slight-stretch) must yield Size M."""
        rec = recommend_size(
            sku_id="SKU-02",
            known_brand="H&M",
            known_size="M",
            fit_preference="tailored",
        )
        assert rec.recommended_size == "M"
        assert rec.fit_zone_breakdown["bust"]["garment_inches"] == 40.0
        assert rec.fit_zone_breakdown["bust"]["shopper_inches"] == 38.0

    def test_denim_jacket_missing_sleeve_length_warning(self) -> None:
        """SKU-03 (Denim Jacket) must include missing sleeve length warning."""
        rec = recommend_size(
            sku_id="SKU-03",
            known_brand="Uniqlo",
            known_size="M",
            fit_preference="regular",
        )
        assert any(
            "Sleeve length not specified by merchant" in w for w in rec.missing_data_warnings
        )

    @pytest.mark.parametrize("pref", ["tight", "tailored", "relaxed", "oversized"])
    @pytest.mark.parametrize("brand", ["Zara", "H&M", "Uniqlo"])
    @pytest.mark.parametrize("size", ["S", "M", "L"])
    def test_denim_jacket_missing_sleeve_never_exceeds_medium_confidence(
        self, pref: str, brand: str, size: str
    ) -> None:
        """Parametrized verification that SKU-03 never evaluates to 'High' confidence."""
        rec = recommend_size(
            sku_id="SKU-03",
            known_brand=brand,
            known_size=size,
            fit_preference=pref,
        )
        assert rec.confidence_level in ("Medium", "Low (Insufficient Data)"), (
            f"Expected <= Medium, got {rec.confidence_level} for {brand} {size} {pref}"
        )
        assert any(
            "Sleeve length not specified by merchant" in w for w in rec.missing_data_warnings
        )

    def test_unknown_sku_yields_low_insufficient_data(self) -> None:
        """Unknown SKU must return Low (Insufficient Data) confidence and clear warning."""
        rec = recommend_size(
            sku_id="SKU-UNKNOWN-99",
            known_brand="Zara",
            known_size="S",
        )
        assert rec.recommended_size == "S"
        assert rec.confidence_level == "Low (Insufficient Data)"
        assert rec.fit_score == 50
        assert any(
            "Merchant has not provided verified pattern measurement tables" in w
            for w in rec.missing_data_warnings
        )


class TestFitPreferencesAndEase:
    """Tests all 4 customer ease preferences: tight, tailored/regular, relaxed, oversized."""

    def test_tight_preference_prefers_closer_fit(self) -> None:
        rec_tight = recommend_size(
            sku_id="SKU-04",
            known_brand="Zara",
            known_size="S",
            fit_preference="tight",
        )
        rec_relaxed = recommend_size(
            sku_id="SKU-04",
            known_brand="Zara",
            known_size="S",
            fit_preference="relaxed",
        )
        # Tight recommendation should never be larger than relaxed
        size_order = ["S", "M", "L", "XL"]
        assert size_order.index(rec_tight.recommended_size) <= size_order.index(
            rec_relaxed.recommended_size
        )

    def test_oversized_preference_calibrated(self) -> None:
        rec_oversized = recommend_size(
            sku_id="SKU-02",
            known_brand="Zara",
            known_size="S",
            fit_preference="oversized",
        )
        # S on Zara has chest 36. Oversized (+6.0") targets 42.0" -> Size L in Linen Shirt
        assert rec_oversized.recommended_size in ("L", "XL")


class TestHeightAndDataGaps:
    """Tests height fit calculation and missing dimension reporting."""

    def test_height_fit_note_attached_when_garment_length_exists(self) -> None:
        rec = recommend_size(
            sku_id="SKU-01",
            known_brand="Zara",
            known_size="M",
            height_cm=165.0,
        )
        assert "length" in rec.fit_zone_breakdown
        assert "165 cm" in rec.fit_zone_breakdown["length"]["note"]

    def test_height_fit_knee_and_hip_notes(self) -> None:
        # SKU-02 length is 29.0" -> mid-hip
        rec_shirt = recommend_size(
            sku_id="SKU-02",
            known_brand="Zara",
            known_size="M",
            height_cm=175.0,
        )
        assert "mid-hip" in rec_shirt.fit_zone_breakdown["length"]["note"]

        # Custom dress with length 40.0" -> knee length
        knee_sku = {
            "name": "Knee Length Dress",
            "fabric_stretch": "slight_stretch",
            "length_inches": 40.0,
            "sizes": {"M": {"chest": 38.0, "shoulder": 16.5}},
        }
        rec_knee = recommend_size(
            sku_id="KNEE-01",
            known_brand="Zara",
            known_size="M",
            height_cm=160.0,
            custom_catalog={"KNEE-01": knee_sku},
        )
        assert "knee" in rec_knee.fit_zone_breakdown["length"]["note"]

    def test_height_provided_without_garment_length_warns(self) -> None:
        no_len_sku = {
            "name": "Lengthless Top",
            "fabric_stretch": "slight_stretch",
            "sizes": {"M": {"chest": 38.0, "shoulder": 16.5}},
        }
        rec = recommend_size(
            sku_id="NOLEN-01",
            known_brand="Zara",
            known_size="M",
            height_cm=165.0,
            custom_catalog={"NOLEN-01": no_len_sku},
        )
        assert any(
            "Shopper height provided but garment length is not specified" in w
            for w in rec.missing_data_warnings
        )

    def test_all_sizes_fail_non_stretch_fallback_to_largest(self) -> None:
        tiny_sku = {
            "name": "Tiny Non-Stretch Top",
            "fabric_stretch": "non_stretch",
            "has_shoulder": True,
            "sizes": {
                "S": {"chest": 28.0, "shoulder": 12.0},
                "M": {"chest": 30.0, "shoulder": 13.0},
            },
        }
        rec = recommend_size(
            sku_id="TINY-01",
            known_brand="Zara",
            known_size="XL",  # Chest 43.0, Shoulder 19.0 -> all fail hard floor
            custom_catalog={"TINY-01": tiny_sku},
        )
        assert rec.recommended_size == "M"
        assert "Maximum available size recommended" in rec.fit_zone_breakdown["overall"]

    def test_missing_shoulder_width_caps_confidence_at_medium(self) -> None:
        custom_sku = {
            "name": "Custom Kurti Without Shoulders",
            "fabric_stretch": "slight_stretch",
            "has_shoulder": False,
            "has_sleeve": True,
            "sizes": {
                "S": {"chest": 36.0, "waist": 32.0},
                "M": {"chest": 38.0, "waist": 34.0},
                "L": {"chest": 40.0, "waist": 36.0},
            },
        }
        rec = recommend_size(
            sku_id="CUSTOM-01",
            known_brand="Zara",
            known_size="S",
            custom_catalog={"CUSTOM-01": custom_sku},
        )
        assert rec.confidence_level in ("Medium", "Low (Insufficient Data)")
        assert any("shoulder width not specified" in w for w in rec.missing_data_warnings)

    def test_unknown_brand_triggers_fallback_and_warning(self) -> None:
        rec = recommend_size(
            sku_id="SKU-02",
            known_brand="NonExistentBrand",
            known_size="M",
        )
        assert any("NonExistentBrand" in w for w in rec.missing_data_warnings)
        assert rec.confidence_level in ("Medium", "Low (Insufficient Data)")

    def test_custom_catalog_alias_resolution(self) -> None:
        # Test custom_catalog lookup when sku_id is an alias not normalized in custom_catalog
        direct_sku = {
            "name": "Alias Keyed SKU",
            "fabric_stretch": "slight_stretch",
            "sizes": {"M": {"chest": 38.0, "shoulder": 16.5}},
        }
        rec = recommend_size(
            sku_id="SKU-CHANDERI-01",
            known_brand="Zara",
            known_size="M",
            custom_catalog={"SKU-CHANDERI-01": direct_sku},
        )
        assert rec.recommended_size == "M"


class TestDeterminism:
    """Verifies that identical inputs produce identical outputs every single time."""

    def test_pure_determinism_invariant(self) -> None:
        for _ in range(5):
            rec1 = recommend_size(
                sku_id="SKU-01", known_brand="Zara", known_size="M", fit_preference="tailored"
            )
            rec2 = recommend_size(
                sku_id="SKU-01", known_brand="Zara", known_size="M", fit_preference="tailored"
            )
            assert rec1 == rec2


class TestNewBrandsAndFixtureAlignment:
    """Verifies calibrated Levi's & Marks & Spencer matrices and SKU-01 fixture parity."""

    @pytest.mark.parametrize("brand", ["Levi's", "levi's", "Marks & Spencer", "m&s"])
    def test_calibrated_new_brands_recognized_without_fallback_warning(self, brand: str) -> None:
        rec = recommend_size(
            sku_id="SKU-02",
            known_brand=brand,
            known_size="M",
            fit_preference="tailored",
        )
        assert not any("not in verified conversion matrix" in w for w in rec.missing_data_warnings)
        assert rec.recommended_size in ("M", "L")

    def test_xxl_size_supported_across_all_brands(self) -> None:
        for brand in ["Zara", "H&M", "Uniqlo", "Levi's", "Marks & Spencer"]:
            rec = recommend_size(sku_id="SKU-03", known_brand=brand, known_size="XXL")
            assert not any(
                "not in verified conversion matrix" in w for w in rec.missing_data_warnings
            )
            assert rec.recommended_size == "XL"

    def test_sku_01_fixture_preserves_zara_m_to_size_l_invariant(self) -> None:
        from app.integrations.gemini.extractor import CatalogExtractor

        attrs = CatalogExtractor().load_fixture("SKU-01")
        custom_catalog = {
            "SKU-01": {
                "id": "SKU-01",
                "name": attrs.garment_type,
                "fabric_stretch": attrs.stretch_category,
                "has_shoulder": True,
                "has_sleeve": True,
                "length_inches": 47.0,
                "sizes": {
                    m.size_label: {
                        "chest": m.chest_inches,
                        "waist": m.waist_inches,
                        "shoulder": m.shoulder_inches,
                        "length": m.length_inches,
                    }
                    for m in attrs.measurements_table
                },
            }
        }
        rec = recommend_size(
            sku_id="SKU-01",
            known_brand="Zara",
            known_size="M",
            fit_preference="tailored",
            custom_catalog=custom_catalog,
        )
        assert rec.recommended_size == "L"

    def test_unknown_stretch_caps_confidence_at_medium(self) -> None:
        """Unknown fabric stretch must never yield High confidence per ADR-004."""
        unknown_stretch_sku = {
            "name": "Mystery Weave Kurta",
            "fabric_stretch": "unknown",
            "has_shoulder": True,
            "has_sleeve": True,
            "sizes": {
                "M": {"chest": 40.0, "waist": 34.0, "shoulder": 17.5},
                "L": {"chest": 42.0, "waist": 36.0, "shoulder": 18.5},
            },
        }
        rec = recommend_size(
            sku_id="UNK-STRETCH",
            known_brand="Zara",
            known_size="M",
            custom_catalog={"UNK-STRETCH": unknown_stretch_sku},
        )
        assert rec.confidence_level in ("Medium", "Low (Insufficient Data)")
