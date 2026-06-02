"""SQLite/PostgreSQL implementation of UserGroupRepository."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.domain.entities.user_group import UserGroup, UserGroupMembership
from app.core.interfaces.repositories import UserGroupRepository
from app.infrastructure.persistence.models.user_models import UserGroupMembershipModel, UserGroupModel


def _group_to_domain(model: UserGroupModel) -> UserGroup:
    return UserGroup(
        id=UUID(str(model.id)),
        name=model.name,
        owner_id=UUID(str(model.owner_id)),
        description=model.description,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _membership_to_domain(model: UserGroupMembershipModel) -> UserGroupMembership:
    return UserGroupMembership(
        id=UUID(str(model.id)),
        group_id=UUID(str(model.group_id)),
        user_id=UUID(str(model.user_id)),
        added_by=UUID(str(model.added_by)),
        added_at=model.added_at,
    )


class SQLiteUserGroupRepository(UserGroupRepository):
    """UserGroup repository backed by SQLite (or PostgreSQL).

    Args:
        session: An active SQLAlchemy session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: UUID) -> UserGroup | None:
        model = self._session.get(UserGroupModel, str(id))
        return _group_to_domain(model) if model else None

    def get_by_owner(self, owner_id: UUID) -> list[UserGroup]:
        models = self._session.query(UserGroupModel).filter_by(owner_id=str(owner_id)).all()
        return [_group_to_domain(m) for m in models]

    def save(self, group: UserGroup) -> UserGroup:
        existing = self._session.get(UserGroupModel, str(group.id))
        if existing:
            existing.name = group.name
            existing.description = group.description
            existing.updated_at = group.updated_at
        else:
            self._session.add(
                UserGroupModel(
                    id=str(group.id),
                    name=group.name,
                    description=group.description,
                    owner_id=str(group.owner_id),
                    created_at=group.created_at,
                    updated_at=group.updated_at,
                )
            )
        self._session.flush()
        return group

    def delete(self, id: UUID) -> None:
        model = self._session.get(UserGroupModel, str(id))
        if model:
            self._session.delete(model)
            self._session.flush()

    def add_member(self, membership: UserGroupMembership) -> UserGroupMembership:
        self._session.add(
            UserGroupMembershipModel(
                id=str(membership.id),
                group_id=str(membership.group_id),
                user_id=str(membership.user_id),
                added_by=str(membership.added_by),
                added_at=membership.added_at,
            )
        )
        self._session.flush()
        return membership

    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        model = (
            self._session.query(UserGroupMembershipModel)
            .filter_by(group_id=str(group_id), user_id=str(user_id))
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()

    def get_members(self, group_id: UUID) -> list[UserGroupMembership]:
        models = self._session.query(UserGroupMembershipModel).filter_by(group_id=str(group_id)).all()
        return [_membership_to_domain(m) for m in models]
