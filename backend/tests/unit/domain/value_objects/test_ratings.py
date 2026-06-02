"""Tests for the Ratings value object."""

import pytest

from app.core.domain.value_objects.certification import Certification
from app.core.domain.value_objects.ratings import Ratings


@pytest.fixture
def us_cert() -> Certification:
    return Certification(country="US", rating="PG-13")


@pytest.fixture
def gb_cert() -> Certification:
    return Certification(country="GB", rating="12A")


class TestRatingsCreation:
    """Valid construction scenarios."""

    def test_creates_fully_populated(self, us_cert: Certification, gb_cert: Certification) -> None:
        ratings = Ratings(
            community_score=8.5,
            vote_count=15000,
            certifications=(us_cert, gb_cert),
        )
        assert ratings.community_score == pytest.approx(8.5)
        assert ratings.vote_count == 15000
        assert ratings.certifications == (us_cert, gb_cert)

    def test_creates_with_all_defaults(self) -> None:
        ratings = Ratings()
        assert ratings.community_score is None
        assert ratings.vote_count is None
        assert ratings.certifications == ()

    def test_score_at_lower_bound(self) -> None:
        assert Ratings(community_score=0.0).community_score == pytest.approx(0.0)

    def test_score_at_upper_bound(self) -> None:
        assert Ratings(community_score=10.0).community_score == pytest.approx(10.0)

    def test_zero_vote_count_with_zero_score_is_valid(self) -> None:
        """TMDB returns vote_average=0.0 and vote_count=0 together for unrated movies."""
        ratings = Ratings(community_score=0.0, vote_count=0)
        assert ratings.vote_count == 0
        assert ratings.community_score == pytest.approx(0.0)


class TestRatingsValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_score_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="community_score"):
            Ratings(community_score=-0.1)

    def test_score_above_ten_raises(self) -> None:
        with pytest.raises(ValueError, match="community_score"):
            Ratings(community_score=10.1)

    def test_negative_vote_count_raises(self) -> None:
        with pytest.raises(ValueError, match="vote_count"):
            Ratings(vote_count=-1)

    def test_vote_count_without_score_raises(self) -> None:
        with pytest.raises(ValueError, match="vote_count"):
            Ratings(community_score=None, vote_count=100)


class TestRatingsImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_community_score_is_immutable(self) -> None:
        ratings = Ratings(community_score=7.0)
        with pytest.raises(AttributeError):
            ratings.community_score = 8.0  # type: ignore[misc]


class TestRatingsEquality:
    """Structural equality."""

    def test_equal_ratings(self, us_cert: Certification) -> None:
        r1 = Ratings(community_score=8.5, vote_count=100, certifications=(us_cert,))
        r2 = Ratings(community_score=8.5, vote_count=100, certifications=(us_cert,))
        assert r1 == r2

    def test_different_score_not_equal(self) -> None:
        assert Ratings(community_score=7.0) != Ratings(community_score=8.0)

    def test_hashable(self, us_cert: Certification) -> None:
        ratings = Ratings(community_score=8.5, certifications=(us_cert,))
        assert isinstance(hash(ratings), int)
