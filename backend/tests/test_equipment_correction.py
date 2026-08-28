"""Correcting an asset, and what a correction must not do.

A mistyped depreciation rate used to be permanent. It silently biased the
depreciation overlay, allocated fixed cost, and the break-even price to cover
total cost — three figures a farmer might quote to a lender — with no route to
put it right.

The two properties under test are the ones that make this safe:

  * a PATCH is PARTIAL, so correcting one field cannot blank another; and
  * a correction is VISIBLE, because it moves already-reported figures, and a
    number that changed silently is indistinguishable from one that was always
    that value.

The last group re-pins the platform's immutability rule, which this change does
NOT relax: financial records are still append-only and are still corrected only
by contra entry. Equipment is correctable because it describes a thing the farm
owns rather than something that happened.
"""
import pytest


def _equipment(client, **overrides):
    body = {"name": "Tractor", "purchase_price": 1_000_000.0, "depreciation_rate": 10.0}
    body.update(overrides)
    resp = client.post("/api/v1/equipment/", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


# --- the correction works -------------------------------------------------

def test_a_mistyped_depreciation_rate_can_be_corrected(client):
    asset = _equipment(client, depreciation_rate=100.0)   # meant 10.0

    resp = client.patch(f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 10.0})
    assert resp.status_code == 200
    assert resp.json()["depreciation_rate"] == 10.0


def test_a_correction_is_visible(client):
    """`updated_at` is NULL until the asset is corrected. Without it, a moved
    break-even price is indistinguishable from one that never moved."""
    asset = _equipment(client)
    assert asset["updated_at"] is None

    corrected = client.patch(
        f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 12.5}
    ).json()
    assert corrected["updated_at"] is not None


def test_a_patch_that_changes_nothing_is_not_recorded_as_a_correction(client):
    """Re-sending the current value is not a correction, and stamping one would
    tell a reader the asset moved when it did not."""
    asset = _equipment(client, depreciation_rate=10.0)
    resp = client.patch(f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 10.0})
    assert resp.status_code == 200
    assert resp.json()["updated_at"] is None


def test_a_correction_is_partial(client):
    """Correcting the rate must not blank the purchase price that was never in
    question. This is the difference between PATCH and PUT, and getting it wrong
    would destroy data while claiming to repair it."""
    asset = _equipment(client, name="Massey 375", purchase_price=4_500_000.0, depreciation_rate=99.0)

    corrected = client.patch(
        f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 9.0}
    ).json()

    assert corrected["depreciation_rate"] == 9.0
    assert corrected["purchase_price"] == 4_500_000.0
    assert corrected["name"] == "Massey 375"


def test_several_fields_can_be_corrected_at_once(client):
    asset = _equipment(client)
    corrected = client.patch(f"/api/v1/equipment/{asset['id']}", json={
        "name": "Massey Ferguson 375", "model": "MF375", "purchase_price": 5_200_000.0,
    }).json()
    assert corrected["name"] == "Massey Ferguson 375"
    assert corrected["model"] == "MF375"
    assert corrected["purchase_price"] == 5_200_000.0
    assert corrected["depreciation_rate"] == 10.0     # untouched


def test_an_empty_patch_is_accepted_and_changes_nothing(client):
    asset = _equipment(client)
    resp = client.patch(f"/api/v1/equipment/{asset['id']}", json={})
    assert resp.status_code == 200
    assert resp.json() == {**asset, "updated_at": None}


# --- the correction is validated -----------------------------------------

@pytest.mark.parametrize("body", [
    {"depreciation_rate": -5.0},
    {"depreciation_rate": 0.0},        # 0 is indistinguishable from "unrated"
    {"depreciation_rate": 150.0},
    {"purchase_price": -1.0},
    {"purchase_price": 1e15},
    {"name": ""},
])
def test_an_invalid_correction_is_rejected(client, body):
    """A correction can be as wrong as an original entry, so it takes the same
    bounds."""
    asset = _equipment(client)
    assert client.patch(f"/api/v1/equipment/{asset['id']}", json=body).status_code == 422


def test_a_rejected_correction_leaves_the_asset_untouched(client):
    asset = _equipment(client)
    client.patch(f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": -5.0})

    after = next(
        e for e in client.get("/api/v1/equipment/").json() if e["id"] == asset["id"]
    )
    assert after["depreciation_rate"] == 10.0
    assert after["updated_at"] is None


# --- scope and authorization ---------------------------------------------

def test_another_farms_asset_cannot_be_corrected(make_client):
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    asset = _equipment(a)

    resp = b.patch(f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 1.0})
    assert resp.status_code == 404      # not 403: existence is not confirmed


def test_correcting_a_missing_asset_is_a_404(client):
    assert client.patch("/api/v1/equipment/99999", json={"name": "x"}).status_code == 404


def test_an_anonymous_caller_cannot_correct_an_asset(client, anon_client):
    asset = _equipment(client)
    assert anon_client.patch(
        f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 1.0}
    ).status_code == 401


def test_a_worker_cannot_correct_an_asset(client, make_client, anon_client):
    """Equipment carries the depreciation rate that moves both break-even
    prices, which is why it sits behind EQUIPMENT_MANAGE."""
    asset = _equipment(client)
    client.post("/api/v1/auth/members", json={
        "email": "fieldhand@test.example", "password": "member-password", "role": "worker",
    })
    token = anon_client.post("/api/v1/auth/login", json={
        "email": "fieldhand@test.example", "password": "member-password",
    }).json()["access_token"]
    anon_client.headers.update({"Authorization": f"Bearer {token}"})

    assert anon_client.patch(
        f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 1.0}
    ).status_code == 403


# --- the correction actually moves the figures it should -----------------

def test_correcting_the_rate_moves_the_depreciation_overlay(client):
    """The whole point. A wrong rate biased the overlay with no way to fix it."""
    asset = _equipment(client, purchase_price=1_000_000.0, depreciation_rate=100.0)
    client.post("/api/v1/ledger/logs", json={
        "activity_type": "seed", "crop": "maize",
        "financial_data": {"amount": 50_000.0, "transaction_type": "debit", "category": "seed"},
    })

    before = client.get("/api/v1/dss/break-even-price?period_days=365").json()
    client.patch(f"/api/v1/equipment/{asset['id']}", json={"depreciation_rate": 10.0})
    after = client.get("/api/v1/dss/break-even-price?period_days=365").json()

    assert before["period_fixed_cost_ngn"] == pytest.approx(1_000_000.0)
    assert after["period_fixed_cost_ngn"] == pytest.approx(100_000.0)


# --- immutability is NOT relaxed -----------------------------------------

def test_ledger_records_are_still_not_editable(client):
    """Equipment became correctable; financial records did not. There is no
    PATCH on a log, and DELETE is still refused with a pointer to reversal."""
    log = client.post("/api/v1/ledger/logs", json={
        "activity_type": "seed", "crop": "maize",
        "financial_data": {"amount": 1000.0, "transaction_type": "debit", "category": "seed"},
    }).json()

    assert client.patch(f"/api/v1/ledger/logs/{log['id']}", json={"description": "x"}).status_code == 405
    assert client.delete(f"/api/v1/ledger/logs/{log['id']}").status_code == 405


def test_maintenance_logs_are_still_not_editable(client):
    asset = _equipment(client)
    maint = client.post("/api/v1/equipment/maintenance", json={
        "equipment_id": asset["id"], "description": "oil change", "cost": 15_000.0,
    }).json()
    assert client.patch(
        f"/api/v1/equipment/maintenance/{maint['id']}", json={"cost": 1.0}
    ).status_code in (404, 405)
