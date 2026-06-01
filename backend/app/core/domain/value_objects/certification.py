"""Age/content certification value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Certification:
    """Age or content certification for a media item in a specific country.

    Attributes:
        country: ISO 3166-1 alpha-2 country code (e.g. ``"US"``, ``"GB"``).
            Automatically normalised to uppercase.
        rating: Content rating string as defined by the country's board
            (e.g. ``"PG-13"``, ``"12A"``, ``"R"``). Leading/trailing
            whitespace is stripped.

    Raises:
        ValueError: If ``country`` is not exactly two alphabetic characters.
        ValueError: If ``rating`` is empty or whitespace only.

    Example:
        >>> cert = Certification(country="us", rating="PG-13")
        >>> cert.country
        'US'
    """

    country: str
    rating: str

    def __post_init__(self) -> None:
        """Validate and normalise fields after initialisation."""
        cleaned_country = self.country.strip().upper()
        if len(cleaned_country) != 2 or not cleaned_country.isalpha():
            raise ValueError(
                f"country must be a 2-letter ISO 3166-1 alpha-2 code, got: {self.country!r}"
            )
        object.__setattr__(self, "country", cleaned_country)

        cleaned_rating = self.rating.strip()
        if not cleaned_rating:
            raise ValueError("rating cannot be empty or whitespace")
        object.__setattr__(self, "rating", cleaned_rating)
