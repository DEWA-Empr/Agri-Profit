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

COWPEA — the enterprise-economics case, and the only crop here whose cost
carries a full Cost Subtype spread: fuel and lubricants and hire (variable),
repairs (semi-variable), a recorded depreciation charge (fixed), and one
mechanisation row deliberately carrying no subtype at all. Its drying run is
coherent with its harvest in the same way maize's is, so it has a Marketable
Mass and therefore real break-even prices rather than nulls — which is what
makes it, not maize, the crop the dual break-even and the sensitivity matrix are
legible on.

SORGHUM — inputs recorded, nothing sold, and no mechanisation subtype missing.
The same shape as tomato but classified, so the two sit either side of the
coverage question: tomato shows what a partially classified loss looks like,
sorghum what a fully classified one does. Neither has revenue, so both carry a
null operating expense ratio rather than an infinite one.

EQUIPMENT — one rated asset and one unrated one, so the depreciation overlay is
visibly PARTIAL. The thresher is the more valuable of the two and contributes
nothing to the charge, which is the point: `equipment_unrated_count` is what
stops a partial overlay being read as a small true fixed cost.

Every log uses a fixed client_id, so re-running is safe: the ledger's client_id
idempotency returns the existing rows instead of duplicating them. Going through
POST /ledger/logs means the demo is created exactly as a farmer's would be.
Equipment has no client_id and no idempotency of its own, so it is matched by
name against what the farm already holds before anything is posted.

NOTHING HERE TOUCHES THE MAIZE ROWS. The 100 kg, the 84 kg, the 3,500 and the
45,000 are quoted in a defended chapter as ₦35.00/kg harvested and ₦41.67/kg
marketable, and per-crop decision support reads only one crop's own rows, so
adding crops cannot move them. There was no maize mechanisation cost to retrofit
a subtype onto in any case: maize's only expense is its drying run.

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

# Resolved to the tractor's real id before the logs are posted. A mechanisation
# row may name the asset it was spent on; a hired machine names none, which is
# why MechanizationParams.equipment_id is nullable and why the threshing-hire
# row below leaves it out.
TRACTOR = "$TRACTOR"

# Equipment carries no client_id, so it has none of the ledger's idempotency.
# It is matched by name instead — see ensure_equipment. The rate is a
# PERCENTAGE per year (12.5 = 12.5%/yr), the unit the farmer enters and reads;
# dss_service.depreciation_rate_as_fraction is the one place it becomes 0.125.
#
# 12.5 rather than 10 on purpose: 10 was the constant the equipment form used to
# inject into every asset created through the interface (register finding N-04),
# and any row still carrying it is a legacy row, not a rate anybody chose. A
# seeded 10 would be indistinguishable from one.
EQUIPMENT = [
    {
        "name": "Massey Ferguson 375 tractor",
        "model": "MF375",
        "purchase_price": 4_200_000.0,
        "depreciation_rate": 12.5,
    },
    {
        # No rate: the farmer does not know what this one loses in a year, and
        # the platform refuses to guess. It contributes ZERO to the overlay and
        # is counted in equipment_unrated_count instead of being charged at
        # zero — which matters here precisely because it is not a trivial asset.
        # An overlay computed over the tractor alone is a partial answer, and
        # the count is what says so.
        "name": "Multi-crop thresher",
        "model": "IAR T-90",
        "purchase_price": 850_000.0,
        "depreciation_rate": None,
    },
]

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

    # --- Cowpea: profitable, fully subtyped mechanisation, and a drying run ---
    #
    # A 0.5 ha plot. This is the crop the enterprise-economics endpoints are
    # legible on, because it is the only one carrying every Cost Behaviour at
    # once AND a Marketable Mass to divide by. Rates, not chosen totals: 20 kg
    # of seed at 1,150/kg, one 50 kg bag of SSP, 11 person-days at 3,000,
    # 38 litres of diesel at 1,250, 4 litres of oil at 4,800, 3 hours of
    # threshing hire at 9,000.
    {
        "activity_type": "seed",
        "description": "Certified cowpea seed, 20 kg (0.5 ha)",
        "crop": "cowpea",
        "client_id": "seed-cowpea-seed-0001",
        "financial_data": {"amount": 23000.0, "transaction_type": "debit", "category": "seed"},
    },
    {
        # SSP, not urea: cowpea fixes its own nitrogen and wants phosphate.
        "activity_type": "fertilizer",
        "description": "Single superphosphate, one 50 kg bag, for cowpea",
        "crop": "cowpea",
        "client_id": "seed-cowpea-fertilizer-0001",
        "financial_data": {"amount": 38500.0, "transaction_type": "debit", "category": "fertilizer"},
    },
    {
        "activity_type": "labour",
        "description": "Cowpea planting, weeding and harvesting, 11 person-days",
        "crop": "cowpea",
        "client_id": "seed-cowpea-labour-0001",
        "financial_data": {"amount": 33000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        # VARIABLE. Fuel burnt is fuel burnt per hectare worked.
        "activity_type": "mechanization",
        "description": "Diesel for cowpea ploughing and harrowing, 38 litres",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-fuel-0001",
        "extra_data": {"cost_subtype": "FUEL", "equipment_id": TRACTOR, "hours_used": 6.0},
        "financial_data": {"amount": 47500.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        # VARIABLE, and separated from fuel rather than folded into it, because
        # the taxonomy distinguishes them and a merged row could not be split
        # back out later.
        "activity_type": "mechanization",
        "description": "Engine and hydraulic oil for the tractor, 4 litres",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-lubricants-0001",
        "extra_data": {"cost_subtype": "LUBRICANTS", "equipment_id": TRACTOR},
        "financial_data": {"amount": 19200.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        # SEMI_VARIABLE, and the whole reason the taxonomy has a third state.
        # A bearing goes because the machine is used and because it is old, and
        # forcing it into either bucket would be a worse answer than reporting
        # it as what it is. It folds into cash_cost for the computation and is
        # still reported on its own line.
        "activity_type": "mechanization",
        "description": "Plough disc bearing replacement after the cowpea ridging",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-repairs-0001",
        "extra_data": {"cost_subtype": "REPAIRS", "equipment_id": TRACTOR},
        "financial_data": {"amount": 26500.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        # VARIABLE, and NO equipment_id: the thresher was hired, so there is no
        # owned asset to point at. The field is nullable for exactly this case.
        "activity_type": "mechanization",
        "description": "Threshing hire for cowpea, 3 hours",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-hire-0001",
        "extra_data": {"cost_subtype": "MACHINERY_HIRE", "hours_used": 3.0},
        "financial_data": {"amount": 27000.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        # FIXED, and a RECORDED depreciation charge — a row the farmer entered,
        # not the derived overlay. ADR-0002 keeps the two apart and never adds
        # them: this lands in fixed_cost_recorded, the overlay lands in
        # allocated_fixed_ngn, and they are reported on separate lines.
        #
        # It is also the row that makes the operating expense ratio's exclusion
        # visible. The ratio is a CASH measure, so this non-cash charge sits
        # inside total_recorded_cost and outside cash_operating_cost_ngn.
        "activity_type": "mechanization",
        "description": "Tractor depreciation charged against the cowpea season",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-depreciation-0001",
        "extra_data": {"cost_subtype": "DEPRECIATION", "equipment_id": TRACTOR},
        "financial_data": {"amount": 18000.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        # THE LEGACY-SHAPED ROW: no extra_data at all, so no Cost Subtype, so
        # UNCLASSIFIED — never defaulted into VARIABLE. It sits on cowpea on
        # purpose. Tomato already carries an unclassified mechanisation row, but
        # tomato has nothing else classified to contrast it against; putting one
        # here drags the coverage of the crop with the FULL subtype spread below
        # 100%, which is the figure worth showing. A demonstration where the
        # well-classified crop reads 100% teaches nothing about coverage.
        "activity_type": "mechanization",
        "description": "Tractor ridging for cowpea (entered with no cost subtype)",
        "crop": "cowpea",
        "client_id": "seed-cowpea-mech-legacy-0001",
        "financial_data": {"amount": 21000.0, "transaction_type": "debit", "category": "mechanization"},
    },
    {
        "activity_type": "yield",
        "description": "Cowpea threshed grain, whole lot to the drying floor",
        "crop": "cowpea",
        "quantity": 480.0,
        "unit": "kg",
        "client_id": "seed-cowpea-yield-0001",
        "financial_data": {"amount": 624950.0, "transaction_type": "credit", "category": "yield"},
    },
    {
        # Coherent with the harvest above, as maize's run is: the whole 480 kg
        # goes through it, so both unit costs are per-kilogram and differ only
        # by the mass drying removed.
        #
        # The run is NOT well behaved, deliberately. Dry-matter conservation
        # predicts an outlet of 480 x (100-18)/(100-11.5) = 444.746 kg; the
        # recorded outlet is 431.0 kg. That is 13.746 kg of process loss, 3.09%
        # — shattered grain, spillage off the drying floor, and what the birds
        # took. It is the gap between observed and predicted that Chapter Four
        # §4.3.2 turns on, so a run landing on the theoretical figure would
        # demonstrate nothing. It stays under the 5% data-quality warning, so it
        # reads as a real run rather than a suspect one.
        #
        # 11.5% wb final is below cowpea's 12.0% safe-storage ceiling, so
        # is_safe_to_store returns True rather than None or False.
        "activity_type": "bioprocess",
        "description": "Cowpea solar drying run, 480 kg lot",
        "crop": "cowpea",
        "client_id": "seed-cowpea-drying-0001",
        "extra_data": {
            "process_type": "DRYING", "method": "SOLAR_DRYER",
            "mass_in_kg": 480.0, "mass_out_kg": 431.0,
            "moisture_initial_wb": 18.0, "moisture_final_wb": 11.5,
            "drying_time_hours": 14.0,
            "readings": [
                {"time_hours": 3.0, "moisture_wb": 16.2},
                {"time_hours": 6.0, "moisture_wb": 14.6},
                {"time_hours": 10.0, "moisture_wb": 12.9},
            ],
        },
        "financial_data": {"amount": 14000.0, "transaction_type": "debit", "category": "bioprocess"},
    },

    # --- Sorghum: inputs recorded, nothing sold (the classified loss case) ---
    #
    # 0.75 ha rain-fed. No yield log and no credit anywhere: the crop was grown
    # and never sold. Unlike tomato, every cost row it has is classified, so the
    # pair shows that a loss and a coverage problem are independent things — a
    # farm can know exactly what it spent and still have lost the money.
    {
        "activity_type": "seed",
        "description": "Sorghum seed, 8 kg (0.75 ha)",
        "crop": "sorghum",
        "client_id": "seed-sorghum-seed-0001",
        "financial_data": {"amount": 7200.0, "transaction_type": "debit", "category": "seed"},
    },
    {
        "activity_type": "fertilizer",
        "description": "NPK 15-15-15 (50 kg) and urea (25 kg) for sorghum",
        "crop": "sorghum",
        "client_id": "seed-sorghum-fertilizer-0001",
        "financial_data": {"amount": 52000.0, "transaction_type": "debit", "category": "fertilizer"},
    },
    {
        "activity_type": "labour",
        "description": "Sorghum land prep, planting, weeding and bird-scaring, 14 person-days",
        "crop": "sorghum",
        "client_id": "seed-sorghum-labour-0001",
        "financial_data": {"amount": 42000.0, "transaction_type": "debit", "category": "labour"},
    },
    {
        "activity_type": "mechanization",
        "description": "Diesel for sorghum ploughing, 15 litres",
        "crop": "sorghum",
        "client_id": "seed-sorghum-mech-fuel-0001",
        "extra_data": {"cost_subtype": "FUEL", "equipment_id": TRACTOR, "hours_used": 4.5},
        "financial_data": {"amount": 18750.0, "transaction_type": "debit", "category": "mechanization"},
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


def ensure_equipment(token):
    """Post the demo assets unless the farm already holds them, keyed by name.

    Equipment carries no client_id, so POST /equipment/ has none of the ledger's
    idempotency and a second run would simply create a second tractor. Matching
    on name is the only key available: there is no natural one on the table, and
    there is no update path either (LIMITATIONS §3), so a duplicate could not be
    cleaned up through the API afterwards. Re-running must therefore not create
    one in the first place.

    Returns {name: id} over every asset the farm now holds, so a mechanisation
    row can name the asset it was spent on.
    """
    _, existing = _call("GET", "/equipment/", token=token)
    by_name = {e["name"]: e["id"] for e in existing}

    for asset in EQUIPMENT:
        if asset["name"] in by_name:
            print(f"    equipment {asset['name']:>27} -> already seeded, id={by_name[asset['name']]}")
            continue
        status, body = _call("POST", "/equipment/", token=token, body=asset)
        by_name[asset["name"]] = body.get("id")
        rate = asset["depreciation_rate"]
        print(f"    equipment {asset['name']:>27} -> HTTP {status}, id={body.get('id')}, "
              f"rate={'unrated' if rate is None else f'{rate}%/yr'}")

    return by_name


def resolve(log, equipment_id):
    """Substitute the real equipment id for the TRACTOR sentinel.

    The logs are declared before the farm exists, so they cannot name an id that
    has not been issued yet. Returns a copy: LOGS is module state and a run must
    not mutate it.
    """
    extra = log.get("extra_data")
    if not extra or extra.get("equipment_id") != TRACTOR:
        return log
    return {**log, "extra_data": {**extra, "equipment_id": equipment_id}}


def main():
    # Register the demo farm, or log in if it already exists (idempotent).
    status, body = _call(
        "POST", "/auth/register",
        body={"email": EMAIL, "password": PASSWORD, "farm_name": "Demo Farm"},
    )
    if status == 409:
        status, body = _call("POST", "/auth/login", body={"email": EMAIL, "password": PASSWORD})
    token = body["access_token"]

    # Before the logs: a mechanisation row may name the asset it was spent on,
    # and it needs the id to do it.
    equipment = ensure_equipment(token)
    tractor_id = equipment["Massey Ferguson 375 tractor"]

    for log in LOGS:
        status, body = _call("POST", "/ledger/logs", token=token, body=resolve(log, tractor_id))
        print(f"{log['activity_type']:>13} {log['crop']:>8} -> HTTP {status}, id={body.get('id')} (201=created, 200=already seeded)")

    # Record counts, so a second run proves idempotency without a psql session:
    # both totals must be identical across runs, and every POST above must come
    # back 200 rather than 201.
    _, logs = _call("GET", "/ledger/logs?limit=1000", token=token)
    _, txs = _call("GET", "/ledger/transactions?limit=1000", token=token)
    _, kit = _call("GET", "/equipment/", token=token)
    print(f"records:    {len(logs)} operational logs, {len(txs)} financial transactions, "
          f"{len(kit)} equipment")
    print(f"view DSS:   GET {BASE}/dss/decision-support")
    for route in ("cost-structure", "break-even-price", "sensitivity", "yield-baseline"):
        print(f"            GET {BASE}/dss/{route}?crop=cowpea")


if __name__ == "__main__":
    main()
