"""Abstract repository interfaces for the domain.

All concrete implementations live in ``app.infrastructure.persistence``.
The service layer depends only on these interfaces, keeping business
logic decoupled from the storage backend.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.domain.entities.event import Event, EventMembership, EventSeries
from app.core.domain.entities.user import User
from app.core.domain.entities.user_group import UserGroup, UserGroupMembership
from app.core.domain.enums import EventStatus, MembershipStatus


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
