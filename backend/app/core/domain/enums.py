"""Domain enumerations for user, group, and event concepts."""

from enum import Enum


class SystemRole(Enum):
    """Platform-level role assigned to a user account.

    Controls access to administrative features. Independent of any
    event-level role a user may hold within a specific event.
    """

    MEMBER = "member"
    ADMIN = "admin"


class ActivityType(Enum):
    """Type of activity that an event is organised around."""

    MOVIE = "movie"
    TV_SERIES = "tv_series"
    VIDEO_GAME = "video_game"
    TABLETOP_GAME = "tabletop_game"


class RecurrenceType(Enum):
    """How often a recurring event series repeats."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class EventPrivacy(Enum):
    """Visibility and join policy for an event.

    ``PUBLIC``: any user may request to join; organiser or co-organiser
    approves the request.

    ``PRIVATE``: only users explicitly invited by an organiser or
    co-organiser may join.
    """

    PUBLIC = "public"
    PRIVATE = "private"


class EventStatus(Enum):
    """Lifecycle status of an event."""

    OPEN = "open"
    VOTING = "voting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventRole(Enum):
    """Role a user holds within a specific event.

    The event organiser is stored directly on the ``Event`` entity and
    does not appear in ``EventMembership``. Only co-organisers and
    participants have membership rows.
    """

    CO_ORGANISER = "co_organiser"
    PARTICIPANT = "participant"


class MembershipStatus(Enum):
    """Lifecycle status of an event membership.

    ``INVITED``: organiser or co-organiser sent an explicit invitation
    (private events).

    ``PENDING_APPROVAL``: user requested to join a public event and is
    awaiting organiser approval.

    ``ACCEPTED``: user is confirmed as a participant.

    ``DECLINED``: user declined the invitation or was rejected.
    """

    INVITED = "invited"
    PENDING_APPROVAL = "pending_approval"
    ACCEPTED = "accepted"
    DECLINED = "declined"
