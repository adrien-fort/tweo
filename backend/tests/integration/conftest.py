"""Shared fixtures for integration tests.

Provides an in-memory SQLite session that is fully rebuilt for each
test function. No files are written; the database lives only in memory
for the duration of the test.

The encryption key is set to a fixed test value so repository tests
can exercise encrypt/decrypt without an environment dependency.
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Fixed test key — never use in production
os.environ.setdefault("DATABASE_ENCRYPTION_KEY", "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleXRlc3Q=")

import app.infrastructure.persistence.models  # noqa: F401 — registers all ORM models
from app.infrastructure.persistence.models.base import Base


@pytest.fixture
def db_session() -> Session:
    """Yield a fresh in-memory SQLite session, rolled back after each test.

    Yields:
        A :class:`sqlalchemy.orm.Session` connected to an in-memory
        SQLite database with the full schema applied.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
