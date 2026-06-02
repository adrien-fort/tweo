"""SQLAlchemy ORM models for User and UserGroup."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.models.base import Base


class UserModel(Base):
    """ORM model for the ``users`` table.

    PII fields:
    - ``email_encrypted``: Fernet-encrypted email bytes.
    - ``email_hash``: HMAC-SHA256 of the lowercase email, used for
      indexed lookups without decryption.

    Neither the plaintext email nor the encryption key is stored here.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email_hash: Mapped[bytes] = mapped_column(LargeBinary(32), unique=True, nullable=False, index=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    system_role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")
    gender: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pronouns: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string (SQLite); JSONB in Postgres
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    anonymized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    group_memberships: Mapped[list["UserGroupMembershipModel"]] = relationship(
        "UserGroupMembershipModel",
        foreign_keys="[UserGroupMembershipModel.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserGroupModel(Base):
    """ORM model for the ``user_groups`` table."""

    __tablename__ = "user_groups"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    memberships: Mapped[list["UserGroupMembershipModel"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class UserGroupMembershipModel(Base):
    """ORM model for the ``user_group_memberships`` table."""

    __tablename__ = "user_group_memberships"

    id: Mapped[UUID] = mapped_column(String(36), primary_key=True)
    group_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("user_groups.id"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    added_by: Mapped[UUID] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    group: Mapped[UserGroupModel] = relationship(back_populates="memberships")
    user: Mapped[UserModel] = relationship(foreign_keys=[user_id], back_populates="group_memberships")
