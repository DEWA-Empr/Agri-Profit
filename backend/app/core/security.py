"""Password hashing and JWT issue/verify — the cryptographic primitives behind
authentication (see api/deps.py for how the token becomes a current user).

Passwords are hashed with bcrypt; tokens are signed with python-jose using the
app secret. We call the `bcrypt` library directly rather than through passlib:
passlib 1.7.4 (its last release) cannot read the version of the installed
bcrypt 5.x and raises spurious errors, so the thin, stable bcrypt API is the
more durable choice for the same algorithm.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from .config import settings

# bcrypt hashes at most the first 72 bytes of a password; longer inputs must be
# truncated or bcrypt 5.x raises. Encode once and cap so hashing and verifying
# agree on exactly the same bytes.
_BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_encode(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_encode(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed/blank stored hash — treat as a failed verification, not a 500.
        return False


def create_access_token(subject: str) -> str:
    """Issue a signed JWT whose `sub` claim is the user id (as a string)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> str | None:
    """Return the `sub` (user id) from a valid token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    return payload.get("sub")
