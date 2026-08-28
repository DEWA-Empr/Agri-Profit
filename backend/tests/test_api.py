import base64
from datetime import timedelta

import pytest


def _post_log(client, *, activity_type, amount, transaction_type, category=None, client_id=None):
    """Create an operational log with its paired financial transaction."""
    payload = {
        "activity_type": activity_type,
        "description": f"{activity_type} entry",
        "quantity": 1.0,
        "unit": "unit",
        "financial_data": {
            "amount": amount,
            "transaction_type": transaction_type,
            "category": category or activity_type,
            "description": f"{activity_type} tx",
        },
    }
    if client_id is not None:
        payload["client_id"] = client_id
    return client.post("/api/v1/ledger/logs", json=payload)


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the AgriProfit API"}

def test_create_log_with_financials(client):
    payload = {
        "activity_type": "fertilizer",
        "description": "Applied 5 bags of NPK",
        "quantity": 5.0,
        "unit": "bags",
        "financial_data": {
            "amount": 25000.0,
            "transaction_type": "debit",
            "category": "fertilizer",
            "description": "Purchase of 5 NPK bags",
            "tax_category": "Agriculture Inputs"
        }
    }
    response = client.post("/api/v1/ledger/logs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["activity_type"] == "fertilizer"
    assert data["financial_transaction_id"] is not None
    assert data["financial_transaction"]["amount"] == 25000.0

def test_get_summary(client):
    # Seed a known debit and credit, then assert exact totals (self-contained).
    assert _post_log(client, activity_type="fertilizer", amount=25000.0, transaction_type="debit").status_code == 201
    assert _post_log(client, activity_type="yield", amount=40000.0, transaction_type="credit").status_code == 201

    response = client.get("/api/v1/ledger/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["revenue"] == 40000.0
    assert data["expenses"] == 25000.0
    assert data["gross_margin"] == 15000.0

def test_dss_predict_rejects_malformed_payload(client):
    # The multi-crop DSS endpoint validates its body against the model's training
    # bounds. A legacy {"features": [...]} payload is missing every required
    # field (rainfall, fertilizer_used, soil_ph, crop), so it is a 422 — not the
    # 503 this test used to assert.
    #
    # The engine's "no model trained" -> 503 branch is unreachable from the API
    # here: the app's startup hook (ensure_dss_model -> train.ensure_model) trains
    # and persists a model before any request runs, so a well-formed payload
    # returns 200 (see below) and a malformed one is rejected at validation.
    response = client.post("/api/v1/dss/predict", json={"features": [1, 2, 3]})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_dss_predict_returns_forecast(client):
    # Honest happy path: the startup hook has trained the synthetic-data model,
    # so a well-formed agronomic payload yields a forecast carrying a confidence
    # and a prediction interval (the shape the dashboard consumes).
    payload = {"rainfall": 1200, "fertilizer_used": 60, "soil_ph": 6.2, "crop": "maize"}
    response = client.post("/api/v1/dss/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] > 0
    assert 0.0 <= data["confidence"] <= 100.0
    assert set(data["interval"]) == {"lower", "upper"}

def _post_crop_log(client, *, activity_type, crop, amount, transaction_type, quantity=None, unit=None):
    """Seed a crop-tagged operational log with its paired financial transaction."""
    payload = {
        "activity_type": activity_type,
        "description": f"{crop} {activity_type}",
        "crop": crop,
        "financial_data": {
            "amount": amount,
            "transaction_type": transaction_type,
            "category": activity_type,
        },
    }
    if quantity is not None:
        payload["quantity"] = quantity
    if unit is not None:
        payload["unit"] = unit
    return client.post("/api/v1/ledger/logs", json=payload)


def test_dss_decision_support_empty_ledger(client):
    # Empty ledger: no crops and zeroed overall totals. The client renders an
    # empty state from this — never fabricated numbers.
    response = client.get("/api/v1/dss/decision-support")
    assert response.status_code == 200
    data = response.json()
    assert data["crops"] == []
    assert data["overall"] == {"revenue": 0.0, "expenses": 0.0, "gross_margin": 0.0}


def test_dss_decision_support_computes_from_ledger(client):
    # Seed real, crop-tagged ledger rows and assert the deterministic Tier-1
    # figures match a hand calculation (Chapter 3 §3.8.1: arithmetic fidelity):
    #
    #   maize: fertilizer debit ₦25,000; yield credit ₦40,000 over 12 bags
    #          gross margin = 40,000 − 25,000            = ₦15,000
    #          unit cost    = 25,000 / 12                = ₦2,083.33…
    #   rice:  labour debit ₦10,000; no yield recorded
    #          gross margin = 0 − 10,000                 = −₦10,000
    #          unit cost    = None (no yield → no divide by zero)
    #   overall gross margin = 15,000 + (−10,000)        = ₦5,000
    assert _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit").status_code == 201
    assert _post_crop_log(client, activity_type="yield", crop="maize", amount=40000.0, transaction_type="credit", quantity=12.0, unit="bags").status_code == 201
    assert _post_crop_log(client, activity_type="labour", crop="rice", amount=10000.0, transaction_type="debit").status_code == 201

    response = client.get("/api/v1/dss/decision-support")
    assert response.status_code == 200
    data = response.json()

    crops = {c["crop"]: c for c in data["crops"]}
    assert set(crops) == {"maize", "rice"}

    maize = crops["maize"]
    assert maize["revenue"] == 40000.0
    assert maize["expenses"] == 25000.0
    assert maize["gross_margin"] == 15000.0
    assert maize["yield_quantity"] == 12.0
    assert maize["yield_unit"] == "bags"
    assert maize["unit_cost_of_production"] == pytest.approx(25000.0 / 12.0)

    rice = crops["rice"]
    assert rice["gross_margin"] == -10000.0
    assert rice["yield_quantity"] == 0.0
    assert rice["unit_cost_of_production"] is None

    assert data["overall"] == {"revenue": 40000.0, "expenses": 35000.0, "gross_margin": 5000.0}


def test_equipment_lifecycle(client):
    # 1. Create equipment
    eq_payload = {
        "name": "Massey Ferguson 375",
        "model": "2024 Model",
        "purchase_price": 15000000.0,
        "depreciation_rate": 10.0
    }
    response = client.post("/api/v1/equipment/", json=eq_payload)
    assert response.status_code == 201
    eq_data = response.json()
    eq_id = eq_data["id"]
    assert eq_data["name"] == "Massey Ferguson 375"

    # 2. Add maintenance
    maint_payload = {
        "equipment_id": eq_id,
        "description": "Oil change and filter replacement",
        "cost": 50000.0
    }
    response = client.post("/api/v1/equipment/maintenance", json=maint_payload)
    assert response.status_code == 201
    maint_data = response.json()
    assert maint_data["equipment_id"] == eq_id
    assert maint_data["cost"] == 50000.0

    # 3. Read maintenance
    response = client.get(f"/api/v1/equipment/{eq_id}/maintenance")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_idempotent_log_creation(client):
    client_id = "test-client-uuid-idempotency-001"
    payload = {
        "activity_type": "seed",
        "description": "Idempotency test",
        "quantity": 2.0,
        "unit": "bags",
        "client_id": client_id,
        "financial_data": {
            "amount": 5000.0,
            "transaction_type": "debit",
            "category": "seed",
            "description": "Seed purchase",
            "tax_category": "Agriculture Inputs"
        }
    }
    # Replaying the same client_id (an offline log flushed twice after a
    # dropped connection) must be idempotent: same id back, and — crucially —
    # exactly one record stored, with no double-booked financial transaction.
    # The genuine creation is 201; the idempotent replay is 200 (found, not
    # newly created).
    r1 = client.post("/api/v1/ledger/logs", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/ledger/logs", json=payload)
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    # Prove single-record persistence, not just id equality: the second POST
    # must not have created a duplicate log or a duplicate paired transaction.
    logs = client.get("/api/v1/ledger/logs")
    assert logs.status_code == 200
    assert len(logs.json()) == 1
    transactions = client.get("/api/v1/ledger/transactions")
    assert transactions.status_code == 200
    assert len(transactions.json()) == 1

# --- client_id: uniqueness is farm-scoped, like the idempotency that reads it ---
#
# Regression for docs/STATE_REPORT_2026-08-25.md Section 9.14. The unique index
# on client_id was global (initial schema 544b85dc2d20, written before farm_id
# existed) while _find_by_client_id has always matched within one farm. Farm B
# reusing farm A's key violated the index, missed the farm-scoped recovery
# lookup, hit the bare `raise` in ledger_service, and came back as a 500.
# Migration e6a2b4c7d130 scopes the constraint to (farm_id, client_id).


def test_same_client_id_in_two_farms_creates_two_records(make_client):
    """The exact failure case: two farms, one shared client_id, no 500."""
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    shared = "seed-bioprocess-yield-0001"  # the seed script's fixed key shape

    first = _post_log(farm_a, activity_type="seed", amount=5000.0,
                      transaction_type="debit", client_id=shared)
    assert first.status_code == 201, first.text

    second = _post_log(farm_b, activity_type="seed", amount=7000.0,
                       transaction_type="debit", client_id=shared)
    # A genuine creation for farm B, not a 500 and not farm A's row handed back.
    assert second.status_code == 201, second.text
    assert second.json()["id"] != first.json()["id"]


def test_cross_farm_client_id_does_not_leak_the_other_farms_row(make_client):
    """Each farm sees exactly its own record, with its own amount."""
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    shared = "shared-offline-key-0001"

    _post_log(farm_a, activity_type="seed", amount=5000.0,
              transaction_type="debit", client_id=shared)
    _post_log(farm_b, activity_type="seed", amount=7000.0,
              transaction_type="debit", client_id=shared)

    a_logs = farm_a.get("/api/v1/ledger/logs").json()
    b_logs = farm_b.get("/api/v1/ledger/logs").json()
    assert len(a_logs) == 1
    assert len(b_logs) == 1
    assert a_logs[0]["id"] != b_logs[0]["id"]
    assert a_logs[0]["financial_transaction"]["amount"] == 5000.0
    assert b_logs[0]["financial_transaction"]["amount"] == 7000.0


def test_farm_scoped_idempotency_still_holds_after_the_constraint_change(make_client):
    """Widening the constraint must not widen idempotency: a replay within one
    farm is still 200-and-the-same-row, and it stays that way once a second farm
    holds the same key."""
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    shared = "replay-across-tenants-0001"

    created = _post_log(farm_a, activity_type="seed", amount=5000.0,
                        transaction_type="debit", client_id=shared)
    assert created.status_code == 201

    _post_log(farm_b, activity_type="seed", amount=7000.0,
              transaction_type="debit", client_id=shared)

    replay = _post_log(farm_a, activity_type="seed", amount=5000.0,
                       transaction_type="debit", client_id=shared)
    assert replay.status_code == 200
    assert replay.json()["id"] == created.json()["id"]
    # And no duplicate was booked on either side.
    assert len(farm_a.get("/api/v1/ledger/logs").json()) == 1
    assert len(farm_b.get("/api/v1/ledger/logs").json()) == 1


def test_a_null_client_id_is_exempt_from_the_composite_constraint(client):
    """Most logs carry no client_id at all. NULLs never compare equal, so any
    number of them coexist in one farm — a UNIQUE(farm_id, client_id) that
    collapsed them would break every non-offline write."""
    for _ in range(3):
        assert _post_log(client, activity_type="seed", amount=100.0,
                         transaction_type="debit").status_code == 201
    assert len(client.get("/api/v1/ledger/logs").json()) == 3


def test_maintenance_for_missing_equipment_returns_404(client):
    payload = {"equipment_id": 999999, "description": "Service on a ghost", "cost": 100.0}
    response = client.post("/api/v1/equipment/maintenance", json=payload)
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_maintenance_for_missing_equipment_returns_404(client):
    response = client.get("/api/v1/equipment/999999/maintenance")
    assert response.status_code == 404


def test_pnl_report_json(client):
    # Seed a fertilizer expense and a yield sale, then assert exact figures.
    _post_log(client, activity_type="fertilizer", amount=25000.0, transaction_type="debit")
    _post_log(client, activity_type="yield", amount=40000.0, transaction_type="credit")

    response = client.get("/api/v1/reports/pnl")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"revenue", "expenses", "gross_margin", "categories"}
    assert data["revenue"] == 40000.0
    assert data["expenses"] == 25000.0
    assert data["gross_margin"] == 15000.0
    # One breakdown row per Activity Category.
    assert len(data["categories"]) == 7
    fertilizer = next(c for c in data["categories"] if c["category"] == "fertilizer")
    assert fertilizer["expenses"] == 25000.0
    assert fertilizer["net"] == fertilizer["revenue"] - fertilizer["expenses"]


def test_pnl_monthly(client):
    response = client.get("/api/v1/reports/pnl/monthly")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    for point in data:
        assert set(point.keys()) == {"month", "revenue", "expenses"}


def test_pnl_report_csv(client):
    response = client.get("/api/v1/reports/pnl.csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    body = response.text
    assert "AgriProfit Profit & Loss Report" in body
    assert "Category,Revenue (NGN),Expenses (NGN),Net (NGN)" in body
    assert "Total" in body


def test_invalid_enum_activity(client):
    payload = {
        "activity_type": "invalid_category",
        "description": "This should fail"
    }
    response = client.post("/api/v1/ledger/logs", json=payload)
    assert response.status_code == 422 # Unprocessable Entity


# --- Authentication -------------------------------------------------------

def test_register_returns_token(anon_client):
    resp = anon_client.post(
        "/api/v1/auth/register",
        json={"email": "grower@test.example", "password": "secret-password", "farm_name": "Sunrise Farm"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_rejects_duplicate_email(anon_client):
    payload = {"email": "dupe@test.example", "password": "secret-password"}
    assert anon_client.post("/api/v1/auth/register", json=payload).status_code == 201
    # Second registration with the same email is a conflict, not a new account.
    assert anon_client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_login_success_and_wrong_password(anon_client):
    anon_client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.example", "password": "correct-horse"},
    )
    ok = anon_client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.example", "password": "correct-horse"},
    )
    assert ok.status_code == 200
    assert ok.json()["access_token"]

    bad = anon_client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.example", "password": "wrong-password"},
    )
    assert bad.status_code == 401


def test_password_is_hashed_not_plaintext(anon_client, db):
    from backend.app.models import models

    anon_client.post(
        "/api/v1/auth/register",
        json={"email": "hash@test.example", "password": "plaintext-secret"},
    )
    user = db.query(models.User).filter(models.User.email == "hash@test.example").first()
    assert user is not None
    # The stored credential is a bcrypt hash — never the plaintext.
    assert user.hashed_password != "plaintext-secret"
    assert user.hashed_password.startswith("$2")  # bcrypt hash prefix


def test_unauthenticated_request_rejected(anon_client):
    # Every domain endpoint now requires a bearer token.
    assert anon_client.get("/api/v1/ledger/logs").status_code == 401
    assert anon_client.get("/api/v1/reports/pnl").status_code == 401
    assert anon_client.get("/api/v1/dss/decision-support").status_code == 401
    assert anon_client.get("/api/v1/equipment/").status_code == 401


# --- Per-farm data boundary ----------------------------------------------

def test_ledger_isolation_between_farms(make_client):
    # Two tenants share one database; each must see only its own ledger.
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")

    assert _post_log(farm_a, activity_type="yield", amount=40000.0, transaction_type="credit").status_code == 201

    # Farm A sees its own row.
    a_logs = farm_a.get("/api/v1/ledger/logs").json()
    assert len(a_logs) == 1

    # Farm B sees nothing of Farm A's — not in logs, transactions, or summary.
    assert farm_b.get("/api/v1/ledger/logs").json() == []
    assert farm_b.get("/api/v1/ledger/transactions").json() == []
    b_summary = farm_b.get("/api/v1/ledger/summary").json()
    assert b_summary == {"revenue": 0.0, "expenses": 0.0, "gross_margin": 0.0}

    # And Farm A's P&L / DSS are unaffected by Farm B's empty ledger.
    assert farm_a.get("/api/v1/reports/pnl").json()["revenue"] == 40000.0
    assert farm_b.get("/api/v1/reports/pnl").json()["revenue"] == 0.0
    assert farm_b.get("/api/v1/dss/decision-support").json()["crops"] == []


def test_equipment_accepts_a_null_depreciation_rate(client):
    """An asset with no rate is a legitimate record, not a validation failure.
    It is excluded from the depreciation overlay and counted there — never
    charged at a rate nobody entered."""
    resp = client.post("/api/v1/equipment/", json={"name": "Unrated hoe", "purchase_price": 9000.0})
    assert resp.status_code == 201
    assert resp.json()["depreciation_rate"] is None

    body = client.get("/api/v1/dss/break-even-price").json()
    assert body["equipment_count"] == 1
    assert body["equipment_unrated_count"] == 1
    # Counted, and contributing nothing — not a small charge that would read as
    # a small true fixed cost.
    assert body["period_fixed_cost_ngn"] == pytest.approx(0.0)


@pytest.mark.parametrize("rate", [0, 0.0, -1.0, 100.1, 1000.0])
def test_equipment_rejects_a_rate_outside_the_percentage_band(client, rate):
    """0 < rate <= 100. Zero is refused because it is indistinguishable from
    unrated in the overlay, and a rate above 100%/yr writes the asset off in
    under a year, which straight-line depreciation cannot express."""
    resp = client.post(
        "/api/v1/equipment/",
        json={"name": "Bad rate", "purchase_price": 1000.0, "depreciation_rate": rate},
    )
    assert resp.status_code == 422


@pytest.mark.parametrize("rate", [0.01, 10.0, 100.0])
def test_equipment_accepts_rates_on_and_inside_the_band(client, rate):
    resp = client.post(
        "/api/v1/equipment/",
        json={"name": "Good rate", "purchase_price": 1000.0, "depreciation_rate": rate},
    )
    assert resp.status_code == 201
    assert resp.json()["depreciation_rate"] == pytest.approx(rate)


def test_equipment_purchase_date_round_trips(client):
    """The column and schema have always accepted it; nothing sent it until the
    form began collecting it."""
    resp = client.post(
        "/api/v1/equipment/",
        json={"name": "Dated dryer", "purchase_price": 1000.0, "purchase_date": "2026-03-01"},
    )
    assert resp.status_code == 201
    assert resp.json()["purchase_date"].startswith("2026-03-01")


def test_depreciation_rate_is_converted_to_a_fraction_exactly_once(client):
    """THE UNIT BOUNDARY. 10%/yr on 240,000 is 24,000 a year, not 24 and not
    2,400,000. The percentage crosses into a fraction in
    dss_service.depreciation_rate_as_fraction and nowhere else."""
    _seed_rated_equipment(client)
    body = client.get("/api/v1/dss/break-even-price?period_days=365").json()
    assert body["period_fixed_cost_ngn"] == pytest.approx(24000.0, rel=1e-9)
    assert body["equipment_unrated_count"] == 0


def test_equipment_isolation_cross_farm_read_rejected(make_client):
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")

    created = farm_a.post(
        "/api/v1/equipment/",
        json={"name": "Farm A Tractor", "purchase_price": 15000000.0, "depreciation_rate": 10.0},
    )
    assert created.status_code == 201
    eq_id = created.json()["id"]

    # Farm B cannot list Farm A's equipment...
    assert farm_b.get("/api/v1/equipment/").json() == []
    # ...nor read its maintenance (another farm's id is simply "not found").
    assert farm_b.get(f"/api/v1/equipment/{eq_id}/maintenance").status_code == 404
    # ...nor attach maintenance to it.
    cross = farm_b.post(
        "/api/v1/equipment/maintenance",
        json={"equipment_id": eq_id, "description": "sabotage", "cost": 1.0},
    )
    assert cross.status_code == 404

    # Farm A still owns and can service it.
    assert len(farm_a.get("/api/v1/equipment/").json()) == 1
    assert farm_a.get(f"/api/v1/equipment/{eq_id}/maintenance").status_code == 200


# --- Investor share links (ticket 05) ------------------------------------

def _seed_maize(client):
    # fertilizer debit 25,000; yield credit 40,000 over 12 bags.
    assert _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit").status_code == 201
    assert _post_crop_log(client, activity_type="yield", crop="maize", amount=40000.0, transaction_type="credit", quantity=12.0, unit="bags").status_code == 201


def test_share_link_mint_and_public_report(make_client, anon_client):
    farm = make_client(farm_name="Sunrise Farm")
    _seed_maize(farm)

    minted = farm.post("/api/v1/share/links", json={"label": "First Bank"})
    assert minted.status_code == 201
    body = minted.json()
    token = body["token"]
    # Opaque: long, and not the row id / a sequential integer.
    assert len(token) >= 40
    assert token != str(body["id"]) and not token.isdigit()

    # The list endpoint never re-serves the token, only metadata.
    listed = farm.get("/api/v1/share/links").json()
    assert len(listed) == 1
    assert "token" not in listed[0]
    assert listed[0]["label"] == "First Bank" and listed[0]["revoked"] is False

    # The public report needs no login — the token is the credential.
    report = anon_client.get(f"/api/v1/share/report/{token}")
    assert report.status_code == 200
    data = report.json()
    assert data["farm_name"] == "Sunrise Farm"
    assert data["pnl"]["revenue"] == 40000.0
    assert data["pnl"]["expenses"] == 25000.0
    assert data["pnl"]["gross_margin"] == 15000.0
    maize = next(c for c in data["crops"] if c["crop"] == "maize")
    assert maize["yield_quantity"] == 12.0
    assert maize["yield_unit"] == "bags"
    assert maize["gross_margin"] == 15000.0


def test_share_report_revoked_token_denied(make_client, anon_client):
    farm = make_client(farm_name="Sunrise Farm")
    _seed_maize(farm)
    minted = farm.post("/api/v1/share/links", json={}).json()
    token, link_id = minted["token"], minted["id"]

    # Works before revocation...
    assert anon_client.get(f"/api/v1/share/report/{token}").status_code == 200
    # ...revoke...
    revoked = farm.post(f"/api/v1/share/links/{link_id}/revoke")
    assert revoked.status_code == 200 and revoked.json()["revoked"] is True
    # ...and the link is dead.
    assert anon_client.get(f"/api/v1/share/report/{token}").status_code == 404


def test_share_link_isolation_between_farms(make_client, anon_client):
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    _seed_maize(farm_a)  # A: revenue 40,000 / expenses 25,000
    assert _post_crop_log(farm_b, activity_type="labour", crop="rice", amount=99999.0, transaction_type="debit").status_code == 201

    token_a = farm_a.post("/api/v1/share/links", json={}).json()["token"]

    # A's token returns A's data only — B's figures can never appear, because the
    # farm is derived from the token row, not from the request.
    data = anon_client.get(f"/api/v1/share/report/{token_a}").json()
    assert data["farm_name"] == "Farm A"
    assert data["pnl"]["revenue"] == 40000.0
    assert data["pnl"]["expenses"] == 25000.0  # not 25,000 + 99,999
    assert {c["crop"] for c in data["crops"]} == {"maize"}


def test_share_unauthenticated_cannot_mint(anon_client):
    assert anon_client.post("/api/v1/share/links", json={"label": "x"}).status_code == 401


def test_share_revoke_scoped_to_owner(make_client, anon_client):
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    _seed_maize(farm_a)
    minted = farm_a.post("/api/v1/share/links", json={}).json()
    token_a, link_id = minted["token"], minted["id"]

    # Farm B cannot revoke Farm A's link (another farm's id is "not found")...
    assert farm_b.post(f"/api/v1/share/links/{link_id}/revoke").status_code == 404
    # ...so A's link still works.
    assert anon_client.get(f"/api/v1/share/report/{token_a}").status_code == 200


def test_share_token_cannot_write_or_use_other_routes(make_client, anon_client):
    farm = make_client(farm_name="Sunrise Farm")
    _seed_maize(farm)
    token = farm.post("/api/v1/share/links", json={}).json()["token"]

    # A share token is not a login credential: presenting it as a bearer token
    # authenticates nothing, so no write (or read) domain route accepts it.
    write = anon_client.post(
        "/api/v1/ledger/logs",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "activity_type": "seed",
            "financial_data": {"amount": 1.0, "transaction_type": "debit", "category": "seed"},
        },
    )
    assert write.status_code == 401
    assert anon_client.get("/api/v1/ledger/logs", headers={"Authorization": f"Bearer {token}"}).status_code == 401

    # The public report route itself is read-only — no write method.
    assert anon_client.post(f"/api/v1/share/report/{token}").status_code == 405


# --- Config hardening: secret-key startup guard (ticket 08) ---------------

def test_default_secret_key_forbidden_in_production():
    from pydantic import ValidationError
    from backend.app.core.config import Settings, DEFAULT_SECRET_KEY

    # Booting a real (non dev/test) environment on the public default key must
    # fail fast rather than sign forgeable tokens with a key that is in the repo.
    with pytest.raises(ValidationError):
        Settings(secret_key=DEFAULT_SECRET_KEY, environment="production")


def test_default_secret_key_allowed_in_dev():
    from backend.app.core.config import Settings, DEFAULT_SECRET_KEY

    # Negative case: the public default is tolerated in dev (no real data at
    # risk), so this must NOT raise.
    s = Settings(secret_key=DEFAULT_SECRET_KEY, environment="dev")
    assert s.secret_key == DEFAULT_SECRET_KEY


def test_real_secret_key_allowed_in_production():
    from backend.app.core.config import Settings

    # Negative case: a real key in production is the intended state, so booting
    # must NOT raise.
    s = Settings(secret_key="a-strong-random-production-secret", environment="production")
    assert s.environment == "production"


# --- Registration input validation (ticket 08) ---------------------------

def test_register_rejects_invalid_email(anon_client):
    # EmailStr rejects a malformed address at validation (422) before it can
    # ever become an account identifier.
    resp = anon_client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "secret-password"},
    )
    assert resp.status_code == 422


# --- JWT verification: forged and expired tokens (ticket 09) --------------

def test_tampered_jwt_rejected(client):
    # A correctly-formed token whose signature has been altered must be rejected.
    # This proves protected routes verify the signature — not merely that *some*
    # bearer token is present — so a forged token can't impersonate a farm.
    valid = client.headers["Authorization"].split(" ", 1)[1]
    header, payload, signature = valid.split(".")
    # Flip the FIRST signature character, not the last.
    #
    # An HS256 signature is 32 bytes, which base64url-encodes to 43 characters
    # once padding is stripped. 43 x 6 = 258 bits carrying 256 bits of data, so
    # the LAST character contributes only 4 significant bits — its low 2 bits are
    # padding and are discarded on decode. Four of the 64 alphabet characters
    # therefore decode to the same byte as "A", so flipping the last character to
    # "A"/"B" left the signature bytes UNCHANGED for ~6.2% of tokens. The token
    # stayed valid, /auth/me correctly returned 200, and this test failed —
    # intermittently, roughly one run in sixteen.
    #
    # The first character carries all 6 of its bits, so flipping it always
    # changes the decoded signature. Zero collisions.
    forged_first = "A" if signature[0] != "A" else "B"
    tampered = f"{header}.{payload}.{forged_first}{signature[1:]}"

    # Guard the premise: if the tamper ever stops changing the decoded bytes,
    # fail here with a clear reason rather than as a confusing 200 != 401.
    def _decode(seg: str) -> bytes:
        return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))

    assert _decode(tampered.split(".")[2]) != _decode(signature), (
        "the tampered signature decodes to the same bytes as the valid one, "
        "so this test would be asserting nothing"
    )

    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered}"}
    )
    assert resp.status_code == 401


def test_expired_jwt_rejected(client):
    # A token signed with the *real* key but whose exp is in the past must be
    # rejected. This proves expiry is enforced independently of the signature —
    # a leaked-but-stale token can't be replayed indefinitely.
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    from backend.app.core.config import settings

    payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    resp = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}
    )
    assert resp.status_code == 401


# --- Ledger immutability + reversal (ticket 10) ---------------------------

def test_ledger_delete_is_blocked(client):
    # Ledger records are immutable: a hard DELETE of a log or its transaction is
    # refused with 405, pointing the caller at reversal instead.
    created = _post_log(client, activity_type="seed", amount=100.0, transaction_type="debit")
    assert created.status_code == 201
    log_id = created.json()["id"]
    tx_id = created.json()["financial_transaction_id"]

    assert client.delete(f"/api/v1/ledger/logs/{log_id}").status_code == 405
    assert client.delete(f"/api/v1/ledger/transactions/{tx_id}").status_code == 405


def test_reversal_nets_pnl_to_zero(client):
    # A standalone expense moves the margin; its reversal returns margin — and
    # the category's net — to zero, without deleting anything.
    created = _post_log(client, activity_type="fertilizer", amount=250.0, transaction_type="debit")
    log_id = created.json()["id"]

    before = client.get("/api/v1/ledger/summary").json()
    assert before["expenses"] == 250.0
    assert before["gross_margin"] == -250.0

    rev = client.post(f"/api/v1/ledger/logs/{log_id}/reverse")
    assert rev.status_code == 201
    assert rev.json()["reverses_id"] == log_id

    after = client.get("/api/v1/ledger/summary").json()
    assert after["gross_margin"] == 0.0
    # 10b: category-preserving contra — the reversal nets within its own pile,
    # so expenses return to zero (they are not offset by an inflated revenue).
    assert after["expenses"] == 0.0

    pnl = client.get("/api/v1/reports/pnl").json()
    fertilizer = next(c for c in pnl["categories"] if c["category"] == "fertilizer")
    assert fertilizer["net"] == 0.0
    assert fertilizer["expenses"] == 0.0


def test_original_and_reversal_both_readable(client):
    # Reversal is non-destructive: the original log AND the reversal entry both
    # remain visible, and the reversal is linked back to what it offsets.
    created = _post_log(client, activity_type="labour", amount=80.0, transaction_type="debit")
    log_id = created.json()["id"]
    rev = client.post(f"/api/v1/ledger/logs/{log_id}/reverse")
    rev_id = rev.json()["id"]

    logs = client.get("/api/v1/ledger/logs").json()
    ids = {log["id"] for log in logs}
    assert log_id in ids
    assert rev_id in ids

    reversal = next(log for log in logs if log["id"] == rev_id)
    assert reversal["reverses_id"] == log_id


def test_reversal_rejected_across_farms(make_client):
    # A farm cannot reverse another farm's log — the log isn't even visible to
    # it, so the attempt is a 404 (the tenant boundary, not a special-case).
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    created = _post_log(farm_a, activity_type="seed", amount=100.0, transaction_type="debit")
    a_log_id = created.json()["id"]

    resp = farm_b.post(f"/api/v1/ledger/logs/{a_log_id}/reverse")
    assert resp.status_code == 404


def test_double_reversal_rejected(client):
    # Reversing an already-reversed log (or a reversal entry itself) would
    # over-correct the ledger, so both are refused with 409.
    created = _post_log(client, activity_type="seed", amount=100.0, transaction_type="debit")
    log_id = created.json()["id"]

    first = client.post(f"/api/v1/ledger/logs/{log_id}/reverse")
    assert first.status_code == 201

    assert client.post(f"/api/v1/ledger/logs/{log_id}/reverse").status_code == 409

    rev_id = first.json()["id"]
    assert client.post(f"/api/v1/ledger/logs/{rev_id}/reverse").status_code == 409


# --- Category-preserving reversal (ticket 10b) ---------------------------

def test_reversal_leaves_revenue_untouched(client):
    # 10b: reversing an expense nets that category's expenses to zero while
    # revenue (a different pile) is left exactly as it was — the contra is the
    # SAME type (debit), so it subtracts from expenses, not from revenue.
    _post_log(client, activity_type="yield", amount=5000.0, transaction_type="credit")
    expense = _post_log(client, activity_type="fertilizer", amount=2000.0, transaction_type="debit")
    exp_id = expense.json()["id"]

    before = client.get("/api/v1/ledger/summary").json()
    assert before == {"revenue": 5000.0, "expenses": 2000.0, "gross_margin": 3000.0}

    rev = client.post(f"/api/v1/ledger/logs/{exp_id}/reverse")
    assert rev.status_code == 201
    assert rev.json()["financial_transaction"]["transaction_type"] == "debit"  # same type

    after = client.get("/api/v1/ledger/summary").json()
    assert after["revenue"] == 5000.0    # untouched
    assert after["expenses"] == 0.0      # netted within its own pile
    assert after["gross_margin"] == 5000.0

    pnl = client.get("/api/v1/reports/pnl").json()
    fert = next(c for c in pnl["categories"] if c["category"] == "fertilizer")
    assert fert["expenses"] == 0.0
    assert fert["revenue"] == 0.0
    assert fert["net"] == 0.0


def test_reversal_of_income_leaves_expenses_untouched(client):
    # 10b mirror: reversing an income nets revenue to zero, expenses untouched.
    _post_log(client, activity_type="fertilizer", amount=2000.0, transaction_type="debit")
    income = _post_log(client, activity_type="yield", amount=5000.0, transaction_type="credit")
    inc_id = income.json()["id"]

    rev = client.post(f"/api/v1/ledger/logs/{inc_id}/reverse")
    assert rev.status_code == 201
    assert rev.json()["financial_transaction"]["transaction_type"] == "credit"  # same type

    after = client.get("/api/v1/ledger/summary").json()
    assert after["expenses"] == 2000.0   # untouched
    assert after["revenue"] == 0.0       # netted within its own pile
    assert after["gross_margin"] == -2000.0


def test_monthly_pnl_nets_reversal_in_month(client):
    # 10b: the monthly series nets a reversal the same way, within its own month
    # and its own pile (Python-side bucketing, no SQL date functions).
    expense = _post_log(client, activity_type="fertilizer", amount=2000.0, transaction_type="debit")
    _post_log(client, activity_type="yield", amount=5000.0, transaction_type="credit")
    exp_id = expense.json()["id"]

    current = client.get("/api/v1/reports/pnl/monthly").json()[-1]  # window ends this month
    assert current["expenses"] == 2000.0
    assert current["revenue"] == 5000.0

    assert client.post(f"/api/v1/ledger/logs/{exp_id}/reverse").status_code == 201

    current2 = client.get("/api/v1/reports/pnl/monthly").json()[-1]
    assert current2["expenses"] == 0.0    # reversal subtracted in-month
    assert current2["revenue"] == 5000.0  # untouched


# --- Bioprocess drying: schema validation (ticket 08, Fixture D) ----------
# Every malformed drying payload must be rejected at the schema edge with 422,
# never reach the service and 500. Validation is conditional on
# activity_type == bioprocess; all other activity types keep extra_data as an
# arbitrary, unvalidated dict.

def _valid_drying() -> dict:
    """A physically consistent drying payload (Fixture A inputs); each test
    mutates exactly one field so the 422 is attributable to that field alone."""
    return {
        "process_type": "DRYING",
        "method": "SUN",
        "mass_in_kg": 100.0,
        "mass_out_kg": 84.0,
        "moisture_initial_wb": 25.0,
        "moisture_final_wb": 13.0,
        "drying_time_hours": 10.0,
    }


def _post_bioprocess(client, extra_data: dict):
    payload = {
        "activity_type": "bioprocess",
        "description": "maize drying run",
        "crop": "maize",
        "extra_data": extra_data,
        # A bioprocess log is still paired with a transaction (0.00 for sun
        # drying with own labour); the drying validation is what's under test.
        "financial_data": {"amount": 0.0, "transaction_type": "debit", "category": "bioprocess"},
    }
    return client.post("/api/v1/ledger/logs", json=payload)


def test_bioprocess_valid_payload_accepted(client):
    # Positive control: the baseline payload is accepted and stored intact, so a
    # 422 below is caused by the mutation, not a broken baseline.
    resp = _post_bioprocess(client, _valid_drying())
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"]["process_type"] == "DRYING"
    assert resp.json()["extra_data"]["mass_out_kg"] == 84.0


def test_bioprocess_missing_payload_rejected(client):
    # A bioprocess log with no drying parameters at all is invalid (422).
    payload = {
        "activity_type": "bioprocess",
        "description": "no params",
        "financial_data": {"amount": 0.0, "transaction_type": "debit", "category": "bioprocess"},
    }
    assert client.post("/api/v1/ledger/logs", json=payload).status_code == 422


def test_bioprocess_mass_out_exceeds_mass_in_rejected(client):
    d = _valid_drying(); d["mass_out_kg"] = 110.0  # > mass_in_kg (100) — mass gain
    assert _post_bioprocess(client, d).status_code == 422


def test_bioprocess_final_moisture_not_below_initial_rejected(client):
    # moisture_final_wb >= moisture_initial_wb is wetting, not drying.
    d = _valid_drying(); d["moisture_initial_wb"] = 20.0; d["moisture_final_wb"] = 25.0
    assert _post_bioprocess(client, d).status_code == 422


def test_bioprocess_nonpositive_mass_rejected(client):
    d = _valid_drying(); d["mass_in_kg"] = -5.0
    assert _post_bioprocess(client, d).status_code == 422
    d = _valid_drying(); d["mass_out_kg"] = 0.0
    assert _post_bioprocess(client, d).status_code == 422


def test_bioprocess_moisture_out_of_range_rejected(client):
    d = _valid_drying(); d["moisture_initial_wb"] = 105.0  # outside 0 < M < 100
    assert _post_bioprocess(client, d).status_code == 422


def test_bioprocess_readings_not_strictly_increasing_rejected(client):
    d = _valid_drying()
    # Times out of order (4h before 2h); moisture values are within the band, so
    # only the ordering rule fires.
    d["readings"] = [
        {"time_hours": 4.0, "moisture_wb": 18.0},
        {"time_hours": 2.0, "moisture_wb": 20.0},
    ]
    assert _post_bioprocess(client, d).status_code == 422


def test_bioprocess_reading_outside_moisture_band_rejected(client):
    d = _valid_drying()  # band is [13.0, 25.0]
    d["readings"] = [{"time_hours": 2.0, "moisture_wb": 30.0}]  # above initial
    assert _post_bioprocess(client, d).status_code == 422


def test_non_bioprocess_log_keeps_arbitrary_extra_data(client):
    # The critical no-regression guarantee: a non-bioprocess log carrying an
    # arbitrary extra_data dict still succeeds and is stored unchanged. Drying
    # validation must never touch it.
    arbitrary = {"whatever": 123, "nested": {"a": [1, 2, 3]}, "note": "free-form"}
    payload = {
        "activity_type": "fertilizer",
        "description": "arbitrary extra_data",
        "extra_data": arbitrary,
        "financial_data": {"amount": 100.0, "transaction_type": "debit", "category": "fertilizer"},
    }
    resp = client.post("/api/v1/ledger/logs", json=payload)
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"] == arbitrary


# --- Mechanisation cost classification: schema validation (Fixture H) ------
# The taxonomy is enforced at the schema edge on the existing extra_data JSON
# column: no ledger column, no migration. Validation is conditional on
# activity_type == mechanization, exactly as drying validation is conditional on
# bioprocess; every other activity type keeps extra_data arbitrary. Classifying
# is opt-in, so a mechanisation log with no extra_data at all is still accepted
# and is simply unclassified.

def _valid_mechanization() -> dict:
    """A well-formed mechanisation cost payload; each test below mutates exactly
    one field so the 422 is attributable to that field alone."""
    return {"cost_subtype": "FUEL", "equipment_id": 1, "hours_used": 4.5}


def _post_mechanization(client, extra_data):
    payload = {
        "activity_type": "mechanization",
        "description": "diesel for the ridger",
        "crop": "maize",
        "extra_data": extra_data,
        "financial_data": {"amount": 3000.0, "transaction_type": "debit", "category": "mechanization"},
    }
    return client.post("/api/v1/ledger/logs", json=payload)


def test_mechanization_valid_payload_accepted(client):
    # Positive control: the baseline payload is accepted and stored intact, so a
    # 422 below is caused by the mutation, not a broken baseline.
    resp = _post_mechanization(client, _valid_mechanization())
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"]["cost_subtype"] == "FUEL"
    assert resp.json()["extra_data"]["hours_used"] == 4.5


def test_mechanization_params_are_captured_and_round_trip_intact(client):
    """equipment_id and hours_used are capture-only fields with no consumer
    (see MechanizationParams and docs/STATE_REPORT_2026-08-25.md Section 10.3).
    Their whole contract is that they are validated and persisted unchanged, so
    that is what is pinned here — including that they survive a read-back rather
    than only a create response, and that cost_subtype is the ONLY one of the
    three that moves a derived figure."""
    resp = _post_mechanization(client, _valid_mechanization())
    assert resp.status_code == 201, resp.text
    log_id = resp.json()["id"]

    stored = next(l for l in client.get("/api/v1/ledger/logs").json() if l["id"] == log_id)
    assert stored["extra_data"] == {"cost_subtype": "FUEL", "equipment_id": 1, "hours_used": 4.5}

    # And the cost structure is driven by cost_subtype alone: FUEL is VARIABLE,
    # so the row's money is in the variable bucket and fully classified. Neither
    # equipment_id nor hours_used appears anywhere in the derived response.
    body = client.get("/api/v1/dss/cost-structure?crop=maize").json()
    crop = body["crops"][0]
    assert crop["variable_cost"] == 3000.0
    assert crop["classification_coverage_pct"] == 100.0
    assert "equipment_id" not in str(body)
    assert "hours_used" not in str(body)


def test_mechanization_omitting_the_capture_only_fields_is_accepted(client):
    """Both are optional. A farmer classifying a cost without naming an asset or
    counting hours must not be forced to invent either."""
    resp = _post_mechanization(client, {"cost_subtype": "MACHINERY_HIRE"})
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"] == {"cost_subtype": "MACHINERY_HIRE"}


def test_mechanization_unrecognised_cost_subtype_rejected(client):
    # A subtype outside the taxonomy is rejected rather than silently stored as
    # unclassified: a typo must not become a missing classification.
    d = _valid_mechanization(); d["cost_subtype"] = "PETROL"
    assert _post_mechanization(client, d).status_code == 422


def test_mechanization_hours_used_out_of_range_rejected(client):
    d = _valid_mechanization(); d["hours_used"] = 0        # must be > 0
    assert _post_mechanization(client, d).status_code == 422
    d = _valid_mechanization(); d["hours_used"] = 1001     # must be <= 1000
    assert _post_mechanization(client, d).status_code == 422


def test_non_mechanization_log_keeps_arbitrary_extra_data(client):
    # The no-regression guarantee, restated for the cost taxonomy: a seed log
    # carrying an arbitrary extra_data dict still succeeds and is stored
    # unchanged. Mechanisation validation must never touch it.
    arbitrary = {"cost_subtype": "NOT_A_REAL_SUBTYPE", "hours_used": -3, "free": [1, 2]}
    payload = {
        "activity_type": "seed",
        "description": "arbitrary extra_data on a seed log",
        "extra_data": arbitrary,
        "financial_data": {"amount": 5000.0, "transaction_type": "debit", "category": "seed"},
    }
    resp = client.post("/api/v1/ledger/logs", json=payload)
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"] == arbitrary


def test_mechanization_without_extra_data_accepted_and_unclassified(client):
    # Legacy rows carry no extra_data. Refusing them would break a shipped write
    # path, so absence is accepted and classifies as None — never defaulted to
    # VARIABLE, which would be indistinguishable from a recorded classification.
    from backend.app.core.enums import Category
    from backend.app.schemas.schemas import cost_behaviour_for

    resp = _post_mechanization(client, None)
    assert resp.status_code == 201, resp.text
    assert resp.json()["extra_data"] is None
    assert cost_behaviour_for(Category.MECHANIZATION, None) is None


# --- Bioprocess drying: read + aggregate endpoints (ticket 08, Phase 4) ----
# Drying runs are created through the single existing write path
# (POST /ledger/logs); the /bioprocess routes only read them back.

def _drying_extra(**overrides) -> dict:
    d = {
        "process_type": "DRYING", "method": "SUN",
        "mass_in_kg": 100.0, "mass_out_kg": 84.0,
        "moisture_initial_wb": 25.0, "moisture_final_wb": 13.0,
        "drying_time_hours": 10.0,
    }
    d.update(overrides)
    return d


def _post_drying(client, *, crop="maize", amount=0.0, extra=None):
    payload = {
        "activity_type": "bioprocess",
        "description": f"{crop} drying run",
        "crop": crop,
        "extra_data": extra if extra is not None else _drying_extra(),
        "financial_data": {"amount": amount, "transaction_type": "debit", "category": "bioprocess"},
    }
    return client.post("/api/v1/ledger/logs", json=payload)


def test_bioprocess_create_zero_cost_still_pairs_transaction(client):
    # Sun drying with own labour costs nothing, but the paired transaction is
    # still created at 0.00 so the pairing invariant is never violated.
    r = _post_drying(client, amount=0.0)
    assert r.status_code == 201, r.text
    assert r.json()["financial_transaction_id"] is not None
    tx = r.json()["financial_transaction"]
    assert tx["amount"] == 0.0
    assert tx["transaction_type"] == "debit"
    assert tx["category"] == "bioprocess"


def test_bioprocess_detail_returns_params_and_metrics(client):
    # Fixture A inputs, surfaced through the API: the detail view carries the
    # stored params plus every derived metric.
    created = _post_drying(client, crop="maize", extra=_drying_extra())
    log_id = created.json()["id"]

    resp = client.get(f"/api/v1/bioprocess/{log_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == log_id
    assert data["crop"] == "maize"
    assert data["params"]["mass_in_kg"] == 100.0
    m = data["metrics"]
    assert m["dry_matter_kg"] == pytest.approx(75.0, rel=1e-4)
    assert m["process_loss_kg"] == pytest.approx(2.2069, rel=1e-4)
    # Water balance: 100*0.25 - 84*0.13 = 25.00 - 10.92 = 14.08 kg.
    assert m["water_removed_kg"] == pytest.approx(14.08, rel=1e-4)
    assert m["newton_k"] == pytest.approx(0.080235, rel=1e-4)
    assert m["safe_storage"] is True
    assert m["page"] is None


def test_bioprocess_detail_cross_farm_is_404(make_client):
    # Fixture E: another farm's drying run is simply not found.
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    log_id = _post_drying(farm_a).json()["id"]

    assert farm_b.get(f"/api/v1/bioprocess/{log_id}").status_code == 404
    assert farm_a.get(f"/api/v1/bioprocess/{log_id}").status_code == 200


def test_bioprocess_detail_non_bioprocess_log_is_404(client):
    # A non-bioprocess log is not a drying run.
    created = _post_log(client, activity_type="fertilizer", amount=100.0, transaction_type="debit")
    assert client.get(f"/api/v1/bioprocess/{created.json()['id']}").status_code == 404


def test_bioprocess_detail_on_reversal_contra_is_404(client):
    # A reversal contra carries no drying payload, so it is not a drying run.
    created = _post_drying(client, crop="maize")
    rev = client.post(f"/api/v1/ledger/logs/{created.json()['id']}/reverse")
    assert rev.status_code == 201
    assert client.get(f"/api/v1/bioprocess/{rev.json()['id']}").status_code == 404


def test_bioprocess_summary_aggregates_per_crop(client):
    _post_drying(client, crop="maize", extra=_drying_extra())
    _post_drying(client, crop="maize", extra=_drying_extra(mass_in_kg=200.0, mass_out_kg=168.0))

    resp = client.get("/api/v1/bioprocess/summary")
    assert resp.status_code == 200
    crops = {c["crop"]: c for c in resp.json()["crops"]}
    assert set(crops) == {"maize"}
    maize = crops["maize"]
    assert maize["drying_runs"] == 2
    assert maize["total_mass_in_kg"] == pytest.approx(300.0)
    assert maize["total_marketable_mass_kg"] == pytest.approx(84.0 + 168.0)
    # Water balance per run, then summed. Run 1: 25.00 - 10.92 = 14.08.
    # Run 2 is exactly double the mass: 50.00 - 21.84 = 28.16.
    assert maize["total_water_removed_kg"] == pytest.approx(14.08 + 28.16)
    assert maize["safe_storage_share"] == pytest.approx(1.0)  # both final 13.0 <= 13.0
    assert "SUN" in maize["mean_newton_k_by_method"]


def test_bioprocess_summary_excludes_reversed_run(client):
    # Fixture E: a reversed drying run drops out of the aggregate entirely (both
    # the reversal contra and the reversed original are excluded).
    maize = _post_drying(client, crop="maize")
    _post_drying(client, crop="rice",
                 extra=_drying_extra(moisture_initial_wb=22.0, moisture_final_wb=13.5, mass_out_kg=90.0))

    rev = client.post(f"/api/v1/ledger/logs/{maize.json()['id']}/reverse")
    assert rev.status_code == 201

    crops = {c["crop"]: c for c in client.get("/api/v1/bioprocess/summary").json()["crops"]}
    assert "maize" not in crops          # reversed -> excluded
    assert crops["rice"]["drying_runs"] == 1
    assert crops["rice"]["safe_storage_share"] == pytest.approx(1.0)  # 13.5 <= 14.0


def test_bioprocess_summary_crop_filter(client):
    _post_drying(client, crop="maize")
    _post_drying(client, crop="rice",
                 extra=_drying_extra(moisture_initial_wb=22.0, moisture_final_wb=13.5, mass_out_kg=90.0))

    crops = {c["crop"] for c in client.get("/api/v1/bioprocess/summary?crop=maize").json()["crops"]}
    assert crops == {"maize"}


# --- DSS coupling: reversal netting + marketable-mass metric (ticket 08, Phase 5)

def _dss_crops(client) -> dict:
    return {c["crop"]: c for c in client.get("/api/v1/dss/decision-support").json()["crops"]}


def test_dss_reversed_crop_expense_no_unspecified_bucket(client):
    # (a) Reversing a crop expense nets within that crop — no phantom
    # "Unspecified" bucket. The contra is attributed to the original's crop,
    # which nets maize to nothing, so maize drops out as an empty bucket too
    # (see test_dss_fully_reversed_crop_is_omitted).
    exp = _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit")
    assert _dss_crops(client)["maize"]["expenses"] == 25000.0

    rev = client.post(f"/api/v1/ledger/logs/{exp.json()['id']}/reverse")
    assert rev.status_code == 201

    after = _dss_crops(client)
    assert "Unspecified" not in after
    assert after == {}


def test_dss_reversed_yield_restores_quantity_and_unit_cost(client):
    # (b) Reversing a yield removes its quantity from the denominator, so
    # unit_cost is recomputed (here back to None) rather than silently shifting.
    _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit")
    y = _post_crop_log(client, activity_type="yield", crop="maize", amount=40000.0, transaction_type="credit", quantity=12.0, unit="bags")

    before = _dss_crops(client)["maize"]
    assert before["yield_quantity"] == 12.0
    assert before["unit_cost_of_production"] == pytest.approx(25000.0 / 12.0)

    assert client.post(f"/api/v1/ledger/logs/{y.json()['id']}/reverse").status_code == 201

    after = _dss_crops(client)["maize"]
    assert after["yield_quantity"] == 0.0                 # quantity left the denominator
    assert after["unit_cost_of_production"] is None       # no yield -> no divide
    assert after["revenue"] == 0.0                        # credit reversed
    assert after["expenses"] == 25000.0                   # expenses untouched


def test_dss_crop_with_drying_reports_both_unit_costs(client):
    # (c) A crop with drying runs reports BOTH unit costs, each with one unit,
    # and their values differ so the two denominators can never be merged.
    _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize", amount=40000.0, transaction_type="credit", quantity=12.0, unit="bags")
    _post_drying(client, crop="maize", amount=3500.0, extra=_drying_extra())  # mass_out 84.0

    m = _dss_crops(client)["maize"]
    assert m["expenses"] == pytest.approx(28500.0)  # includes the 3500 drying cost
    assert m["yield_quantity"] == 12.0
    # Unchanged metric: currency per harvest unit (bags).
    assert m["unit_cost_of_production"] == pytest.approx(28500.0 / 12.0)
    # New metric: currency per kg marketable (84 kg).
    assert m["marketable_mass_kg"] == pytest.approx(84.0)
    assert m["unit_cost_per_kg_marketable"] == pytest.approx(28500.0 / 84.0)
    assert m["unit_cost_of_production"] != pytest.approx(m["unit_cost_per_kg_marketable"])


def test_dss_crop_without_drying_runs_unchanged(client):
    # (d) A crop with no drying runs: both new fields null, unit_cost unchanged.
    _post_crop_log(client, activity_type="fertilizer", crop="sorghum", amount=5000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="sorghum", amount=8000.0, transaction_type="credit", quantity=4.0, unit="bags")

    m = _dss_crops(client)["sorghum"]
    assert m["unit_cost_of_production"] == pytest.approx(5000.0 / 4.0)
    assert m["marketable_mass_kg"] is None
    assert m["unit_cost_per_kg_marketable"] is None


def test_dss_reversed_only_drying_run_no_division_error(client):
    # (e) Reversing the only drying run leaves marketable mass empty and the
    # per-kg cost null — a guarded division, not 0 or infinity.
    d = _post_drying(client, crop="maize", amount=3500.0, extra=_drying_extra())
    assert _dss_crops(client)["maize"]["marketable_mass_kg"] == pytest.approx(84.0)

    assert client.post(f"/api/v1/ledger/logs/{d.json()['id']}/reverse").status_code == 201

    # The run was maize's only record, so the bucket is now empty and omitted.
    # The point of the test still holds: the guarded division is never reached
    # with a zero denominator, and the response is assembled without error.
    resp = client.get("/api/v1/dss/decision-support")
    assert resp.status_code == 200
    assert "maize" not in {c["crop"] for c in resp.json()["crops"]}


# --- Empty-bucket filtering: a crop with nothing left in it is not a row -----

def test_dss_fully_reversed_crop_is_omitted(client):
    """A crop whose every record has been reversed disappears entirely.

    It nets to no money and no yield, so rendering it as a row of zeros would
    imply activity that no longer stands. This is the "Unspecified" case in the
    field: untagged records collect there and empty it out once corrected.
    """
    exp = _post_crop_log(client, activity_type="fertilizer", crop="maize",
                         amount=25000.0, transaction_type="debit")
    sale = _post_crop_log(client, activity_type="yield", crop="maize",
                          amount=25000.0, transaction_type="credit",
                          quantity=100.0, unit="kg")

    before = _dss_crops(client)["maize"]
    assert before["revenue"] == 25000.0
    assert before["expenses"] == 25000.0
    assert before["yield_quantity"] == 100.0

    assert client.post(f"/api/v1/ledger/logs/{exp.json()['id']}/reverse").status_code == 201
    assert client.post(f"/api/v1/ledger/logs/{sale.json()['id']}/reverse").status_code == 201

    after = _dss_crops(client)
    assert "maize" not in after
    assert after == {}          # and it does not reappear under any other key


def test_dss_zero_margin_crop_is_kept(client):
    """Equal revenue and cost is a REAL result, not an empty bucket.

    The filter tests revenue and expenses separately and never tests gross
    margin, precisely so this crop survives: breaking even is a finding a
    farmer needs to see, and it is arithmetically indistinguishable from a
    fully-reversed crop if you only look at the margin.
    """
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=25000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=25000.0, transaction_type="credit",
                   quantity=100.0, unit="kg")

    crops = _dss_crops(client)
    assert "maize" in crops
    assert crops["maize"]["gross_margin"] == 0.0     # the zero that must survive
    assert crops["maize"]["revenue"] == 25000.0
    assert crops["maize"]["expenses"] == 25000.0


def test_dss_zero_margin_crop_with_no_yield_is_kept(client):
    """Zero margin with no yield recorded at all still survives.

    Guards the filter against being loosened to "no yield means empty": the
    money is real here even though nothing has been harvested yet.
    """
    _post_crop_log(client, activity_type="fertilizer", crop="rice",
                   amount=10000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="other", crop="rice",
                   amount=10000.0, transaction_type="credit")

    crops = _dss_crops(client)
    assert "rice" in crops
    assert crops["rice"]["gross_margin"] == 0.0
    assert crops["rice"]["yield_by_unit"] == []


def test_dss_crop_kept_when_only_yield_remains(client):
    """Yield alone keeps a bucket alive even when the money nets to zero.

    A reversed sale leaves the harvest quantity standing (the contra carries no
    quantity), and that recorded output is still a fact worth showing.
    """
    sale = _post_crop_log(client, activity_type="yield", crop="sorghum",
                          amount=8000.0, transaction_type="credit",
                          quantity=40.0, unit="bags")
    _post_crop_log(client, activity_type="yield", crop="sorghum",
                   amount=0.0, transaction_type="credit",
                   quantity=15.0, unit="bags")

    assert client.post(f"/api/v1/ledger/logs/{sale.json()['id']}/reverse").status_code == 201

    crops = _dss_crops(client)
    assert "sorghum" in crops                        # kept: yield remains
    assert crops["sorghum"]["revenue"] == 0.0
    assert crops["sorghum"]["yield_quantity"] == 15.0


def test_dss_zero_cost_drying_run_survives_the_filter(client):
    """A free sun-drying run is real processing data, not an empty bucket.

    Sun drying with the farm's own labour is the normal case, and it is
    recorded at 0.00 (the paired transaction still exists — see
    test_bioprocess_create_zero_cost_still_pairs_transaction). Such a crop has
    no revenue, no expenses and no harvest quantity, so the money-and-yield
    test alone would delete it along with its marketable mass.
    """
    r = _post_drying(client, crop="cassava", amount=0.0)
    assert r.status_code == 201, r.text

    crops = _dss_crops(client)
    assert "cassava" in crops                                   # kept by mass alone
    c = crops["cassava"]
    assert c["revenue"] == 0.0
    assert c["expenses"] == 0.0
    assert c["gross_margin"] == 0.0
    assert c["yield_by_unit"] == []                             # nothing harvested here
    assert c["marketable_mass_kg"] == pytest.approx(84.0)       # the reason it survives
    # No cost to divide, so the per-kg cost is a guarded 0.0/None, never junk.
    assert c["unit_cost_per_kg_marketable"] in (None, 0.0)


# --- Ranking: best-performing crop first ------------------------------------

def _dss_order(client) -> list:
    return [c["crop"] for c in client.get("/api/v1/dss/decision-support").json()["crops"]]


def test_dss_crops_ranked_by_gross_margin_desc(client):
    """Three distinct margins come back highest-first, not alphabetically.

    Seeded deliberately so that alphabetical order (cassava, maize, sorghum)
    and margin order (sorghum, maize, cassava) are exact opposites — an
    alphabetical regression cannot pass this by accident.
    """
    # cassava: +2,000   maize: +5,000   sorghum: +9,000
    _post_crop_log(client, activity_type="yield", crop="cassava", amount=2000.0, transaction_type="credit")
    _post_crop_log(client, activity_type="yield", crop="maize", amount=5000.0, transaction_type="credit")
    _post_crop_log(client, activity_type="yield", crop="sorghum", amount=9000.0, transaction_type="credit")

    assert _dss_order(client) == ["sorghum", "maize", "cassava"]


def test_dss_equal_margins_break_ties_alphabetically(client):
    """Equal margins fall back to crop name ascending, so the order is total.

    Posted in reverse alphabetical order to prove the result comes from the
    sort key and not from insertion order.
    """
    for crop in ("soybean", "rice", "maize"):
        _post_crop_log(client, activity_type="yield", crop=crop, amount=4000.0, transaction_type="credit")

    order = _dss_order(client)
    assert order == ["maize", "rice", "soybean"]
    margins = {c["crop"]: c["gross_margin"] for c in client.get("/api/v1/dss/decision-support").json()["crops"]}
    assert set(margins.values()) == {4000.0}      # the tie is real, not an artefact


# --- Break-even yield: retrospective, guarded, never fabricated -------------

def test_dss_break_even_yield_normal_case(client):
    """Costs 6,000; sold 100 kg for 10,000 -> price 100/kg -> break-even 60 kg."""
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=6000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=10000.0, transaction_type="credit",
                   quantity=100.0, unit="kg")

    c = _dss_crops(client)["maize"]
    assert c["break_even_yield"] == pytest.approx(60.0)
    assert c["break_even_unit"] == "kg"
    # Sanity: they sold more than break-even, hence a positive margin.
    assert c["yield_quantity"] > c["break_even_yield"]
    assert c["gross_margin"] == 4000.0


def test_dss_break_even_null_on_mixed_units(client):
    """Mixed units leave no single quantity to price against."""
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=6000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=5000.0, transaction_type="credit", quantity=100.0, unit="kg")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=5000.0, transaction_type="credit", quantity=12.0, unit="bags")

    c = _dss_crops(client)["maize"]
    assert c["yield_quantity"] is None          # the precondition
    assert c["break_even_yield"] is None
    assert c["break_even_unit"] is None


def test_dss_break_even_null_on_zero_revenue(client):
    """No sale means no realised price, so break-even is unknowable — not
    infinite, and not zero."""
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=6000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=0.0, transaction_type="credit", quantity=100.0, unit="kg")

    c = _dss_crops(client)["maize"]
    assert c["revenue"] == 0.0
    assert c["yield_quantity"] == 100.0         # harvested, but unsold
    assert c["break_even_yield"] is None
    assert c["break_even_unit"] is None


def test_dss_break_even_null_on_zero_yield(client):
    """Revenue with nothing harvested recorded: no quantity to price."""
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=6000.0, transaction_type="debit")
    _post_crop_log(client, activity_type="yield", crop="maize",
                   amount=10000.0, transaction_type="credit")   # no quantity

    c = _dss_crops(client)["maize"]
    assert c["yield_quantity"] == 0.0
    assert c["break_even_yield"] is None
    assert c["break_even_unit"] is None


def test_dss_break_even_reflects_reversal(client):
    """A reversed sale removes the realised price, so break-even reverts to None
    rather than lingering on a price that no longer stands."""
    _post_crop_log(client, activity_type="fertilizer", crop="maize",
                   amount=6000.0, transaction_type="debit")
    sale = _post_crop_log(client, activity_type="yield", crop="maize",
                          amount=10000.0, transaction_type="credit",
                          quantity=100.0, unit="kg")
    assert _dss_crops(client)["maize"]["break_even_yield"] == pytest.approx(60.0)

    assert client.post(f"/api/v1/ledger/logs/{sale.json()['id']}/reverse").status_code == 201

    c = _dss_crops(client)["maize"]
    assert c["revenue"] == 0.0
    assert c["break_even_yield"] is None


def test_dss_break_even_null_on_zero_expenses(client):
    """No attributed cost means there is nothing to recover.

    The arithmetic would yield 0, which is true but misleading: it reads as
    "you broke even on your first kilogram" when it actually means no cost has
    been tagged to this crop. Undefined is the honest answer.
    """
    _post_crop_log(client, activity_type="yield", crop="rice",
                   amount=20000.0, transaction_type="credit",
                   quantity=50.0, unit="kg")

    c = _dss_crops(client)["rice"]
    assert c["expenses"] == 0.0
    assert c["revenue"] == 20000.0      # revenue and yield both present
    assert c["yield_quantity"] == 50.0
    assert c["break_even_yield"] is None    # ...but nothing to break even on
    assert c["break_even_unit"] is None


# --- GET /dss/model: the honesty guarantee Chapter 4 leans on ---------------
# Three states: unauthenticated, trained, and NOT trained. The untrained branch
# is the one that matters: Chapters 2 (§2.6.4) and 3 (§3.6.5) both state that
# model quality "is expressed" as R² and MAE, and the prediction page renders
# those figures. If an untrained model reported zero-valued metrics instead of
# saying it is untrained, the page would show "R² 0.0000" — which reads as a
# uselessly bad model rather than as no model at all. That distinction is the
# whole point, and until now it had no test.

def test_dss_model_requires_authentication(anon_client):
    """State 1: no token, no metadata. Model quality is farm-agnostic but the
    route is still behind auth like every other endpoint."""
    assert anon_client.get("/api/v1/dss/model").status_code == 401


def test_dss_model_reports_metrics_when_trained(client):
    """State 2: trained. R² and MAE are present, numeric, and in range."""
    # /predict trains on first use if no model exists, so this guarantees one.
    assert client.post("/api/v1/dss/predict", json={
        "rainfall": 1200, "fertilizer_used": 50, "soil_ph": 6.5, "crop": "maize",
    }).status_code == 200

    body = client.get("/api/v1/dss/model").json()
    assert body["trained"] is True
    assert "metrics" in body

    r2, mae = body["metrics"]["r2"], body["metrics"]["mae"]
    assert isinstance(r2, (int, float)) and isinstance(mae, (int, float))
    assert r2 <= 1.0            # R² is bounded above by 1; below is unbounded
    assert mae >= 0.0           # an absolute error is never negative
    # The figures describe a real fit, not a placeholder.
    assert (r2, mae) != (0.0, 0.0)

    # Enough context to qualify the numbers on the page.
    assert body["target_unit"]
    assert body["n_samples"] > 0


def test_dss_model_reports_untrained_without_zero_metrics(client, monkeypatch):
    """State 3: NOT trained. It must SAY so, and must not emit zero-valued
    metrics that a reader would mistake for a measured result.

    Simulated by pointing the metadata path at a file that does not exist,
    which is exactly the condition the endpoint branches on.
    """
    from backend.app.ml import train
    monkeypatch.setattr(train, "META_PATH", "/nonexistent/model_meta.json")

    response = client.get("/api/v1/dss/model")
    assert response.status_code == 200
    body = response.json()

    assert body["trained"] is False
    # The honesty guarantee, asserted explicitly: absent, never zero.
    assert "metrics" not in body
    assert body.get("metrics") is None
    for key in ("r2", "mae"):
        assert key not in body
    # No zero-valued NUMERIC field can be mistaken for a metric. bool is
    # excluded deliberately: in Python isinstance(False, int) is True and
    # False == 0, so `trained: false` — the very field carrying the honest
    # answer — would otherwise trip this check.
    numeric = [v for v in body.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert not any(v == 0 for v in numeric)


# --- Enterprise economics endpoints (Phase 4, Fixture H) ------------------
# Five read/appraise routes over the same farm-scoped ledger. Every cost figure
# below is aggregated by enterprise_service (pure) from rows selected here; the
# routes write nothing, and the depreciation overlay is never posted.

def _post_mech_cost(client, *, crop, amount, subtype, hours=4.5):
    """A mechanisation cost carrying a cost subtype (so it classifies)."""
    extra = {"cost_subtype": subtype, "hours_used": hours} if subtype else None
    payload = {
        "activity_type": "mechanization",
        "description": "{} mechanisation cost".format(crop),
        "crop": crop,
        "extra_data": extra,
        "financial_data": {"amount": amount, "transaction_type": "debit", "category": "mechanization"},
    }
    return client.post("/api/v1/ledger/logs", json=payload)


def _seed_fixture_a(client):
    """Fixture A cost profile for maize, through the real write path: fuel 1,200
    + hire 800 + repairs 500 + fertilizer 900 + labour 600, plus one legacy
    mechanisation row of 400 carrying no extra_data at all."""
    assert _post_mech_cost(client, crop="maize", amount=1200.0, subtype="FUEL").status_code == 201
    assert _post_mech_cost(client, crop="maize", amount=800.0, subtype="MACHINERY_HIRE").status_code == 201
    assert _post_mech_cost(client, crop="maize", amount=500.0, subtype="REPAIRS").status_code == 201
    assert _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=900.0, transaction_type="debit").status_code == 201
    assert _post_crop_log(client, activity_type="labour", crop="maize", amount=600.0, transaction_type="debit").status_code == 201
    assert _post_mech_cost(client, crop="maize", amount=400.0, subtype=None).status_code == 201


def test_enterprise_cost_structure_matches_fixture_a(client):
    # Fixture A, end to end: the same numbers the unit tests assert, but reached
    # through the ledger, so the projection from log rows to (amount, category,
    # subtype) tuples is exercised too.
    _seed_fixture_a(client)
    body = client.get("/api/v1/dss/cost-structure").json()

    maize = next(c for c in body["crops"] if c["crop"] == "maize")
    assert maize["variable_cost"] == pytest.approx(3500.0)
    assert maize["semi_variable_cost"] == pytest.approx(500.0)
    assert maize["unclassified_cost"] == pytest.approx(400.0)
    assert maize["total_recorded_cost"] == pytest.approx(4400.0)
    assert maize["cash_cost"] == pytest.approx(4000.0)
    assert maize["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)
    # Farm-wide mirrors the single crop when only one crop has cost.
    assert body["farm"]["total_recorded_cost"] == pytest.approx(4400.0)
    assert body["farm"]["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)


def test_enterprise_cost_structure_reads_subtype_only_for_mechanization(client):
    # A seed log may carry an arbitrary extra_data dict, and that dict may happen
    # to contain the key cost_subtype. It is NOT a classification: only
    # mechanisation rows carry the taxonomy. Reading the key off every category
    # would turn ("SEED", "FUEL") into a missing lookup and silently push a
    # correctly classified row into the unclassified pile.
    payload = {
        "activity_type": "seed",
        "crop": "maize",
        "extra_data": {"cost_subtype": "FUEL", "note": "arbitrary"},
        "financial_data": {"amount": 1000.0, "transaction_type": "debit", "category": "seed"},
    }
    assert client.post("/api/v1/ledger/logs", json=payload).status_code == 201

    maize = next(
        c for c in client.get("/api/v1/dss/cost-structure").json()["crops"] if c["crop"] == "maize"
    )
    assert maize["variable_cost"] == pytest.approx(1000.0)
    assert maize["unclassified_cost"] == pytest.approx(0.0)
    assert maize["classification_coverage_pct"] == pytest.approx(100.0)


def test_enterprise_reversal_excluded_from_buckets_and_does_not_lower_coverage(client):
    """THE SUBTLE ONE. A reversal contra carries no cost subtype, so if it is
    merely netted out of the numerator while its amount stays in the
    denominator, classification coverage silently falls and a correction to the
    ledger starts to look like a data-quality problem. Both the reversal AND the
    log it reverses are excluded from every bucket, numerator and denominator
    alike."""
    _seed_fixture_a(client)
    before = client.get("/api/v1/dss/cost-structure").json()
    maize_before = next(c for c in before["crops"] if c["crop"] == "maize")
    assert maize_before["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)

    # Post a large classified mechanisation cost, then reverse it.
    created = _post_mech_cost(client, crop="maize", amount=9000.0, subtype="FUEL")
    assert created.status_code == 201
    log_id = created.json()["id"]
    assert client.post("/api/v1/ledger/logs/{}/reverse".format(log_id)).status_code == 201

    after = client.get("/api/v1/dss/cost-structure").json()
    maize_after = next(c for c in after["crops"] if c["crop"] == "maize")

    # Every bucket is exactly as it was: the pair leaves no trace anywhere.
    assert maize_after == maize_before
    assert after["farm"] == before["farm"]

    # Stated individually too, because == on the whole dict would also pass if
    # both sides were wrong in the same way.
    assert maize_after["variable_cost"] == pytest.approx(3500.0)      # not 12,500
    assert maize_after["unclassified_cost"] == pytest.approx(400.0)   # not 9,400
    assert maize_after["total_recorded_cost"] == pytest.approx(4400.0)
    # The denominator assertion: coverage did NOT fall. Still 400 unclassified
    # out of 4,400 — not 9,400/13,400 (70.1%), and not 400/13,400 (97.0%).
    assert maize_after["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)

    # And the pair is absent from every downstream figure, not just this one.
    be = client.get("/api/v1/dss/break-even-price?crop=maize").json()["crops"][0]
    assert be["total_recorded_cost_ngn"] == pytest.approx(4400.0)
    assert be["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)


# --- Amendment 1: the operating expense ratio, on the cost structure -------
# It is a whole-enterprise CASH measure — naira over naira — and NOT a figure
# per marketable kilogram, so it rides on /dss/cost-structure and deliberately
# not on /dss/break-even-price.

def _seed_input_only_sorghum(client):
    """Seed sorghum: 1,600 of recorded input cost and no sale at all. The
    realistic loss case, and the one that exercises the null ratio."""
    assert _post_crop_log(
        client, activity_type="seed", crop="sorghum", amount=1000.0,
        transaction_type="debit",
    ).status_code == 201
    assert _post_mech_cost(client, crop="sorghum", amount=600.0, subtype="FUEL").status_code == 201


def test_enterprise_operating_expense_ratio_is_reported_on_cost_structure(client):
    # Fixture E through the ledger. Maize cash operating cost is 4,400 —
    # variable 3,500 + semi-variable 500 + UNCLASSIFIED 400 — against revenue
    # 45,000, so 9.7778%. Farm-wide adds sorghum's 1,600 for 6,000/45,000 =
    # 13.3333%, exactly the two figures the unit fixture asserts.
    _seed_fixture_a(client)
    _seed_input_only_sorghum(client)
    assert _post_crop_log(
        client, activity_type="yield", crop="maize", amount=45000.0,
        transaction_type="credit", quantity=12.0, unit="bags",
    ).status_code == 201

    body = client.get("/api/v1/dss/cost-structure").json()
    maize = next(c for c in body["crops"] if c["crop"] == "maize")

    assert maize["revenue_ngn"] == pytest.approx(45000.0)
    assert maize["cash_operating_cost_ngn"] == pytest.approx(4400.0)
    assert maize["operating_expense_ratio_pct"] == pytest.approx(9.7778, rel=1e-4)

    assert body["farm"]["revenue_ngn"] == pytest.approx(45000.0)
    assert body["farm"]["cash_operating_cost_ngn"] == pytest.approx(6000.0)
    assert body["farm"]["operating_expense_ratio_pct"] == pytest.approx(13.3333, rel=1e-4)


def test_enterprise_operating_expense_ratio_is_null_for_an_input_only_crop(client):
    """Seed sorghum: cost recorded, nothing sold. The ratio is UNDEFINED — not
    zero (which reads as "spent nothing") and not a large number (which would
    need a denominator that does not exist). The farm-wide ratio is still
    defined, because maize did sell, so a null crop ratio is visibly a property
    of that crop and not of the report."""
    _seed_fixture_a(client)
    _seed_input_only_sorghum(client)
    assert _post_crop_log(
        client, activity_type="yield", crop="maize", amount=45000.0,
        transaction_type="credit", quantity=12.0, unit="bags",
    ).status_code == 201

    body = client.get("/api/v1/dss/cost-structure").json()
    sorghum = next(c for c in body["crops"] if c["crop"] == "sorghum")

    assert sorghum["revenue_ngn"] == pytest.approx(0.0)
    # The cost is known and reported; only the ratio is undefined.
    assert sorghum["cash_operating_cost_ngn"] == pytest.approx(1600.0)
    assert sorghum["total_recorded_cost"] == pytest.approx(1600.0)
    assert sorghum["operating_expense_ratio_pct"] is None
    assert body["farm"]["operating_expense_ratio_pct"] is not None


def test_enterprise_operating_expense_ratio_excludes_recorded_depreciation(client):
    """THE TRAP: the ratio is a CASH measure. A recorded DEPRECIATION row is a
    real ledger entry and a real fixed cost, but it is not cash, so it raises
    total_recorded_cost and must leave the ratio exactly where it was."""
    _seed_fixture_a(client)
    assert _post_crop_log(
        client, activity_type="yield", crop="maize", amount=45000.0,
        transaction_type="credit", quantity=12.0, unit="bags",
    ).status_code == 201
    before = next(
        c for c in client.get("/api/v1/dss/cost-structure").json()["crops"]
        if c["crop"] == "maize"
    )["operating_expense_ratio_pct"]

    assert _post_mech_cost(
        client, crop="maize", amount=2000.0, subtype="DEPRECIATION"
    ).status_code == 201

    maize = next(
        c for c in client.get("/api/v1/dss/cost-structure").json()["crops"]
        if c["crop"] == "maize"
    )
    assert maize["fixed_cost_recorded"] == pytest.approx(2000.0)
    assert maize["total_recorded_cost"] == pytest.approx(6400.0)   # it IS recorded
    assert maize["cash_operating_cost_ngn"] == pytest.approx(4400.0)  # but not cash
    assert maize["operating_expense_ratio_pct"] == pytest.approx(before, rel=1e-9)
    assert maize["operating_expense_ratio_pct"] == pytest.approx(9.7778, rel=1e-4)
    # Explicitly NOT total_recorded_cost / revenue, which would be this.
    assert maize["operating_expense_ratio_pct"] != pytest.approx(14.2222, rel=1e-4)


def test_enterprise_operating_expense_ratio_is_not_on_the_break_even_response(client):
    """It belongs to the cost structure, not beside the two per-kilogram prices.
    Placed there it would be read as a third break-even figure, which is exactly
    the naming failure the three metrics are kept apart to avoid."""
    _seed_fixture_a(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201

    be = client.get("/api/v1/dss/break-even-price?crop=maize").json()
    assert "operating_expense_ratio_pct" not in be
    assert "operating_expense_ratio_pct" not in be["crops"][0]


def test_enterprise_break_even_prices_null_without_marketable_mass(client):
    # Fixture H: a crop with recorded cost but no drying run has no marketable
    # mass, and a price per marketable kilogram is undefined — never a
    # fabricated zero, never a division by zero.
    _seed_fixture_a(client)
    body = client.get("/api/v1/dss/break-even-price?crop=maize").json()
    maize = body["crops"][0]

    assert maize["marketable_mass_kg"] is None
    assert maize["break_even_price_cash_ngn_per_kg"] is None
    assert maize["break_even_price_total_ngn_per_kg"] is None
    # The cost lines are still reported: the costs are known, only the price is not.
    assert maize["variable_and_semi_variable_cost_ngn"] == pytest.approx(4000.0)
    assert maize["total_recorded_cost_ngn"] == pytest.approx(4400.0)


def test_enterprise_break_even_prices_with_marketable_mass_never_collapse(client):
    # With a drying run present both prices are defined — and they must not be
    # the same number. The gap between them IS the fixed-cost argument.
    _seed_fixture_a(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201  # 84.0 kg out

    body = client.get("/api/v1/dss/break-even-price?crop=maize").json()
    maize = body["crops"][0]
    assert maize["marketable_mass_kg"] == pytest.approx(84.0)
    assert maize["break_even_price_cash_ngn_per_kg"] == pytest.approx(4000.0 / 84.0, rel=1e-4)
    assert maize["break_even_price_cash_ngn_per_kg"] < maize["break_even_price_total_ngn_per_kg"]
    assert "equipment_unrated_count" in body


def test_enterprise_zero_total_cost_gives_null_coverage(client):
    # Fixture H: a crop with revenue but no recorded cost. Coverage of nothing
    # is undefined — not 100 (reads as fully classified), not 0 (reads as
    # nothing classified).
    assert _post_crop_log(
        client, activity_type="yield", crop="cowpea", amount=8000.0,
        transaction_type="credit", quantity=5.0, unit="bags",
    ).status_code == 201

    cowpea = next(
        c for c in client.get("/api/v1/dss/cost-structure").json()["crops"] if c["crop"] == "cowpea"
    )
    assert cowpea["total_recorded_cost"] == pytest.approx(0.0)
    assert cowpea["classification_coverage_pct"] is None


def test_enterprise_sensitivity_matrix_is_labelled_conditional(client):
    _seed_fixture_a(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201

    body = client.get("/api/v1/dss/sensitivity?crop=maize").json()
    maize = body["crops"][0]
    assert maize["conditional"] is True
    assert [r["percentage"] for r in maize["rows"]] == [75, 90, 100, 110, 125]
    at_100 = next(r for r in maize["rows"] if r["percentage"] == 100)
    assert at_100["marketable_mass_kg"] == pytest.approx(84.0)
    assert at_100["break_even_price_cash_ngn_per_kg"] == pytest.approx(4000.0 / 84.0, rel=1e-4)

    # Caller-supplied percentages are honoured.
    custom = client.get("/api/v1/dss/sensitivity?crop=maize&percentages=50&percentages=200").json()
    assert [r["percentage"] for r in custom["crops"][0]["rows"]] == [50, 200]


# --- Amendment 2: the depreciation window, derived by default and pinnable --
# A derived span WIDENS with every new log, so a break-even price to cover total
# cost computed over one cannot be re-derived after the next entry. period_days
# pins the window; period_source says which the reader is looking at.

def _seed_rated_equipment(client):
    """One rated asset: 240,000 at 10%/yr, so 24,000 a year of charge.

    The rate is a PERCENTAGE here, because that is the unit the API takes.
    `dss_service.depreciation_rate_as_fraction` turns it into the 0.10 that
    Fixture B feeds `depreciation_overlay` directly."""
    resp = client.post(
        "/api/v1/equipment/",
        json={"name": "Bench dryer", "purchase_price": 240000.0, "depreciation_rate": 10.0},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_enterprise_period_defaults_to_the_derived_ledger_span(client):
    _seed_fixture_a(client)
    _seed_rated_equipment(client)

    body = client.get("/api/v1/dss/break-even-price?crop=maize").json()
    assert body["period_source"] == "derived"
    # Every log in this test was written in one request cycle, so the span is
    # one day — inclusive of both endpoints, never a zero-length window.
    assert body["period_days"] == pytest.approx(1.0)
    assert body["period_fixed_cost_ngn"] == pytest.approx(24000.0 / 365.0, rel=1e-4)


def test_enterprise_specified_period_overrides_the_derived_span(client):
    _seed_fixture_a(client)
    _seed_rated_equipment(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201  # 84.0 kg

    derived = client.get("/api/v1/dss/break-even-price?crop=maize").json()
    pinned = client.get("/api/v1/dss/break-even-price?crop=maize&period_days=30").json()

    assert pinned["period_source"] == "specified"
    assert pinned["period_days"] == pytest.approx(30.0)
    # Fixture B's 30-day charge, and maize is the only crop bearing direct cost
    # so its share of the allocation is the whole of it.
    assert pinned["period_fixed_cost_ngn"] == pytest.approx(1972.60, rel=1e-4)

    maize = pinned["crops"][0]
    assert maize["allocated_fixed_ngn"] == pytest.approx(1972.60, rel=1e-4)
    assert maize["total_cost_ngn"] == pytest.approx(4400.0 + 1972.60, rel=1e-4)
    assert maize["break_even_price_total_ngn_per_kg"] == pytest.approx(
        (4400.0 + 1972.60) / 84.0, rel=1e-4
    )

    # The window moves the TOTAL price and must not touch the CASH one: the
    # overlay is not cash and has no route into that base.
    assert maize["break_even_price_cash_ngn_per_kg"] == pytest.approx(
        derived["crops"][0]["break_even_price_cash_ngn_per_kg"], rel=1e-9
    )
    assert maize["break_even_price_total_ngn_per_kg"] != pytest.approx(
        derived["crops"][0]["break_even_price_total_ngn_per_kg"], rel=1e-6
    )


def test_enterprise_pinned_period_is_reproducible_when_a_new_log_widens_the_span(client, db):
    """THE REASON THE OVERRIDE EXISTS. A derived span runs first log to last, so
    entering ANY further log widens it, scales the depreciation charge, and
    silently moves a break-even price to cover total cost that was already
    reported. A figure quoted last week could not be re-derived, because the
    window it was computed over no longer exists. A pinned window is stable
    across the same edit."""
    from backend.app.models import models as m

    _seed_fixture_a(client)
    _seed_rated_equipment(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201

    def total_price(query=""):
        body = client.get("/api/v1/dss/break-even-price?crop=maize" + query).json()
        return body["period_days"], body["crops"][0]["break_even_price_total_ngn_per_kg"]

    derived_days_before, derived_before = total_price()
    pinned_days_before, pinned_before = total_price("&period_days=30")

    # Backdate the farm's earliest log by 100 days — the shape of "a record was
    # entered that the reported figure did not cover". The span widens from one
    # day to 101.
    earliest = db.query(m.OperationalLog).order_by(m.OperationalLog.id).first()
    earliest.timestamp = earliest.timestamp - timedelta(days=100)
    db.commit()

    derived_days_after, derived_after = total_price()
    pinned_days_after, pinned_after = total_price("&period_days=30")

    # The derived window moved, and so did the price computed over it.
    assert derived_days_after == pytest.approx(101.0)
    assert derived_days_after != pytest.approx(derived_days_before)
    assert derived_after != pytest.approx(derived_before, rel=1e-6)

    # The pinned window did not, and neither did its price. Same query, same
    # number, after a ledger edit — which is the whole claim.
    assert pinned_days_after == pytest.approx(pinned_days_before) == pytest.approx(30.0)
    assert pinned_after == pytest.approx(pinned_before, rel=1e-9)


def test_enterprise_sensitivity_honours_the_pinned_period(client):
    # Every price in the matrix is a break-even price, so the matrix inherits
    # the same reproducibility problem and the same fix. The 100% row must be
    # the number /break-even-price reports for the same pin.
    _seed_fixture_a(client)
    _seed_rated_equipment(client)
    assert _post_drying(client, crop="maize", amount=0.0).status_code == 201

    matrix = client.get("/api/v1/dss/sensitivity?crop=maize&period_days=30").json()
    assert matrix["period_source"] == "specified"
    assert matrix["period_days"] == pytest.approx(30.0)

    at_100 = next(r for r in matrix["crops"][0]["rows"] if r["percentage"] == 100)
    be = client.get("/api/v1/dss/break-even-price?crop=maize&period_days=30").json()
    assert at_100["break_even_price_total_ngn_per_kg"] == pytest.approx(
        be["crops"][0]["break_even_price_total_ngn_per_kg"], rel=1e-9
    )
    # Unpinned, the same route says so rather than leaving the reader to guess.
    assert client.get(
        "/api/v1/dss/sensitivity?crop=maize"
    ).json()["period_source"] == "derived"


@pytest.mark.parametrize("route", ["break-even-price", "sensitivity"])
@pytest.mark.parametrize("bad", [0, -1, 36526])
def test_enterprise_period_days_is_bounded_at_the_edge(client, route, bad):
    # A zero window would zero the overlay, a negative one would make the charge
    # negative and drop the total price BELOW the cash price, and an unbounded
    # one would let a single request scale the charge arbitrarily far above any
    # cost it is set beside. All three are 422 at the edge, never a 500.
    _seed_fixture_a(client)
    resp = client.get("/api/v1/dss/{}?period_days={}".format(route, bad))
    assert resp.status_code == 422


def test_enterprise_partial_budget_returns_a_negative_net_change(client):
    # Stateless: four numbers in, net change out, nothing written.
    resp = client.post(
        "/api/v1/dss/partial-budget",
        json={"added_revenue_ngn": 12000.0, "reduced_cost_ngn": 3000.0,
              "lost_revenue_ngn": 0.0, "added_cost_ngn": 9500.0},
    )
    assert resp.status_code == 200
    assert resp.json()["net_change_ngn"] == pytest.approx(5500.0)

    negative = client.post(
        "/api/v1/dss/partial-budget",
        json={"added_revenue_ngn": 4000.0, "reduced_cost_ngn": 1000.0,
              "lost_revenue_ngn": 500.0, "added_cost_ngn": 9500.0},
    )
    assert negative.status_code == 200
    # A negative result is a valid answer: the change is not worth making.
    assert negative.json()["net_change_ngn"] == pytest.approx(-5000.0)

    # The four inputs are non-negative by contract; the sign lives in which slot
    # a quantity occupies, not in the number.
    bad = client.post(
        "/api/v1/dss/partial-budget",
        json={"added_revenue_ngn": -1.0, "reduced_cost_ngn": 0.0,
              "lost_revenue_ngn": 0.0, "added_cost_ngn": 0.0},
    )
    assert bad.status_code == 422

    # It writes nothing: the ledger is untouched by an appraisal.
    assert client.get("/api/v1/ledger/logs").json() == []


def test_enterprise_yield_baseline_needs_three_seasons(client):
    # A season is a calendar year of recorded yield. Two are not enough for an
    # Olympic average, and a two-value mean is not one under another name.
    for _ in range(2):
        assert _post_crop_log(
            client, activity_type="yield", crop="maize", amount=1000.0,
            transaction_type="credit", quantity=12.0, unit="bags",
        ).status_code == 201

    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"] if c["crop"] == "maize"
    )
    # Both logs land in the same calendar year, so this is ONE season, not two.
    assert maize["n_seasons"] == 1
    assert maize["olympic_average_kg"] is None
    assert maize["reason"] is not None      # nulls travel with a reason, never bare
    assert maize["grand_average_kg"] == pytest.approx(24.0)


@pytest.mark.parametrize(
    "route",
    [
        "/api/v1/dss/cost-structure?crop=maize",
        "/api/v1/dss/break-even-price?crop=maize",
        "/api/v1/dss/sensitivity?crop=maize",
        "/api/v1/dss/yield-baseline?crop=maize",
    ],
)
def test_enterprise_routes_cross_farm_read_is_404(make_client, route):
    # Fixture H: another farm's crop is simply "not found" — the same verdict
    # every other resource gives, and no existence leak in either direction.
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")
    _seed_fixture_a(farm_a)

    assert farm_a.get(route).status_code == 200
    assert farm_b.get(route).status_code == 404

    # Unfiltered, B sees its own (empty) farm rather than A's figures.
    unfiltered = route.split("?")[0]
    b_body = farm_b.get(unfiltered).json()
    assert b_body["crops"] == []


def test_enterprise_yield_baseline_mixed_units_is_null_with_a_reason(client):
    # Same verdict get_decision_support gives for the same cause: quantities in
    # two units cannot be summed, so no honest single baseline exists. Null with
    # a stated reason, never a total that was never true.
    assert _post_crop_log(
        client, activity_type="yield", crop="maize", amount=1000.0,
        transaction_type="credit", quantity=12.0, unit="bags",
    ).status_code == 201
    assert _post_crop_log(
        client, activity_type="yield", crop="maize", amount=1000.0,
        transaction_type="credit", quantity=100.0, unit="kg",
    ).status_code == 201

    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"] if c["crop"] == "maize"
    )
    assert maize["olympic_average_kg"] is None
    assert maize["grand_average_kg"] is None      # not 112 across two units
    assert maize["unit"] is None
    assert "more than one unit" in maize["reason"]


# --- Amendment 3: a null Olympic average never stands without its count -----
# A season is a calendar year of recorded yield — ADR-0002 records that as a
# temporary assumption pending a Season entity. n_seasons is therefore reported
# in every branch, including the ones that refuse to give an average.

def _backdate_yields_across_years(db, crop, years):
    """Move a crop's yield logs into distinct calendar years, oldest first.

    The API cannot set a timestamp — it is server-stamped — so multi-season
    history is only reachable through the session. `years` is a per-log offset
    in whole years, applied in log-id order.
    """
    from backend.app.models import models as m

    logs = (
        db.query(m.OperationalLog)
        .filter(m.OperationalLog.crop == crop, m.OperationalLog.activity_type == "yield")
        .order_by(m.OperationalLog.id)
        .all()
    )
    assert len(logs) == len(years)
    for log, back in zip(logs, years):
        log.timestamp = log.timestamp - timedelta(days=365 * back)
    db.commit()


def test_enterprise_yield_baseline_mixed_units_still_reports_its_season_count(client, db):
    """A null with no count beside it is unreadable: the reader cannot tell "no
    history yet" from "three seasons of history that cannot be summed". The
    units are inconsistent, so no average is given — but the seasons were found,
    and saying zero would be a different and false statement."""
    for unit, quantity in (("bags", 12.0), ("bags", 14.0), ("kg", 900.0)):
        assert _post_crop_log(
            client, activity_type="yield", crop="maize", amount=1000.0,
            transaction_type="credit", quantity=quantity, unit=unit,
        ).status_code == 201
    _backdate_yields_across_years(db, "maize", [2, 1, 0])

    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"]
        if c["crop"] == "maize"
    )
    assert maize["olympic_average_kg"] is None
    assert maize["grand_average_kg"] is None
    assert maize["n_seasons"] == 3          # not 0: the history exists
    assert "more than one unit" in maize["reason"]
    assert "3 season" in maize["reason"]


def test_enterprise_yield_baseline_season_count_distinguishes_two_kinds_of_null(client, db):
    """Two seasons and three seasons give different answers for the same reason
    field to explain, and the count is what tells them apart."""
    for quantity in (10.0, 20.0):
        assert _post_crop_log(
            client, activity_type="yield", crop="maize", amount=1000.0,
            transaction_type="credit", quantity=quantity, unit="bags",
        ).status_code == 201
    _backdate_yields_across_years(db, "maize", [1, 0])

    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"]
        if c["crop"] == "maize"
    )
    assert maize["n_seasons"] == 2
    assert maize["olympic_average_kg"] is None      # two is below the minimum
    assert "2" in maize["reason"]
    # The grand average is still given, so the two baselines stay comparable.
    assert maize["grand_average_kg"] == pytest.approx(15.0)


def test_enterprise_yield_baseline_three_seasons_discards_one_high_and_one_low(client, db):
    # A calendar year is one season even where several yields were logged in it,
    # so the four logs below are three seasons: 10, 20+5, 30.
    for quantity in (10.0, 20.0, 5.0, 30.0):
        assert _post_crop_log(
            client, activity_type="yield", crop="maize", amount=1000.0,
            transaction_type="credit", quantity=quantity, unit="bags",
        ).status_code == 201
    _backdate_yields_across_years(db, "maize", [2, 1, 1, 0])

    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"]
        if c["crop"] == "maize"
    )
    assert maize["n_seasons"] == 3
    assert maize["n_used"] == 1
    assert maize["n_discarded"] == 2
    # Seasons are 10, 25, 30. Drop one high and one low, leaving 25.
    assert maize["olympic_average_kg"] == pytest.approx(25.0)
    assert maize["grand_average_kg"] == pytest.approx(65.0 / 3.0, rel=1e-4)
    assert maize["reason"] is None


def test_enterprise_yield_baseline_reports_a_crop_with_no_yield(client):
    # A crop with cost but no harvest recorded yet: both averages null, with the
    # reason saying which of the two possible causes it is.
    _seed_fixture_a(client)
    maize = next(
        c for c in client.get("/api/v1/dss/yield-baseline").json()["crops"] if c["crop"] == "maize"
    )
    assert maize["n_seasons"] == 0
    assert maize["olympic_average_kg"] is None
    assert maize["grand_average_kg"] is None
    assert "No yield" in maize["reason"]
