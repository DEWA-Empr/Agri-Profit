# TICKET — Bioprocess: post-harvest drying capture and analysis

**Repo:** `C:\Users\DELL\Desktop\Agri P`
**Label:** `ready-for-agent`
**Why this exists:** `BIOPROCESS` is currently an enum value with zero records and no capture path. This ticket makes post-harvest drying a first-class, measured process, computes real drying engineering from the farmer's own records, and couples the result into the existing per-crop gross margin so that bioprocess becomes structurally necessary to the platform rather than decorative.

---

## 0. Read before writing any code

Read these and report back a one-paragraph summary of what you found **before** starting Phase 1. Do not assume the shapes below are correct — they are inferred from database dumps and documentation, not from the source.

```
CONTEXT.md
backend/app/models/models.py
backend/app/schemas/schemas.py
backend/app/core/enums.py
backend/app/services/ledger_service.py
backend/app/services/dss_service.py
backend/app/api/endpoints/ledger.py
backend/app/api/endpoints/dss.py
backend/app/api/deps.py
backend/app/api/router.py
backend/tests/            (whole directory — match the existing test style exactly)
frontend/package.json     (identify the charting library already in use)
```

Specifically establish:

1. The exact signature of the function that creates an `OperationalLog` + paired `FinancialTransaction`. **Reuse it. Do not write a second write path.**
2. How `extra_data` is currently typed and serialised (the dumps show a `json` column holding JSON `null` on every row — it has never carried a payload).
3. How reversals are represented (migration `d5c1f0a9b8e2`) and how a reversed log is identified in a query.
4. How the per-crop aggregation in `dss_service.py` groups by `crop`, and where unit cost of production is computed.
5. Whether an existing generic log-create endpoint can be extended, versus needing a new one.

---

## 1. Decisions already made — do not relitigate

| Decision | Rationale |
|---|---|
| A Bioprocess is an `OperationalLog` with `activity_type = BIOPROCESS`, **not** a new table | Inherits per-farm scoping, the reversal/immutability machinery, the offline sync queue, and the paired-transaction guarantee for free. `CONTEXT.md` already specifies "optional structured parameters" for Bioprocess. |
| Drying parameters live in the existing `extra_data` JSON column | No migration, therefore no schema risk tonight. The parameter set differs per process type (drying vs storage vs hydrolysis), which is exactly what a JSON payload is for. |
| The payload is **validated by a Pydantic model at the schema edge**, not stored freeform | Structure without a migration. This is the defensible middle and it is what you will write in the thesis. |
| All derived metrics are **computed on read, never stored** | Consistent with the existing deterministic Tier 1 philosophy — transparent, recomputable, no stale denormalised values. |
| Moisture is **entered** as % wet basis and **modelled** on dry basis | Wet basis is what a moisture meter reads and what a farmer is quoted at market. Thin-layer drying models are conventionally fitted on dry basis. Convert internally; never make the user do it. |
| Write an ADR under `docs/adr/` recording the extra_data-vs-table choice | The repo convention requires it, and it becomes a citable artifact for Chapter 3. |

---

## 2. Phase 1 — Domain and documentation

Use the `domain-modeling` skill.

Add to `CONTEXT.md` under **Operations**, in the existing house style (definition, then `_Avoid_:` line):

- **Drying Run** — a single post-harvest drying operation on one crop lot, recorded as an Operational Log with Activity Category Bioprocess, carrying the lot's inlet and outlet mass, inlet and outlet moisture content, duration, air temperature and drying method. *Avoid:* drying session, dry-down, batch.
- **Moisture Content** — the mass fraction of water in a crop lot, entered on a **wet basis** (mass of water ÷ total mass) because that is what field moisture meters report and what buyers price against. Converted to dry basis internally for drying-kinetics modelling. *Avoid:* humidity, water content, moisture level.
- **Marketable Mass** — the outlet mass of a crop after its drying runs; the quantity the farm can actually sell. Where a crop has drying runs, unit cost of production is computed against Marketable Mass rather than harvested wet mass. *Avoid:* net weight, final yield, saleable yield.
- **Process Loss** — the difference between the outlet mass predicted by dry-matter conservation and the outlet mass actually recorded, attributable to spillage, handling and over-drying. A data-quality and efficiency signal, not a financial entry. *Avoid:* shrinkage, wastage, drying loss.

Also update the existing **Bioprocess** entry so it points at Drying Run as the first implemented process type.

---

## 3. Phase 2 — Schema

In `backend/app/schemas/schemas.py`, add:

```python
class DryingReading(BaseModel):
    time_hours: float          # > 0, <= 720
    moisture_wb: float         # > 0, < 100

class DryingParams(BaseModel):
    process_type: Literal["DRYING"]
    method: Literal["SUN", "SOLAR_DRYER", "MECHANICAL", "AMBIENT"]
    mass_in_kg: float          # > 0, <= 100_000
    mass_out_kg: float         # > 0, <= mass_in_kg
    moisture_initial_wb: float # > 0, < 100
    moisture_final_wb: float   # > 0, < moisture_initial_wb
    drying_time_hours: float   # > 0, <= 720
    air_temperature_c: float | None = None   # -10 .. 150
    readings: list[DryingReading] = []       # optional intermediate points
```

Validation requirements — all must return **422**, never 500:

- `mass_out_kg > mass_in_kg` → reject (mass cannot increase during drying).
- `moisture_final_wb >= moisture_initial_wb` → reject (that is wetting, not drying).
- Any negative or zero mass, or a moisture outside `0 < M < 100` → reject.
- `readings` must be strictly increasing in `time_hours`, and every `moisture_wb` must lie in `[moisture_final_wb, moisture_initial_wb]`.

> **Note for the thesis:** LIMITATIONS §3 records that monetary and quantity fields are currently unbounded floats. This ticket is the first place bounds are enforced. Say so in the ADR — it establishes the pattern that the near-term hardening item will follow.

---

## 4. Phase 3 — Service (use the `tdd` skill; write the tests first)

New file `backend/app/services/bioprocess_service.py`. **Pure functions, no database access, no I/O.** They take numbers and return numbers. This is the part that is graded as engineering, so it must be independently testable.

Use `numpy` only (already present via scikit-learn). **Do not add scipy or any new dependency.**

### 4.1 Basis conversion

```
M_db = 100 * M_wb / (100 - M_wb)
M_wb = 100 * M_db / (100 + M_db)
```

### 4.2 Dry-matter balance

Dry matter is conserved through drying:

```
dry_matter        = mass_in * (1 - M_i_wb/100)
mass_out_expected = mass_in * (100 - M_i_wb) / (100 - M_f_wb)
process_loss_kg   = mass_out_expected - mass_out_actual
process_loss_pct  = 100 * process_loss_kg / mass_out_expected
```

`process_loss_kg` may be slightly negative from measurement error; return it signed and do not clamp. Flag `|process_loss_pct| > 5` as a data-quality warning rather than an error.

### 4.3 Water removed and drying rate

```
water_removed_kg   = mass_in - mass_out_actual
drying_rate_kg_h   = water_removed_kg / drying_time_hours
specific_rate      = water_removed_kg / (dry_matter * drying_time_hours)   # kg water / kg dry matter / h
```

### 4.4 Thin-layer drying kinetics

Moisture ratio, on dry basis, with equilibrium moisture neglected (state this simplification in the docstring):

```
MR(t) = M_db(t) / M_db(0)
```

**Newton / Lewis model** — always computable from the two endpoints alone:

```
MR = exp(-k*t)   =>   k = -ln(MR_final) / drying_time_hours
```

**Page model** — only when `len(readings) >= 3`. Linearise and fit with `numpy.polyfit(x, y, 1)`:

```
MR = exp(-k * t**n)
ln(-ln(MR)) = ln(k) + n*ln(t)
x = ln(t),  y = ln(-ln(MR))
=> slope = n,  intercept = ln(k)
```

Guard `0 < MR < 1` before taking the double log; drop any reading that violates it and record how many were dropped. Report the coefficient of determination of the **linearised** fit and label it as such — do not present it as the R² of the model in moisture space.

Return `None` for the Page fit when there are fewer than three usable readings. Never fabricate a fit.

### 4.5 Safe-storage rule (deterministic, explainable)

```
safe = moisture_final_wb <= threshold[crop]
```

| Crop | Safe storage moisture (% wet basis) |
|---|---|
| maize | 13.0 |
| rice (paddy) | 14.0 |
| sorghum | 12.5 |
| millet | 12.0 |
| cowpea | 12.0 |
| groundnut (shelled) | 7.0 |
| soybean | 12.0 |
| cassava chips | 12.0 |
| yam chips | 12.0 |

Unknown crop → return `None` for the verdict, never a default. Put the table in one module-level constant so it is easy to cite and easy to change.

> ⚠ **VERIFY BEFORE THE THESIS.** These are widely used indicative figures for tropical storage, but you must cite a real source for them — FAO post-harvest handling guidance or an IITA/NSPRI publication. An examiner will ask where the numbers came from, and "the agent supplied them" is not an answer. Leave a `# TODO(cite)` on the constant.

---

## 5. Phase 4 — Endpoints

Extend the existing log-create path rather than adding a parallel one:

- **Create.** When `activity_type == BIOPROCESS`, validate `extra_data` against `DryingParams` and reject with 422 on failure. The paired `FinancialTransaction` is a **DEBIT** with category `BIOPROCESS` for the drying cost (fuel, labour, dryer hire). If the cost is zero — sun drying with own labour — still create the paired transaction at 0.00 so the pairing invariant is never violated.
- **Read.** `GET /bioprocess/{id}` returns the stored parameters plus every derived metric from Phase 3.
- **Aggregate.** `GET /bioprocess/summary?crop=` returns, per crop: number of drying runs, total mass in, total marketable mass out, total water removed, mean drying rate, mean Newton k by method, and the share of runs meeting the safe-storage threshold.

All routes go through the existing farm-scoping dependency in `deps.py`. A cross-farm read must 404, consistent with every other resource. Add a test proving it.

**Reversal handling.** Exclude both reversed logs and reversal logs from all bioprocess analytics — a reversal carries no crop and no quantity, so it has no physical parameters and must not enter a mass balance. Add an explicit test.

---

## 6. Phase 5 — DSS coupling (this is the contribution; do not skip it)

In `dss_service.py`, for the per-crop breakdown:

1. Compute `marketable_mass_kg` per crop as the sum of `mass_out_kg` across that crop's non-reversed drying runs.
2. Where `marketable_mass_kg > 0`, compute unit cost of production as **total crop cost (now including drying cost) ÷ marketable mass**, and label the metric so the denominator is unambiguous in the response.
3. Where a crop has no drying runs, fall back to the existing behaviour unchanged.
4. Preserve the current contract from LIMITATIONS §4: unit cost is reported as **undefined**, never a fabricated zero, when there is no quantity to divide by.

**Do this in the same pass:** you are already editing the per-crop aggregation, and LIMITATIONS §3 records that it does not net reversals — after reversing a crop expense, the original crop still shows the reversed cost and a phantom "Unspecified" cost appears. Fix it here by attributing a contra entry to its original's crop. Two known defects, one trip through the code. Add a regression test that reverses a crop expense and asserts no "Unspecified" bucket appears.

---

## 7. Phase 6 — Frontend (only if the backend is complete and tested)

Minimum viable: a drying-run form on the existing log-entry screen, shown when Bioprocess is selected — mass in/out, moisture in/out, hours, method, temperature, optional cost. Then a result panel showing water removed, drying rate, process loss and the safe-storage verdict as a pass/fail chip.

If time allows: a drying curve plotting moisture against time with the fitted Page or Newton curve overlaid, using the charting library already in `package.json`. **Do not add a new charting dependency** — LIMITATIONS §7 already flags the bundle at ~245 KB gzip with no code splitting, and a second chart library would make that finding worse.

---

## 8. Test fixtures — these are hand-calculated and must pass exactly

Use `pytest.approx(..., rel=1e-4)`.

### Fixture A — maize, with process loss

Input: `mass_in = 100 kg`, `M_i = 25 %wb`, `M_f = 13 %wb`, `t = 10 h`, `mass_out_actual = 84.0 kg`, crop `maize`

| Quantity | Expected |
|---|---|
| dry matter | 75.0000 kg |
| mass_out_expected | 86.2069 kg |
| process_loss_kg | 2.2069 kg |
| process_loss_pct | 2.560 % |
| water_removed_kg | 16.0000 kg (from actual outlet mass) |
| M_i dry basis | 33.3333 % |
| M_f dry basis | 14.9425 % |
| MR_final | 0.448276 |
| Newton k | 0.080235 /h |
| safe storage (maize, 13.0) | True (at threshold) |

> Note the deliberate distinction: `water_removed_kg` uses the **actual** outlet mass (16.0 kg), while `process_loss_kg` compares actual against the **dry-matter-predicted** outlet (86.2069 kg). Keep these two separate — conflating them is the easiest bug to write here.

### Fixture B — rice paddy, clean balance

Input: `mass_in = 500 kg`, `M_i = 22 %wb`, `M_f = 13.5 %wb`, `t = 18 h`, `mass_out_actual = 450.8671 kg`, crop `rice`

| Quantity | Expected |
|---|---|
| dry matter | 390.0000 kg |
| mass_out_expected | 450.8671 kg |
| process_loss_kg | 0.0000 kg |
| water_removed_kg | 49.1329 kg |
| drying_rate_kg_h | 2.7296 kg/h |
| MR_final | 0.553337 |
| Newton k | 0.032877 /h |
| safe storage (rice, 14.0) | True |

### Fixture C — Page model, exact recovery

Constructed from a known Page curve with `M_0 = 30.0 %wb`, `k = 0.30`, `n = 0.75`. Readings (`time_hours`, `moisture_wb`):

```
(1, 24.098299)
(2, 20.557042)
(4, 15.501120)
(6, 11.947665)
(8,  9.326998)
```

The fit must recover `n = 0.750000`, `k = 0.300000`, linearised R² = `1.000000`. If your implementation does not return these to four decimal places, the basis conversion or the linearisation is wrong — fix it before moving on.

### Fixture D — rejections (all 422, none 500)

- `mass_out_kg = 110` with `mass_in_kg = 100`
- `moisture_final_wb = 25` with `moisture_initial_wb = 20`
- `mass_in_kg = -5`
- `moisture_initial_wb = 105`
- `readings` out of time order
- unknown crop → summary returns `safe_storage: null`, not `false`

### Fixture E — isolation and reversals

- A drying run created under farm A is 404 for a token from farm B.
- A reversed drying run is excluded from `GET /bioprocess/summary`.
- Reversing a crop expense produces no "Unspecified" crop bucket in the DSS per-crop breakdown.

---

## 9. Definition of done

- [ ] All fixtures A–E pass.
- [ ] `pytest --cov` shows `bioprocess_service.py` at 100 % — it is pure functions, there is no excuse for less.
- [ ] Overall coverage has not dropped below the current 88 %.
- [ ] `CONTEXT.md` updated with the four new terms.
- [ ] ADR written under `docs/adr/` covering the extra_data-vs-table decision and the wet/dry basis convention.
- [ ] One seeded demo drying run exists so the feature can be shown live without typing during the defence.
- [ ] No new Python or JavaScript dependency added.
- [ ] No Alembic migration created.

## 10. Explicitly out of scope tonight

Storage-condition monitoring; starch hydrolysis; rehydration; equilibrium moisture content modelling (we neglect `M_e` and say so); multi-stage drying runs; energy consumption and specific energy per kg water removed; anything touching the ML forecast tier.

If you find yourself editing `ml/`, stop — you have gone out of scope.

---

## Comments

### 2026-08-19 — Phase 6 (frontend) implemented

Phases 1–5 were already on `feat/bioprocess-drying`; Phase 6 was the outstanding
gap — the backend shipped `/bioprocess/*` with no frontend consumer at all, and
`FarmRecordCreateForm` had removed the Bioprocess option outright (its comment
explained why: an unvalidatable payload would have poisoned the offline queue).

Built to §7's "minimum viable":

- `types/domain.ts` — mirrors of `DryingParams`, `DryingMetrics`,
  `BioprocessDetail`, `BioprocessCropSummary`, `BioprocessSummary`.
- `lib/apiClient.ts` — `bioprocessService` (read-only: `getRun`, `getSummary`).
  Runs are still created through `ledgerService.createLog`; no second write path.
- `farm-records/dryingParams.ts` — form state + `buildDryingParams`, which
  mirrors the backend field bounds **and** `_check_physical_consistency`. This
  is what makes the Bioprocess option safe to re-offer: an invalid payload is
  rejected before it can be queued in IndexedDB, so the permanently-422 record
  the old comment warned about cannot be created. Unit-tested against Fixture D
  in `dryingParams.test.ts`.
- `farm-records/DryingFields.tsx` — method, mass in/out, moisture in/out (wet
  basis), drying time, optional air temperature; shown only for Bioprocess.
- `farm-records/DryingRunResult.tsx` — the result panel: water removed, drying
  rate, process loss (kg, %, against the dry-matter-predicted outlet), the
  safe-storage verdict as a pass / fail / unknown chip (unknown crop shows as
  unknown, never as a failure), plus dry matter, moisture ratio and Newton k
  with the Page fit when the run has one.

Verified end to end against the running API: the exact payload the form emits
creates a run (201), `GET /bioprocess/{id}` returns every field the panel reads,
`GET /bioprocess/summary` aggregates it, and `mass_out_kg > mass_in_kg` is a 422
that the client-side validator also blocks.

Not built (§7 "if time allows"): the drying-curve chart. It needs intermediate
readings, and the form does not collect them yet — a curve through two endpoints
would just be the Newton fit drawn back at itself. Collecting `readings[]` is
the natural next slice, and it is also what unlocks the Page model in the UI.

Note for §8: Fixture A's `water_removed_kg = 16.0 kg` is superseded by commit
8690289 — water removed is a water balance (14.08 kg), not the mass difference.
