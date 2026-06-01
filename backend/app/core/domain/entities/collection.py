"""Collection domain entity."""

from dataclasses import dataclass


@dataclass(frozen=True, eq=False)
class Collection:
    """A collection or franchise that groups related media items.

    Intentionally media-agnostic: movies, TV series, and games can all
    reference the same ``Collection`` via a
    :class:`~app.core.domain.value_objects.collection_membership.CollectionMembership`
    value object, keeping the aggregate free of circular dependencies.

    For TMDB movies, ``collection_id`` maps directly to TMDB's
    ``belongs_to_collection.id``. Cross-media franchises use internally
    managed IDs.

    Identity is determined solely by ``collection_id``.

    Attributes:
        collection_id: TMDB collection ID or internal franchise ID.
            Must be a positive integer.
        name: Human-readable name of the collection or franchise
            (e.g. ``"The Dark Knight Trilogy"``).

    Raises:
        ValueError: If ``collection_id`` is not a positive integer.
        ValueError: If ``name`` is empty or whitespace only.

    Example:
        >>> col = Collection(collection_id=263, name="The Dark Knight Trilogy")
    """

    collection_id: int
    name: str

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not isinstance(self.collection_id, int) or isinstance(self.collection_id, bool) or self.collection_id <= 0:
            raise ValueError(f"collection_id must be a positive integer, got: {self.collection_id!r}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace")

    def __eq__(self, other: object) -> bool:
        """Compare by ``collection_id`` only."""
        if not isinstance(other, Collection):
            return NotImplemented
        return self.collection_id == other.collection_id

    def __hash__(self) -> int:
        """Hash by ``collection_id`` only."""
        return hash(self.collection_id)
