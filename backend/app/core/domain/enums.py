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


class WishlistEntryStatus(Enum):
    """Lifecycle status of a wishlist entry.

    ``PENDING``: the entry is on the active wishlist, available to be
    selected as a candidate for a future event.

    ``SCHEDULED``: the entry has been selected as a candidate for an
    upcoming event and is currently in an :class:`EventCandidate` list.
    Returns to ``PENDING`` if the event is cancelled before completion.

    ``COMPLETED``: the entry was the winning pick for an event and that
    event has completed. The entry is kept for history and excluded from
    the active wishlist view.

    ``REMOVED``: the entry was manually removed by the suggester or an
    organiser. Excluded from the active wishlist view.
    """

    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    REMOVED = "removed"


class VotingSystem(Enum):
    """Voting system used to tally event ballots within a series.

    ``APPROVAL``: each voter selects one or more candidates they approve
    of; the candidate with the most approvals wins.

    ``RANKED_CHOICE``: each voter ranks all candidates; the winner is
    determined by instant-runoff elimination.

    ``TWO_ROUND_RUNOFF``: a first round narrows the field to the top two
    candidates; a second round determines the winner.
    """

    APPROVAL = "approval"
    RANKED_CHOICE = "ranked_choice"
    TWO_ROUND_RUNOFF = "two_round_runoff"
