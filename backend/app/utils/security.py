"""Security utilities for password hashing and JWT access tokens."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from app.config import settings

PBKDF2_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    """Hash a password with a per-password random salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${derived}"


def verify_password(password: str, stored_hash: Optional[str]) -> bool:
    """Verify a plaintext password against a stored PBKDF2 hash."""
    if not stored_hash:
        return False
    parts = stored_hash.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False
    _, iter_str, salt, expected_hex = parts
    try:
        iterations = int(iter_str)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()
    return hmac.compare_digest(derived, expected_hex)


def create_access_token(
    subject: str,
    email: str,
    expires_minutes: Optional[int] = None,
) -> str:
    """Generate a signed JWT access token."""
    expire_delta = timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
    }
    return jwt.encode(
        payload,
        settings.effective_secret_key,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    return jwt.decode(
        token,
        settings.effective_secret_key,
        algorithms=[settings.JWT_ALGORITHM],
    )
