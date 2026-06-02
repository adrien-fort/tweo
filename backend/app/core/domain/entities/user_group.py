"""UserGroup and UserGroupMembership domain entities."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(eq=False)
class UserGroup:
    """A reusable preset group of users.

    Allows organisers to invite a named set of users to an event in one
    action rather than adding members individually. Membership is managed
    via :class:`UserGroupMembership`.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        name: Display name for the group (e.g. ``"Friday Film Club"``).
        owner_id: UUID of the :class:`~app.core.domain.entities.user.User`
            who created and manages the group.
        description: Optional description of the group's purpose.
        created_at: Timestamp of group creation (UTC).
        updated_at: Timestamp of last modification (UTC).

    Raises:
        ValueError: If ``name`` is empty or whitespace only.

    Example:
        >>> from uuid import uuid4
        >>> group = UserGroup(id=uuid4(), name="Friday Film Club", owner_id=uuid4())
    """

    id: UUID
    name: str
    owner_id: UUID
    description: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        """Validate fields after initialisation."""
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty or whitespace")

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, UserGroup):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)


@dataclass(eq=False)
class UserGroupMembership:
    """Membership of a user in a preset group.

    Tracks who added the member and when, providing an audit trail for
    group composition changes.

    Identity is determined solely by ``id``.

    Attributes:
        id: Internal UUID primary key.
        group_id: UUID of the parent :class:`UserGroup`.
        user_id: UUID of the member :class:`~app.core.domain.entities.user.User`.
        added_by: UUID of the :class:`~app.core.domain.entities.user.User`
            who added this member to the group.
        added_at: Timestamp when the membership was created (UTC).

    Example:
        >>> from uuid import uuid4
        >>> membership = UserGroupMembership(
        ...     id=uuid4(), group_id=uuid4(), user_id=uuid4(), added_by=uuid4()
        ... )
    """

    id: UUID
    group_id: UUID
    user_id: UUID
    added_by: UUID
    added_at: datetime = field(default_factory=_utcnow)

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, UserGroupMembership):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)
