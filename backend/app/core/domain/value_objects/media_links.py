"""External media resource links value object."""

from dataclasses import dataclass

from app.core.domain.validators import validate_https_url


@dataclass(frozen=True)
class MediaLinks:
    """External media resource links for a media item.

    All URLs must use HTTPS. Fields are optional; pass ``None`` (or omit
    them) when a resource is not yet available.

    Attributes:
        poster_url: HTTPS URL to the poster image, or ``None``.
        trailer_url: HTTPS URL to the trailer video, or ``None``.

    Raises:
        ValueError: If a provided URL is empty, whitespace, or does not
            start with ``"https://"``.

    Example:
        >>> links = MediaLinks(
        ...     poster_url="https://image.tmdb.org/poster.jpg",
        ...     trailer_url="https://youtube.com/watch?v=abc",
        ... )
    """

    poster_url: str | None = None
    trailer_url: str | None = None

    def __post_init__(self) -> None:
        """Validate all URL fields after initialisation."""
        for field_name in ("poster_url", "trailer_url"):
            value: str | None = getattr(self, field_name)
            if value is not None:
                validate_https_url(value, field_name)
