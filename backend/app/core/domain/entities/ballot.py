"""EventBallot domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(eq=False)
class EventBallot:
    """A member's cast ballot for a specific event.

    One ballot is created per member per event per round. Revisions are
    recorded by superseding the previous ballot (setting its
    ``superseded_at`` timestamp) and inserting a new row, preserving the
    full audit trail.

    The ``payload`` structure is determined by the
    :class:`~app.core.domain.enums.VotingSystem` configured on the parent
    :class:`~app.core.domain.entities.event.EventSeries`::

        # Approval voting — member selects one or more candidates
        {"approved": ["<candidate-uuid>", "<candidate-uuid>"]}

        # Ranked choice — member ranks all candidates (1st to last)
        {"rankings": ["<candidate-uuid>", "<candidate-uuid>", ...]}

        # Two-round runoff — member picks one candidate per round
        {"pick": "<candidate-uuid>"}

    Candidate UUIDs reference :class:`~app.core.domain.entities.wishlist.EventCandidate`
    ids, scoping the ballot to the event's shortlist.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        event_id: UUID of the :class:`~app.core.domain.entities.event.Event`
            this ballot belongs to.
        user_id: UUID of the member who cast this ballot.
        payload: Voting choices encoded as a dictionary.  Structure varies
            by voting system; see above.
        cast_at: Timestamp when this ballot was cast (UTC).
        round: Voting round number.  Defaults to ``1``; increments for
            multi-round systems such as ``TWO_ROUND_RUNOFF``.
        superseded_at: Timestamp when this ballot was replaced by a
            revised version, or ``None`` if this is the current ballot.

    Raises:
        ValueError: If ``round`` is not a positive integer.
        ValueError: If ``payload`` is not a dictionary.

    Example:
        >>> from uuid import uuid4
        >>> ballot = EventBallot(
        ...     id=uuid4(),
        ...     event_id=uuid4(),
        ...     user_id=uuid4(),
        ...     payload={"approved": [str(uuid4())]},
        ... )
    """

    id: UUID
    event_id: UUID
    user_id: UUID
    payload: dict[str, Any]
    cast_at: datetime = field(default_factory=_utcnow)
    round: int = 1
    superseded_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not isinstance(self.round, int) or isinstance(self.round, bool) or self.round < 1:
            raise ValueError(f"round must be a positive integer, got: {self.round!r}")
        if not isinstance(self.payload, dict):
            raise ValueError(f"payload must be a dictionary, got: {type(self.payload).__name__!r}")

    @property
    def is_current(self) -> bool:
        """Return ``True`` if this ballot has not been superseded."""
        return self.superseded_at is None

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, EventBallot):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)
