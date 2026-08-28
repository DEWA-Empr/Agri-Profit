"""Where the rate limiter meets HTTP.

Kept apart from `core/rate_limit.py` so the counting logic stays free of FastAPI
and stays unit-testable on its own. This module owns two things the core module
should not know about: how a rejection becomes a response (429 with
`Retry-After`), and what each protected route's key looks like.

KEYS ARE NAMESPACED BY ROUTE. "login:ip:10.0.0.4" and "register:ip:10.0.0.4" are
different budgets on purpose — exhausting one must not close the other, or a
single noisy client would take out an unrelated endpoint.
"""
from fastapi import HTTPException, Request, status

from ..core.config import settings
from ..core.rate_limit import client_ip, limiter


def _reject(retry_after: int) -> HTTPException:
    """A 429 that tells the caller when to come back.

    The message names no account and confirms no email: an error that said
    "too many attempts for this address" would confirm the address exists,
    which is the enumeration leak the login flow is otherwise careful to avoid
    (see auth_service.authenticate and schemas.LoginRequest).
    """
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many requests. Please wait and try again.",
        headers={"Retry-After": str(retry_after)},
    )


def _enforce(key: str, limit: int, window: int) -> None:
    retry_after = limiter.check(key, limit, window)
    if retry_after is not None:
        raise _reject(retry_after)


def guard_login(request: Request, email: str) -> None:
    """Throttle a login attempt on two independent budgets.

    Per account, so one address cannot be guessed at indefinitely from a
    rotating set of hosts; and per client IP, so one host cannot spray a
    dictionary across many accounts while staying under each account's limit.
    Either budget alone leaves the other attack open.

    The email is lower-cased to match how `auth_service` stores and compares it,
    so "Farmer@x.com" and "farmer@x.com" cannot be used as two budgets for one
    account.
    """
    _enforce(
        f"login:acct:{email.strip().lower()}",
        settings.login_max_attempts,
        settings.login_window_seconds,
    )
    _enforce(
        f"login:ip:{client_ip(request)}",
        settings.login_ip_max_attempts,
        settings.login_window_seconds,
    )


def clear_login(email: str) -> None:
    """Forget an account's failed attempts after a successful sign-in.

    The IP budget is deliberately NOT cleared: a host that has just produced
    twenty failures against twenty accounts has not become trustworthy by
    finally guessing one of them right.
    """
    limiter.clear(f"login:acct:{email.strip().lower()}")


def guard_register(request: Request) -> None:
    _enforce(
        f"register:ip:{client_ip(request)}",
        settings.register_max_attempts,
        settings.register_window_seconds,
    )


def guard_share_report(request: Request) -> None:
    """Throttle the one unauthenticated read path.

    Keyed on IP only — keying on the token would give each guessed value its own
    fresh budget, which is no limit at all.
    """
    _enforce(
        f"share:ip:{client_ip(request)}",
        settings.share_report_max_attempts,
        settings.share_report_window_seconds,
    )
