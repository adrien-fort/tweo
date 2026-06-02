"""SQLAlchemy ORM models for EventSeries, Event, and EventMembership."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base


class EventSeriesModel(Base):
    """ORM model for the ``event_series`` table.

    A scheduling/grouping container — deliberately has no activity_type.
    Each Event instance carries its own type independently.
    """

    __tablename__ = "event_series"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organiser_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    recurrence: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    events: Mapped[list["EventModel"]] = relationship(back_populates="series")


class EventModel(Base):
    """ORM model for the ``events`` table."""

    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    series_id: Mapped[UUID | None] = mapped_column(String(36), ForeignKey("event_series.id"), nullable=True, index=True)
    series_sequence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    activity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    organiser_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    privacy: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    series: Mapped[EventSeriesModel | None] = relationship(back_populates="events")
    memberships: Mapped[list["EventMembershipModel"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EventMembershipModel(Base):
    """ORM model for the ``event_memberships`` table."""

    __tablename__ = "event_memberships"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("events.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    invited_by: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    invited_via_group_id: Mapped[UUID | None] = mapped_column(String(36), ForeignKey("user_groups.id"), nullable=True)
    invited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    event: Mapped[EventModel] = relationship(
        "EventModel",
        foreign_keys="[EventMembershipModel.event_id]",
        back_populates="memberships",
    )
