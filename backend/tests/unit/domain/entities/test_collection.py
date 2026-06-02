"""Tests for the Collection entity."""

import pytest

from app.core.domain.entities.collection import Collection


class TestCollectionCreation:
    """Valid construction scenarios."""

    def test_creates_with_valid_fields(self) -> None:
        col = Collection(collection_id=263, name="The Dark Knight Trilogy")
        assert col.collection_id == 263
        assert col.name == "The Dark Knight Trilogy"


class TestCollectionValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_zero_collection_id_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_id"):
            Collection(collection_id=0, name="Some Collection")

    def test_negative_collection_id_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_id"):
            Collection(collection_id=-1, name="Some Collection")

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Collection(collection_id=1, name="")

    def test_whitespace_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Collection(collection_id=1, name="   ")


class TestCollectionImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_collection_id_is_immutable(self) -> None:
        col = Collection(collection_id=263, name="The Dark Knight Trilogy")
        with pytest.raises(AttributeError):
            col.collection_id = 1  # type: ignore[misc]


class TestCollectionEquality:
    """Identity-based equality on collection_id."""

    def test_same_collection_id_are_equal(self) -> None:
        assert Collection(collection_id=263, name="DK Trilogy") == Collection(
            collection_id=263, name="Dark Knight Trilogy"
        )

    def test_different_collection_id_not_equal(self) -> None:
        assert Collection(collection_id=1, name="A") != Collection(collection_id=2, name="A")

    def test_hashable_and_usable_in_set(self) -> None:
        c1 = Collection(collection_id=263, name="DK Trilogy")
        c2 = Collection(collection_id=263, name="DK Trilogy")
        assert len({c1, c2}) == 1

    def test_not_equal_to_other_types(self) -> None:
        col = Collection(collection_id=263, name="DK Trilogy")
        assert col != 263
