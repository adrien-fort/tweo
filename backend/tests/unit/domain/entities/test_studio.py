"""Tests for the Studio entity."""

import pytest

from app.core.domain.entities.studio import Studio


class TestStudioCreation:
    """Valid construction scenarios."""

    def test_creates_with_valid_fields(self) -> None:
        studio = Studio(tmdb_id=174, name="Warner Bros. Pictures")
        assert studio.tmdb_id == 174
        assert studio.name == "Warner Bros. Pictures"


class TestStudioValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_zero_tmdb_id_raises(self) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            Studio(tmdb_id=0, name="Warner Bros.")

    def test_negative_tmdb_id_raises(self) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            Studio(tmdb_id=-5, name="Warner Bros.")

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Studio(tmdb_id=174, name="")

    def test_whitespace_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Studio(tmdb_id=174, name="   ")


class TestStudioImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_tmdb_id_is_immutable(self) -> None:
        studio = Studio(tmdb_id=174, name="Warner Bros.")
        with pytest.raises(Exception):
            studio.tmdb_id = 1  # type: ignore[misc]


class TestStudioEquality:
    """Identity-based equality on tmdb_id."""

    def test_same_tmdb_id_are_equal(self) -> None:
        assert Studio(tmdb_id=174, name="Warner Bros. Pictures") == Studio(tmdb_id=174, name="WB")

    def test_different_tmdb_id_not_equal(self) -> None:
        assert Studio(tmdb_id=174, name="Warner Bros.") != Studio(tmdb_id=4, name="Warner Bros.")

    def test_hashable_and_usable_in_set(self) -> None:
        s1 = Studio(tmdb_id=174, name="Warner Bros.")
        s2 = Studio(tmdb_id=174, name="Warner Bros.")
        assert len({s1, s2}) == 1

    def test_not_equal_to_other_types(self) -> None:
        studio = Studio(tmdb_id=174, name="Warner Bros.")
        assert studio != 174
