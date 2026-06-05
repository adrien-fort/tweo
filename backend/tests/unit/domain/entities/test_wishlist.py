"""Tests for WishlistEntry and EventCandidate entities."""

from uuid import UUID, uuid4

import pytest

from app.core.domain.entities.wishlist import EventCandidate, WishlistEntry
from app.core.domain.enums import ActivityType, WishlistEntryStatus


@pytest.fixture
def series_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_entry(series_id: UUID) -> WishlistEntry:
    return WishlistEntry(
        id=uuid4(),
        series_id=series_id,
        activity_type=ActivityType.MOVIE,
        tmdb_id=550,
        added_by=uuid4(),
    )


@pytest.fixture
def valid_candidate() -> EventCandidate:
    return EventCandidate(
        id=uuid4(),
        event_id=uuid4(),
        wishlist_entry_id=uuid4(),
    )


# ── WishlistEntry ─────────────────────────────────────────────────────────────


class TestWishlistEntryCreation:
    """Valid WishlistEntry construction scenarios."""

    def test_creates_with_required_fields(self, valid_entry: WishlistEntry, series_id: UUID) -> None:
        assert isinstance(valid_entry.id, UUID)
        assert valid_entry.series_id == series_id
        assert valid_entry.activity_type == ActivityType.MOVIE
        assert valid_entry.tmdb_id == 550

    def test_status_defaults_to_pending(self, valid_entry: WishlistEntry) -> None:
        assert valid_entry.status == WishlistEntryStatus.PENDING

    def test_completed_event_id_defaults_to_none(self, valid_entry: WishlistEntry) -> None:
        assert valid_entry.completed_event_id is None

    def test_added_at_defaults_to_utc_now(self, valid_entry: WishlistEntry) -> None:
        assert valid_entry.added_at.tzinfo is not None

    def test_creates_with_explicit_status(self, series_id: UUID) -> None:
        entry = WishlistEntry(
            id=uuid4(),
            series_id=series_id,
            activity_type=ActivityType.TV_SERIES,
            tmdb_id=1396,
            added_by=uuid4(),
            status=WishlistEntryStatus.REMOVED,
        )
        assert entry.status == WishlistEntryStatus.REMOVED

    def test_creates_with_completed_event_id(self, series_id: UUID) -> None:
        event_id = uuid4()
        entry = WishlistEntry(
            id=uuid4(),
            series_id=series_id,
            activity_type=ActivityType.MOVIE,
            tmdb_id=550,
            added_by=uuid4(),
            status=WishlistEntryStatus.COMPLETED,
            completed_event_id=event_id,
        )
        assert entry.completed_event_id == event_id


class TestWishlistEntryValidation:
    """WishlistEntry field validation."""

    def test_zero_tmdb_id_raises(self, series_id: UUID) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            WishlistEntry(
                id=uuid4(),
                series_id=series_id,
                activity_type=ActivityType.MOVIE,
                tmdb_id=0,
                added_by=uuid4(),
            )

    def test_negative_tmdb_id_raises(self, series_id: UUID) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            WishlistEntry(
                id=uuid4(),
                series_id=series_id,
                activity_type=ActivityType.MOVIE,
                tmdb_id=-1,
                added_by=uuid4(),
            )

    def test_bool_tmdb_id_raises(self, series_id: UUID) -> None:
        with pytest.raises(ValueError, match="tmdb_id"):
            WishlistEntry(
                id=uuid4(),
                series_id=series_id,
                activity_type=ActivityType.MOVIE,
                tmdb_id=True,
                added_by=uuid4(),  # type: ignore[arg-type]
            )

    def test_completed_event_id_requires_completed_status(self, series_id: UUID) -> None:
        with pytest.raises(ValueError, match="completed_event_id"):
            WishlistEntry(
                id=uuid4(),
                series_id=series_id,
                activity_type=ActivityType.MOVIE,
                tmdb_id=550,
                added_by=uuid4(),
                status=WishlistEntryStatus.PENDING,
                completed_event_id=uuid4(),
            )

    def test_completed_event_id_with_scheduled_status_raises(self, series_id: UUID) -> None:
        with pytest.raises(ValueError, match="completed_event_id"):
            WishlistEntry(
                id=uuid4(),
                series_id=series_id,
                activity_type=ActivityType.MOVIE,
                tmdb_id=550,
                added_by=uuid4(),
                status=WishlistEntryStatus.SCHEDULED,
                completed_event_id=uuid4(),
            )


class TestWishlistEntryImmutability:
    """WishlistEntry is a mutable dataclass — fields can be reassigned."""

    def test_status_can_be_updated(self, valid_entry: WishlistEntry) -> None:
        valid_entry.status = WishlistEntryStatus.SCHEDULED
        assert valid_entry.status == WishlistEntryStatus.SCHEDULED


class TestWishlistEntryEquality:
    """WishlistEntry identity is determined by id only."""

    def test_same_id_are_equal(self, series_id: UUID) -> None:
        shared_id = uuid4()
        a = WishlistEntry(
            id=shared_id,
            series_id=series_id,
            activity_type=ActivityType.MOVIE,
            tmdb_id=550,
            added_by=uuid4(),
        )
        b = WishlistEntry(
            id=shared_id,
            series_id=series_id,
            activity_type=ActivityType.TV_SERIES,
            tmdb_id=999,
            added_by=uuid4(),
        )
        assert a == b

    def test_different_id_not_equal(self, series_id: UUID) -> None:
        a = WishlistEntry(
            id=uuid4(),
            series_id=series_id,
            activity_type=ActivityType.MOVIE,
            tmdb_id=550,
            added_by=uuid4(),
        )
        b = WishlistEntry(
            id=uuid4(),
            series_id=series_id,
            activity_type=ActivityType.MOVIE,
            tmdb_id=550,
            added_by=uuid4(),
        )
        assert a != b

    def test_not_equal_to_other_types(self, valid_entry: WishlistEntry) -> None:
        assert valid_entry != "not an entry"

    def test_hashable_and_usable_in_set(self, valid_entry: WishlistEntry) -> None:
        assert len({valid_entry, valid_entry}) == 1


# ── EventCandidate ────────────────────────────────────────────────────────────


class TestEventCandidateCreation:
    """Valid EventCandidate construction scenarios."""

    def test_creates_with_required_fields(self, valid_candidate: EventCandidate) -> None:
        assert isinstance(valid_candidate.id, UUID)
        assert isinstance(valid_candidate.event_id, UUID)
        assert isinstance(valid_candidate.wishlist_entry_id, UUID)

    def test_added_by_defaults_to_none(self, valid_candidate: EventCandidate) -> None:
        assert valid_candidate.added_by is None

    def test_added_at_defaults_to_utc_now(self, valid_candidate: EventCandidate) -> None:
        assert valid_candidate.added_at.tzinfo is not None

    def test_creates_with_explicit_added_by(self) -> None:
        user_id = uuid4()
        candidate = EventCandidate(
            id=uuid4(),
            event_id=uuid4(),
            wishlist_entry_id=uuid4(),
            added_by=user_id,
        )
        assert candidate.added_by == user_id

    def test_added_by_none_represents_system_selection(self) -> None:
        """None added_by indicates the system auto-selected the candidate."""
        candidate = EventCandidate(
            id=uuid4(),
            event_id=uuid4(),
            wishlist_entry_id=uuid4(),
            added_by=None,
        )
        assert candidate.added_by is None


class TestEventCandidateEquality:
    """EventCandidate identity is determined by id only."""

    def test_same_id_are_equal(self) -> None:
        shared_id = uuid4()
        a = EventCandidate(id=shared_id, event_id=uuid4(), wishlist_entry_id=uuid4())
        b = EventCandidate(id=shared_id, event_id=uuid4(), wishlist_entry_id=uuid4())
        assert a == b

    def test_different_id_not_equal(self) -> None:
        event_id = uuid4()
        entry_id = uuid4()
        a = EventCandidate(id=uuid4(), event_id=event_id, wishlist_entry_id=entry_id)
        b = EventCandidate(id=uuid4(), event_id=event_id, wishlist_entry_id=entry_id)
        assert a != b

    def test_not_equal_to_other_types(self, valid_candidate: EventCandidate) -> None:
        assert valid_candidate != "not a candidate"

    def test_hashable_and_usable_in_set(self, valid_candidate: EventCandidate) -> None:
        assert len({valid_candidate, valid_candidate}) == 1
