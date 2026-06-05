"""Tests for EventBallot entity."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.domain.entities.ballot import EventBallot


@pytest.fixture
def approval_payload() -> dict[str, list[str]]:
    return {"approved": [str(uuid4()), str(uuid4())]}


@pytest.fixture
def valid_ballot(approval_payload: dict[str, list[str]]) -> EventBallot:
    return EventBallot(
        id=uuid4(),
        event_id=uuid4(),
        user_id=uuid4(),
        payload=approval_payload,
    )


# ── EventBallot ───────────────────────────────────────────────────────────────


class TestEventBallotCreation:
    """Valid EventBallot construction scenarios."""

    def test_creates_with_required_fields(self, valid_ballot: EventBallot) -> None:
        assert isinstance(valid_ballot.id, UUID)
        assert isinstance(valid_ballot.event_id, UUID)
        assert isinstance(valid_ballot.user_id, UUID)
        assert isinstance(valid_ballot.payload, dict)

    def test_round_defaults_to_one(self, valid_ballot: EventBallot) -> None:
        assert valid_ballot.round == 1

    def test_superseded_at_defaults_to_none(self, valid_ballot: EventBallot) -> None:
        assert valid_ballot.superseded_at is None

    def test_cast_at_defaults_to_utc_now(self, valid_ballot: EventBallot) -> None:
        assert valid_ballot.cast_at.tzinfo is not None

    def test_creates_with_explicit_round(self, approval_payload: dict[str, list[str]]) -> None:
        ballot = EventBallot(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            payload=approval_payload,
            round=2,
        )
        assert ballot.round == 2

    def test_creates_ranked_choice_payload(self) -> None:
        c1, c2, c3 = str(uuid4()), str(uuid4()), str(uuid4())
        ballot = EventBallot(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            payload={"rankings": [c1, c2, c3]},
        )
        assert ballot.payload["rankings"] == [c1, c2, c3]

    def test_creates_with_empty_payload(self) -> None:
        """Empty dict is valid — represents a ballot not yet filled in."""
        ballot = EventBallot(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            payload={},
        )
        assert ballot.payload == {}

    def test_superseded_at_can_be_set(self, approval_payload: dict[str, list[str]]) -> None:
        ts = datetime.now(UTC)
        ballot = EventBallot(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            payload=approval_payload,
            superseded_at=ts,
        )
        assert ballot.superseded_at == ts

    def test_is_current_when_superseded_at_is_none(self, valid_ballot: EventBallot) -> None:
        assert valid_ballot.is_current is True

    def test_is_not_current_when_superseded(self, approval_payload: dict[str, list[str]]) -> None:
        ballot = EventBallot(
            id=uuid4(),
            event_id=uuid4(),
            user_id=uuid4(),
            payload=approval_payload,
            superseded_at=datetime.now(UTC),
        )
        assert ballot.is_current is False


class TestEventBallotValidation:
    """EventBallot field validation."""

    def test_round_zero_raises(self, approval_payload: dict[str, list[str]]) -> None:
        with pytest.raises(ValueError, match="round"):
            EventBallot(
                id=uuid4(),
                event_id=uuid4(),
                user_id=uuid4(),
                payload=approval_payload,
                round=0,
            )

    def test_negative_round_raises(self, approval_payload: dict[str, list[str]]) -> None:
        with pytest.raises(ValueError, match="round"):
            EventBallot(
                id=uuid4(),
                event_id=uuid4(),
                user_id=uuid4(),
                payload=approval_payload,
                round=-1,
            )

    def test_bool_round_raises(self, approval_payload: dict[str, list[str]]) -> None:
        with pytest.raises(ValueError, match="round"):
            EventBallot(
                id=uuid4(),
                event_id=uuid4(),
                user_id=uuid4(),
                payload=approval_payload,
                round=True,  # type: ignore[arg-type]
            )

    def test_non_dict_payload_raises(self) -> None:
        with pytest.raises(ValueError, match="payload"):
            EventBallot(
                id=uuid4(),
                event_id=uuid4(),
                user_id=uuid4(),
                payload=["not", "a", "dict"],  # type: ignore[arg-type]
            )


class TestEventBallotEquality:
    """EventBallot identity is determined by id only."""

    def test_same_id_are_equal(self, approval_payload: dict[str, list[str]]) -> None:
        shared_id = uuid4()
        a = EventBallot(id=shared_id, event_id=uuid4(), user_id=uuid4(), payload=approval_payload)
        b = EventBallot(id=shared_id, event_id=uuid4(), user_id=uuid4(), payload={})
        assert a == b

    def test_different_id_not_equal(self, approval_payload: dict[str, list[str]]) -> None:
        event_id = uuid4()
        user_id = uuid4()
        a = EventBallot(id=uuid4(), event_id=event_id, user_id=user_id, payload=approval_payload)
        b = EventBallot(id=uuid4(), event_id=event_id, user_id=user_id, payload=approval_payload)
        assert a != b

    def test_not_equal_to_other_types(self, valid_ballot: EventBallot) -> None:
        assert valid_ballot != "not a ballot"

    def test_hashable_and_usable_in_set(self, valid_ballot: EventBallot) -> None:
        assert len({valid_ballot, valid_ballot}) == 1
