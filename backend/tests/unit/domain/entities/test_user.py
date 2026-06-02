"""Tests for the User entity."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.domain.entities.user import User
from app.core.domain.enums import SystemRole


@pytest.fixture
def valid_user() -> User:
    return User(
        id=uuid4(),
        firebase_uid="firebase-uid-abc123",
        email="alice@example.com",
    )


class TestUserCreation:
    """Valid construction scenarios."""

    def test_creates_with_required_fields(self, valid_user: User) -> None:
        assert isinstance(valid_user.id, UUID)
        assert valid_user.firebase_uid == "firebase-uid-abc123"
        assert valid_user.email == "alice@example.com"

    def test_optional_fields_default_to_none(self, valid_user: User) -> None:
        assert valid_user.nickname is None
        assert valid_user.avatar_url is None
        assert valid_user.gender is None
        assert valid_user.pronouns is None
        assert valid_user.bio is None
        assert valid_user.preferences is None
        assert valid_user.anonymized_at is None

    def test_system_role_defaults_to_member(self, valid_user: User) -> None:
        assert valid_user.system_role == SystemRole.MEMBER

    def test_creates_with_admin_role(self) -> None:
        user = User(id=uuid4(), firebase_uid="uid", email="admin@example.com", system_role=SystemRole.ADMIN)
        assert user.system_role == SystemRole.ADMIN

    def test_email_is_stripped(self) -> None:
        user = User(id=uuid4(), firebase_uid="uid", email="  bob@example.com  ")
        assert user.email == "bob@example.com"

    def test_timestamps_default_to_utc_now(self, valid_user: User) -> None:
        assert valid_user.created_at.tzinfo is not None
        assert valid_user.updated_at.tzinfo is not None

    def test_creates_with_all_optional_fields(self) -> None:
        user = User(
            id=uuid4(),
            firebase_uid="uid",
            email="full@example.com",
            nickname="AliceW",
            avatar_url="https://cdn.example.com/avatar.jpg",
            gender="female",
            pronouns="she/her",
            bio="Loves sci-fi films.",
            preferences={"genres": ["sci-fi", "thriller"]},
            system_role=SystemRole.MEMBER,
        )
        assert user.nickname == "AliceW"
        assert user.avatar_url == "https://cdn.example.com/avatar.jpg"
        assert user.preferences == {"genres": ["sci-fi", "thriller"]}


class TestUserValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_empty_firebase_uid_raises(self) -> None:
        with pytest.raises(ValueError, match="firebase_uid"):
            User(id=uuid4(), firebase_uid="", email="a@b.com")

    def test_whitespace_firebase_uid_raises(self) -> None:
        with pytest.raises(ValueError, match="firebase_uid"):
            User(id=uuid4(), firebase_uid="   ", email="a@b.com")

    def test_invalid_email_raises(self) -> None:
        with pytest.raises(ValueError, match="email"):
            User(id=uuid4(), firebase_uid="uid", email="not-an-email")

    def test_empty_email_raises(self) -> None:
        with pytest.raises(ValueError, match="email"):
            User(id=uuid4(), firebase_uid="uid", email="")

    def test_avatar_url_without_https_raises(self) -> None:
        with pytest.raises(ValueError, match="avatar_url"):
            User(id=uuid4(), firebase_uid="uid", email="a@b.com", avatar_url="http://cdn.example.com/img.jpg")

    def test_empty_avatar_url_raises(self) -> None:
        with pytest.raises(ValueError, match="avatar_url"):
            User(id=uuid4(), firebase_uid="uid", email="a@b.com", avatar_url="")


class TestUserMutability:
    """User fields can be updated after creation."""

    def test_nickname_can_be_updated(self, valid_user: User) -> None:
        valid_user.nickname = "NewNick"
        assert valid_user.nickname == "NewNick"

    def test_system_role_can_be_elevated(self, valid_user: User) -> None:
        valid_user.system_role = SystemRole.ADMIN
        assert valid_user.system_role == SystemRole.ADMIN

    def test_anonymized_at_can_be_set(self, valid_user: User) -> None:
        now = datetime.now(UTC)
        valid_user.anonymized_at = now
        assert valid_user.anonymized_at == now


class TestUserEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self) -> None:
        uid = uuid4()
        u1 = User(id=uid, firebase_uid="uid1", email="a@b.com")
        u2 = User(id=uid, firebase_uid="uid2", email="c@d.com")
        assert u1 == u2

    def test_different_id_not_equal(self) -> None:
        assert User(id=uuid4(), firebase_uid="uid", email="a@b.com") != User(
            id=uuid4(), firebase_uid="uid", email="a@b.com"
        )

    def test_hashable_for_use_in_sets(self, valid_user: User) -> None:
        assert len({valid_user, valid_user}) == 1

    def test_not_equal_to_other_types(self, valid_user: User) -> None:
        assert valid_user != valid_user.id
        assert valid_user != "user"
