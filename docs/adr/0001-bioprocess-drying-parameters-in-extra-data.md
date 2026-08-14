# 1. Bioprocess drying parameters in `extra_data`, not a new table

Status: Accepted

## Context

`BIOPROCESS` has existed as an Activity Category since the domain was first
modelled, but with zero capture path — no way to record the parameters of a
post-harvest processing step. This ticket makes the **Drying Run** a first-class,
measured process.

The data model already anticipated this. `backend/app/models/models.py:76`
carries the `extra_data` JSON column with the comment:

> `extra_data = Column(JSON, nullable=True) # e.g., {"drying_time": 48, "humidity": 12.5}`

The column was designed to hold drying parameters. This decision is therefore
**continuity with the original schema intent, not a workaround**: we implement
what the column was put there for.

The alternative — a dedicated `drying_runs` table with typed columns — was
considered and rejected. It would require an Alembic migration (schema risk),
and the parameter set genuinely differs per process type (drying vs storage
conditioning vs starch hydrolysis), which is exactly the shape a JSON payload
serves well. A rigid table would either be sparse across process types or force
one table per type before we know the others' shapes.

Two supporting conventions are settled here because they are hard to reverse
once data exists:

- **Moisture is entered wet basis, modelled dry basis.** Wet basis (water ÷
  total mass) is what a field moisture meter reads and what a buyer prices
  against, so it is what the farmer enters. Thin-layer drying kinetics are
  conventionally fitted on dry basis. We convert internally and never make the
  user do the arithmetic.
- **Bounds are validated at the schema edge.** A `DryingParams` Pydantic model
  validates the payload before it is stored, rejecting physically impossible
  inputs (mass gain, moisture increase, out-of-range values) with a 422. This is
  the **first place in the codebase where numeric bounds are enforced** —
  LIMITATIONS §3 records that monetary and quantity fields are currently
  unbounded floats. This ticket establishes the validation-at-edge pattern that
  the near-term hardening item will follow.

## Decision

Drying Run parameters are stored in the existing `operational_logs.extra_data`
JSON column, validated on write against a `DryingParams` Pydantic model, and all
derived engineering metrics (dry-matter balance, process loss, drying rate,
thin-layer kinetics, safe-storage verdict) are **computed on read, never
stored** — consistent with the existing deterministic Tier 1 philosophy:
transparent, recomputable, no stale denormalised values.

No new database table and no Alembic migration are introduced.

## Consequences

- A Drying Run inherits, for free, everything an Operational Log already has:
  per-farm scoping, the reversal/immutability machinery, the offline sync queue,
  and the paired-transaction guarantee.
- Because the payload lives in JSON, drying analytics cannot be expressed as
  SQL aggregates over typed columns; they are computed in Python on read from
  the deserialised payload. At this data volume that is a non-issue, and it
  keeps the computation in one testable place (`bioprocess_service.py`, pure
  functions).
- The structure lives in the Pydantic model rather than the schema, so evolving
  the parameter set is a code change, not a migration — the intended trade-off.
- Derived metrics neglect equilibrium moisture content (`M_e`); the moisture
  ratio is `M_db(t) / M_db(0)`. This simplification is stated in the fitter's
  docstring and in LIMITATIONS.

## Demonstration

A seeded demo drying run lets the feature be shown live without typing during
the defence. It is created through the real write path, not a direct database
insert, so it is provably identical to a farmer's record:

```
# backend + db running:
python backend/scripts/seed_bioprocess_demo.py
```

The script registers (or reuses) a "Demo Farm" and posts one Bioprocess drying
run with a fixed `client_id`, so re-running is idempotent — the ledger returns
the existing row rather than duplicating it. It prints the created log id and
the `GET /bioprocess/{id}` URL to view the derived metrics.
