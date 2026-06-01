"""Person domain entity."""

from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Person:
    """A person involved in a media production.

    Serves as both director and actor depending on context; no subclassing
    needed. A director who also acts in their own film is represented by the
    same ``Person`` instance appearing in both ``Movie.director`` and one of
    the ``CastMember`` entries in ``Movie.cast``.

    Identity is determined solely by ``tmdb_id``.

    Attributes:
        tmdb_id: TMDB unique identifier. Strictly used as primary key;
            must be a positive integer.
        name: Full name of the person.

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``name`` is empty or whitespace only.

    Example:
        >>> director = Person(tmdb_id=525, name="Christopher Nolan")
        >>> actor = Person(tmdb_id=525, name="Christopher Nolan")
        >>> director == actor
        True
    """

    tmdb_id: int
    name: str

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not isinstance(self.tmdb_id, int) or isinstance(self.tmdb_id, bool) or self.tmdb_id <= 0:
            raise ValueError(f"tmdb_id must be a positive integer, got: {self.tmdb_id!r}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace")

    def __eq__(self, other: object) -> bool:
        """Compare by ``tmdb_id`` only."""
        if not isinstance(other, Person):
            return NotImplemented
        return self.tmdb_id == other.tmdb_id

    def __hash__(self) -> int:
        """Hash by ``tmdb_id`` only."""
        return hash(self.tmdb_id)
