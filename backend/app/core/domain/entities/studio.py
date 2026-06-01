"""Studio domain entity."""

from dataclasses import dataclass

from app.core.domain.validators import validate_country_code


@dataclass(frozen=True, eq=False)
class Studio:
    """A film production studio or company.

    Identity is determined solely by ``tmdb_id``.

    Attributes:
        tmdb_id: TMDB unique identifier. Must be a positive integer.
        name: Official name of the studio (e.g. ``"Warner Bros. Pictures"``).
        country: ISO 3166-1 alpha-2 country code for the studio's
            headquarters (e.g. ``"US"``). Normalised to uppercase.
            ``None`` when not available from TMDB.

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``name`` is empty or whitespace only.
        ValueError: If ``country`` is provided but is not a valid
            ISO 3166-1 alpha-2 country code.

    Example:
        >>> studio = Studio(tmdb_id=174, name="Warner Bros. Pictures", country="US")
    """

    tmdb_id: int
    name: str
    country: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalise fields after initialisation."""
        if not isinstance(self.tmdb_id, int) or isinstance(self.tmdb_id, bool) or self.tmdb_id <= 0:
            raise ValueError(f"tmdb_id must be a positive integer, got: {self.tmdb_id!r}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace")
        if self.country is not None:
            object.__setattr__(self, "country", validate_country_code(self.country, "country"))

    def __eq__(self, other: object) -> bool:
        """Compare by ``tmdb_id`` only."""
        if not isinstance(other, Studio):
            return NotImplemented
        return self.tmdb_id == other.tmdb_id

    def __hash__(self) -> int:
        """Hash by ``tmdb_id`` only."""
        return hash(self.tmdb_id)
