"""Integration tests for SQLiteUserRepository."""

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.domain.entities.user import User
from app.core.domain.enums import SystemRole
from app.infrastructure.persistence.sqlite.user_repository import SQLiteUserRepository


@pytest.fixture
def repo(db_session: Session) -> SQLiteUserRepository:
    return SQLiteUserRepository(db_session)


@pytest.fixture
def sample_user() -> User:
    return User(id=uuid4(), firebase_uid="firebase-abc", email="alice@example.com")


class TestSQLiteUserRepositoryRoundTrip:
    """Verify save → retrieve round-trips preserve all fields."""

    def test_save_and_get_by_id(self, repo: SQLiteUserRepository, sample_user: User, db_session: Session) -> None:
        repo.save(sample_user)
        db_session.commit()
        result = repo.get_by_id(sample_user.id)
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == "alice@example.com"
        assert result.firebase_uid == "firebase-abc"

    def test_save_and_get_by_firebase_uid(
        self, repo: SQLiteUserRepository, sample_user: User, db_session: Session
    ) -> None:
        repo.save(sample_user)
        db_session.commit()
        result = repo.get_by_firebase_uid("firebase-abc")
        assert result is not None
        assert result.id == sample_user.id

    def test_save_and_get_by_email(self, repo: SQLiteUserRepository, sample_user: User, db_session: Session) -> None:
        repo.save(sample_user)
        db_session.commit()
        result = repo.get_by_email("alice@example.com")
        assert result is not None
        assert result.id == sample_user.id

    def test_email_lookup_is_case_insensitive(
        self, repo: SQLiteUserRepository, sample_user: User, db_session: Session
    ) -> None:
        repo.save(sample_user)
        db_session.commit()
        result = repo.get_by_email("ALICE@EXAMPLE.COM")
        assert result is not None

    def test_get_by_id_returns_none_for_unknown(self, repo: SQLiteUserRepository) -> None:
        assert repo.get_by_id(uuid4()) is None

    def test_update_existing_user(self, repo: SQLiteUserRepository, sample_user: User, db_session: Session) -> None:
        repo.save(sample_user)
        db_session.commit()
        sample_user.nickname = "Alice W"
        sample_user.system_role = SystemRole.ADMIN
        repo.save(sample_user)
        db_session.commit()
        result = repo.get_by_id(sample_user.id)
        assert result is not None
        assert result.nickname == "Alice W"
        assert result.system_role == SystemRole.ADMIN

    def test_anonymize_clears_pii(self, repo: SQLiteUserRepository, sample_user: User, db_session: Session) -> None:
        repo.save(sample_user)
        db_session.commit()
        repo.anonymize(sample_user.id)
        db_session.commit()
        result = repo.get_by_id(sample_user.id)
        assert result is not None
        assert result.nickname is None
        assert result.anonymized_at is not None

    def test_email_is_encrypted_at_rest(
        self, repo: SQLiteUserRepository, sample_user: User, db_session: Session
    ) -> None:
        """Raw bytes stored in the DB must not be the plaintext email."""
        from app.infrastructure.persistence.models.user_models import UserModel

        repo.save(sample_user)
        db_session.commit()
        row = db_session.query(UserModel).filter_by(firebase_uid="firebase-abc").first()
        assert row is not None
        assert b"alice@example.com" not in row.email_encrypted
