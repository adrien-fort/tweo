"""SQLite/PostgreSQL implementations of event-related repositories."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.domain.entities.event import Event, EventMembership, EventSeries
from app.core.domain.enums import ActivityType, EventPrivacy, EventRole, EventStatus, MembershipStatus, RecurrenceType
from app.core.interfaces.repositories import EventMembershipRepository, EventRepository, EventSeriesRepository
from app.infrastructure.persistence.models.event_models import EventMembershipModel, EventModel, EventSeriesModel


def _series_to_domain(model: EventSeriesModel) -> EventSeries:
    return EventSeries(
        id=UUID(str(model.id)),
        title=model.title,
        organiser_id=UUID(str(model.organiser_id)),
        recurrence=RecurrenceType(model.recurrence),
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _event_to_domain(model: EventModel) -> Event:
    return Event(
        id=UUID(str(model.id)),
        title=model.title,
        activity_type=ActivityType(model.activity_type),
        organiser_id=UUID(str(model.organiser_id)),
        privacy=EventPrivacy(model.privacy),
        status=EventStatus(model.status),
        series_id=UUID(str(model.series_id)) if model.series_id else None,
        series_sequence=model.series_sequence,
        description=model.description,
        scheduled_at=model.scheduled_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _membership_to_domain(model: EventMembershipModel) -> EventMembership:
    return EventMembership(
        id=UUID(str(model.id)),
        event_id=UUID(str(model.event_id)),
        user_id=UUID(str(model.user_id)),
        role=EventRole(model.role),
        status=MembershipStatus(model.status),
        invited_by=UUID(str(model.invited_by)),
        invited_at=model.invited_at,
        invited_via_group_id=UUID(str(model.invited_via_group_id)) if model.invited_via_group_id else None,
        responded_at=model.responded_at,
    )


class SQLiteEventSeriesRepository(EventSeriesRepository):
    """EventSeries repository backed by SQLite (or PostgreSQL).

    Args:
        session: An active SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: UUID) -> EventSeries | None:
        model = self._session.get(EventSeriesModel, str(id))
        return _series_to_domain(model) if model else None

    def get_by_organiser(self, organiser_id: UUID) -> list[EventSeries]:
        models = self._session.query(EventSeriesModel).filter_by(organiser_id=str(organiser_id)).all()
        return [_series_to_domain(m) for m in models]

    def save(self, series: EventSeries) -> EventSeries:
        existing = self._session.get(EventSeriesModel, str(series.id))
        if existing:
            existing.title = series.title
            existing.description = series.description
            existing.recurrence = series.recurrence.value
            existing.updated_at = series.updated_at
        else:
            self._session.add(
                EventSeriesModel(
                    id=str(series.id),
                    title=series.title,
                    description=series.description,
                    organiser_id=str(series.organiser_id),
                    recurrence=series.recurrence.value,
                    created_at=series.created_at,
                    updated_at=series.updated_at,
                )
            )
        self._session.flush()
        return series


class SQLiteEventRepository(EventRepository):
    """Event repository backed by SQLite (or PostgreSQL).

    Args:
        session: An active SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: UUID) -> Event | None:
        model = self._session.get(EventModel, str(id))
        return _event_to_domain(model) if model else None

    def get_by_series(self, series_id: UUID) -> list[Event]:
        models = (
            self._session.query(EventModel)
            .filter_by(series_id=str(series_id))
            .order_by(EventModel.series_sequence)
            .all()
        )
        return [_event_to_domain(m) for m in models]

    def get_by_organiser(self, organiser_id: UUID) -> list[Event]:
        models = self._session.query(EventModel).filter_by(organiser_id=str(organiser_id)).all()
        return [_event_to_domain(m) for m in models]

    def get_by_status(self, status: EventStatus) -> list[Event]:
        models = self._session.query(EventModel).filter_by(status=status.value).all()
        return [_event_to_domain(m) for m in models]

    def save(self, event: Event) -> Event:
        existing = self._session.get(EventModel, str(event.id))
        if existing:
            existing.title = event.title
            existing.description = event.description
            existing.activity_type = event.activity_type.value
            existing.privacy = event.privacy.value
            existing.status = event.status.value
            existing.series_id = str(event.series_id) if event.series_id else None  # type: ignore[assignment]
            existing.series_sequence = event.series_sequence
            existing.scheduled_at = event.scheduled_at
            existing.updated_at = event.updated_at
        else:
            self._session.add(
                EventModel(
                    id=str(event.id),
                    series_id=str(event.series_id) if event.series_id else None,
                    series_sequence=event.series_sequence,
                    title=event.title,
                    description=event.description,
                    activity_type=event.activity_type.value,
                    organiser_id=str(event.organiser_id),
                    privacy=event.privacy.value,
                    status=event.status.value,
                    scheduled_at=event.scheduled_at,
                    created_at=event.created_at,
                    updated_at=event.updated_at,
                )
            )
        self._session.flush()
        return event


class SQLiteEventMembershipRepository(EventMembershipRepository):
    """EventMembership repository backed by SQLite (or PostgreSQL).

    Args:
        session: An active SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: UUID) -> EventMembership | None:
        model = self._session.get(EventMembershipModel, str(id))
        return _membership_to_domain(model) if model else None

    def get_by_event(self, event_id: UUID) -> list[EventMembership]:
        models = self._session.query(EventMembershipModel).filter_by(event_id=str(event_id)).all()
        return [_membership_to_domain(m) for m in models]

    def get_by_user(self, user_id: UUID) -> list[EventMembership]:
        models = self._session.query(EventMembershipModel).filter_by(user_id=str(user_id)).all()
        return [_membership_to_domain(m) for m in models]

    def get_by_event_and_user(self, event_id: UUID, user_id: UUID) -> EventMembership | None:
        model = (
            self._session.query(EventMembershipModel).filter_by(event_id=str(event_id), user_id=str(user_id)).first()
        )
        return _membership_to_domain(model) if model else None

    def save(self, membership: EventMembership) -> EventMembership:
        existing = self._session.get(EventMembershipModel, str(membership.id))
        if existing:
            existing.role = membership.role.value
            existing.status = membership.status.value
            existing.responded_at = membership.responded_at
        else:
            self._session.add(
                EventMembershipModel(
                    id=str(membership.id),
                    event_id=str(membership.event_id),
                    user_id=str(membership.user_id),
                    role=membership.role.value,
                    status=membership.status.value,
                    invited_by=str(membership.invited_by),
                    invited_via_group_id=(
                        str(membership.invited_via_group_id) if membership.invited_via_group_id else None
                    ),
                    invited_at=membership.invited_at,
                    responded_at=membership.responded_at,
                )
            )
        self._session.flush()
        return membership

    def get_by_status(self, event_id: UUID, status: MembershipStatus) -> list[EventMembership]:
        models = self._session.query(EventMembershipModel).filter_by(event_id=str(event_id), status=status.value).all()
        return [_membership_to_domain(m) for m in models]
