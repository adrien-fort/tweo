"""FastAPI dependency providers for API v1.

Inject these via ``Depends()`` in endpoint function signatures::

    @router.get("/me")
    async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
        ...

All database access goes through a session provided by
:func:`get_db_session` — callers do not manage session lifecycle.
"""

from collections.abc import Generator

import structlog
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.domain.entities.user import User
from app.infrastructure.persistence.database import SessionFactory

log = structlog.get_logger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for the duration of a single request.

    Commits on clean exit; rolls back and re-raises on any exception.
    The session is always closed after the request completes.

    Yields:
        An active :class:`sqlalchemy.orm.Session`.
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_current_user(
    session: Session = Depends(get_db_session),  # noqa: B008
) -> User:
    """Resolve the authenticated user from the Firebase JWT in the request.

    This is a placeholder. Full implementation will:

    1. Extract the ``Authorization: Bearer <token>`` header.
    2. Verify the Firebase JWT using the Firebase Admin SDK.
    3. Look up or create the ``User`` record by ``firebase_uid``.

    Args:
        session: Database session provided by :func:`get_db_session`.

    Returns:
        The authenticated :class:`~app.core.domain.entities.user.User`.

    Raises:
        HTTPException: 401 if the token is missing or invalid.
        HTTPException: 403 if the account has been anonymised (GDPR).
    """
    # TODO: replace with real Firebase JWT verification
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented.",
    )


async def get_current_admin(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> User:
    """Require the authenticated user to have ADMIN system role.

    Args:
        current_user: The user resolved by :func:`get_current_user`.

    Returns:
        The same user, confirmed to hold the ADMIN role.

    Raises:
        HTTPException: 403 if the user is not an admin.
    """
    from app.core.domain.enums import SystemRole

    if current_user.system_role != SystemRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user
