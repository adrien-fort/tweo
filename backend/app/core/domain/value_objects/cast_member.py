"""CastMember value object."""

from dataclasses import dataclass

from app.core.domain.entities.person import Person


@dataclass(frozen=True)
class CastMember:
    """A person's acting role in a specific media production.

    Pairs a :class:`~app.core.domain.entities.person.Person` with the
    character they portray. Two ``CastMember`` instances are equal when
    both their ``person`` and ``character_name`` match (structural equality).

    A director who also acts in their own production is represented by
    the same ``Person`` instance in both ``Movie.director`` and a
    ``CastMember`` entry in ``Movie.cast`` — no special handling required.

    Attributes:
        person: The person performing the role.
        character_name: Name of the character portrayed in the production.

    Raises:
        ValueError: If ``character_name`` is empty or whitespace only.

    Example:
        >>> from app.core.domain.entities.person import Person
        >>> leo = Person(tmdb_id=6193, name="Leonardo DiCaprio")
        >>> member = CastMember(person=leo, character_name="Dom Cobb")
    """

    person: Person
    character_name: str

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not self.character_name or not self.character_name.strip():
            raise ValueError("character_name cannot be empty or whitespace")
