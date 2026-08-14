"""Seed one demo drying run through the real API (ticket 08, idempotent).

Creates (or reuses) a demo farm and POSTs a single Bioprocess drying run with a
fixed client_id. Re-running is safe: the ledger's client_id idempotency returns
the existing row instead of duplicating it. Going through POST /ledger/logs
means the demo record is created exactly as a farmer's would be — which is the
point when showing the feature live.

Run (backend + db up):   python backend/scripts/seed_bioprocess_demo.py
Override the base URL:    API_BASE=http://host:8000 python backend/scripts/seed_bioprocess_demo.py
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("API_BASE", "http://localhost:8000") + "/api/v1"
EMAIL = "demo-bioprocess@agriprofit.local"
PASSWORD = "demo-bioprocess-pw"


def _call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def main():
    # Register the demo farm, or log in if it already exists (idempotent).
    status, body = _call(
        "POST", "/auth/register",
        body={"email": EMAIL, "password": PASSWORD, "farm_name": "Demo Farm"},
    )
    if status == 409:
        status, body = _call("POST", "/auth/login", body={"email": EMAIL, "password": PASSWORD})
    token = body["access_token"]

    log = {
        "activity_type": "bioprocess",
        "description": "Demo maize drying run",
        "crop": "maize",
        "client_id": "seed-bioprocess-demo-0001",  # fixed -> re-run is idempotent
        "extra_data": {
            "process_type": "DRYING", "method": "SOLAR_DRYER",
            "mass_in_kg": 100.0, "mass_out_kg": 84.0,
            "moisture_initial_wb": 25.0, "moisture_final_wb": 13.0,
            "drying_time_hours": 10.0,
            "readings": [
                {"time_hours": 2.0, "moisture_wb": 21.0},
                {"time_hours": 5.0, "moisture_wb": 17.0},
                {"time_hours": 8.0, "moisture_wb": 14.5},
            ],
        },
        "financial_data": {"amount": 3500.0, "transaction_type": "debit", "category": "bioprocess"},
    }
    status, body = _call("POST", "/ledger/logs", token=token, body=log)
    print(f"drying run -> HTTP {status}, id={body.get('id')} (201=created, 200=already seeded)")
    print(f"view it:    GET {BASE}/bioprocess/{body.get('id')}")


if __name__ == "__main__":
    main()
