"""Tests for the CastMember value object."""

import pytest

from app.core.domain.entities.person import Person
from app.core.domain.value_objects.cast_member import CastMember


@pytest.fixture
def actor() -> Person:
    return Person(tmdb_id=6193, name="Leonardo DiCaprio")


class TestCastMemberCreation:
    """Valid construction scenarios."""

    def test_creates_with_valid_fields(self, actor: Person) -> None:
        member = CastMember(person=actor, character_name="Dom Cobb")
        assert member.person == actor
        assert member.character_name == "Dom Cobb"

    def test_director_can_also_be_cast_member(self) -> None:
        """A director acting in their own film uses the same Person instance."""
        clint = Person(tmdb_id=190, name="Clint Eastwood")
        member = CastMember(person=clint, character_name="Walt Kowalski")
        assert member.person.tmdb_id == 190


class TestCastMemberValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_empty_character_name_raises(self, actor: Person) -> None:
        with pytest.raises(ValueError, match="character_name"):
            CastMember(person=actor, character_name="")

    def test_whitespace_character_name_raises(self, actor: Person) -> None:
        with pytest.raises(ValueError, match="character_name"):
            CastMember(person=actor, character_name="   ")


class TestCastMemberImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_character_name_is_immutable(self, actor: Person) -> None:
        member = CastMember(person=actor, character_name="Dom Cobb")
        with pytest.raises(Exception):
            member.character_name = "Other"  # type: ignore[misc]


class TestCastMemberEquality:
    """Structural equality: same person + same character = same CastMember."""

    def test_equal_cast_members(self, actor: Person) -> None:
        assert CastMember(person=actor, character_name="Dom Cobb") == CastMember(person=actor, character_name="Dom Cobb")

    def test_different_character_not_equal(self, actor: Person) -> None:
        assert CastMember(person=actor, character_name="Dom Cobb") != CastMember(person=actor, character_name="Jack Dawson")

    def test_hashable(self, actor: Person) -> None:
        member = CastMember(person=actor, character_name="Dom Cobb")
        assert isinstance(hash(member), int)
