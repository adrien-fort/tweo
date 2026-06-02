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


def validate_https_url(url: str, field_name: str = "url") -> str:
    """Validate that a URL is non-empty and uses HTTPS.

    Args:
        url: The URL string to validate.
        field_name: Name of the field being validated, used in the
            error message (e.g. ``"avatar_url"``).

    Returns:
        The original URL string unchanged.

    Raises:
        ValueError: If ``url`` is empty or whitespace only.
        ValueError: If ``url`` does not start with ``"https://"``.

    Example:
        >>> validate_https_url("https://example.com/img.jpg", "avatar_url")
        'https://example.com/img.jpg'
    """
    if not url.strip():
        raise ValueError(f"{field_name} must be a non-empty string or None")
    if not url.startswith("https://"):
        raise ValueError(f"{field_name} must start with 'https://', got: {url!r}")
    return url


def validate_email(email: str, field_name: str = "email") -> str:
    """Validate that a string is a plausible email address.

    Performs lightweight structural validation only: non-empty, contains
    exactly one ``@``, with non-empty local and domain parts. Full RFC
    5321 validation is the responsibility of the API boundary layer.

    Args:
        email: The email string to validate.
        field_name: Name of the field being validated, used in the
            error message.

    Returns:
        The email string stripped of surrounding whitespace.

    Raises:
        ValueError: If ``email`` is empty, whitespace only, or does not
            contain a valid ``local@domain`` structure.

    Example:
        >>> validate_email("user@example.com")
        'user@example.com'
    """
    cleaned = email.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty or whitespace")
    parts = cleaned.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"{field_name} must be a valid email address, got: {email!r}")
    return cleaned
