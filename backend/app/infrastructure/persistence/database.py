"""SQLAlchemy engine and session factory.

The database URL is read from the ``DATABASE_URL`` environment variable.
Defaults to a local SQLite file for development.

In production (AKS), ``DATABASE_URL`` is a PostgreSQL connection string
supplied by Ansible from Azure Key Vault.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./tweo.db")

# connect_args is only required for SQLite to enable multi-thread access
_connect_args = {"check_same_thread": False} if _DATABASE_URL.startswith("sqlite") else {}

_engine = create_engine(_DATABASE_URL, connect_args=_connect_args)

SessionFactory: sessionmaker[Session] = sessionmaker(bind=_engine, expire_on_commit=False)


def get_engine():  # type: ignore[no-untyped-def]
    """Return the configured SQLAlchemy engine.

    Returns:
        The application-level SQLAlchemy engine instance.
    """
    return _engine


def get_session() -> Session:
    """Return a new SQLAlchemy session from the factory.

    Callers are responsible for closing or using the session as a
    context manager::

        with get_session() as session:
            repo = SQLiteUserRepository(session)
            user = repo.get_by_id(some_id)

    Returns:
        A new :class:`sqlalchemy.orm.Session` instance.
    """
    return SessionFactory()
