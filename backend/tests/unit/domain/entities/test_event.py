"""Tests for EventSeries, Event, and EventMembership entities."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.domain.entities.event import Event, EventMembership, EventSeries
from app.core.domain.enums import (
    ActivityType,
    EventPrivacy,
    EventRole,
    EventStatus,
    MembershipStatus,
    RecurrenceType,
    VotingSystem,
)


@pytest.fixture
def organiser_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_series(organiser_id: UUID) -> EventSeries:
    return EventSeries(
        id=uuid4(),
        title="MCU Marathon",
        organiser_id=organiser_id,
        recurrence=RecurrenceType.WEEKLY,
    )


@pytest.fixture
def valid_event(organiser_id: UUID) -> Event:
    return Event(
        id=uuid4(),
        title="Avengers: Endgame Night",
        activity_type=ActivityType.MOVIE,
        organiser_id=organiser_id,
        privacy=EventPrivacy.PRIVATE,
    )


# ── EventSeries ───────────────────────────────────────────────────────────────


class TestEventSeriesCreation:
    """Valid EventSeries construction scenarios."""

    def test_creates_with_required_fields(self, valid_series: EventSeries, organiser_id: UUID) -> None:
        assert isinstance(valid_series.id, UUID)
        assert valid_series.title == "MCU Marathon"
        assert valid_series.organiser_id == organiser_id
        assert valid_series.recurrence == RecurrenceType.WEEKLY

    def test_description_defaults_to_none(self, valid_series: EventSeries) -> None:
        assert valid_series.description is None

    def test_series_has_no_activity_type(self, valid_series: EventSeries) -> None:
        """EventSeries is a scheduling container — activity type lives on each Event."""
        assert not hasattr(valid_series, "activity_type")

    def test_timestamps_default_to_utc_now(self, valid_series: EventSeries) -> None:
        assert valid_series.created_at.tzinfo is not None
        assert valid_series.updated_at.tzinfo is not None


class TestEventSeriesValidation:
    """EventSeries field validation."""

    def test_empty_title_raises(self, organiser_id: UUID) -> None:
        with pytest.raises(ValueError, match="title"):
            EventSeries(id=uuid4(), title="", organiser_id=organiser_id, recurrence=RecurrenceType.WEEKLY)

    def test_whitespace_title_raises(self, organiser_id: UUID) -> None:
        with pytest.raises(ValueError, match="title"):
            EventSeries(id=uuid4(), title="   ", organiser_id=organiser_id, recurrence=RecurrenceType.WEEKLY)


class TestEventSeriesVotingSystem:
    """EventSeries.voting_system field."""

    def test_voting_system_defaults_to_approval(self, valid_series: EventSeries) -> None:
        assert valid_series.voting_system == VotingSystem.APPROVAL

    def test_voting_system_can_be_set_explicitly(self, organiser_id: UUID) -> None:
        series = EventSeries(
            id=uuid4(),
            title="Ranked Night",
            organiser_id=organiser_id,
            recurrence=RecurrenceType.WEEKLY,
            voting_system=VotingSystem.RANKED_CHOICE,
        )
        assert series.voting_system == VotingSystem.RANKED_CHOICE

    def test_two_round_runoff_system(self, organiser_id: UUID) -> None:
        series = EventSeries(
            id=uuid4(),
            title="Runoff Night",
            organiser_id=organiser_id,
            recurrence=RecurrenceType.MONTHLY,
            voting_system=VotingSystem.TWO_ROUND_RUNOFF,
        )
        assert series.voting_system == VotingSystem.TWO_ROUND_RUNOFF


class TestEventSeriesEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self, organiser_id: UUID) -> None:
        uid = uuid4()
        s1 = EventSeries(id=uid, title="Series A", organiser_id=organiser_id, recurrence=RecurrenceType.MONTHLY)
        s2 = EventSeries(id=uid, title="Series B", organiser_id=organiser_id, recurrence=RecurrenceType.WEEKLY)
        assert s1 == s2

    def test_different_id_not_equal(self, organiser_id: UUID) -> None:
        assert EventSeries(
            id=uuid4(), title="S", organiser_id=organiser_id, recurrence=RecurrenceType.WEEKLY
        ) != EventSeries(id=uuid4(), title="S", organiser_id=organiser_id, recurrence=RecurrenceType.WEEKLY)

    def test_hashable(self, valid_series: EventSeries) -> None:
        assert len({valid_series, valid_series}) == 1


# ── Event ─────────────────────────────────────────────────────────────────────


class TestEventCreation:
    """Valid Event construction scenarios."""

    def test_creates_with_required_fields(self, valid_event: Event, organiser_id: UUID) -> None:
        assert isinstance(valid_event.id, UUID)
        assert valid_event.title == "Avengers: Endgame Night"
        assert valid_event.activity_type == ActivityType.MOVIE
        assert valid_event.organiser_id == organiser_id
        assert valid_event.privacy == EventPrivacy.PRIVATE

    def test_status_defaults_to_open(self, valid_event: Event) -> None:
        assert valid_event.status == EventStatus.OPEN

    def test_series_fields_default_to_none(self, valid_event: Event) -> None:
        assert valid_event.series_id is None
        assert valid_event.series_sequence is None

    def test_optional_fields_default_to_none(self, valid_event: Event) -> None:
        assert valid_event.description is None
        assert valid_event.scheduled_at is None

    def test_creates_as_series_instance(self, organiser_id: UUID) -> None:
        series_id = uuid4()
        event = Event(
            id=uuid4(),
            title="Episode 3",
            activity_type=ActivityType.TV_SERIES,
            organiser_id=organiser_id,
            privacy=EventPrivacy.PRIVATE,
            series_id=series_id,
            series_sequence=3,
        )
        assert event.series_id == series_id
        assert event.series_sequence == 3

    def test_event_in_mcu_series_can_be_tv_series(self, organiser_id: UUID) -> None:
        """A MOVIE series can contain TV_SERIES events — no type lock."""
        event = Event(
            id=uuid4(),
            title="WandaVision S01",
            activity_type=ActivityType.TV_SERIES,
            organiser_id=organiser_id,
            privacy=EventPrivacy.PRIVATE,
            series_id=uuid4(),
            series_sequence=5,
        )
        assert event.activity_type == ActivityType.TV_SERIES

    def test_timestamps_default_to_utc_now(self, valid_event: Event) -> None:
        assert valid_event.created_at.tzinfo is not None
        assert valid_event.updated_at.tzinfo is not None


class TestEventValidation:
    """Event field validation."""

    def test_empty_title_raises(self, organiser_id: UUID) -> None:
        with pytest.raises(ValueError, match="title"):
            Event(
                id=uuid4(),
                title="",
                activity_type=ActivityType.MOVIE,
                organiser_id=organiser_id,
                privacy=EventPrivacy.PUBLIC,
            )

    def test_series_sequence_without_series_id_raises(self, organiser_id: UUID) -> None:
        with pytest.raises(ValueError, match="series_sequence"):
            Event(
                id=uuid4(),
                title="Episode",
                activity_type=ActivityType.TV_SERIES,
                organiser_id=organiser_id,
                privacy=EventPrivacy.PRIVATE,
                series_sequence=1,
            )

    def test_zero_series_sequence_raises(self, organiser_id: UUID) -> None:
        with pytest.raises(ValueError, match="series_sequence"):
            Event(
                id=uuid4(),
                title="Episode",
                activity_type=ActivityType.TV_SERIES,
                organiser_id=organiser_id,
                privacy=EventPrivacy.PRIVATE,
                series_id=uuid4(),
                series_sequence=0,
            )


class TestEventMutability:
    """Event status and description can be updated."""

    def test_status_can_be_updated(self, valid_event: Event) -> None:
        valid_event.status = EventStatus.VOTING
        assert valid_event.status == EventStatus.VOTING

    def test_description_can_be_set(self, valid_event: Event) -> None:
        valid_event.description = "Watch Endgame together!"
        assert valid_event.description == "Watch Endgame together!"


class TestEventEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self, organiser_id: UUID) -> None:
        uid = uuid4()
        kwargs = {"activity_type": ActivityType.MOVIE, "organiser_id": organiser_id, "privacy": EventPrivacy.PUBLIC}
        e1 = Event(id=uid, title="A", **kwargs)
        e2 = Event(id=uid, title="B", **kwargs)
        assert e1 == e2

    def test_different_id_not_equal(self, organiser_id: UUID) -> None:
        kwargs = {"title": "E", "activity_type": ActivityType.MOVIE, "organiser_id": organiser_id}
        assert Event(id=uuid4(), privacy=EventPrivacy.PUBLIC, **kwargs) != Event(
            id=uuid4(), privacy=EventPrivacy.PUBLIC, **kwargs
        )

    def test_hashable(self, valid_event: Event) -> None:
        assert len({valid_event, valid_event}) == 1


# ── EventMembership ───────────────────────────────────────────────────────────


class TestEventMembershipCreation:
    """Valid EventMembership construction scenarios."""

    def test_creates_with_required_fields(self) -> None:
        event_id, user_id, invited_by = uuid4(), uuid4(), uuid4()
        membership = EventMembership(
            id=uuid4(),
            event_id=event_id,
            user_id=user_id,
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=invited_by,
        )
        assert membership.event_id == event_id
        assert membership.user_id == user_id
        assert membership.role == EventRole.PARTICIPANT
        assert membership.status == MembershipStatus.INVITED
        assert membership.invited_by == invited_by

    def test_optional_fields_default_to_none(self) -> None:
        membership = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.CO_ORGANISER,
            status=MembershipStatus.ACCEPTED,
            invited_by=uuid4(),
        )
        assert membership.invited_via_group_id is None
        assert membership.responded_at is None

    def test_creates_with_group_invite(self) -> None:
        group_id = uuid4()
        membership = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
            invited_via_group_id=group_id,
        )
        assert membership.invited_via_group_id == group_id

    def test_timestamps_default_to_utc_now(self) -> None:
        membership = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
        )
        assert membership.invited_at.tzinfo is not None


class TestEventMembershipMutability:
    """Membership status and responded_at can be updated."""

    def test_status_can_be_updated(self) -> None:
        membership = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
        )
        membership.status = MembershipStatus.ACCEPTED
        assert membership.status == MembershipStatus.ACCEPTED

    def test_responded_at_can_be_set(self) -> None:
        membership = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
        )
        now = datetime.now(UTC)
        membership.responded_at = now
        assert membership.responded_at == now


class TestEventMembershipEquality:
    """Identity-based equality on UUID id."""

    def test_same_id_are_equal(self) -> None:
        uid = uuid4()
        eid, uid2 = uuid4(), uuid4()
        m1 = EventMembership(
            id=uid,
            event_id=eid,
            user_id=uid2,
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
        )
        m2 = EventMembership(
            id=uid,
            event_id=eid,
            user_id=uid2,
            role=EventRole.CO_ORGANISER,
            status=MembershipStatus.ACCEPTED,
            invited_by=uuid4(),
        )
        assert m1 == m2

    def test_hashable(self) -> None:
        m = EventMembership(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            role=EventRole.PARTICIPANT,
            status=MembershipStatus.INVITED,
            invited_by=uuid4(),
        )
        assert len({m, m}) == 1
