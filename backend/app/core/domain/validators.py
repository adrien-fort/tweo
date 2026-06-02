"""Shared domain validation helpers.

Centralises format validation for standardised code fields so that
individual domain classes do not duplicate the logic.
"""


def validate_country_code(code: str, field_name: str = "country") -> str:
    """Validate and normalise an ISO 3166-1 alpha-2 country code.

    Strips surrounding whitespace and normalises to uppercase before
    validation. Use the ``field_name`` argument to produce meaningful
    error messages in the calling class.

    Args:
        code: The raw country code string to validate.
        field_name: Name of the field being validated, used in the
            error message (e.g. ``"nationalities"``, ``"country"``).

    Returns:
        The normalised, uppercase country code (e.g. ``"US"``).

    Raises:
        ValueError: If ``code`` is not exactly two alphabetic characters
            after stripping whitespace.

    Example:
        >>> validate_country_code("us")
        'US'
        >>> validate_country_code("USA")
        Traceback (most recent call last):
            ...
        ValueError: country must be a 2-letter ISO 3166-1 alpha-2 code, got: 'USA'
    """
    cleaned = code.strip().upper()
    if len(cleaned) != 2 or not cleaned.isalpha():
        raise ValueError(f"{field_name} must be a 2-letter ISO 3166-1 alpha-2 code, got: {code!r}")
    return cleaned


def validate_language_code(code: str, field_name: str = "language") -> str:
    """Validate and normalise an ISO 639-1 alpha-2 language code.

    Strips surrounding whitespace and normalises to lowercase before
    validation. Use the ``field_name`` argument to produce meaningful
    error messages in the calling class.

    Args:
        code: The raw language code string to validate.
        field_name: Name of the field being validated, used in the
            error message (e.g. ``"mother_tongue"``, ``"original_language"``).

    Returns:
        The normalised, lowercase language code (e.g. ``"en"``).

    Raises:
        ValueError: If ``code`` is not exactly two alphabetic characters
            after stripping whitespace.

    Example:
        >>> validate_language_code("EN")
        'en'
        >>> validate_language_code("eng")
        Traceback (most recent call last):
            ...
        ValueError: language must be a 2-letter ISO 639-1 alpha-2 code, got: 'eng'
    """
    cleaned = code.strip().lower()
    if len(cleaned) != 2 or not cleaned.isalpha():
        raise ValueError(f"{field_name} must be a 2-letter ISO 639-1 alpha-2 code, got: {code!r}")
    return cleaned
