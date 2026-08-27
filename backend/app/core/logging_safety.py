"""Keeping credentials out of the application log.

THE PROBLEM THIS SOLVES. The public investor report is addressed as
``GET /api/v1/share/report/{token}`` — the token is not an identifier that
happens to be secret, it *is* the credential, and it is the whole credential.
The request middleware logs ``request.url.path`` for every request, so before
this module every investor report view wrote a working, unexpiring capability
into stdout and from there into the container log, the log aggregator and
whatever backup holds them. Anyone with read access to operational logs could
open any farm's financial report.

WHY NOT JUST DROP THE SEGMENT. An operator diagnosing "the investor link is
returning 404" needs to tell one link from another across a log file. Replacing
every token with a constant would make all of them indistinguishable and would
trade a security defect for an operability one. So a scrubbed path carries a
short SHA-256 fingerprint of the secret instead: stable for a given token, so
two requests with the same link correlate, and preimage-resistant, so the
fingerprint cannot be turned back into a usable link. Twelve hex characters is
far too short to attack a 256-bit token by brute force and far more than enough
to distinguish the handful of links one farm mints.

SCOPE. This is deliberately a small allow-list of route shapes rather than a
general secret detector. A general detector would either miss the shapes it was
not taught or mangle ordinary paths; an explicit list is auditable, and it fails
in the safe direction because the sensitive routes are few and known. When a new
route carries a secret in its path, add it here and add a test to
``test_logging_safety.py`` — the test file is the enforcement.
"""
import hashlib
import logging
import re

# Route shapes whose final path segment is a credential rather than an
# identifier. Anchored, and matched against the path only (never the query
# string, which is scrubbed wholesale — see `scrub_path`).
_SECRET_PATH_SEGMENT = re.compile(
    r"^(?P<prefix>/api/v[0-9]+/share/report/)(?P<secret>[^/]+)(?P<suffix>/?)$"
)

# Query parameters whose VALUE is a credential. The public report takes none
# today; this exists so a future `?token=` cannot quietly reintroduce the leak.
_SECRET_QUERY_KEYS = frozenset({"token", "access_token", "api_key", "key", "secret", "password"})

REDACTED = "[redacted]"


def fingerprint(secret: str) -> str:
    """A short, stable, non-reversible handle for a secret.

    Twelve hex characters of SHA-256. Enough to correlate two requests carrying
    the same link in a log file; nowhere near enough to recover the link.
    """
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:12]


def scrub_path(path: str) -> str:
    """Return `path` with any credential segment replaced by a fingerprint.

    A path that carries no credential is returned unchanged, so ordinary log
    lines read exactly as they did before.
    """
    match = _SECRET_PATH_SEGMENT.match(path)
    if match is None:
        return path
    return (
        f"{match.group('prefix')}{REDACTED}:{fingerprint(match.group('secret'))}"
        f"{match.group('suffix')}"
    )


def scrub_query(query: str) -> str:
    """Return `query` with the values of credential-bearing keys replaced.

    Operates on the raw query string rather than a parsed mapping so that the
    scrubbed form stays a faithful rendering of what arrived — a malformed query
    is logged as malformed, not silently normalised.
    """
    if not query:
        return query
    parts = []
    for pair in query.split("&"):
        key, sep, _value = pair.partition("=")
        if sep and key.lower() in _SECRET_QUERY_KEYS:
            parts.append(f"{key}={REDACTED}")
        else:
            parts.append(pair)
    return "&".join(parts)


def safe_request_line(method: str, path: str, query: str = "") -> str:
    """The one string every log call should use to describe a request."""
    scrubbed = scrub_path(path)
    query = scrub_query(query)
    return f"{method} {scrubbed}?{query}" if query else f"{method} {scrubbed}"


def scrub_request_target(target: str) -> str:
    """Scrub a raw request target — ``/path`` or ``/path?query`` as it arrived.

    `scrub_path` and `scrub_query` each take one half; a server access log hands
    over the two joined, so this splits, scrubs and rejoins them.
    """
    path, sep, query = target.partition("?")
    scrubbed = scrub_path(path)
    if not sep:
        return scrubbed
    return f"{scrubbed}?{scrub_query(query)}"


class UvicornAccessScrubber(logging.Filter):
    """Removes credentials from uvicorn's access log.

    WHY THIS IS NEEDED ON TOP OF THE MIDDLEWARE. The application's own request
    log goes through `safe_request_line` and has done since the token leak was
    first reported. Uvicorn's access log is a SEPARATE mechanism that this
    application does not route through: it is emitted by the server, from
    `scope["path"]` and the raw query string, before and independently of any
    middleware. So the app log showed `[redacted]:5e7f4f9e` while the line
    directly beneath it read

        127.0.0.1:50685 - "GET /api/v1/share/report/<the real token>" 200 OK

    and the container's stdout — which is the log the department will actually
    collect — carried a working, unexpired capability to a farm's finances on
    every investor view. Verified by running uvicorn and reading its output; the
    regression test in test_logging_safety.py pins it.

    WHY A FILTER RATHER THAN --no-access-log. Turning the access log off would
    remove the leak by removing the diagnostics: the client address, the HTTP
    version and the server's own view of the status code all live there and
    nowhere else. A filter keeps every one of those and rewrites only the
    credential, which is the smallest change that fixes the defect.

    WHY IT REWRITES EVERY STRING ARGUMENT rather than indexing the one it
    expects. Uvicorn formats this record as
    ``'%s - "%s %s HTTP/%s" %d' % (client, method, full_path, version, status)``.
    Pinning to ``args[2]`` would silently stop scrubbing if that tuple were ever
    reordered — a leak that returns quietly on a dependency upgrade. Passing
    every string through `scrub_request_target` costs nothing (a path with no
    credential is returned unchanged) and cannot be broken by a reordering.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple):
            record.args = tuple(
                scrub_request_target(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True


def install_access_log_scrubber() -> None:
    """Attach the scrubber to uvicorn's access logger, once.

    Idempotent: importing the app twice in one process (the test suite does)
    must not stack duplicate filters. Safe to call when uvicorn is not running —
    the logger simply exists with nothing writing to it.
    """
    logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(f, UvicornAccessScrubber) for f in logger.filters):
        logger.addFilter(UvicornAccessScrubber())
