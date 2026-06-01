"""Tests for the CollectionMembership value object."""

import pytest

from app.core.domain.value_objects.collection_membership import CollectionMembership


class TestCollectionMembershipCreation:
    """Valid construction scenarios."""

    def test_creates_with_required_fields(self) -> None:
        membership = CollectionMembership(collection_id=1, collection_name="The Dark Knight Trilogy")
        assert membership.collection_id == 1
        assert membership.collection_name == "The Dark Knight Trilogy"
        assert membership.order is None

    def test_creates_with_order(self) -> None:
        membership = CollectionMembership(
            collection_id=263,
            collection_name="The Dark Knight Trilogy",
            order=2,
        )
        assert membership.order == 2

    def test_order_is_none_by_default(self) -> None:
        membership = CollectionMembership(collection_id=1, collection_name="Marvel Cinematic Universe")
        assert membership.order is None


class TestCollectionMembershipValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_zero_collection_id_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_id"):
            CollectionMembership(collection_id=0, collection_name="Some Collection")

    def test_negative_collection_id_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_id"):
            CollectionMembership(collection_id=-1, collection_name="Some Collection")

    def test_empty_collection_name_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_name"):
            CollectionMembership(collection_id=1, collection_name="")

    def test_whitespace_collection_name_raises(self) -> None:
        with pytest.raises(ValueError, match="collection_name"):
            CollectionMembership(collection_id=1, collection_name="   ")

    def test_zero_order_raises(self) -> None:
        with pytest.raises(ValueError, match="order"):
            CollectionMembership(collection_id=1, collection_name="Trilogy", order=0)

    def test_negative_order_raises(self) -> None:
        with pytest.raises(ValueError, match="order"):
            CollectionMembership(collection_id=1, collection_name="Trilogy", order=-1)


class TestCollectionMembershipImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_collection_id_is_immutable(self) -> None:
        membership = CollectionMembership(collection_id=1, collection_name="Trilogy")
        with pytest.raises(Exception):
            membership.collection_id = 2  # type: ignore[misc]


class TestCollectionMembershipEquality:
    """Structural equality."""

    def test_equal_memberships(self) -> None:
        m1 = CollectionMembership(collection_id=1, collection_name="Trilogy", order=1)
        m2 = CollectionMembership(collection_id=1, collection_name="Trilogy", order=1)
        assert m1 == m2

    def test_different_order_not_equal(self) -> None:
        m1 = CollectionMembership(collection_id=1, collection_name="Trilogy", order=1)
        m2 = CollectionMembership(collection_id=1, collection_name="Trilogy", order=2)
        assert m1 != m2

    def test_hashable(self) -> None:
        m = CollectionMembership(collection_id=1, collection_name="Trilogy", order=1)
        assert isinstance(hash(m), int)
