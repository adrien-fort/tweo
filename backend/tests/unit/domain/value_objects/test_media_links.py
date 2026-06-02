"""Tests for the MediaLinks value object."""

import pytest

from app.core.domain.value_objects.media_links import MediaLinks


class TestMediaLinksCreation:
    """Valid construction scenarios."""

    def test_creates_with_both_urls(self) -> None:
        links = MediaLinks(
            poster_url="https://image.tmdb.org/poster.jpg",
            trailer_url="https://youtube.com/watch?v=abc123",
        )
        assert links.poster_url == "https://image.tmdb.org/poster.jpg"
        assert links.trailer_url == "https://youtube.com/watch?v=abc123"

    def test_creates_with_all_none(self) -> None:
        links = MediaLinks()
        assert links.poster_url is None
        assert links.trailer_url is None

    def test_creates_with_poster_only(self) -> None:
        links = MediaLinks(poster_url="https://image.tmdb.org/poster.jpg")
        assert links.poster_url == "https://image.tmdb.org/poster.jpg"
        assert links.trailer_url is None

    def test_creates_with_trailer_only(self) -> None:
        links = MediaLinks(trailer_url="https://youtube.com/watch?v=abc123")
        assert links.poster_url is None
        assert links.trailer_url == "https://youtube.com/watch?v=abc123"


class TestMediaLinksValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_poster_url_without_https_raises(self) -> None:
        with pytest.raises(ValueError, match="poster_url"):
            MediaLinks(poster_url="http://image.tmdb.org/poster.jpg")

    def test_trailer_url_without_https_raises(self) -> None:
        with pytest.raises(ValueError, match="trailer_url"):
            MediaLinks(trailer_url="http://youtube.com/watch?v=abc123")

    def test_empty_poster_url_raises(self) -> None:
        with pytest.raises(ValueError, match="poster_url"):
            MediaLinks(poster_url="")

    def test_whitespace_trailer_url_raises(self) -> None:
        with pytest.raises(ValueError, match="trailer_url"):
            MediaLinks(trailer_url="   ")


class TestMediaLinksImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_poster_url_is_immutable(self) -> None:
        links = MediaLinks(poster_url="https://image.tmdb.org/poster.jpg")
        with pytest.raises(AttributeError):
            links.poster_url = "https://other.com/img.jpg"  # type: ignore[misc]


class TestMediaLinksEquality:
    """Structural equality."""

    def test_equal_when_same_urls(self) -> None:
        url = "https://image.tmdb.org/poster.jpg"
        assert MediaLinks(poster_url=url) == MediaLinks(poster_url=url)

    def test_not_equal_when_different_poster(self) -> None:
        assert MediaLinks(poster_url="https://a.com/1.jpg") != MediaLinks(poster_url="https://b.com/2.jpg")

    def test_hashable(self) -> None:
        links = MediaLinks(poster_url="https://image.tmdb.org/poster.jpg")
        assert isinstance(hash(links), int)
