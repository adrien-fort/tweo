"""SQLite/PostgreSQL implementation of UserRepository."""

import json
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.domain.entities.user import User
from app.core.domain.enums import SystemRole
from app.core.interfaces.repositories import UserRepository
from app.infrastructure.persistence.encryption import decrypt, email_hmac, encrypt
from app.infrastructure.persistence.models.user_models import UserModel


def _to_domain(model: UserModel) -> User:
    """Map a UserModel row to a User domain entity."""
    return User(
        id=UUID(str(model.id)),
        firebase_uid=model.firebase_uid,
        email=decrypt(model.email_encrypted),
        nickname=model.nickname,
        avatar_url=model.avatar_url,
        system_role=SystemRole(model.system_role),
        gender=model.gender,
        pronouns=model.pronouns,
        bio=model.bio,
        preferences=json.loads(model.preferences) if model.preferences else None,
        created_at=model.created_at,
        updated_at=model.updated_at,
        anonymized_at=model.anonymized_at,
    )


def _to_model(user: User) -> UserModel:
    """Map a User domain entity to a UserModel row."""
    return UserModel(
        id=str(user.id),
        firebase_uid=user.firebase_uid,
        email_encrypted=encrypt(user.email),
        email_hash=email_hmac(user.email),
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        system_role=user.system_role.value,
        gender=user.gender,
        pronouns=user.pronouns,
        bio=user.bio,
        preferences=json.dumps(user.preferences) if user.preferences is not None else None,
        created_at=user.created_at,
        updated_at=user.updated_at,
        anonymized_at=user.anonymized_at,
    )


class SQLiteUserRepository(UserRepository):
    """User repository backed by SQLite (or PostgreSQL — engine-agnostic).

    Args:
        session: An active SQLAlchemy session. The caller manages the
            session lifecycle and commits.

    Example:
        >>> with get_session() as session:
        ...     repo = SQLiteUserRepository(session)
        ...     user = repo.get_by_firebase_uid("abc123")
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: UUID) -> User | None:
        """Return the user with the given UUID, or ``None``."""
        model = self._session.get(UserModel, str(id))
        return _to_domain(model) if model else None

    def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """Return the user with the given Firebase UID, or ``None``."""
        model = self._session.query(UserModel).filter_by(firebase_uid=firebase_uid).first()
        return _to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or ``None``.

        Uses the stored HMAC hash for the lookup — never decrypts all rows.
        """
        hashed = email_hmac(email.lower().strip())
        model = self._session.query(UserModel).filter_by(email_hash=hashed).first()
        return _to_domain(model) if model else None

    def save(self, user: User) -> User:
        """Persist a new or updated user and return the saved instance."""
        existing = self._session.get(UserModel, str(user.id))
        if existing:
            existing.firebase_uid = user.firebase_uid
            existing.email_encrypted = encrypt(user.email)
            existing.email_hash = email_hmac(user.email)
            existing.nickname = user.nickname
            existing.avatar_url = user.avatar_url
            existing.system_role = user.system_role.value
            existing.gender = user.gender
            existing.pronouns = user.pronouns
            existing.bio = user.bio
            existing.preferences = json.dumps(user.preferences) if user.preferences is not None else None
            existing.updated_at = datetime.now(UTC)
            existing.anonymized_at = user.anonymized_at
        else:
            self._session.add(_to_model(user))
        self._session.flush()
        return user

    def anonymize(self, id: UUID) -> None:
        """Anonymise a user's PII in place (GDPR right to erasure)."""
        model = self._session.get(UserModel, str(id))
        if not model:
            return
        placeholder = f"deleted+{id}@anonymized.invalid"
        model.email_encrypted = encrypt(placeholder)
        model.email_hash = email_hmac(placeholder)
        model.nickname = None
        model.avatar_url = None
        model.gender = None
        model.pronouns = None
        model.bio = None
        model.preferences = None
        model.anonymized_at = datetime.now(UTC)
        model.updated_at = datetime.now(UTC)
        self._session.flush()
