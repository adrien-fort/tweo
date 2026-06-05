"""WishlistEntry and EventCandidate domain entities."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from app.core.domain.enums import ActivityType, WishlistEntryStatus


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(eq=False)
class WishlistEntry:
    """A media item nominated for future events within a recurring series.

    Entries live on the series-level wishlist (the full pool). An entry is
    promoted to an :class:`EventCandidate` when it is shortlisted for a
    specific event.

    ``completed_event_id`` is set only when status reaches ``COMPLETED``
    and records the event in which this entry was the winning pick.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        series_id: UUID of the parent :class:`~app.core.domain.entities.event.EventSeries`.
        activity_type: The category of media being nominated.
        tmdb_id: External identifier for the media item (TMDB for movies
            and TV series; mapped to equivalent source IDs for other
            activity types in future).  Must be a positive integer.
        added_by: UUID of the user who nominated this entry. Retained for
            audit purposes only; does not influence selection logic.
        added_at: Timestamp when the entry was added to the wishlist (UTC).
        status: Lifecycle status. Defaults to ``PENDING``.
        completed_event_id: UUID of the :class:`~app.core.domain.entities.event.Event`
            in which this entry won, or ``None`` while still active.

    Raises:
        ValueError: If ``tmdb_id`` is not a positive integer.
        ValueError: If ``completed_event_id`` is set but ``status`` is not
            ``COMPLETED``.

    Example:
        >>> from uuid import uuid4
        >>> entry = WishlistEntry(
        ...     id=uuid4(),
        ...     series_id=uuid4(),
        ...     activity_type=ActivityType.MOVIE,
        ...     tmdb_id=550,
        ...     added_by=uuid4(),
        ... )
    """

    id: UUID
    series_id: UUID
    activity_type: ActivityType
    tmdb_id: int
    added_by: UUID
    added_at: datetime = field(default_factory=_utcnow)
    status: WishlistEntryStatus = WishlistEntryStatus.PENDING
    completed_event_id: UUID | None = None

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not isinstance(self.tmdb_id, int) or isinstance(self.tmdb_id, bool) or self.tmdb_id <= 0:
            raise ValueError(f"tmdb_id must be a positive integer, got: {self.tmdb_id!r}")
        if self.completed_event_id is not None and self.status != WishlistEntryStatus.COMPLETED:
            raise ValueError(
                f"completed_event_id can only be set when status is COMPLETED, got status: {self.status!r}"
            )

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, WishlistEntry):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)


@dataclass(eq=False)
class EventCandidate:
    """A wishlist entry shortlisted as a candidate for a specific event.

    Bridges the series-level :class:`WishlistEntry` pool and the
    event-level ballot. The set of candidates for an event defines
    the options members vote on.

    ``added_by`` is ``None`` when the system automatically selected the
    candidate; a UUID when an organiser or co-organiser made a manual pick.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        event_id: UUID of the :class:`~app.core.domain.entities.event.Event`
            this candidate belongs to.
        wishlist_entry_id: UUID of the source :class:`WishlistEntry`.
        added_at: Timestamp when the candidate was added to the shortlist (UTC).
        added_by: UUID of the user who added this candidate, or ``None``
            if auto-selected by the system.

    Example:
        >>> from uuid import uuid4
        >>> candidate = EventCandidate(
        ...     id=uuid4(),
        ...     event_id=uuid4(),
        ...     wishlist_entry_id=uuid4(),
        ... )
    """

    id: UUID
    event_id: UUID
    wishlist_entry_id: UUID
    added_at: datetime = field(default_factory=_utcnow)
    added_by: UUID | None = None

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, EventCandidate):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)
