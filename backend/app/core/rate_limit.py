"""A small in-process rate limiter for the unauthenticated edges of the API.

WHAT THIS DEFENDS. Three routes accept traffic from anyone: login, registration,
and the public investor report. Before this module each was unbounded — a
password could be guessed as fast as bcrypt would answer, the database could be
filled with accounts by a loop, and the one endpoint that trades a bearer token
for a farm's finances could be probed without limit.

WHY IN-PROCESS, AND WHEN THAT STOPS BEING RIGHT. Counters live in this
process's memory. That is the correct shape for the deployment this platform
actually targets — a single backend container run by a department — and it costs
no new dependency, no Redis to operate, and no network round trip on the hot
path. It has two honest limits, both of which are stated in the operations guide
rather than hidden:

  * **It does not span replicas.** Run two backend containers behind a load
    balancer and each keeps its own counters, so the effective limit doubles. It
    still bounds an attacker; it stops being an exact number.
  * **It does not survive a restart.** A crash or redeploy clears the windows.
    An attacker who could force restarts could reset their budget — but an
    attacker who can force restarts has a larger problem to sell you.

Either limit is the trigger to move the counters into Redis or the reverse
proxy, and neither is reached by the target deployment. Solving them now would
add an operational component to a system that has no other reason to need one.

FIXED WINDOW, NOT SLIDING. A fixed window admits at most 2N requests across a
window boundary, which a sliding log would not. That burst is irrelevant to the
threat here — the point is to turn an unbounded guessing loop into a bounded one
— and a fixed window costs one integer and one timestamp per key instead of a
list of every hit. The simpler structure is also the one that cannot leak memory
under a flood of distinct keys, because a key holds a fixed-size record.

WHAT IS COUNTED, AND WHAT IS NOT. Login counts FAILURES only. Counting successes
would let an attacker lock a farmer out of their own account by burning the
budget from another host, turning a brute-force defence into a denial-of-service
tool. A successful login clears the account's counter outright, so a farmer who
mistypes a password four times and then gets it right starts clean.
"""
import threading
import time
from dataclasses import dataclass
from typing import Optional

from .config import settings


@dataclass
class _Window:
    count: int
    started_at: float


class RateLimiter:
    """Fixed-window counters keyed by an arbitrary string.

    Thread-safe: uvicorn serves requests from a worker thread pool, and two
    login attempts on one account can land at once. A lock around a dictionary
    is ample — the critical section is a few microseconds and the contention is
    per-key in practice.
    """

    def __init__(self) -> None:
        self._windows: dict[str, _Window] = {}
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> Optional[int]:
        """Record a hit against `key`.

        Returns None when the caller is within budget, or the number of seconds
        until the window resets when it is not. The retry hint is returned
        rather than raising so that callers can decide the response shape —
        the API layer turns it into a 429 with `Retry-After`.

        A blocked hit does NOT extend the window. Extending it on every rejected
        attempt would let a persistent attacker hold a legitimate user out
        indefinitely, which is the denial-of-service failure mode this whole
        module is supposed to avoid creating.
        """
        if not settings.rate_limit_enabled:
            return None

        now = time.monotonic()
        with self._lock:
            window = self._windows.get(key)
            if window is None or (now - window.started_at) >= window_seconds:
                self._windows[key] = _Window(count=1, started_at=now)
                return None
            if window.count >= limit:
                remaining = window_seconds - (now - window.started_at)
                return max(1, int(remaining) + 1)
            window.count += 1
            return None

    def clear(self, key: str) -> None:
        """Forget one key. Called when a login succeeds, so a legitimate user's
        earlier fumbles do not count against their next session."""
        with self._lock:
            self._windows.pop(key, None)

    def reset(self) -> None:
        """Drop every window. For tests, which must not inherit counters from
        whichever test ran before them, and for an operator recovering from a
        misconfigured limit without a restart."""
        with self._lock:
            self._windows.clear()

    def prune(self, max_age_seconds: int = 86_400) -> int:
        """Drop windows older than `max_age_seconds`; returns how many went.

        Without this the dictionary grows once per distinct key seen — one entry
        per client IP per route, forever. The entries are tiny, but "tiny and
        unbounded" is still a leak on a long-lived process, and a department's
        server is meant to run for months between restarts.
        """
        cutoff = time.monotonic() - max_age_seconds
        with self._lock:
            stale = [k for k, w in self._windows.items() if w.started_at < cutoff]
            for key in stale:
                del self._windows[key]
        return len(stale)


# One limiter for the process. Module-level rather than injected because it is
# shared state by definition — a per-request instance would count to one.
limiter = RateLimiter()


def client_ip(request) -> str:
    """The caller's address, honouring one layer of reverse proxy.

    `X-Forwarded-For` is only consulted when `settings.trust_proxy_headers` is
    on, and only its FIRST entry is used. A client can send that header itself,
    so trusting it unconditionally would hand every attacker a free way to
    rotate their identity and bypass every per-IP limit here. It is therefore
    opt-in, and the operations guide is explicit that it must be enabled only
    when a proxy the deployment controls is guaranteed to overwrite it.
    """
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first = forwarded.split(",")[0].strip()
            if first:
                return first
    client = getattr(request, "client", None)
    return getattr(client, "host", None) or "unknown"
