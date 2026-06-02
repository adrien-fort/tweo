"""Application-level encryption helpers for PII fields.

Uses Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256) from the
``cryptography`` library. The encryption key is read from the
``DATABASE_ENCRYPTION_KEY`` environment variable.

In development, generate a key with::

    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

In production (AKS), the key is retrieved from Azure Key Vault by Ansible
and injected as an environment variable at pod startup — never stored in
code or committed to the repository.

The email HMAC is stored alongside the encrypted value to enable indexed
lookups without decrypting every row.
"""

import hashlib
import hmac
import os

from cryptography.fernet import Fernet

_RAW_KEY = os.environ.get("DATABASE_ENCRYPTION_KEY", "")


def _get_fernet() -> Fernet:
    if not _RAW_KEY:
        raise RuntimeError(
            "DATABASE_ENCRYPTION_KEY environment variable is not set. "
            "Generate one with: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )
    return Fernet(_RAW_KEY.encode())


def encrypt(plaintext: str) -> bytes:
    """Encrypt a plaintext string and return the ciphertext bytes.

    Args:
        plaintext: The string to encrypt (e.g. an email address).

    Returns:
        Fernet-encrypted bytes, safe to store in the database.

    Raises:
        RuntimeError: If ``DATABASE_ENCRYPTION_KEY`` is not set.
    """
    return _get_fernet().encrypt(plaintext.encode())


def decrypt(ciphertext: bytes) -> str:
    """Decrypt Fernet ciphertext and return the original plaintext string.

    Args:
        ciphertext: Bytes previously produced by :func:`encrypt`.

    Returns:
        The original plaintext string.

    Raises:
        RuntimeError: If ``DATABASE_ENCRYPTION_KEY`` is not set.
        cryptography.fernet.InvalidToken: If decryption fails (wrong key
            or tampered data).
    """
    return _get_fernet().decrypt(ciphertext).decode()


def email_hmac(email: str) -> bytes:
    """Produce a stable HMAC of an email address for indexed lookups.

    Stores an HMAC rather than the plaintext so that the database index
    can answer ``WHERE email_hash = ?`` without decrypting every row.

    Args:
        email: Plaintext email address (already validated and lowercased).

    Returns:
        32-byte HMAC-SHA256 digest.

    Raises:
        RuntimeError: If ``DATABASE_ENCRYPTION_KEY`` is not set.
    """
    if not _RAW_KEY:
        raise RuntimeError("DATABASE_ENCRYPTION_KEY environment variable is not set.")
    return hmac.new(_RAW_KEY.encode(), email.lower().encode(), hashlib.sha256).digest()
