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
