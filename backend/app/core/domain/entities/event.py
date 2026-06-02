"""EventSeries, Event, and EventMembership domain entities."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.core.domain.enums import ActivityType, EventPrivacy, EventRole, EventStatus, MembershipStatus, RecurrenceType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(eq=False)
class EventSeries:
    """A recurring series of related events.

    Acts as a scheduling and grouping container only. It intentionally
    has no ``activity_type`` — each :class:`Event` instance declares its
    own type independently, allowing a series to mix movies, TV episodes,
    games, and so on (e.g. an MCU marathon spanning films and Disney+
    shows).

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        title: Human-readable series name (e.g. ``"MCU Marathon"``).
        organiser_id: UUID of the user who created the series.
        recurrence: How often new instances are scheduled.
        description: Optional longer description of the series.
        created_at: Timestamp of series creation (UTC).
        updated_at: Timestamp of last modification (UTC).

    Raises:
        ValueError: If ``title`` is empty or whitespace only.

    Example:
        >>> from uuid import uuid4
        >>> series = EventSeries(
        ...     id=uuid4(),
        ...     title="MCU Marathon",
        ...     organiser_id=uuid4(),
        ...     recurrence=RecurrenceType.WEEKLY,
        ... )
    """

    id: UUID
    title: str
    organiser_id: UUID
    recurrence: RecurrenceType
    description: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not self.title or not self.title.strip():
            raise ValueError("title cannot be empty or whitespace")

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, EventSeries):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)


@dataclass(eq=False)
class Event:
    """A single event instance, either standalone or part of a series.

    The organiser is stored directly on the entity and never appears in
    :class:`EventMembership`. Co-organisers and participants each have a
    membership row.

    ``series_sequence`` is 1-based and requires ``series_id`` to be set.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        title: Display title for this specific event instance.
        activity_type: The type of activity for this event. Declared
            per-instance so a series can mix types freely.
        organiser_id: UUID of the user who created the event. Immutable
            after creation.
        privacy: Join policy — ``PUBLIC`` (request + approval) or
            ``PRIVATE`` (invite-only).
        status: Lifecycle status. Defaults to ``OPEN``.
        series_id: UUID of the parent :class:`EventSeries`, or ``None``
            for standalone events.
        series_sequence: 1-based position within the series. Requires
            ``series_id`` to be set.
        description: Optional notes or context for this event.
        scheduled_at: Optional planned date and time (UTC).
        created_at: Timestamp of event creation (UTC).
        updated_at: Timestamp of last modification (UTC).

    Raises:
        ValueError: If ``title`` is empty or whitespace only.
        ValueError: If ``series_sequence`` is set without ``series_id``.
        ValueError: If ``series_sequence`` is set but is not a positive integer.

    Example:
        >>> from uuid import uuid4
        >>> event = Event(
        ...     id=uuid4(),
        ...     title="Avengers: Endgame Night",
        ...     activity_type=ActivityType.MOVIE,
        ...     organiser_id=uuid4(),
        ...     privacy=EventPrivacy.PRIVATE,
        ... )
    """

    id: UUID
    title: str
    activity_type: ActivityType
    organiser_id: UUID
    privacy: EventPrivacy
    status: EventStatus = EventStatus.OPEN
    series_id: UUID | None = None
    series_sequence: int | None = None
    description: str | None = None
    scheduled_at: datetime | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not self.title or not self.title.strip():
            raise ValueError("title cannot be empty or whitespace")
        if self.series_sequence is not None:
            if self.series_id is None:
                raise ValueError("series_sequence requires series_id to be set")
            if not isinstance(self.series_sequence, int) or self.series_sequence < 1:
                raise ValueError(f"series_sequence must be a positive integer, got: {self.series_sequence!r}")

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, Event):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)


@dataclass(eq=False)
class EventMembership:
    """A user's membership in a specific event.

    The event organiser is stored on :class:`Event` directly and does
    not have a membership row. All other participants — co-organisers and
    regular participants — are represented here.

    ``invited_via_group_id`` preserves the audit trail when a user is
    invited as part of a bulk group invite rather than individually.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        event_id: UUID of the parent :class:`Event`.
        user_id: UUID of the invited or requesting user.
        role: The user's role within this event.
        status: Current lifecycle status of the membership.
        invited_by: UUID of the user who issued the invitation or
            approved the join request.
        invited_at: Timestamp when the membership was created (UTC).
        invited_via_group_id: UUID of the :class:`~app.core.domain.entities.user_group.UserGroup`
            used for a bulk invite, or ``None`` for individual invites.
        responded_at: Timestamp when the user accepted or declined,
            or ``None`` if still pending.

    Example:
        >>> from uuid import uuid4
        >>> membership = EventMembership(
        ...     id=uuid4(),
        ...     event_id=uuid4(),
        ...     user_id=uuid4(),
        ...     role=EventRole.PARTICIPANT,
        ...     status=MembershipStatus.INVITED,
        ...     invited_by=uuid4(),
        ... )
    """

    id: UUID
    event_id: UUID
    user_id: UUID
    role: EventRole
    status: MembershipStatus
    invited_by: UUID
    invited_at: datetime = field(default_factory=_utcnow)
    invited_via_group_id: UUID | None = None
    responded_at: datetime | None = None

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, EventMembership):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)
