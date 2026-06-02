"""Tests for the UserGroup and UserGroupMembership entities."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from app.core.domain.entities.user_group import UserGroup, UserGroupMembership


@pytest.fixture
def owner_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_group(owner_id: UUID) -> UserGroup:
    return UserGroup(id=uuid4(), name="Friday Film Club", owner_id=owner_id)


class TestUserGroupCreation:
    """Valid construction scenarios."""

    def test_creates_with_required_fields(self, valid_group: UserGroup, owner_id: UUID) -> None:
        assert isinstance(valid_group.id, UUID)
        assert valid_group.name == "Friday Film Club"
        assert valid_group.owner_id == owner_id

    def test_description_defaults_to_none(self, valid_group: UserGroup) -> None:
        assert valid_group.description is None

    def test_creates_with_description(self, owner_id: UUID) -> None:
        group = UserGroup(id=uuid4(), name="D&D Party", owner_id=owner_id, description="Weekly campaign")
        assert group.description == "Weekly campaign"

    def test_timestamps_default_to_utc_now(self, valid_group: UserGroup) -> None:
        assert valid_group.created_at.tzinfo is not None
        assert valid_group.updated_at.tzinfo is not None


class TestUserGroupValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_empty_name_raises(self, owner_id: UUID) -> None:
        with pytest.raises(ValueError, match="name"):
            UserGroup(id=uuid4(), name="", owner_id=owner_id)

    def test_whitespace_name_raises(self, owner_id: UUID) -> None:
        with pytest.raises(ValueError, match="name"):
            UserGroup(id=uuid4(), name="   ", owner_id=owner_id)


class TestUserGroupMutability:
    """UserGroup fields can be updated after creation."""

    def test_name_can_be_updated(self, valid_group: UserGroup) -> None:
        valid_group.name = "Saturday Film Club"
        assert valid_group.name == "Saturday Film Club"

    def test_description_can_be_set(self, valid_group: UserGroup) -> None:
        valid_group.description = "A new description"
        assert valid_group.description == "A new description"


class TestUserGroupEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self, owner_id: UUID) -> None:
        uid = uuid4()
        g1 = UserGroup(id=uid, name="Group A", owner_id=owner_id)
        g2 = UserGroup(id=uid, name="Group B", owner_id=owner_id)
        assert g1 == g2

    def test_different_id_not_equal(self, owner_id: UUID) -> None:
        assert UserGroup(id=uuid4(), name="Group", owner_id=owner_id) != UserGroup(
            id=uuid4(), name="Group", owner_id=owner_id
        )

    def test_hashable(self, valid_group: UserGroup) -> None:
        assert len({valid_group, valid_group}) == 1


class TestUserGroupMembershipCreation:
    """Valid UserGroupMembership construction scenarios."""

    def test_creates_with_required_fields(self) -> None:
        group_id = uuid4()
        user_id = uuid4()
        added_by = uuid4()
        membership = UserGroupMembership(
            id=uuid4(),
            group_id=group_id,
            user_id=user_id,
            added_by=added_by,
        )
        assert membership.group_id == group_id
        assert membership.user_id == user_id
        assert membership.added_by == added_by
        assert isinstance(membership.added_at, datetime)
        assert membership.added_at.tzinfo is not None


class TestUserGroupMembershipEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self) -> None:
        uid = uuid4()
        gid = uuid4()
        uid2 = uuid4()
        m1 = UserGroupMembership(id=uid, group_id=gid, user_id=uid2, added_by=uuid4())
        m2 = UserGroupMembership(id=uid, group_id=gid, user_id=uid2, added_by=uuid4())
        assert m1 == m2

    def test_different_id_not_equal(self) -> None:
        gid, uid = uuid4(), uuid4()
        assert UserGroupMembership(id=uuid4(), group_id=gid, user_id=uid, added_by=uuid4()) != UserGroupMembership(
            id=uuid4(), group_id=gid, user_id=uid, added_by=uuid4()
        )
