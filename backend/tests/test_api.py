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
    # This assumes previous test added a debit
    response = client.get("/api/v1/ledger/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["expenses"] == 25000.0
    assert data["gross_margin"] == -25000.0

def test_dss_predict(client):
    payload = {"features": [1, 2, 3]}
    response = client.post("/api/v1/dss/predict", json=payload)
    assert response.status_code == 200
    # Since model doesn't exist yet, it should return error from our placeholder
    assert "error" in response.json()

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
    r1 = client.post("/api/v1/ledger/logs", json=payload)
    assert r1.status_code == 200
    r2 = client.post("/api/v1/ledger/logs", json=payload)
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

def test_invalid_enum_activity(client):
    payload = {
        "activity_type": "invalid_category",
        "description": "This should fail"
    }
    response = client.post("/api/v1/ledger/logs", json=payload)
    assert response.status_code == 422 # Unprocessable Entity
