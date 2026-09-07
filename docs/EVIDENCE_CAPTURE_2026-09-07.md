# Evidence capture — 2026-09-07

Verbatim API payloads and database census for **farm 26**, captured at commit
**`598eab0`**. Nothing in this document is retyped, rounded or reconciled: every
block below is the response body exactly as returned.

**This document captures. It corrects nothing.** No thesis figure was changed on
the basis of it.

---

## 1. Capture identity

| | |
| --- | --- |
| Commit (code state) | `598eab0a02533e9692332d92382d42f16fc9e346` |
| Working `HEAD` at capture | `da57b2022f182e7a28296fd16fbb3391c76f8a08` |
| Why they differ | `da57b20` is the docs-only commit recording the freeze; `git diff 598eab0 HEAD -- backend/ frontend/` is **empty**, so the running code is byte-identical to `598eab0` |
| Capture date | 7 September 2026 |
| Farm | 26, `Demo Farm` |
| Signed in as | `demo-bioprocess-v2@test.example` (user id 25), farm 26's own user |
| Backend image | rebuilt from this tree (`docker compose up -d --build db backend`) |
| Alembic revision | `b9e5f30c74a1` |

### 1.1 Which composition was used, and why not the production one

**The dev composition (`docker-compose.yml`) was used, not `docker-compose.prod.yml`.**

This is deliberate and material. The production composition mounts the named
volume `postgres_data_prod`, which **does not exist on this host** — the only
project volume is `agrip_postgres_data`, belonging to the dev composition.
Bringing up the production stack would have created an empty database, run the
Alembic chain onto it, and produced a capture containing no farm 26 at all. It
also requires a `.env` supplying `POSTGRES_DB` and `POSTGRES_USER`, and the
repository tracks only `.env.example`.

The dev composition is where farm 26's data lives, and it is the same stack the
29 August freeze used for its own census (`docker start agrip-db-1`, then
`docker exec agrip-db-1 psql -U postgres -d agriprofit`).

### 1.2 Commands used

```
git diff --stat 598eab0 HEAD -- backend/ frontend/     # empty: code == 598eab0
docker compose up -d --build db backend

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"email":"demo-bioprocess-v2@test.example","password":"demo-bioprocess-pw"}'   | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

H="Authorization: Bearer $TOKEN"
B=http://localhost:8000/api/v1

curl -s -H "$H" "$B/dss/cost-structure"
for c in maize cowpea cassava tomato sorghum; do
  curl -s -H "$H" "$B/dss/cost-structure?crop=$c"
done
curl -s -H "$H" "$B/dss/decision-support"
curl -s -H "$H" "$B/dss/break-even-price"
curl -s -H "$H" "$B/dss/sensitivity"
curl -s -H "$H" "$B/dss/yield-baseline"
curl -s -H "$H" "$B/equipment/"
curl -s -H "$H" "$B/bioprocess/summary"
curl -s -H "$H" "$B/reports/pnl"
```

Census:

```
docker exec agrip-db-1 psql -U postgres -d agriprofit -tAc   "SELECT count(*) FROM <table>;"          # per table
docker exec agrip-db-1 psql -U postgres -d agriprofit -tAc   "SELECT version_num FROM alembic_version;"
docker exec agrip-db-1 psql -U postgres -d agriprofit -tAc   "SELECT count(*) FROM operational_logs WHERE financial_transaction_id IS NULL;"
docker exec agrip-db-1 psql -U postgres -d agriprofit -tAc   "SELECT farm_id, count(*) FROM operational_logs GROUP BY farm_id ORDER BY farm_id;"
```

Note on the unpaired query: the pairing link is
`operational_logs.financial_transaction_id`. There is no
`financial_transactions.operational_log_id` column — a join written that way
errors rather than returning rows.

---

## 2. Live database census

Queried 7 September 2026 against the running `agriprofit` database.

| Table | 29 Aug 2026 (freeze §4) | **7 Sep 2026** | Delta |
| --- | --- | --- | --- |
| `farms` | 14 | **15** | **+1** |
| `users` | 13 | **14** | **+1** |
| `operational_logs` | 109 | **110** | **+1** |
| `financial_transactions` | 109 | **110** | **+1** |
| `equipment` | 3 | **3** | 0 |
| `maintenance_logs` | 1 | **1** | 0 |
| `share_tokens` | 10 | **12** | **+2** |
| `alembic_version` | `b9e5f30c74a1` | **`b9e5f30c74a1`** | unchanged |
| Unpaired operational logs | 0 | **0** | unchanged |

### 2.1 What changed, and why farm 26 did not

Per-farm operational-log counts:

```
farm_id |  1 |  3 |  4 | 17 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 30
count   | 34 |  4 |  9 |  2 |  7 |  3 |  5 |  4 |  3 |  5 |  5 | 28 |  1
```

Every farm present on 25 August carries an identical count to
`docs/DATA_CLEANUP_2026-08-25.md` §4, **farm 26 included at 28 logs**. The entire
delta is one new farm:

| | |
| --- | --- |
| Farm | **30, `Miller Farms`** |
| Created | 2026-09-01 17:50:20 UTC |
| Holds | 1 operational log (id 1081), a `BIOPROCESS` / `DRYING` maize run with three intermediate readings |
| Logged | 2026-09-01 17:54:12 UTC |

Farm 26's most recent write is **2026-08-24 19:51:33 UTC**. Nothing has been
written to farm 26 since 24 August 2026.

This resolves the open question raised against commit `ef270a9` (A-07), whose
message records verifying a mechanisation cost "against the demo farm" and moving
a crop's classification coverage from 44.0% to 46.5%. **That write landed on
farm 30, not farm 26.** Farm 26's cost structure is untouched, and §4 of the
paired-write invariant still holds across the whole database: zero unpaired logs
at 110/110.

---

## 3. Payloads, verbatim

All responses HTTP 200, farm 26, 7 September 2026, commit `598eab0`.

### GET /api/v1/dss/cost-structure

```json
{
  "crops": [
    {
      "variable_cost": 94400.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 94400.0,
      "cash_cost": 94400.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 178600.0,
      "cash_operating_cost_ngn": 94400.0,
      "operating_expense_ratio_pct": 52.8555431131019,
      "crop": "cassava"
    },
    {
      "variable_cost": 202200.0,
      "semi_variable_cost": 26500.0,
      "fixed_cost_recorded": 18000.0,
      "unclassified_cost": 21000.0,
      "total_recorded_cost": 267700.0,
      "cash_cost": 228700.0,
      "classification_coverage_pct": 92.1553978333956,
      "revenue_ngn": 624950.0,
      "cash_operating_cost_ngn": 249700.0,
      "operating_expense_ratio_pct": 39.95519641571326,
      "crop": "cowpea"
    },
    {
      "variable_cost": 3500.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 3500.0,
      "cash_cost": 3500.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 45000.0,
      "cash_operating_cost_ngn": 3500.0,
      "operating_expense_ratio_pct": 7.777777777777778,
      "crop": "maize"
    },
    {
      "variable_cost": 119950.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 119950.0,
      "cash_cost": 119950.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 0.0,
      "cash_operating_cost_ngn": 119950.0,
      "operating_expense_ratio_pct": null,
      "crop": "sorghum"
    },
    {
      "variable_cost": 63600.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 49300.0,
      "total_recorded_cost": 112900.0,
      "cash_cost": 63600.0,
      "classification_coverage_pct": 56.33303808680248,
      "revenue_ngn": 0.0,
      "cash_operating_cost_ngn": 112900.0,
      "operating_expense_ratio_pct": null,
      "crop": "tomato"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/cost-structure?crop=maize

```json
{
  "crops": [
    {
      "variable_cost": 3500.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 3500.0,
      "cash_cost": 3500.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 45000.0,
      "cash_operating_cost_ngn": 3500.0,
      "operating_expense_ratio_pct": 7.777777777777778,
      "crop": "maize"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/cost-structure?crop=cowpea

```json
{
  "crops": [
    {
      "variable_cost": 202200.0,
      "semi_variable_cost": 26500.0,
      "fixed_cost_recorded": 18000.0,
      "unclassified_cost": 21000.0,
      "total_recorded_cost": 267700.0,
      "cash_cost": 228700.0,
      "classification_coverage_pct": 92.1553978333956,
      "revenue_ngn": 624950.0,
      "cash_operating_cost_ngn": 249700.0,
      "operating_expense_ratio_pct": 39.95519641571326,
      "crop": "cowpea"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/cost-structure?crop=cassava

```json
{
  "crops": [
    {
      "variable_cost": 94400.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 94400.0,
      "cash_cost": 94400.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 178600.0,
      "cash_operating_cost_ngn": 94400.0,
      "operating_expense_ratio_pct": 52.8555431131019,
      "crop": "cassava"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/cost-structure?crop=tomato

```json
{
  "crops": [
    {
      "variable_cost": 63600.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 49300.0,
      "total_recorded_cost": 112900.0,
      "cash_cost": 63600.0,
      "classification_coverage_pct": 56.33303808680248,
      "revenue_ngn": 0.0,
      "cash_operating_cost_ngn": 112900.0,
      "operating_expense_ratio_pct": null,
      "crop": "tomato"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/cost-structure?crop=sorghum

```json
{
  "crops": [
    {
      "variable_cost": 119950.0,
      "semi_variable_cost": 0.0,
      "fixed_cost_recorded": 0.0,
      "unclassified_cost": 0.0,
      "total_recorded_cost": 119950.0,
      "cash_cost": 119950.0,
      "classification_coverage_pct": 100.0,
      "revenue_ngn": 0.0,
      "cash_operating_cost_ngn": 119950.0,
      "operating_expense_ratio_pct": null,
      "crop": "sorghum"
    }
  ],
  "farm": {
    "variable_cost": 483650.0,
    "semi_variable_cost": 26500.0,
    "fixed_cost_recorded": 18000.0,
    "unclassified_cost": 70300.0,
    "total_recorded_cost": 598450.0,
    "cash_cost": 510150.0,
    "classification_coverage_pct": 88.25298688278052,
    "revenue_ngn": 848550.0,
    "cash_operating_cost_ngn": 580450.0,
    "operating_expense_ratio_pct": 68.40492605032114
  }
}
```

### GET /api/v1/dss/decision-support

```json
{
  "crops": [
    {
      "crop": "cowpea",
      "revenue": 624950.0,
      "expenses": 267700.0,
      "gross_margin": 357250.0,
      "yield_quantity": 480.0,
      "yield_unit": "kg",
      "yield_by_unit": [
        {
          "unit": "kg",
          "quantity": 480.0
        }
      ],
      "unit_cost_of_production": 557.7083333333334,
      "marketable_mass_kg": 431.0,
      "unit_cost_per_kg_marketable": 621.1136890951276,
      "break_even_yield": 205.6100488039043,
      "break_even_unit": "kg"
    },
    {
      "crop": "cassava",
      "revenue": 178600.0,
      "expenses": 94400.0,
      "gross_margin": 84200.0,
      "yield_quantity": 1880.0,
      "yield_unit": "kg",
      "yield_by_unit": [
        {
          "unit": "kg",
          "quantity": 1880.0
        }
      ],
      "unit_cost_of_production": 50.212765957446805,
      "marketable_mass_kg": null,
      "unit_cost_per_kg_marketable": null,
      "break_even_yield": 993.6842105263158,
      "break_even_unit": "kg"
    },
    {
      "crop": "maize",
      "revenue": 45000.0,
      "expenses": 3500.0,
      "gross_margin": 41500.0,
      "yield_quantity": 100.0,
      "yield_unit": "kg",
      "yield_by_unit": [
        {
          "unit": "kg",
          "quantity": 100.0
        }
      ],
      "unit_cost_of_production": 35.0,
      "marketable_mass_kg": 84.0,
      "unit_cost_per_kg_marketable": 41.666666666666664,
      "break_even_yield": 7.777777777777778,
      "break_even_unit": "kg"
    },
    {
      "crop": "tomato",
      "revenue": 0.0,
      "expenses": 112900.0,
      "gross_margin": -112900.0,
      "yield_quantity": 0.0,
      "yield_unit": null,
      "yield_by_unit": [],
      "unit_cost_of_production": null,
      "marketable_mass_kg": null,
      "unit_cost_per_kg_marketable": null,
      "break_even_yield": null,
      "break_even_unit": null
    },
    {
      "crop": "sorghum",
      "revenue": 0.0,
      "expenses": 119950.0,
      "gross_margin": -119950.0,
      "yield_quantity": 0.0,
      "yield_unit": null,
      "yield_by_unit": [],
      "unit_cost_of_production": null,
      "marketable_mass_kg": null,
      "unit_cost_per_kg_marketable": null,
      "break_even_yield": null,
      "break_even_unit": null
    }
  ],
  "overall": {
    "revenue": 848550.0,
    "expenses": 598450.0,
    "gross_margin": 250100.0
  }
}
```

### GET /api/v1/dss/break-even-price

```json
{
  "crops": [
    {
      "crop": "cassava",
      "break_even_price_cash_ngn_per_kg": null,
      "break_even_price_total_ngn_per_kg": null,
      "variable_and_semi_variable_cost_ngn": 94400.0,
      "total_recorded_cost_ngn": 94400.0,
      "allocated_fixed_ngn": 1588.2124712585137,
      "total_cost_ngn": 95988.2124712585,
      "marketable_mass_kg": null,
      "classification_coverage_pct": 100.0
    },
    {
      "crop": "cowpea",
      "break_even_price_cash_ngn_per_kg": 530.6264501160093,
      "break_even_price_total_ngn_per_kg": 631.5634826024396,
      "variable_and_semi_variable_cost_ngn": 228700.0,
      "total_recorded_cost_ngn": 267700.0,
      "allocated_fixed_ngn": 4503.861001651527,
      "total_cost_ngn": 272203.8610016515,
      "marketable_mass_kg": 431.0,
      "classification_coverage_pct": 92.1553978333956
    },
    {
      "crop": "maize",
      "break_even_price_cash_ngn_per_kg": 41.666666666666664,
      "break_even_price_total_ngn_per_kg": 42.36767852721509,
      "variable_and_semi_variable_cost_ngn": 3500.0,
      "total_recorded_cost_ngn": 3500.0,
      "allocated_fixed_ngn": 58.884996286067775,
      "total_cost_ngn": 3558.8849962860677,
      "marketable_mass_kg": 84.0,
      "classification_coverage_pct": 100.0
    },
    {
      "crop": "sorghum",
      "break_even_price_cash_ngn_per_kg": null,
      "break_even_price_total_ngn_per_kg": null,
      "variable_and_semi_variable_cost_ngn": 119950.0,
      "total_recorded_cost_ngn": 119950.0,
      "allocated_fixed_ngn": 2018.0729441468084,
      "total_cost_ngn": 121968.07294414681,
      "marketable_mass_kg": null,
      "classification_coverage_pct": 100.0
    },
    {
      "crop": "tomato",
      "break_even_price_cash_ngn_per_kg": null,
      "break_even_price_total_ngn_per_kg": null,
      "variable_and_semi_variable_cost_ngn": 63600.0,
      "total_recorded_cost_ngn": 112900.0,
      "allocated_fixed_ngn": 1899.4617373420147,
      "total_cost_ngn": 114799.46173734202,
      "marketable_mass_kg": null,
      "classification_coverage_pct": 56.33303808680248
    }
  ],
  "period_days": 7.0,
  "period_source": "derived",
  "period_fixed_cost_ngn": 10068.493150684932,
  "equipment_count": 2,
  "equipment_unrated_count": 1,
  "total_direct_cost_all_crops": 598450.0
}
```

### GET /api/v1/dss/sensitivity

```json
{
  "crops": [
    {
      "crop": "cassava",
      "conditional": true,
      "baseline_marketable_mass_kg": null,
      "cash_cost_ngn": 94400.0,
      "total_cost_ngn": 95988.2124712585,
      "rows": [
        {
          "percentage": 75,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 90,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 100,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 110,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 125,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        }
      ]
    },
    {
      "crop": "cowpea",
      "conditional": true,
      "baseline_marketable_mass_kg": 431.0,
      "cash_cost_ngn": 228700.0,
      "total_cost_ngn": 272203.8610016515,
      "rows": [
        {
          "percentage": 75,
          "marketable_mass_kg": 323.25,
          "break_even_price_cash_ngn_per_kg": 707.5019334880124,
          "break_even_price_total_ngn_per_kg": 842.0846434699196
        },
        {
          "percentage": 90,
          "marketable_mass_kg": 387.9,
          "break_even_price_cash_ngn_per_kg": 589.5849445733437,
          "break_even_price_total_ngn_per_kg": 701.7372028915997
        },
        {
          "percentage": 100,
          "marketable_mass_kg": 431.0,
          "break_even_price_cash_ngn_per_kg": 530.6264501160093,
          "break_even_price_total_ngn_per_kg": 631.5634826024396
        },
        {
          "percentage": 110,
          "marketable_mass_kg": 474.1,
          "break_even_price_cash_ngn_per_kg": 482.3876819236448,
          "break_even_price_total_ngn_per_kg": 574.1486205476724
        },
        {
          "percentage": 125,
          "marketable_mass_kg": 538.75,
          "break_even_price_cash_ngn_per_kg": 424.5011600928074,
          "break_even_price_total_ngn_per_kg": 505.25078608195173
        }
      ]
    },
    {
      "crop": "maize",
      "conditional": true,
      "baseline_marketable_mass_kg": 84.0,
      "cash_cost_ngn": 3500.0,
      "total_cost_ngn": 3558.8849962860677,
      "rows": [
        {
          "percentage": 75,
          "marketable_mass_kg": 63.0,
          "break_even_price_cash_ngn_per_kg": 55.55555555555556,
          "break_even_price_total_ngn_per_kg": 56.49023803628679
        },
        {
          "percentage": 90,
          "marketable_mass_kg": 75.6,
          "break_even_price_cash_ngn_per_kg": 46.2962962962963,
          "break_even_price_total_ngn_per_kg": 47.075198363572326
        },
        {
          "percentage": 100,
          "marketable_mass_kg": 84.0,
          "break_even_price_cash_ngn_per_kg": 41.666666666666664,
          "break_even_price_total_ngn_per_kg": 42.36767852721509
        },
        {
          "percentage": 110,
          "marketable_mass_kg": 92.4,
          "break_even_price_cash_ngn_per_kg": 37.878787878787875,
          "break_even_price_total_ngn_per_kg": 38.516071388377355
        },
        {
          "percentage": 125,
          "marketable_mass_kg": 105.0,
          "break_even_price_cash_ngn_per_kg": 33.333333333333336,
          "break_even_price_total_ngn_per_kg": 33.89414282177207
        }
      ]
    },
    {
      "crop": "sorghum",
      "conditional": true,
      "baseline_marketable_mass_kg": null,
      "cash_cost_ngn": 119950.0,
      "total_cost_ngn": 121968.07294414681,
      "rows": [
        {
          "percentage": 75,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 90,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 100,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 110,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 125,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        }
      ]
    },
    {
      "crop": "tomato",
      "conditional": true,
      "baseline_marketable_mass_kg": null,
      "cash_cost_ngn": 63600.0,
      "total_cost_ngn": 114799.46173734202,
      "rows": [
        {
          "percentage": 75,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 90,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 100,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 110,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        },
        {
          "percentage": 125,
          "marketable_mass_kg": null,
          "break_even_price_cash_ngn_per_kg": null,
          "break_even_price_total_ngn_per_kg": null
        }
      ]
    }
  ],
  "period_days": 7.0,
  "period_source": "derived"
}
```

### GET /api/v1/dss/yield-baseline

```json
{
  "crops": [
    {
      "crop": "cassava",
      "olympic_average_kg": null,
      "grand_average_kg": 1880.0,
      "n_seasons": 1,
      "n_used": 0,
      "n_discarded": 0,
      "unit": "kg",
      "reason": "An Olympic average needs at least 3 seasons; this crop has 1. The grand average is shown instead."
    },
    {
      "crop": "cowpea",
      "olympic_average_kg": null,
      "grand_average_kg": 480.0,
      "n_seasons": 1,
      "n_used": 0,
      "n_discarded": 0,
      "unit": "kg",
      "reason": "An Olympic average needs at least 3 seasons; this crop has 1. The grand average is shown instead."
    },
    {
      "crop": "maize",
      "olympic_average_kg": null,
      "grand_average_kg": 100.0,
      "n_seasons": 1,
      "n_used": 0,
      "n_discarded": 0,
      "unit": "kg",
      "reason": "An Olympic average needs at least 3 seasons; this crop has 1. The grand average is shown instead."
    },
    {
      "crop": "sorghum",
      "olympic_average_kg": null,
      "grand_average_kg": null,
      "n_seasons": 0,
      "n_used": 0,
      "n_discarded": 0,
      "unit": null,
      "reason": "No yield has been recorded for this crop."
    },
    {
      "crop": "tomato",
      "olympic_average_kg": null,
      "grand_average_kg": null,
      "n_seasons": 0,
      "n_used": 0,
      "n_discarded": 0,
      "unit": null,
      "reason": "No yield has been recorded for this crop."
    }
  ]
}
```

### GET /api/v1/equipment/

```json
[
  {
    "name": "Massey Ferguson 375 tractor",
    "model": "MF375",
    "purchase_date": null,
    "purchase_price": 4200000.0,
    "depreciation_rate": 12.5,
    "id": 6,
    "updated_at": null
  },
  {
    "name": "Multi-crop thresher",
    "model": "IAR T-90",
    "purchase_date": null,
    "purchase_price": 850000.0,
    "depreciation_rate": null,
    "id": 7,
    "updated_at": null
  }
]
```

### GET /api/v1/bioprocess/summary

```json
{
  "crops": [
    {
      "crop": "cowpea",
      "drying_runs": 1,
      "total_mass_in_kg": 480.0,
      "total_marketable_mass_kg": 431.0,
      "total_water_removed_kg": 36.83500000000001,
      "mean_drying_rate_kg_h": 2.631071428571429,
      "mean_newton_k_by_method": {
        "SOLAR_DRYER": 0.03745057337689937
      },
      "safe_storage_share": 1.0
    },
    {
      "crop": "maize",
      "drying_runs": 1,
      "total_mass_in_kg": 100.0,
      "total_marketable_mass_kg": 84.0,
      "total_water_removed_kg": 14.08,
      "mean_drying_rate_kg_h": 1.408,
      "mean_newton_k_by_method": {
        "SOLAR_DRYER": 0.08023464725249374
      },
      "safe_storage_share": 1.0
    }
  ]
}
```

### GET /api/v1/reports/pnl

```json
{
  "revenue": 848550.0,
  "expenses": 598450.0,
  "gross_margin": 250100.0,
  "categories": [
    {
      "category": "seed",
      "revenue": 0.0,
      "expenses": 45400.0,
      "net": -45400.0
    },
    {
      "category": "fertilizer",
      "revenue": 0.0,
      "expenses": 146300.0,
      "net": -146300.0
    },
    {
      "category": "labour",
      "revenue": 0.0,
      "expenses": 162000.0,
      "net": -162000.0
    },
    {
      "category": "mechanization",
      "revenue": 0.0,
      "expenses": 215550.0,
      "net": -215550.0
    },
    {
      "category": "yield",
      "revenue": 848550.0,
      "expenses": 0.0,
      "net": 848550.0
    },
    {
      "category": "bioprocess",
      "revenue": 0.0,
      "expenses": 17500.0,
      "net": -17500.0
    },
    {
      "category": "other",
      "revenue": 0.0,
      "expenses": 11700.0,
      "net": -11700.0
    }
  ]
}
```

