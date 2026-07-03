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
    assert response.status_code == 200
    data = response.json()
    assert data["activity_type"] == "fertilizer"
    assert data["financial_transaction_id"] is not None
    assert data["financial_transaction"]["amount"] == 25000.0

def test_get_summary(client):
    # Seed a known debit and credit, then assert exact totals (self-contained).
    assert _post_log(client, activity_type="fertilizer", amount=25000.0, transaction_type="debit").status_code == 200
    assert _post_log(client, activity_type="yield", amount=40000.0, transaction_type="credit").status_code == 200

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
    assert _post_crop_log(client, activity_type="fertilizer", crop="maize", amount=25000.0, transaction_type="debit").status_code == 200
    assert _post_crop_log(client, activity_type="yield", crop="maize", amount=40000.0, transaction_type="credit", quantity=12.0, unit="bags").status_code == 200
    assert _post_crop_log(client, activity_type="labour", crop="rice", amount=10000.0, transaction_type="debit").status_code == 200

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
    assert response.status_code == 200
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
    assert response.status_code == 200
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
    r1 = client.post("/api/v1/ledger/logs", json=payload)
    assert r1.status_code == 200
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

    assert _post_log(farm_a, activity_type="yield", amount=40000.0, transaction_type="credit").status_code == 200

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


def test_equipment_isolation_cross_farm_read_rejected(make_client):
    farm_a = make_client(farm_name="Farm A")
    farm_b = make_client(farm_name="Farm B")

    created = farm_a.post(
        "/api/v1/equipment/",
        json={"name": "Farm A Tractor", "purchase_price": 15000000.0, "depreciation_rate": 10.0},
    )
    assert created.status_code == 200
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
