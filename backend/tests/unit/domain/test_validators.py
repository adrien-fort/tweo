"""Tests for domain validators."""

import pytest

from app.core.domain.validators import validate_country_code, validate_language_code


class TestValidateCountryCode:
    """validate_country_code normalises and validates ISO 3166-1 alpha-2 codes."""

    def test_valid_uppercase_code_returned_unchanged(self) -> None:
        assert validate_country_code("US") == "US"

    def test_lowercase_normalised_to_uppercase(self) -> None:
        assert validate_country_code("us") == "US"

    def test_mixed_case_normalised(self) -> None:
        assert validate_country_code("gB") == "GB"

    def test_various_valid_codes(self) -> None:
        for code in ("US", "GB", "FR", "DE", "JP", "KR"):
            assert validate_country_code(code) == code

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="field_name"):
            validate_country_code("", field_name="field_name")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            validate_country_code("   ")

    def test_single_letter_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            validate_country_code("U")

    def test_three_letter_code_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            validate_country_code("USA")

    def test_digit_in_code_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            validate_country_code("U1")

    def test_custom_field_name_in_error(self) -> None:
        with pytest.raises(ValueError, match="nationalities"):
            validate_country_code("X1", field_name="nationalities")


class TestValidateLanguageCode:
    """validate_language_code normalises and validates ISO 639-1 alpha-2 codes."""

    def test_valid_lowercase_code_returned_unchanged(self) -> None:
        assert validate_language_code("en") == "en"

    def test_uppercase_normalised_to_lowercase(self) -> None:
        assert validate_language_code("EN") == "en"

    def test_mixed_case_normalised(self) -> None:
        assert validate_language_code("Fr") == "fr"

    def test_various_valid_codes(self) -> None:
        for code in ("en", "fr", "ja", "ko", "de", "es"):
            assert validate_language_code(code) == code

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="field_name"):
            validate_language_code("", field_name="field_name")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="language"):
            validate_language_code("   ")

    def test_single_letter_raises(self) -> None:
        with pytest.raises(ValueError, match="language"):
            validate_language_code("e")

    def test_three_letter_code_raises(self) -> None:
        with pytest.raises(ValueError, match="language"):
            validate_language_code("eng")

    def test_digit_in_code_raises(self) -> None:
        with pytest.raises(ValueError, match="language"):
            validate_language_code("e1")

    def test_custom_field_name_in_error(self) -> None:
        with pytest.raises(ValueError, match="mother_tongue"):
            validate_language_code("e1", field_name="mother_tongue")
