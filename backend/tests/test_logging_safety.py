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
