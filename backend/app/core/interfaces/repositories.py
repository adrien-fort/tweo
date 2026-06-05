"""Abstract repository interfaces for the domain.

All concrete implementations live in ``app.infrastructure.persistence``.
The service layer depends only on these interfaces, keeping business
logic decoupled from the storage backend.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.domain.entities.ballot import EventBallot
from app.core.domain.entities.event import Event, EventMembership, EventSeries
from app.core.domain.entities.user import User
from app.core.domain.entities.user_group import UserGroup, UserGroupMembership
from app.core.domain.entities.wishlist import EventCandidate, WishlistEntry
from app.core.domain.enums import EventStatus, MembershipStatus, WishlistEntryStatus


class UserRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.user.User` entities.

    All email lookups use the HMAC hash of the email (never the plaintext)
    to avoid decrypting every row. Implementations are responsible for
    encrypting/decrypting PII fields transparently.
    """

    @abstractmethod
    def get_by_id(self, id: UUID) -> User | None:
        """Return the user with the given internal UUID, or ``None``."""

    @abstractmethod
    def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """Return the user with the given Firebase UID, or ``None``."""

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email address, or ``None``.

        Implementations must derive the HMAC of the email internally
        and query against the stored hash — never the plaintext.
        """

    @abstractmethod
    def save(self, user: User) -> User:
        """Persist a new or updated user and return the saved instance."""

    @abstractmethod
    def anonymize(self, id: UUID) -> None:
        """Anonymise a user's PII in place (GDPR right to erasure).

        Sets ``anonymized_at`` and nulls PII fields (email, nickname,
        avatar_url, gender, pronouns, bio, preferences). The user row
        is retained for referential integrity.
        """


class UserGroupRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.user_group.UserGroup` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> UserGroup | None:
        """Return the group with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_owner(self, owner_id: UUID) -> list[UserGroup]:
        """Return all groups owned by the given user."""

    @abstractmethod
    def save(self, group: UserGroup) -> UserGroup:
        """Persist a new or updated group and return the saved instance."""

    @abstractmethod
    def delete(self, id: UUID) -> None:
        """Delete the group and all its memberships."""

    @abstractmethod
    def add_member(self, membership: UserGroupMembership) -> UserGroupMembership:
        """Add a member to a group."""

    @abstractmethod
    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        """Remove a user from a group."""

    @abstractmethod
    def get_members(self, group_id: UUID) -> list[UserGroupMembership]:
        """Return all memberships for the given group."""


class EventSeriesRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.event.EventSeries` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> EventSeries | None:
        """Return the series with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_organiser(self, organiser_id: UUID) -> list[EventSeries]:
        """Return all series created by the given organiser."""

    @abstractmethod
    def save(self, series: EventSeries) -> EventSeries:
        """Persist a new or updated series and return the saved instance."""


class EventRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.event.Event` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> Event | None:
        """Return the event with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_series(self, series_id: UUID) -> list[Event]:
        """Return all events belonging to the given series, ordered by ``series_sequence``."""

    @abstractmethod
    def get_by_organiser(self, organiser_id: UUID) -> list[Event]:
        """Return all events created by the given organiser."""

    @abstractmethod
    def get_by_status(self, status: EventStatus) -> list[Event]:
        """Return all events with the given status."""

    @abstractmethod
    def save(self, event: Event) -> Event:
        """Persist a new or updated event and return the saved instance."""


class EventMembershipRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.event.EventMembership` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> EventMembership | None:
        """Return the membership with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_event(self, event_id: UUID) -> list[EventMembership]:
        """Return all memberships for the given event."""

    @abstractmethod
    def get_by_user(self, user_id: UUID) -> list[EventMembership]:
        """Return all event memberships for the given user."""

    @abstractmethod
    def get_by_event_and_user(self, event_id: UUID, user_id: UUID) -> EventMembership | None:
        """Return the membership for a specific user in a specific event, or ``None``."""

    @abstractmethod
    def save(self, membership: EventMembership) -> EventMembership:
        """Persist a new or updated membership and return the saved instance."""

    @abstractmethod
    def get_by_status(self, event_id: UUID, status: MembershipStatus) -> list[EventMembership]:
        """Return all memberships for an event filtered by status."""


class WishlistEntryRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.wishlist.WishlistEntry` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> WishlistEntry | None:
        """Return the entry with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_series(self, series_id: UUID) -> list[WishlistEntry]:
        """Return all entries for the given series, regardless of status."""

    @abstractmethod
    def get_active_by_series(self, series_id: UUID) -> list[WishlistEntry]:
        """Return entries with status ``PENDING`` or ``SCHEDULED`` for the given series."""

    @abstractmethod
    def get_by_series_and_status(self, series_id: UUID, status: WishlistEntryStatus) -> list[WishlistEntry]:
        """Return entries for the given series filtered by status."""

    @abstractmethod
    def save(self, entry: WishlistEntry) -> WishlistEntry:
        """Persist a new or updated entry and return the saved instance."""


class EventCandidateRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.wishlist.EventCandidate` entities."""

    @abstractmethod
    def get_by_id(self, id: UUID) -> EventCandidate | None:
        """Return the candidate with the given UUID, or ``None``."""

    @abstractmethod
    def get_by_event(self, event_id: UUID) -> list[EventCandidate]:
        """Return all candidates shortlisted for the given event."""

    @abstractmethod
    def save(self, candidate: EventCandidate) -> EventCandidate:
        """Persist a new candidate and return the saved instance."""

    @abstractmethod
    def delete(self, id: UUID) -> None:
        """Remove a candidate from the shortlist."""


class EventBallotRepository(ABC):
    """Persistence interface for :class:`~app.core.domain.entities.ballot.EventBallot` entities.

    Ballots are append-only. Revisions supersede prior rows rather than
    updating them in place, so ``save`` always inserts a new row.
    """

    @abstractmethod
    def get_by_id(self, id: UUID) -> EventBallot | None:
        """Return the ballot with the given UUID, or ``None``."""

    @abstractmethod
    def get_current_by_event_and_user(self, event_id: UUID, user_id: UUID, round: int = 1) -> EventBallot | None:
        """Return the current (non-superseded) ballot for a user in a given event round, or ``None``."""

    @abstractmethod
    def get_all_by_event(self, event_id: UUID, round: int = 1) -> list[EventBallot]:
        """Return all current ballots for the given event and round."""

    @abstractmethod
    def get_history_by_event_and_user(self, event_id: UUID, user_id: UUID) -> list[EventBallot]:
        """Return the full ballot history for a user in an event, ordered by ``cast_at`` ascending."""

    @abstractmethod
    def save(self, ballot: EventBallot) -> EventBallot:
        """Insert a new ballot row and return the saved instance.

        Callers are responsible for superseding the previous current ballot
        before calling ``save`` with the revised one.
        """

    @abstractmethod
    def supersede(self, ballot_id: UUID) -> None:
        """Mark the given ballot as superseded by setting ``superseded_at`` to now."""
