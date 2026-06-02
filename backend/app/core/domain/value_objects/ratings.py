"""Ratings value object."""

from dataclasses import dataclass, field

from app.core.domain.value_objects.certification import Certification


@dataclass(frozen=True)
class Ratings:
    """Community score and age certifications for a media item.

    All fields are optional to accommodate items that are newly added
    and do not yet have rating data from TMDB.

    Attributes:
        community_score: TMDB community vote average in the range
            ``[0.0, 10.0]``, or ``None`` if not yet rated.
        vote_count: Number of TMDB votes contributing to
            ``community_score``. Must be ``None`` when
            ``community_score`` is ``None``, and non-negative otherwise.
        certifications: Age/content certifications by country, as a
            tuple of :class:`~app.core.domain.value_objects.certification.Certification`
            instances. Defaults to an empty tuple.

    Raises:
        ValueError: If ``community_score`` is outside ``[0.0, 10.0]``.
        ValueError: If ``vote_count`` is negative.
        ValueError: If ``vote_count`` is provided without ``community_score``.

    Example:
        >>> from app.core.domain.value_objects.certification import Certification
        >>> cert = Certification(country="US", rating="PG-13")
        >>> ratings = Ratings(community_score=8.5, vote_count=15000, certifications=(cert,))
    """

    community_score: float | None = None
    vote_count: int | None = None
    certifications: tuple[Certification, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate all fields after initialisation."""
        if self.community_score is not None:
            if not (0.0 <= self.community_score <= 10.0):
                raise ValueError(f"community_score must be between 0.0 and 10.0, got: {self.community_score}")

        if self.vote_count is not None:
            if self.community_score is None:
                raise ValueError("vote_count cannot be set without community_score")
            if self.vote_count < 0:
                raise ValueError(f"vote_count must be non-negative, got: {self.vote_count}")
