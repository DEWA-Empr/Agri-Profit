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
    # Flip the final signature character to a guaranteed-different one (staying in
    # the base64url alphabet), so the HMAC no longer matches the payload.
    forged_last = "A" if signature[-1] != "A" else "B"
    tampered = f"{header}.{payload}.{signature[:-1]}{forged_last}"

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
    assert m["water_removed_kg"] == pytest.approx(16.0, rel=1e-4)
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
    assert maize["total_water_removed_kg"] == pytest.approx(16.0 + 32.0)
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
