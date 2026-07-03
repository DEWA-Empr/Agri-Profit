"""Password hashing and JWT issue/verify — the cryptographic primitives behind
authentication (see api/deps.py for how the token becomes a current user).

Passwords are hashed with bcrypt; tokens are signed with python-jose using the
app secret. We call the `bcrypt` library directly rather than through passlib:
passlib 1.7.4 (its last release) cannot read the version of the installed
bcrypt 5.x and raises spurious errors, so the thin, stable bcrypt API is the
more durable choice for the same algorithm.
"""
import hashlib
import secrets
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


# --- Share tokens (ticket 05) ---
def generate_share_token() -> str:
    """A long, opaque, cryptographically-random share token (256 bits).

    URL-safe and unguessable — this is the secret embedded in an investor link.
    Only its hash is persisted (see hash_share_token); the raw value is shown to
    the owner once at mint time and never again.
    """
    return secrets.token_urlsafe(32)


def hash_share_token(token: str) -> str:
    """SHA-256 hex digest of a share token — what we store and look up by.

    A plain (unsalted) hash is deliberate: lookups must find a row by the token
    alone, and the 256-bit random input already makes precomputation/brute force
    infeasible, so a per-row salt would only break lookups without adding
    meaningful strength.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
