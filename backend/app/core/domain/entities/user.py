"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.domain.enums import SystemRole
from app.core.domain.validators import validate_email, validate_https_url


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(eq=False)
class User:
    """A registered user of the TWEO platform.

    Identity is determined solely by ``id``. The ``firebase_uid`` is
    the external identifier from Firebase Authentication and is
    immutable after creation.

    The ``email`` field stores the plaintext address in the domain.
    Encryption is the responsibility of the infrastructure layer
    (repository) before persisting to the database.

    Supports GDPR right to erasure via ``anonymized_at``: set this
    field and null out PII fields (email, nickname, avatar_url, etc.)
    to anonymise without deleting the row.

    Attributes:
        id: Internal UUID primary key.
        firebase_uid: Immutable external identifier from Firebase Auth.
        email: User's email address (plaintext in domain layer).
        nickname: Optional display name chosen by the user.
        avatar_url: Optional HTTPS URL to the user's avatar image.
        system_role: Platform-level privilege. Defaults to ``MEMBER``.
        gender: Optional self-reported gender (free text).
        pronouns: Optional self-reported pronouns (free text).
        bio: Optional short biography or description.
        preferences: Optional free-form media and activity preferences
            stored as a dict. Persisted as JSONB. May be normalised to
            a dedicated table in a future migration.
        created_at: Timestamp of account creation (UTC).
        updated_at: Timestamp of last profile update (UTC).
        anonymized_at: When set, indicates the account has been
            anonymised (GDPR erasure). ``None`` for active accounts.

    Raises:
        ValueError: If ``firebase_uid`` is empty or whitespace.
        ValueError: If ``email`` is not a valid ``local@domain`` address.
        ValueError: If ``avatar_url`` is provided but is not an HTTPS URL.

    Example:
        >>> from uuid import uuid4
        >>> user = User(id=uuid4(), firebase_uid="abc123", email="alice@example.com")
    """

    id: UUID
    firebase_uid: str
    email: str
    nickname: str | None = None
    avatar_url: str | None = None
    system_role: SystemRole = SystemRole.MEMBER
    gender: str | None = None
    pronouns: str | None = None
    bio: str | None = None
    preferences: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    anonymized_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate and normalise fields after initialisation."""
        if not self.firebase_uid or not self.firebase_uid.strip():
            raise ValueError("firebase_uid cannot be empty or whitespace")
        self.email = validate_email(self.email, "email")
        if self.avatar_url is not None:
            validate_https_url(self.avatar_url, "avatar_url")

    def __eq__(self, other: object) -> bool:
        """Compare by ``id`` only."""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash by ``id`` only."""
        return hash(self.id)
