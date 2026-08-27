"""The share token is the credential; it must never reach the log.

These are regression tests in the strict sense: the defect they pin existed and
was reachable. `GET /api/v1/share/report/{token}` carries the whole credential
in its path, and the request middleware logged `request.url.path` verbatim, so
every investor view wrote a working link into stdout.

The assertions are on the CAPTURED LOG TEXT, not on whether a scrubbing function
was called. A test that asserted `scrub_path` had been invoked would pass just as
happily if the middleware logged the raw path alongside it.

The application logger sets `propagate = False` so its records never reach the
root logger, which is where pytest's `caplog` attaches. These tests therefore
attach their own handler to the `agriprofit` logger directly — going through
caplog here would capture nothing and pass vacuously.
"""
import logging

import pytest

from backend.app.core import logging_safety


@pytest.fixture
def captured_logs():
    """Every record the application logger emits during the test, as text."""
    logger = logging.getLogger("agriprofit")
    records: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record):
            records.append(self.format(record))

    handler = _Capture()
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(handler)
    try:
        yield records
    finally:
        logger.removeHandler(handler)


def _mint(client, label="First Bank"):
    resp = client.post("/api/v1/share/links", json={"label": label})
    assert resp.status_code == 201, resp.text
    return resp.json()["token"]


# --- the defect itself ----------------------------------------------------

def test_share_token_is_not_written_to_the_log_on_a_successful_read(client, captured_logs):
    token = _mint(client)
    captured_logs.clear()  # drop the mint request's own line

    assert client.get(f"/api/v1/share/report/{token}").status_code == 200

    assert captured_logs, "the middleware should still log the request"
    joined = "\n".join(captured_logs)
    assert token not in joined
    assert "[redacted]" in joined


def test_share_token_is_not_written_to_the_log_on_an_invalid_token(client, captured_logs):
    """The 404 path is the one an attacker probing links actually exercises."""
    captured_logs.clear()
    bogus = "not-a-real-token-abcdefghijklmnop"

    assert client.get(f"/api/v1/share/report/{bogus}").status_code == 404

    joined = "\n".join(captured_logs)
    assert bogus not in joined
    assert "[redacted]" in joined


def test_a_revoked_token_is_not_written_to_the_log(client, captured_logs):
    token = _mint(client)
    link_id = client.get("/api/v1/share/links").json()[0]["id"]
    assert client.post(f"/api/v1/share/links/{link_id}/revoke").status_code == 200
    captured_logs.clear()

    assert client.get(f"/api/v1/share/report/{token}").status_code == 404

    assert token not in "\n".join(captured_logs)


# --- the log must stay useful --------------------------------------------

def test_two_reads_of_the_same_link_share_one_fingerprint(client, captured_logs):
    """Scrubbing must not make every link indistinguishable — an operator has to
    be able to tell one investor link from another across a log file."""
    token = _mint(client)
    captured_logs.clear()

    client.get(f"/api/v1/share/report/{token}")
    client.get(f"/api/v1/share/report/{token}")

    fingerprints = {
        line.split("[redacted]:")[1].split()[0]
        for line in captured_logs
        if "[redacted]:" in line
    }
    assert len(fingerprints) == 1


def test_two_different_links_get_different_fingerprints(client, captured_logs):
    a = _mint(client, "Bank A")
    b = _mint(client, "Bank B")
    captured_logs.clear()

    client.get(f"/api/v1/share/report/{a}")
    client.get(f"/api/v1/share/report/{b}")

    fingerprints = {
        line.split("[redacted]:")[1].split()[0]
        for line in captured_logs
        if "[redacted]:" in line
    }
    assert len(fingerprints) == 2


def test_ordinary_paths_are_logged_unchanged(client, captured_logs):
    """Scrubbing is an allow-list, so a normal route must read exactly as before."""
    captured_logs.clear()
    client.get("/api/v1/ledger/logs")

    joined = "\n".join(captured_logs)
    assert "/api/v1/ledger/logs" in joined
    assert "[redacted]" not in joined


# --- the scrubber in isolation -------------------------------------------

def test_scrub_path_leaves_a_non_secret_path_alone():
    for path in ("/api/v1/ledger/logs", "/api/v1/dss/decision-support", "/", "/health"):
        assert logging_safety.scrub_path(path) == path


def test_scrub_path_replaces_the_share_token_segment():
    out = logging_safety.scrub_path("/api/v1/share/report/SECRET-VALUE")
    assert "SECRET-VALUE" not in out
    assert out.startswith("/api/v1/share/report/[redacted]:")


def test_scrub_path_handles_a_trailing_slash():
    out = logging_safety.scrub_path("/api/v1/share/report/SECRET-VALUE/")
    assert "SECRET-VALUE" not in out
    assert out.endswith("/")


def test_scrub_path_does_not_touch_the_links_collection():
    """`/share/links` carries ids, not credentials, and must stay readable."""
    assert logging_safety.scrub_path("/api/v1/share/links") == "/api/v1/share/links"
    assert logging_safety.scrub_path("/api/v1/share/links/7/revoke") == "/api/v1/share/links/7/revoke"


def test_fingerprint_is_stable_and_not_the_secret():
    fp = logging_safety.fingerprint("some-token")
    assert fp == logging_safety.fingerprint("some-token")
    assert fp != logging_safety.fingerprint("some-other-token")
    assert "some-token" not in fp
    assert len(fp) == 12


def test_scrub_query_redacts_credential_bearing_parameters():
    assert logging_safety.scrub_query("token=abc123") == "token=[redacted]"
    assert logging_safety.scrub_query("crop=maize") == "crop=maize"
    out = logging_safety.scrub_query("crop=maize&access_token=abc123&period_days=7")
    assert "abc123" not in out
    assert "crop=maize" in out
    assert "period_days=7" in out


def test_safe_request_line_composes_method_path_and_query():
    line = logging_safety.safe_request_line("GET", "/api/v1/share/report/SECRET", "")
    assert "SECRET" not in line
    assert line.startswith("GET /api/v1/share/report/[redacted]:")


# --- the server's own access log ------------------------------------------
# A SECOND, INDEPENDENT LEAK, found after the middleware above was fixed.
#
# Uvicorn writes its own access log from the raw request target, before any
# middleware runs and without passing through this application at all. So the
# scrubbed line the middleware emitted sat directly above an unscrubbed one:
#
#   ERROR: [agriprofit] ... /api/v1/share/report/[redacted]:5e7f4f9ed044
#   INFO:  127.0.0.1:50685 - "GET /api/v1/share/report/<the live token>" 200 OK
#
# and stdout — the log a department actually collects — carried a working
# capability to a farm's finances on every investor view. Confirmed by running
# uvicorn against this app and reading its output; fixed with a logging filter
# on the `uvicorn.access` logger, which keeps the client address, HTTP version
# and status that only that log carries.
#
# These tests construct the record uvicorn really emits rather than calling the
# scrubbing helper, because the helper was never the thing that was broken — the
# wiring was.

TOKEN = "vY3xK9pQ2mR7tL4nB8wZ6cF1jH5dS0aG"


def _uvicorn_access_record(target: str) -> logging.LogRecord:
    """The record uvicorn's access logger emits, in its real shape.

    Format and argument order are uvicorn's own
    (`'%s - "%s %s HTTP/%s" %d'`), so if either changes upstream this test
    stops resembling reality — which is the point at which the filter should be
    re-checked rather than trusted.
    """
    return logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:50685", "GET", target, "1.1", 200),
        exc_info=None,
    )


@pytest.fixture
def access_logger():
    """The real `uvicorn.access` logger with the app's filter installed."""
    logging_safety.install_access_log_scrubber()
    logger = logging.getLogger("uvicorn.access")
    records: list[str] = []

    class _Capture(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = _Capture()
    logger.addHandler(handler)
    previous = logger.level
    logger.setLevel(logging.INFO)
    try:
        yield logger, records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous)


def test_the_access_log_does_not_carry_a_raw_share_token(access_logger):
    logger, records = access_logger

    logger.handle(_uvicorn_access_record(f"/api/v1/share/report/{TOKEN}"))

    assert records, "the access record was dropped instead of logged"
    assert TOKEN not in records[0]
    assert "[redacted]" in records[0]


def test_the_access_log_keeps_the_diagnostics_that_live_only_there(access_logger):
    """Scrubbing must not cost the client address, method, version or status —
    removing the leak by removing the access log would trade one defect for
    another."""
    logger, records = access_logger

    logger.handle(_uvicorn_access_record(f"/api/v1/share/report/{TOKEN}"))

    line = records[0]
    assert "127.0.0.1:50685" in line
    assert "GET" in line
    assert "HTTP/1.1" in line
    assert "200" in line


def test_the_access_log_leaves_an_ordinary_path_untouched(access_logger):
    logger, records = access_logger

    logger.handle(_uvicorn_access_record("/api/v1/ledger/logs?skip=0&limit=100"))

    assert records[0].endswith('"GET /api/v1/ledger/logs?skip=0&limit=100 HTTP/1.1" 200')


def test_the_access_log_redacts_a_token_passed_as_a_query_parameter(access_logger):
    logger, records = access_logger

    logger.handle(_uvicorn_access_record(f"/api/v1/anything?token={TOKEN}"))

    assert TOKEN not in records[0]


def test_two_views_of_one_link_stay_correlatable_in_the_access_log(access_logger):
    """The fingerprint is what makes the scrubbed log still usable for "which
    link is 404ing?" — identical tokens must produce identical handles."""
    logger, records = access_logger

    logger.handle(_uvicorn_access_record(f"/api/v1/share/report/{TOKEN}"))
    logger.handle(_uvicorn_access_record(f"/api/v1/share/report/{TOKEN}"))
    logger.handle(_uvicorn_access_record("/api/v1/share/report/a-different-token"))

    assert records[0] == records[1]
    assert records[2] != records[0]


def test_installing_the_scrubber_twice_does_not_stack_filters():
    """The app module installs on import, and importing it twice in one process
    (which the suite does) must not attach a second copy."""
    logging_safety.install_access_log_scrubber()
    logging_safety.install_access_log_scrubber()

    logger = logging.getLogger("uvicorn.access")
    installed = [f for f in logger.filters if isinstance(f, logging_safety.UvicornAccessScrubber)]
    assert len(installed) == 1


def test_the_filter_survives_an_unexpected_record_shape():
    """If uvicorn ever reorders its arguments, the filter must still scrub
    rather than pass the target through because it was not where we expected."""
    scrubber = logging_safety.UvicornAccessScrubber()
    record = logging.LogRecord(
        name="uvicorn.access", level=logging.INFO, pathname=__file__, lineno=1,
        msg="%s %s",
        args=(f"/api/v1/share/report/{TOKEN}", "reordered"),
        exc_info=None,
    )

    scrubber.filter(record)

    assert TOKEN not in record.getMessage()
