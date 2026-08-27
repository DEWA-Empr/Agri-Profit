"""Rate limiting on the three unauthenticated edges of the API.

Every test here lowers the configured limit to something small and then proves
the boundary by CROSSING it — the assertion is on a real 429 from a real
request, not on whether a limiter function was reached.

Two properties get as much attention as the limits themselves, because both are
ways a rate limiter can be worse than none at all:

  * a successful login must clear the account's budget, or a farmer who mistypes
    their password a few times carries those failures into their next session;
  * failing to log in as somebody must not lock that somebody out, or the
    brute-force defence becomes a denial-of-service tool aimed at any address an
    attacker knows.
"""
import pytest

from backend.app.core import rate_limit
from backend.app.core.config import settings
from backend.app.core.rate_limit import RateLimiter


@pytest.fixture
def tight_limits(monkeypatch):
    """Small windows so a test can cross a boundary in a few requests."""
    monkeypatch.setattr(settings, "login_max_attempts", 3)
    monkeypatch.setattr(settings, "login_ip_max_attempts", 100)
    monkeypatch.setattr(settings, "login_window_seconds", 900)
    monkeypatch.setattr(settings, "register_max_attempts", 3)
    monkeypatch.setattr(settings, "register_window_seconds", 3600)
    monkeypatch.setattr(settings, "share_report_max_attempts", 3)
    monkeypatch.setattr(settings, "share_report_window_seconds", 300)


def _register(anon_client, email):
    return anon_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "a-good-password", "farm_name": "F"},
    )


def _login(anon_client, email, password):
    return anon_client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


# --- login ----------------------------------------------------------------

def test_repeated_failed_logins_are_eventually_refused(anon_client, tight_limits):
    assert _register(anon_client, "brute@test.example").status_code == 201

    for _ in range(3):
        assert _login(anon_client, "brute@test.example", "wrong").status_code == 401

    blocked = _login(anon_client, "brute@test.example", "wrong")
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    assert int(blocked.headers["Retry-After"]) > 0


def test_the_lockout_survives_the_correct_password(anon_client, tight_limits):
    """Once the budget is spent the door stays shut for the window — otherwise
    an attacker gets an unlimited number of guesses at the cost of one 429."""
    assert _register(anon_client, "spent@test.example").status_code == 201
    for _ in range(4):
        _login(anon_client, "spent@test.example", "wrong")

    assert _login(anon_client, "spent@test.example", "a-good-password").status_code == 429


def test_a_successful_login_clears_the_accounts_budget(anon_client, tight_limits):
    """A farmer who fumbles twice and then succeeds must not be two failures
    away from a lockout for the next fifteen minutes."""
    assert _register(anon_client, "fumble@test.example").status_code == 201

    assert _login(anon_client, "fumble@test.example", "wrong").status_code == 401
    assert _login(anon_client, "fumble@test.example", "wrong").status_code == 401
    assert _login(anon_client, "fumble@test.example", "a-good-password").status_code == 200

    # Budget reset: three more failures are tolerated before the fourth is refused.
    for _ in range(3):
        assert _login(anon_client, "fumble@test.example", "wrong").status_code == 401
    assert _login(anon_client, "fumble@test.example", "wrong").status_code == 429


def test_locking_one_account_does_not_lock_another(anon_client, tight_limits):
    """The per-account budget must be per account, or one attacker denies the
    whole platform by burning a single shared counter."""
    assert _register(anon_client, "victim@test.example").status_code == 201
    assert _register(anon_client, "bystander@test.example").status_code == 201

    for _ in range(4):
        _login(anon_client, "victim@test.example", "wrong")
    assert _login(anon_client, "victim@test.example", "wrong").status_code == 429

    assert _login(anon_client, "bystander@test.example", "a-good-password").status_code == 200


def test_the_account_budget_is_case_insensitive(anon_client, tight_limits):
    """Otherwise 'Victim@x' and 'victim@x' are two budgets for one account."""
    assert _register(anon_client, "case@test.example").status_code == 201

    for _ in range(3):
        _login(anon_client, "case@test.example", "wrong")
    assert _login(anon_client, "CASE@Test.Example", "wrong").status_code == 429


def test_the_throttle_message_does_not_confirm_the_account_exists(anon_client, tight_limits):
    """A 429 that said 'too many attempts for this address' would be an
    enumeration oracle — the rest of the login flow is careful not to be one."""
    for _ in range(4):
        _login(anon_client, "nobody@test.example", "wrong")
    blocked = _login(anon_client, "nobody@test.example", "wrong")

    assert blocked.status_code == 429
    assert "nobody@test.example" not in blocked.text


# --- registration ---------------------------------------------------------

def test_registration_is_capped_per_client(anon_client, tight_limits):
    for i in range(3):
        assert _register(anon_client, f"bulk{i}@test.example").status_code == 201

    blocked = _register(anon_client, "bulk-overflow@test.example")
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


# --- public investor report ----------------------------------------------

def test_the_public_report_is_capped_per_client(client, anon_client, tight_limits):
    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()["token"]

    for _ in range(3):
        assert anon_client.get(f"/api/v1/share/report/{token}").status_code == 200

    blocked = anon_client.get(f"/api/v1/share/report/{token}")
    assert blocked.status_code == 429


def test_probing_many_tokens_shares_one_budget(anon_client, tight_limits):
    """Keying the limit on the token would give every guess its own fresh
    budget, which is not a limit at all."""
    for i in range(3):
        assert anon_client.get(f"/api/v1/share/report/guess-{i}").status_code == 404

    assert anon_client.get("/api/v1/share/report/guess-99").status_code == 429


# --- budgets are namespaced ----------------------------------------------

def test_exhausting_registration_does_not_block_login(anon_client, tight_limits):
    assert _register(anon_client, "keep@test.example").status_code == 201
    for i in range(5):
        _register(anon_client, f"flood{i}@test.example")

    assert _login(anon_client, "keep@test.example", "a-good-password").status_code == 200


# --- the limiter in isolation --------------------------------------------

def test_limiter_admits_up_to_the_limit_then_refuses():
    lim = RateLimiter()
    for _ in range(5):
        assert lim.check("k", limit=5, window_seconds=60) is None
    assert lim.check("k", limit=5, window_seconds=60) is not None


def test_limiter_keys_are_independent():
    lim = RateLimiter()
    for _ in range(5):
        lim.check("a", limit=5, window_seconds=60)
    assert lim.check("a", limit=5, window_seconds=60) is not None
    assert lim.check("b", limit=5, window_seconds=60) is None


def test_limiter_window_expires(monkeypatch):
    lim = RateLimiter()
    clock = {"t": 1000.0}
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock["t"])

    for _ in range(3):
        lim.check("k", limit=3, window_seconds=60)
    assert lim.check("k", limit=3, window_seconds=60) is not None

    clock["t"] += 61
    assert lim.check("k", limit=3, window_seconds=60) is None


def test_a_blocked_attempt_does_not_extend_the_window(monkeypatch):
    """A persistent attacker must not be able to hold a real user out forever by
    hammering a key that is already blocked."""
    lim = RateLimiter()
    clock = {"t": 1000.0}
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock["t"])

    for _ in range(3):
        lim.check("k", limit=3, window_seconds=60)
    for _ in range(50):                      # keep pounding while blocked
        clock["t"] += 0.5
        assert lim.check("k", limit=3, window_seconds=60) is not None

    clock["t"] = 1000.0 + 61                 # past the ORIGINAL window
    assert lim.check("k", limit=3, window_seconds=60) is None


def test_limiter_retry_after_counts_down():
    lim = RateLimiter()
    for _ in range(2):
        lim.check("k", limit=2, window_seconds=300)
    retry = lim.check("k", limit=2, window_seconds=300)
    assert 0 < retry <= 301


def test_limiter_can_be_disabled(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", False)
    lim = RateLimiter()
    for _ in range(100):
        assert lim.check("k", limit=1, window_seconds=60) is None


def test_prune_drops_only_stale_windows(monkeypatch):
    """Without pruning the dictionary grows one entry per distinct key, forever."""
    lim = RateLimiter()
    clock = {"t": 1000.0}
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: clock["t"])

    lim.check("old", limit=5, window_seconds=60)
    clock["t"] += 100_000
    lim.check("fresh", limit=5, window_seconds=60)

    assert lim.prune(max_age_seconds=86_400) == 1
    assert lim.check("fresh", limit=1, window_seconds=60) is not None   # survived
    assert lim.check("old", limit=1, window_seconds=60) is None         # forgotten


# --- proxy header handling -----------------------------------------------

def test_forwarded_header_is_ignored_unless_explicitly_trusted(monkeypatch, anon_client, tight_limits):
    """A client can send X-Forwarded-For itself. If it were believed by default,
    rotating the header would defeat every per-IP limit in the API."""
    monkeypatch.setattr(settings, "trust_proxy_headers", False)

    for i in range(3):
        anon_client.post(
            "/api/v1/auth/register",
            json={"email": f"spoof{i}@test.example", "password": "a-good-password"},
            headers={"X-Forwarded-For": f"10.0.0.{i}"},
        )

    blocked = anon_client.post(
        "/api/v1/auth/register",
        json={"email": "spoof-final@test.example", "password": "a-good-password"},
        headers={"X-Forwarded-For": "10.0.0.99"},
    )
    assert blocked.status_code == 429


def test_forwarded_header_is_used_when_trusted(monkeypatch, anon_client, tight_limits):
    monkeypatch.setattr(settings, "trust_proxy_headers", True)

    for i in range(3):
        resp = anon_client.post(
            "/api/v1/auth/register",
            json={"email": f"proxied{i}@test.example", "password": "a-good-password"},
            headers={"X-Forwarded-For": "10.0.0.1"},
        )
        assert resp.status_code == 201

    # Same budget, exhausted.
    assert anon_client.post(
        "/api/v1/auth/register",
        json={"email": "proxied-over@test.example", "password": "a-good-password"},
        headers={"X-Forwarded-For": "10.0.0.1"},
    ).status_code == 429

    # A genuinely different upstream client has its own.
    assert anon_client.post(
        "/api/v1/auth/register",
        json={"email": "other-host@test.example", "password": "a-good-password"},
        headers={"X-Forwarded-For": "10.0.0.2"},
    ).status_code == 201
