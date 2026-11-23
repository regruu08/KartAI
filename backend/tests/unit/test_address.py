"""Unit tests for pure address quality evaluator in app.domain.address.

Verifies PIN regex validation, premises regex detection, English & Hinglish landmark
parsing, and Complete/NeedsLandmark/Poor categorization per ADR-003 and ADR-015.
"""

from app.domain.address import address_quality


class TestAddressQuality:
    """Tests address completeness evaluation."""

    def test_complete_address_with_english_landmarks(self) -> None:
        result = address_quality("Flat 402, Sai Residency, near Hanuman Mandir", "143001")
        assert result.status == "Complete"
        assert result.is_valid_pin is True
        assert result.has_house_identifier is True
        assert result.has_landmark is True
        assert "near" in result.matched_landmarks
        assert "mandir" in result.matched_landmarks
        assert "residency" in result.matched_landmarks

    def test_complete_address_with_hinglish_landmarks(self) -> None:
        result = address_quality("House 14B, Gandhi Chowk, purani gali, Azamgarh", "276001")
        assert result.status == "Complete"
        assert result.is_valid_pin is True
        assert result.has_house_identifier is True
        assert result.has_landmark is True
        assert "chowk" in result.matched_landmarks
        assert "gali" in result.matched_landmarks

    def test_complete_address_with_commercial_landmarks(self) -> None:
        result = address_quality("Shop 12, Main Market, opp SBI ATM, Alwar", "301001")
        assert result.status == "Complete"
        assert result.has_house_identifier is True
        assert "opp" in result.matched_landmarks
        assert "market" in result.matched_landmarks
        assert "atm" in result.matched_landmarks

    def test_needs_landmark_when_landmark_missing(self) -> None:
        # Has premise number and length, but no recognized directional landmark
        result = address_quality("Flat 301, Hillview Enclave, Block C", "560001")
        # Hillview Enclave has 'enclave'
        assert "enclave" in result.matched_landmarks

        # Truly missing landmark
        result2 = address_quality("Flat 301, Hillview, Floor 3", "560001")
        assert result2.status == "NeedsLandmark"
        assert result2.has_house_identifier is True
        assert result2.has_landmark is False

    def test_needs_landmark_when_house_number_missing(self) -> None:
        # Has landmark but lacks premise/flat number
        result = address_quality("Near Hanuman Mandir, Station Road, Jaipur", "302001")
        assert result.status == "NeedsLandmark"
        assert result.has_house_identifier is False
        assert result.has_landmark is True

    def test_poor_address_when_pin_invalid(self) -> None:
        # Invalid 5-digit PIN
        result1 = address_quality("Flat 402, Sai Residency, near Hanuman Mandir", "14300")
        assert result1.status == "Poor"
        assert result1.is_valid_pin is False

        # Invalid alphanumeric PIN
        result2 = address_quality("Flat 402, Sai Residency, near Hanuman Mandir", "14300A")
        assert result2.status == "Poor"
        assert result2.is_valid_pin is False

    def test_poor_address_when_too_short(self) -> None:
        result = address_quality("Jaipur", "302001")
        assert result.status == "Poor"
        assert "too brief" in result.reason.lower()

    def test_poor_address_when_structure_missing(self) -> None:
        result = address_quality("Somewhere outside town near nothing", "110001")
        # 'near' is matched, but missing house identifier
        assert result.status == "NeedsLandmark"

        result2 = address_quality("Somewhere outside town", "110001")
        assert result2.status == "Poor"
