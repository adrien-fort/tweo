"""Studio domain entity."""

from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Studio:
    """A film production studio or company.

    Identity is determined solely by ``tmdb_id``.

    Attributes:
        tmdb_id: TMDB unique identifier. Must be a positive integer.
        name: Official name of the studio (e.g. ``"Warner Bros. Pictures"``).

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``name`` is empty or whitespace only.

    Example:
        >>> studio = Studio(tmdb_id=174, name="Warner Bros. Pictures")
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
        if not isinstance(other, Studio):
            return NotImplemented
        return self.tmdb_id == other.tmdb_id

    def __hash__(self) -> int:
        """Hash by ``tmdb_id`` only."""
        return hash(self.tmdb_id)
