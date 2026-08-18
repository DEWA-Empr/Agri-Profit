"""Seed a coherent demo crop through the real API (ticket 08, idempotent).

Creates (or reuses) a fresh demo farm and posts three crops.

MAIZE — the coherent bioprocess lot: a 100 kg harvest, and a drying run that
dries that whole 100 kg down to 84 kg marketable. Because the entire harvest
passes through the recorded drying run, BOTH unit costs are per-kilogram and
differ only by the mass drying removed (100 kg harvested vs 84 kg marketable) —
which is exactly what the feature surfaces. See the ADR for the assumption this
coherence relies on. These figures are load-bearing for the write-up: do not
change the 3,500 of expenses, the 100 kg, the 84 kg or the 45,000 sale.

CASSAVA — profitable, and deliberately WITHOUT a drying run, so the per-crop
panel has to fall back from unit cost per kg marketable (undefined, no
marketable mass) to unit cost per kg harvested. Fresh roots sold at the farm
gate is the honest reason there is no drying run, not an omission.

TOMATO — the loss-making case: inputs bought, nothing sold. Dry-season irrigated
tomato is expensive to grow and routinely lost to spoilage or a price collapse
before it reaches market, which is precisely why a farmer needs to see it. It
exercises the negative gross margin and the null break-even (no revenue means no
realised price to divide by, so the metric is undefined rather than infinite).

Both records use fixed client_ids, so re-running is safe: the ledger's client_id
idempotency returns the existing rows instead of duplicating them. Going through
POST /ledger/logs means the demo is created exactly as a farmer's would be.

Run (backend + db up):   python backend/scripts/seed_bioprocess_demo.py
Override the base URL:    API_BASE=http://host:8000 python backend/scripts/seed_bioprocess_demo.py
"""
import json
import os
import urllib.error
import urllib.request

# NB: the address must pass EmailStr — a reserved TLD like `.local` is rejected
# (RFC 6762 special-use). Use `.example`, as the test suite does.
BASE = os.environ.get("API_BASE", "http://localhost:8000") + "/api/v1"
EMAIL = "demo-bioprocess-v2@test.example"
PASSWORD = "demo-bioprocess-pw"

LOGS = [
    {
        "activity_type": "yield",
        "description": "Demo maize harvest",
        "crop": "maize",
        "quantity": 100.0,
        "unit": "kg",
        "client_id": "seed-bioprocess-yield-0001",  # fixed -> re-run is idempotent
        "financial_data": {"amount": 45000.0, "transaction_type": "credit", "category": "yield"},
    },
    {
        "activity_type": "bioprocess",
        "description": "Demo maize drying run",
        "crop": "maize",
        "client_id": "seed-bioprocess-drying-0001",  # fixed -> re-run is idempotent
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
    },

    # --- Cassava: profitable, no drying run (the unit-cost fallback path) ---
    #
    # A 0.2 ha plot of fresh cassava roots. Every figure below is a rate times a
    # quantity rather than a chosen total, so nothing is tuned to make the
    # margin land on a round number or the ranking come out in a particular
    # order — see the commit message for the rate each one uses.
    {
        "activity_type": "seed",
        "description": "Cassava stem cuttings, 12 bundles (0.2 ha)",
        "crop": "cassava",
        "client_id": "seed-cassava-stems-0001",
        "financial_data": {"amount": 8400.0, "transaction_type": "debit", "category": "seed"},
    },
    {
        "activity_type": "fertilizer",
        "description": "NPK 15-15-15, 25 kg for cassava",
        "crop": "cassava",
        "client_id": "seed-cassava-fertilizer-0001",
        "financial_data": {"amount": 26000.0, "transaction_type": "debit", "category": "fertilizer"},
    },
    {
        "activity_type": "labour",
        "description": "Cassava land clearing and ridging, 7 person-days",
        "crop": "cassava",
        "client_id": "seed-cassava-landprep-0001",
        "financial_data": {"amount": 21000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        "activity_type": "labour",
        "description": "Cassava weeding, two rounds, 8 person-days",
        "crop": "cassava",
        "client_id": "seed-cassava-weeding-0001",
        "financial_data": {"amount": 24000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        "activity_type": "labour",
        "description": "Cassava harvesting and heaping, 5 person-days",
        "crop": "cassava",
        "client_id": "seed-cassava-harvest-labour-0001",
        "financial_data": {"amount": 15000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        # No bioprocess log for cassava, on purpose: roots go to the buyer
        # fresh. marketable_mass_kg stays None, so unit_cost_per_kg_marketable
        # is None and the panel must show unit_cost_of_production instead.
        "activity_type": "yield",
        "description": "Cassava fresh roots sold at farm gate",
        "crop": "cassava",
        "quantity": 1880.0,
        "unit": "kg",
        "client_id": "seed-cassava-yield-0001",
        "financial_data": {"amount": 178600.0, "transaction_type": "credit", "category": "yield"},
    },

    # --- Tomato: loss-making, nothing sold (negative margin, null break-even) ---
    #
    # A 0.1 ha dry-season irrigated plot. There is deliberately NO yield log and
    # NO credit anywhere: the crop was grown and never sold. Revenue is a
    # genuine zero, which is what drives break_even_yield to None — the null
    # here is the "no realised price" case, not the mixed-unit or zero-expense
    # one. The bucket survives the empty-crop filter on its expenses alone.
    {
        "activity_type": "seed",
        "description": "Hybrid tomato seed, one 10 g sachet",
        "crop": "tomato",
        "client_id": "seed-tomato-seed-0001",
        "financial_data": {"amount": 6800.0, "transaction_type": "debit", "category": "seed"},
    },
    {
        "activity_type": "fertilizer",
        "description": "NPK 15-15-15 (20 kg) and urea (10 kg) for tomato",
        "crop": "tomato",
        "client_id": "seed-tomato-fertilizer-0001",
        "financial_data": {"amount": 29800.0, "transaction_type": "debit", "category": "fertilizer"},
    },
    {
        "activity_type": "labour",
        "description": "Tomato nursery, transplanting, staking and weeding, 9 person-days",
        "crop": "tomato",
        "client_id": "seed-tomato-labour-0001",
        "financial_data": {"amount": 27000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        "activity_type": "other",
        "description": "Tomato insecticide, three sprays against Tuta absoluta",
        "crop": "tomato",
        "client_id": "seed-tomato-insecticide-0001",
        "financial_data": {"amount": 11700.0, "transaction_type": "debit", "category": "other"},
    },
    {
        "activity_type": "mechanization",
        "description": "Petrol for the irrigation pump, dry-season tomato",
        "crop": "tomato",
        "client_id": "seed-tomato-pump-fuel-0001",
        "financial_data": {"amount": 37600.0, "transaction_type": "debit", "category": "mechanization"},
    },
]


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

    for log in LOGS:
        status, body = _call("POST", "/ledger/logs", token=token, body=log)
        print(f"{log['activity_type']:>13} {log['crop']:>8} -> HTTP {status}, id={body.get('id')} (201=created, 200=already seeded)")

    # Record counts, so a second run proves idempotency without a psql session:
    # both totals must be identical across runs, and every POST above must come
    # back 200 rather than 201.
    _, logs = _call("GET", "/ledger/logs?limit=1000", token=token)
    _, txs = _call("GET", "/ledger/transactions?limit=1000", token=token)
    print(f"records:    {len(logs)} operational logs, {len(txs)} financial transactions")
    print(f"view DSS:   GET {BASE}/dss/decision-support")


if __name__ == "__main__":
    main()
