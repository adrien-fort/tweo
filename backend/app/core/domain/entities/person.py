"""Person domain entity."""

from dataclasses import dataclass, field

from app.core.domain.validators import validate_country_code, validate_language_code


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
        nationalities: ISO 3166-1 alpha-2 country codes representing the
            person's nationalities (e.g. ``("GB", "US")``). Normalised to
            uppercase. Defaults to an empty tuple when not available.
        mother_tongue: ISO 639-1 language code for the person's native
            language (e.g. ``"en"``). Normalised to lowercase. ``None``
            when not available.
        spoken_languages: ISO 639-1 language codes for additional languages
            the person speaks, separate from ``mother_tongue``
            (e.g. ``("fr", "de")``). Normalised to lowercase. Defaults to
            an empty tuple when not available.

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``name`` is empty or whitespace only.
        ValueError: If any code in ``nationalities`` is not a valid
            ISO 3166-1 alpha-2 country code.
        ValueError: If ``mother_tongue`` is provided but is not a valid
            ISO 639-1 alpha-2 language code.
        ValueError: If any code in ``spoken_languages`` is not a valid
            ISO 639-1 alpha-2 language code.

    Example:
        >>> person = Person(
        ...     tmdb_id=525,
        ...     name="Christopher Nolan",
        ...     nationalities=("GB", "US"),
        ...     mother_tongue="en",
        ...     spoken_languages=("fr",),
        ... )
    """

    tmdb_id: int
    name: str
    nationalities: tuple[str, ...] = field(default_factory=tuple)
    mother_tongue: str | None = None
    spoken_languages: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate and normalise all fields after initialisation."""
        if not isinstance(self.tmdb_id, int) or isinstance(self.tmdb_id, bool) or self.tmdb_id <= 0:
            raise ValueError(f"tmdb_id must be a positive integer, got: {self.tmdb_id!r}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace")

        object.__setattr__(
            self,
            "nationalities",
            tuple(validate_country_code(c, "nationalities") for c in self.nationalities),
        )

        if self.mother_tongue is not None:
            object.__setattr__(
                self,
                "mother_tongue",
                validate_language_code(self.mother_tongue, "mother_tongue"),
            )

        object.__setattr__(
            self,
            "spoken_languages",
            tuple(validate_language_code(c, "spoken_languages") for c in self.spoken_languages),
        )

    def __eq__(self, other: object) -> bool:
        """Compare by ``tmdb_id`` only."""
        if not isinstance(other, Person):
            return NotImplemented
        return self.tmdb_id == other.tmdb_id

    def __hash__(self) -> int:
        """Hash by ``tmdb_id`` only."""
        return hash(self.tmdb_id)
