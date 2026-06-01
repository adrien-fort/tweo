"""Collection membership value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CollectionMembership:
    """Membership of a media item in a collection or franchise.

    Decouples the media item from the full collection aggregate,
    avoiding circular references while preserving enough context for
    display and ordering purposes.

    Attributes:
        collection_id: TMDB collection ID or internal franchise ID.
            Must be a positive integer.
        collection_name: Human-readable name of the collection
            (e.g. ``"The Dark Knight Trilogy"``).
        order: 1-based position of this item within the collection,
            or ``None`` for unordered collections such as shared
            universes.

    Raises:
        ValueError: If ``collection_id`` is not a positive integer.
        ValueError: If ``collection_name`` is empty or whitespace only.
        ValueError: If ``order`` is provided but is not a positive integer.

    Example:
        >>> membership = CollectionMembership(
        ...     collection_id=263,
        ...     collection_name="The Dark Knight Trilogy",
        ...     order=2,
        ... )
    """

    collection_id: int
    collection_name: str
    order: int | None = None

    def __post_init__(self) -> None:
        """Validate all fields after initialisation."""
        if not isinstance(self.collection_id, int) or isinstance(self.collection_id, bool) or self.collection_id <= 0:
            raise ValueError(f"collection_id must be a positive integer, got: {self.collection_id!r}")

        if not self.collection_name or not self.collection_name.strip():
            raise ValueError("collection_name cannot be empty or whitespace")

        if self.order is not None:
            if not isinstance(self.order, int) or isinstance(self.order, bool) or self.order <= 0:
                raise ValueError(f"order must be a positive integer when specified, got: {self.order!r}")
