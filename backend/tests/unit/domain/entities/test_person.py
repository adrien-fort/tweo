"""Tests for the Person entity."""

import pytest

from app.core.domain.entities.person import Person


class TestPersonCreation:
    """Valid construction scenarios."""

    def test_creates_with_valid_fields(self) -> None:
        person = Person(tmdb_id=525, name="Christopher Nolan")
        assert person.tmdb_id == 525
        assert person.name == "Christopher Nolan"

    def test_name_with_accents(self) -> None:
        person = Person(tmdb_id=1, name="Jean-Pierre Jeunet")
        assert person.name == "Jean-Pierre Jeunet"

    def test_optional_fields_default_to_empty(self) -> None:
        person = Person(tmdb_id=1, name="Someone")
        assert person.nationalities == ()
        assert person.mother_tongue is None
        assert person.spoken_languages == ()

    def test_creates_with_all_optional_fields(self) -> None:
        person = Person(
            tmdb_id=525,
            name="Christopher Nolan",
            nationalities=("GB", "US"),
            mother_tongue="en",
            spoken_languages=("en", "fr"),
        )
        assert person.nationalities == ("GB", "US")
        assert person.mother_tongue == "en"
        assert person.spoken_languages == ("en", "fr")

    def test_nationalities_normalised_to_uppercase(self) -> None:
        person = Person(tmdb_id=1, name="Someone", nationalities=("gb", "us"))
        assert person.nationalities == ("GB", "US")

    def test_mother_tongue_normalised_to_lowercase(self) -> None:
        person = Person(tmdb_id=1, name="Someone", mother_tongue="EN")
        assert person.mother_tongue == "en"

    def test_spoken_languages_normalised_to_lowercase(self) -> None:
        person = Person(tmdb_id=1, name="Someone", spoken_languages=("EN", "FR"))
        assert person.spoken_languages == ("en", "fr")


class TestPersonValidation:
    """Field validation raises ValueError on invalid inputs."""

    def test_zero_tmdb_id_raises(self) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            Person(tmdb_id=0, name="Someone")

    def test_negative_tmdb_id_raises(self) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            Person(tmdb_id=-1, name="Someone")

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Person(tmdb_id=1, name="")

    def test_whitespace_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):
            Person(tmdb_id=1, name="   ")

    def test_invalid_nationality_code_raises(self) -> None:
        with pytest.raises(ValueError, match="nationalities"):
            Person(tmdb_id=1, name="Someone", nationalities=("GBR",))

    def test_invalid_mother_tongue_raises(self) -> None:
        with pytest.raises(ValueError, match="mother_tongue"):
            Person(tmdb_id=1, name="Someone", mother_tongue="eng")

    def test_invalid_spoken_language_raises(self) -> None:
        with pytest.raises(ValueError, match="spoken_languages"):
            Person(tmdb_id=1, name="Someone", spoken_languages=("en", "xxx"))


class TestPersonImmutability:
    """Frozen dataclass cannot be mutated."""

    def test_tmdb_id_is_immutable(self) -> None:
        person = Person(tmdb_id=1, name="Christopher Nolan")
        with pytest.raises(AttributeError):
            person.tmdb_id = 2  # type: ignore[misc]

    def test_name_is_immutable(self) -> None:
        person = Person(tmdb_id=1, name="Christopher Nolan")
        with pytest.raises(AttributeError):
            person.name = "Other"  # type: ignore[misc]


class TestPersonEquality:
    """Identity-based equality: two persons are equal if they share a tmdb_id."""

    def test_same_tmdb_id_are_equal(self) -> None:
        assert Person(tmdb_id=525, name="Christopher Nolan") == Person(tmdb_id=525, name="Christopher Nolan")

    def test_same_tmdb_id_different_name_are_equal(self) -> None:
        """Name is not part of identity; tmdb_id is the authoritative key."""
        assert Person(tmdb_id=525, name="Chris Nolan") == Person(tmdb_id=525, name="Christopher Nolan")

    def test_different_tmdb_id_not_equal(self) -> None:
        assert Person(tmdb_id=1, name="A") != Person(tmdb_id=2, name="A")

    def test_hashable_and_usable_in_set(self) -> None:
        p1 = Person(tmdb_id=525, name="Christopher Nolan")
        p2 = Person(tmdb_id=525, name="Christopher Nolan")
        assert len({p1, p2}) == 1

    def test_not_equal_to_other_types(self) -> None:
        person = Person(tmdb_id=525, name="Christopher Nolan")
        assert person != 525
        assert person != "Christopher Nolan"
