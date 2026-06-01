"""Tests for the Certification value object."""

import pytest

from app.core.domain.value_objects.certification import Certification


class TestCertificationCreation:
    """Valid construction scenarios."""

    def test_creates_with_valid_country_and_rating(self) -> None:
        cert = Certification(country="US", rating="PG-13")
        assert cert.country == "US"
        assert cert.rating == "PG-13"

    def test_normalises_country_to_uppercase(self) -> None:
        cert = Certification(country="us", rating="R")
        assert cert.country == "US"

    def test_strips_whitespace_from_rating(self) -> None:
        cert = Certification(country="GB", rating="  12A  ")
        assert cert.rating == "12A"

    def test_various_valid_countries(self) -> None:
        for country in ("US", "GB", "FR", "DE", "JP"):
            cert = Certification(country=country, rating="PG")
            assert cert.country == country


class TestCertificationValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_empty_country_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            Certification(country="", rating="PG-13")

    def test_whitespace_country_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            Certification(country="  ", rating="PG-13")

    def test_country_too_short_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            Certification(country="U", rating="PG-13")

    def test_country_too_long_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            Certification(country="USA", rating="PG-13")

    def test_country_with_digits_raises(self) -> None:
        with pytest.raises(ValueError, match="country"):
            Certification(country="U1", rating="PG-13")

    def test_empty_rating_raises(self) -> None:
        with pytest.raises(ValueError, match="rating"):
            Certification(country="US", rating="")

    def test_whitespace_rating_raises(self) -> None:
        with pytest.raises(ValueError, match="rating"):
            Certification(country="US", rating="   ")


class TestCertificationImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_country_is_immutable(self) -> None:
        cert = Certification(country="US", rating="PG-13")
        with pytest.raises(Exception):
            cert.country = "GB"  # type: ignore[misc]

    def test_rating_is_immutable(self) -> None:
        cert = Certification(country="US", rating="PG-13")
        with pytest.raises(Exception):
            cert.rating = "R"  # type: ignore[misc]


class TestCertificationEquality:
    """Structural equality: same country + rating are equal."""

    def test_equal_certifications(self) -> None:
        assert Certification(country="US", rating="PG-13") == Certification(country="US", rating="PG-13")

    def test_different_country_not_equal(self) -> None:
        assert Certification(country="US", rating="PG-13") != Certification(country="GB", rating="PG-13")

    def test_different_rating_not_equal(self) -> None:
        assert Certification(country="US", rating="PG-13") != Certification(country="US", rating="R")

    def test_hashable_for_use_in_sets(self) -> None:
        certs = {Certification(country="US", rating="PG-13"), Certification(country="US", rating="PG-13")}
        assert len(certs) == 1
