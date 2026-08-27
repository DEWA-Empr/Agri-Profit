"""Share-link lifecycle: expiry, revocation, and the links that predate expiry.

The property that matters most here is the BACKWARD-COMPATIBILITY one. Migration
f7b3c2d94e15 adds `expires_at` as nullable and backfills nothing, because a
farmer cannot be told that the link already sitting in a bank's inbox stopped
working on upgrade night. `test_a_legacy_link_with_no_expiry_still_resolves`
pins that: it is the test that would catch someone "tidying up" the column to
NOT NULL later.
"""
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.core.config import settings
from backend.app.models import models


def _mint(client, **body):
    resp = client.post("/api/v1/share/links", json=body or {"label": "First Bank"})
    assert resp.status_code == 201, resp.text
    return resp.json()


def _row(db, token_id):
    return db.query(models.ShareToken).filter(models.ShareToken.id == token_id).first()


# --- default lifetime -----------------------------------------------------

def test_a_new_link_expires_by_default(client):
    minted = _mint(client)
    assert minted["expires_at"] is not None

    expires = datetime.fromisoformat(minted["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    expected = datetime.now(timezone.utc) + timedelta(days=settings.share_link_default_ttl_days)
    # Generous window: the assertion is "roughly the configured default", not a
    # clock comparison that would flake on a slow test machine.
    assert abs((expires - expected).total_seconds()) < 120


def test_an_explicit_lifetime_is_honoured(client):
    minted = _mint(client, label="Short", expires_in_days=1)
    expires = datetime.fromisoformat(minted["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    delta = expires - datetime.now(timezone.utc)
    assert timedelta(hours=23) < delta < timedelta(hours=25)


@pytest.mark.parametrize("days", [0, -1, 366, 10_000])
def test_an_out_of_range_lifetime_is_rejected_at_the_schema_edge(client, days):
    resp = client.post("/api/v1/share/links", json={"label": "x", "expires_in_days": days})
    assert resp.status_code == 422


def test_the_owner_can_see_when_each_link_expires(client):
    _mint(client, label="Bank A", expires_in_days=30)
    links = client.get("/api/v1/share/links").json()
    assert len(links) == 1
    assert links[0]["expires_at"] is not None


# --- expiry actually takes effect ----------------------------------------

def test_an_expired_link_returns_404(client, db):
    minted = _mint(client)
    token = minted["token"]
    assert client.get(f"/api/v1/share/report/{token}").status_code == 200

    row = _row(db, minted["id"])
    row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()

    assert client.get(f"/api/v1/share/report/{token}").status_code == 404


def test_a_link_expiring_in_the_future_still_resolves(client, db):
    minted = _mint(client)
    row = _row(db, minted["id"])
    row.expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
    db.commit()

    assert client.get(f"/api/v1/share/report/{minted['token']}").status_code == 200


def test_an_expired_link_is_indistinguishable_from_an_unknown_one(client, db):
    """No oracle: 'expired' and 'never existed' must answer identically, or a
    caller probing recovered candidates learns which were once real."""
    minted = _mint(client)
    row = _row(db, minted["id"])
    row.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db.commit()

    expired = client.get(f"/api/v1/share/report/{minted['token']}")
    unknown = client.get("/api/v1/share/report/definitely-not-a-real-token")

    assert expired.status_code == unknown.status_code == 404
    assert expired.json() == unknown.json()


def test_a_revoked_link_is_indistinguishable_from_an_unknown_one(client):
    minted = _mint(client)
    client.post(f"/api/v1/share/links/{minted['id']}/revoke")

    revoked = client.get(f"/api/v1/share/report/{minted['token']}")
    unknown = client.get("/api/v1/share/report/definitely-not-a-real-token")

    assert revoked.status_code == unknown.status_code == 404
    assert revoked.json() == unknown.json()


# --- the compatibility guarantee -----------------------------------------

def test_a_legacy_link_with_no_expiry_still_resolves(client, db):
    """A token minted before expiry existed carries NULL and must never lapse.

    This is the guarantee migration f7b3c2d94e15 rests on. If `expires_at` is
    ever made NOT NULL, or the query drops its NULL branch, this test is what
    fails — and what it is protecting is every investor link already in
    circulation at upgrade time.
    """
    minted = _mint(client)
    row = _row(db, minted["id"])
    row.expires_at = None          # the shape every pre-migration row has
    db.commit()

    resp = client.get(f"/api/v1/share/report/{minted['token']}")
    assert resp.status_code == 200
    assert "pnl" in resp.json()


def test_a_legacy_link_can_still_be_revoked(client, db):
    minted = _mint(client)
    row = _row(db, minted["id"])
    row.expires_at = None
    db.commit()

    assert client.post(f"/api/v1/share/links/{minted['id']}/revoke").status_code == 200
    assert client.get(f"/api/v1/share/report/{minted['token']}").status_code == 404


# --- the boundary that already existed, re-pinned -------------------------

def test_expiry_does_not_weaken_farm_scoping(make_client, db):
    """Two farms, one link each: expiry must not have opened a cross-farm path."""
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    a_link = _mint(a, label="A's bank")

    # B cannot revoke A's link...
    assert b.post(f"/api/v1/share/links/{a_link['id']}/revoke").status_code == 404
    # ...and B's link list does not contain it.
    assert client_ids(b) == []
    assert len(client_ids(a)) == 1


def client_ids(c):
    return [row["id"] for row in c.get("/api/v1/share/links").json()]
