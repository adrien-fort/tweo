"""Movie domain entity."""

from dataclasses import dataclass

from app.core.domain.entities.person import Person
from app.core.domain.entities.studio import Studio
from app.core.domain.value_objects.cast_member import CastMember
from app.core.domain.value_objects.collection_membership import CollectionMembership
from app.core.domain.value_objects.media_links import MediaLinks
from app.core.domain.value_objects.ratings import Ratings

_FIRST_FILM_YEAR = 1888


@dataclass(frozen=True, eq=False)
class Movie:
    """An immutable movie record as sourced from TMDB and stored locally.

    The app does not mutate movie data; all information is loaded from
    TMDB and persisted as-is. Identity is determined solely by
    ``tmdb_id``; no fallback to title or year is applied — any ID
    discrepancy must be resolved at the data source.

    A director who also acts in their own film is represented by the
    same :class:`~app.core.domain.entities.person.Person` instance in
    both ``director`` and a :class:`~app.core.domain.value_objects.cast_member.CastMember`
    entry within ``cast``.

    Attributes:
        tmdb_id: TMDB unique identifier. Strictly enforced as primary
            key; must be a positive integer.
        title: Official release title of the movie.
        synopsis: Plot summary or overview.
        release_year: Year of original theatrical release. Must be
            ``>= 1888``, the year of the earliest surviving film.
        director: Person who directed the movie.
        cast: Ordered tuple of cast members. Must contain at least one
            entry.
        studios: Tuple of production studios. Must contain at least one
            entry.
        media_links: External poster and trailer URLs.
        ratings: Community score and age certifications.
        collection_membership: Describes this movie's position within a
            collection or franchise, or ``None`` for standalone films.

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``title`` or ``synopsis`` is empty or whitespace.
        ValueError: If ``release_year`` is before 1888.
        ValueError: If ``cast`` or ``studios`` is an empty tuple.

    Example:
        >>> from app.core.domain.entities.person import Person
        >>> from app.core.domain.entities.studio import Studio
        >>> from app.core.domain.value_objects.cast_member import CastMember
        >>> from app.core.domain.value_objects.media_links import MediaLinks
        >>> from app.core.domain.value_objects.ratings import Ratings
        >>> nolan = Person(tmdb_id=525, name="Christopher Nolan")
        >>> wb = Studio(tmdb_id=174, name="Warner Bros. Pictures")
        >>> movie = Movie(
        ...     tmdb_id=27205,
        ...     title="Inception",
        ...     synopsis="A thief who steals secrets through dreams.",
        ...     release_year=2010,
        ...     director=nolan,
        ...     cast=(CastMember(person=nolan, character_name="Himself"),),
        ...     studios=(wb,),
        ...     media_links=MediaLinks(),
        ...     ratings=Ratings(),
        ... )
    """

    tmdb_id: int
    title: str
    synopsis: str
    release_year: int
    director: Person
    cast: tuple[CastMember, ...]
    studios: tuple[Studio, ...]
    media_links: MediaLinks
    ratings: Ratings
    collection_membership: CollectionMembership | None = None

    def __post_init__(self) -> None:
        """Validate all fields after initialisation."""
        if not isinstance(self.tmdb_id, int) or isinstance(self.tmdb_id, bool) or self.tmdb_id <= 0:
            raise ValueError(f"tmdb_id must be a positive integer, got: {self.tmdb_id!r}")

        if not self.title or not self.title.strip():
            raise ValueError("title cannot be empty or whitespace")

        if not self.synopsis or not self.synopsis.strip():
            raise ValueError("synopsis cannot be empty or whitespace")

        if not isinstance(self.release_year, int) or self.release_year < _FIRST_FILM_YEAR:
            raise ValueError(
                f"release_year must be >= {_FIRST_FILM_YEAR} (year of earliest surviving film),"
                f" got: {self.release_year!r}"
            )

        if not self.cast:
            raise ValueError("cast must contain at least one CastMember")

        if not self.studios:
            raise ValueError("studios must contain at least one Studio")

    def __eq__(self, other: object) -> bool:
        """Compare by ``tmdb_id`` only."""
        if not isinstance(other, Movie):
            return NotImplemented
        return self.tmdb_id == other.tmdb_id

    def __hash__(self) -> int:
        """Hash by ``tmdb_id`` only."""
        return hash(self.tmdb_id)
