# Chapter Four — data pack

Everything needed to finish Chapter Four, assembled from the artefacts produced
in Phases 0–4 of this branch. Every figure below is copied from a command
output, an endpoint response or a committed file. Nothing is retyped from the
chapter, and nothing is rounded, reconciled or tidied on the way in.

Measured 2026-08-19 on branch `feat/bioprocess-drying` at `e3bb674`.

> **Superseded for current figures — kept as a dated capture, not corrected.**
> This pack records what was measured on 2026-08-19 at `e3bb674`, and its
> numbers are left exactly as captured because rewriting a dated measurement
> would destroy the evidence it exists to be. They are **not** current: the
> suite has since grown and two defects have been fixed. For the state of the
> repository today see `docs/STATE_REPORT_2026-08-25.md` (the read-only audit of
> 2026-08-25) and `docs/EVIDENCE.md` (the commands behind every current figure).
> Two figures below have moved furthest: the backend suite is now 190 tests at
> 93% (1,286 statements, 91 missed), and §7's "there is **no readings input** on
> the form" is no longer true — the form collects intermediate readings and the
> result panel draws the drying curve from them. The current figures are frozen
> at tag `thesis-evidence-freeze-2026-08-25`; see
> `docs/EVIDENCE_FREEZE_2026-08-25.md`.

Sources: `docs/ch4-data/dss_per_crop.json`, `dss_break_even.json`,
`bioprocess_summary.json`, `model_info.json`, `screenshot-runsheet.md`, and two
live test runs reproduced below.

---

## 1 · Test suite

### 1.1 Backend — final state

**91 tests, 91 passed, 0 failed.** Overall coverage **91%** of `backend/app`
(1,043 statements, 98 missed).

Modules below 100%:

| Module | Stmts | Miss | Cover |
|---|---|---|---|
| `backend/app/ml/dataset.py` | 50 | 32 | **36%** |
| `backend/app/ml/train.py` | 53 | 31 | **42%** |
| `backend/app/models/database.py` | 11 | 4 | **64%** |
| `backend/app/api/deps.py` | 20 | 3 | **85%** |
| `backend/app/services/ledger_service.py` | 56 | 8 | **86%** |
| `backend/app/main.py` | 48 | 6 | **88%** |
| `backend/app/api/endpoints/dss.py` | 28 | 3 | **89%** |
| `backend/app/ml/predict.py` | 46 | 4 | **91%** |
| `backend/app/core/security.py` | 30 | 2 | **93%** |
| `backend/app/services/reports_service.py` | 68 | 4 | **94%** |
| `backend/app/api/endpoints/auth.py` | 21 | 1 | **95%** |

Every other module under `backend/app` is at 100%, including all four the
branch touched: `services/bioprocess_service.py` (68/68),
`services/dss_service.py` (59/59), `api/endpoints/bioprocess.py` (54/54) and
`schemas/schemas.py` (121/121).

The three lowest are the machine-learning training path (`dataset.py`,
`train.py`) and the engine factory (`database.py`). Those run at container boot,
not under the test client, which uses its own in-memory SQLite engine and the
already-fitted model artefact.

### 1.2 Backend — `pytest --cov` tail, pasted raw

Command, from the repo root:

```
DATABASE_URL="sqlite:///./test.db" python -m pytest --cov=backend/app
```

```
============================== warnings summary ===============================
..\..\AppData\Roaming\Python\Python314\site-packages\fastapi\testclient.py:1
  C:\Users\DELL\AppData\Roaming\Python\Python314\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.5-final-0 _______________

Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
backend\app\__init__.py                          0      0   100%
backend\app\api\__init__.py                      0      0   100%
backend\app\api\deps.py                         20      3    85%
backend\app\api\endpoints\__init__.py            0      0   100%
backend\app\api\endpoints\auth.py               21      1    95%
backend\app\api\endpoints\bioprocess.py         54      0   100%
backend\app\api\endpoints\dss.py                28      3    89%
backend\app\api\endpoints\equipment.py          21      0   100%
backend\app\api\endpoints\investor.py           22      0   100%
backend\app\api\endpoints\ledger.py             34      0   100%
backend\app\api\endpoints\reports.py            20      0   100%
backend\app\api\router.py                       10      0   100%
backend\app\core\__init__.py                     0      0   100%
backend\app\core\config.py                      18      0   100%
backend\app\core\enums.py                       12      0   100%
backend\app\core\exceptions.py                  16      0   100%
backend\app\core\security.py                    30      2    93%
backend\app\main.py                             48      6    88%
backend\app\ml\__init__.py                       0      0   100%
backend\app\ml\dataset.py                       50     32    36%
backend\app\ml\predict.py                       46      4    91%
backend\app\ml\train.py                         53     31    42%
backend\app\models\__init__.py                   0      0   100%
backend\app\models\database.py                  11      4    64%
backend\app\models\models.py                    76      0   100%
backend\app\schemas\__init__.py                  0      0   100%
backend\app\schemas\schemas.py                 121      0   100%
backend\app\services\__init__.py                 0      0   100%
backend\app\services\auth_service.py            22      0   100%
backend\app\services\bioprocess_service.py      68      0   100%
backend\app\services\dss_service.py             59      0   100%
backend\app\services\equipment_service.py       27      0   100%
backend\app\services\ledger_service.py          56      8    86%
backend\app\services\reports_service.py         68      4    94%
backend\app\services\share_service.py           32      0   100%
----------------------------------------------------------------
TOTAL                                         1043     98    91%
======================= 91 passed, 1 warning in 57.01s ========================
```

Collection line from the same run:

```
collected 91 items

backend\tests\test_api.py .............................................. [ 50%]
..................................                                       [ 87%]
backend\tests\test_bioprocess_service.py ...........                     [100%]
```

**Caveat the chapter must carry.** The repository has no `pytest.ini`,
`setup.cfg`, `pyproject.toml` or `.coveragerc`, so bare `--cov` has no
configured source and measures the test files too. Run that way the same suite
reports **TOTAL 1866 stmts, 99 miss, 95%** — the four-point difference is
entirely `conftest.py` (51/51), `test_api.py` (684 stmts, 1 miss, 99%) and
`test_bioprocess_service.py` (88/88) inflating the denominator with test code.
**91% is the figure to quote**: it is application code only, and it is what the
branch's commit messages carry.

### 1.3 Frontend — final state

**21 tests across 4 test files, 21 passed, 0 failed.**

```
 Test Files  4 passed (4)
      Tests  21 passed (21)
   Start at  05:03:21
   Duration  5.89s (transform 247ms, setup 0ms, import 813ms, tests 316ms, environment 7.94s)
```

Coverage summary, raw:

```
Statements   : 10.33% ( 86/832 )
Branches     : 7.27% ( 42/577 )
Functions    : 6.22% ( 19/305 )
Lines        : 9.62% ( 72/748 )
```

Per-file table, raw (`npm run test:coverage`, provider v8):

```
 % Coverage report from v8
-------------------|---------|----------|---------|---------|-------------------
File               | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s 
-------------------|---------|----------|---------|---------|-------------------
All files          |   10.33 |     7.27 |    6.22 |    9.62 |                   
 src               |       0 |        0 |       0 |       0 |                   
  App.tsx          |       0 |        0 |       0 |       0 | 13-47             
  main.tsx         |       0 |        0 |       0 |       0 | 12-18             
 src/app           |       0 |      100 |       0 |       0 |                   
  navigation.tsx   |       0 |      100 |     100 |       0 | 30                
  router.tsx       |       0 |      100 |       0 |       0 | 9-24              
 src/app/layout    |       0 |        0 |       0 |       0 |                   
  AppShell.tsx     |       0 |        0 |       0 |       0 | 25-87             
  Header.tsx       |       0 |        0 |       0 |       0 | 14-46             
  NavItem.tsx      |       0 |        0 |       0 |       0 | 6-11              
  Sidebar.tsx      |       0 |        0 |       0 |       0 | 15-57             
  SyncStatus.tsx   |       0 |        0 |       0 |       0 | 11-33             
 src/components    |       0 |        0 |       0 |       0 |                   
  EmptyState.tsx   |       0 |        0 |       0 |       0 | 18-31             
 src/features/auth |   43.85 |     2.63 |      50 |   43.63 |                   
  AuthProvider.tsx |   86.95 |      100 |   77.77 |   90.47 | 36-37             
  Login.tsx        |       0 |        0 |       0 |       0 | 9-86              
  useAuth.ts       |   83.33 |       50 |     100 |   83.33 | 17                
 ...ures/dashboard |       0 |        0 |       0 |       0 |                   
  ...boardPage.tsx |       0 |        0 |       0 |       0 | 13-59             
 ...ard/components |       0 |        0 |       0 |       0 |                   
  ...Breakdown.tsx |       0 |        0 |       0 |       0 | 9-81              
  ...nboarding.tsx |       0 |      100 |       0 |       0 | 18-57             
  ...onSupport.tsx |       0 |        0 |       0 |       0 | 14-109            
  MetricCard.tsx   |       0 |        0 |       0 |       0 | 17-18             
  PnlChart.tsx     |       0 |        0 |       0 |       0 | 10-65             
  QuickLogForm.tsx |       0 |        0 |       0 |       0 | 15-62             
  ...ionHeader.tsx |       0 |        0 |       0 |       0 | 15-16             
 src/features/dss  |       0 |        0 |       0 |       0 |                   
  ...edictPage.tsx |       0 |        0 |       0 |       0 | 10-150            
 ...ures/equipment |       0 |        0 |       0 |       0 |                   
  ...pmentPage.tsx |       0 |        0 |       0 |       0 | 10-112            
 ...ent/components |       0 |        0 |       0 |       0 |                   
  ...ancePanel.tsx |       0 |        0 |       0 |       0 | 7-122             
 ...s/farm-records |   12.68 |    19.65 |    3.17 |   11.17 |                   
  DryingFields.tsx |       0 |      100 |       0 |       0 | 10-65             
  ...RunResult.tsx |       0 |        0 |       0 |       0 | 12-69             
  ...reateForm.tsx |       0 |        0 |       0 |       0 | 18-200            
  ...cordsPage.tsx |       0 |        0 |       0 |       0 | 15-213            
  ...irmDialog.tsx |       0 |        0 |       0 |       0 | 20-50             
  dryingParams.ts  |   92.85 |    94.44 |     100 |     100 | 47,50             
 ...ures/investors |       0 |        0 |       0 |       0 |                   
  ...storsPage.tsx |       0 |        0 |       0 |       0 | 11-148            
  ...torReport.tsx |       0 |        0 |       0 |       0 | 10-141            
 ...atures/reports |       0 |        0 |       0 |       0 |                   
  ReportsPage.tsx  |       0 |        0 |       0 |       0 | 8-68              
  ...loadPnlCsv.ts |       0 |      100 |       0 |       0 | 6-11              
 src/hooks         |       0 |        0 |       0 |       0 |                   
  useMediaQuery.ts |       0 |        0 |       0 |       0 | 17-39             
  ...lineStatus.ts |       0 |      100 |       0 |       0 | 7-22              
  ...endingSync.ts |       0 |      100 |       0 |       0 | 7-16              
  ...ecordCount.ts |       0 |      100 |       0 |       0 | 9-19              
 src/lib           |   35.35 |       35 |   21.95 |   30.76 |                   
  apiCache.ts      |      75 |       50 |     100 |     100 | 13                
  apiClient.ts     |       0 |        0 |       0 |       0 | 25-168            
  db.ts            |       0 |      100 |       0 |       0 | 17-24             
  logs.ts          |       0 |        0 |       0 |       0 | 26-41             
 src/styles        |       0 |      100 |     100 |       0 |                   
  theme.ts         |       0 |      100 |     100 |       0 | 10-97             
-------------------|---------|----------|---------|---------|-------------------
```

**The v8 text reporter omits fully-covered files, so the table above IS the list
of modules below 100%.** One file is missing from it because it is at 100%:
`src/lib/sync.ts` — 24/24 statements, 6/6 branches, 5/5 functions, 20/20 lines,
per the `json-summary` reporter.

Two points the chapter should not soften:

- **10.33% is the honest denominator, and it is low.** `vitest.config.ts` sets
  `include: ['src/**/*.{ts,tsx}']` deliberately. Vitest 4 has no `coverage.all`;
  without `include`, v8 measures only the files a test happened to import and
  reports **91.39%** — a number describing four modules, not the frontend.
  Nothing is excluded to flatter the figure.
- **Frontend testing is concentrated in four non-UI modules.** Every `.tsx`
  screen and component is at 0%. There is no component-render test in the
  project at all.

---

## 2 · The two Section 4.2.3 gaps

Section 4.2.3 records two behaviours as having no automated test. **Both are now
closed.** No existing test was modified to accommodate a new one.

### 2a · Model-information endpoint, untrained state — CLOSED

Closed in commit `dd8ebac`, before this phase. Phase 3 verified it and found it
already sufficient, so no new test was written.

`backend/tests/test_api.py`:

| Line | Test |
|---|---|
| 1332 | `test_dss_model_requires_authentication` |
| 1338 | `test_dss_model_reports_metrics_when_trained` |
| 1361 | `test_dss_model_reports_untrained_without_zero_metrics` |

The third is the one Section 4.2.3 asks for, and its name states the guarantee:
an untrained model is reported as **untrained**, never as zero-valued metrics.

### 2b · Offline write queue — CLOSED

Closed in commits `d2f45af` (6 tests) and `ec00162` (2 further tests), in
`frontend/src/lib/sync.test.ts`. Eight tests in three describe blocks:

**`flushPendingLogs`**
- `posts a queued log and clears it from the queue`
- `keeps the rest of the queue moving when one log fails`
- `runs one pass at a time when connectivity fires several flushes at once`
- `gives up after exactly three failed attempts`

**`registerSyncListener`**
- `flushes the queue when the browser reports the connection back`
- `does not flush on load when the browser is already offline`

**`retryFailedLogs`**
- `requeues a failed log and flushes it once the server is back`
- `restarts the three-strike count instead of failing again immediately`

No new dependency. Dexie is replaced by an in-memory stand-in implementing only
the four operations `sync.ts` uses; the axios client by a `vi.fn` whose
rejection is what "server down" means. **No fake timers were needed** — nothing
in `sync.ts` uses a timer, and the one unawaited flush (the `online` handler) is
observed with `vi.waitFor`. The scaffolding concern raised in the Phase 3 brief
did not materialise.

**Verified discriminating rather than vacuous.** Six mutations of `sync.ts`,
each reverted after: threshold 3 → 4 fails the three-strike test; dropping the
post-success delete fails four tests; binding the listener to `offline` fails
the reconnect test; dropping `failCount: 0` from the requeue fails the retry
test; deleting `if (flushing) return` fails the single-flight test; making the
on-load flush unconditional fails the offline-load test.

`sync.ts` is at **100%** on all four metrics.

---

## 3 · Per-crop DSS table — all three seeded crops

Source: `docs/ch4-data/dss_per_crop.json`, from
`GET /api/v1/dss/decision-support`. Values verbatim, unrounded.

| Field | cassava | maize | tomato |
|---|---|---|---|
| `crop` | cassava | maize | tomato |
| `revenue` | 178600.0 | 45000.0 | 0.0 |
| `expenses` | 94400.0 | 3500.0 | 112900.0 |
| `gross_margin` | 84200.0 | 41500.0 | **−112900.0** |
| `yield_quantity` | 1880.0 | 100.0 | 0.0 |
| `yield_unit` | kg | kg | **null** |
| `yield_by_unit` | `[{unit: kg, quantity: 1880.0}]` | `[{unit: kg, quantity: 100.0}]` | `[]` |
| `unit_cost_of_production` | 50.212765957446805 | 35.0 | **null** |
| `marketable_mass_kg` | **null** | 84.0 | **null** |
| `unit_cost_per_kg_marketable` | **null** | 41.666666666666664 | **null** |
| `break_even_yield` | 993.6842105263158 | 7.777777777777778 | **null** |
| `break_even_unit` | kg | kg | **null** |
| Rank (position in `crops[]`) | 1 | 2 | 3 |

Overall block, same response:

```json
"overall": { "revenue": 223600.0, "expenses": 210800.0, "gross_margin": 12800.0 }
```

**There is no `rank` field.** `dss_service.py` sorts with
`crops.sort(key=lambda c: (-c["gross_margin"], c["crop"]))` and returns the list
in that order — ties break on crop name ascending, so the ordering is total and
deterministic. The rank in the table above is array position, not a returned
value, and the UI renders no numeric rank badge. The chapter must be worded as
*ordering plus profit/alert colouring*, not as a rank field. See §9.8.

**Null unit costs, and why.** Two distinct causes, which the chapter should not
merge:

- **cassava — `unit_cost_per_kg_marketable` is null** because the crop has no
  drying run, so `marketable_mass_kg` is undefined. The guard is
  `(b["expenses"] / mm) if (mm and mm > 0) else None`. This is the fallback path
  the seed was designed to exercise: the panel falls back to the harvested
  basis, ₦50.21/kg. Fresh cassava roots go to the buyer at the farm gate, so
  there is honestly no bioprocess record.
- **tomato — both bases are null** because nothing was harvested.
  `yield_by_unit` is empty, so `yq = 0.0`, and `unit_cost` requires `yq > 0`.
  There is no drying run either, so the marketable basis is null for the same
  reason as cassava's.

---

## 4 · Break-even

### 4.1 Maize — exact value, unit, rounding

**Returned value `7.777777777777778`. Unit `kg` (`break_even_unit`). Rounding:
none at the API layer.**

The endpoint returns the raw double. `dss_service.py`:

```python
break_even_yield = None
if yq is not None and yq > 0 and b["revenue"] > 0 and b["expenses"] > 0:
    unit_price = b["revenue"] / yq
    break_even_yield = b["expenses"] / unit_price
```

`unit_price = 45000.0 / 100.0 = 450.0`; `3500.0 / 450.0 = 7.777777777777778`.

**This agrees with the chapter's stated 7.8 kg** — the same arithmetic
(3,500 ÷ 450) presented to one decimal place. The rounding happens in the
**presentation layer**, not the service: `DecisionSupport.tsx:60` renders
`c.break_even_yield.toLocaleString(undefined, { maximumFractionDigits: 1 })`,
which produces `7.8`. If the chapter needs a sentence on rounding behaviour, the
correct statement is that the API does not round and the UI rounds to one
decimal place for display.

Cassava for comparison: `178600.0 / 1880.0 = 95.0` per kg;
`94400.0 / 95.0 = 993.6842105263158` kg, rendered as `993.7 kg`.

**The metric is retrospective, and the wording matters.** The price is derived
from realised revenue, so it answers "at the price you actually got, you needed
X to cover your costs." It cannot forecast a break-even before a sale exists.
The UI wording already reflects this: "Break-even was 7.8 kg at the price you
got".

### 4.2 Tomato — the null, and which case fired

**`break_even_yield: null`, `break_even_unit: null`.**

`dss_service.py` documents four null cases. Tomato's figures are
`yield_quantity: 0.0`, `revenue: 0.0`, `expenses: 112900.0`, so **two of the
four hold simultaneously**:

| Case | Condition | Tomato |
|---|---|---|
| 1 · mixed units | `yq is None` | does not hold — `yq = 0.0` |
| 2 · nothing harvested | `yq == 0` | **holds** |
| 3 · no realised price | `revenue == 0` | **holds** |
| 4 · no cost tagged | `expenses == 0` | does not hold — 112,900.0 |

The guard is one left-to-right conjunction, so **case 2 (`yq > 0` fails) is what
short-circuits** and is strictly "the case that fired". Case 3 holds
independently and would have produced the same null on its own.

The chapter should describe this as the **no-sale case**, in which the absent
harvest and the absent realised price each independently make the metric
undefined — not as a single-condition result. Reported as `null` rather than
infinity: with no realised price there is nothing to divide by, so the metric is
undefined, not infinite.

(Note: the Phase 4 run-sheet labels this shot "the no-realised-price case",
which is case 3 — accurate as a description of the scenario, but case 2 is what
the code short-circuits on. Reconciled here rather than silently corrected.)

---

## 5 · Maize unit cost, both bases — confirmed unchanged

| Basis | Field | Value | Derivation |
|---|---|---|---|
| Per kg **harvested** | `unit_cost_of_production` | **35.0** | 3,500.0 ÷ 100.0 kg |
| Per kg **marketable** | `unit_cost_per_kg_marketable` | **41.666666666666664** | 3,500.0 ÷ 84.0 kg |

Confirmed unchanged. The four figures Section 4.3.2 depends on are intact in the
live response: expenses **3,500.0**, yield **100.0 kg**, marketable mass
**84.0 kg**, revenue **45,000.0**. The Phase 1 seed extension added cassava and
tomato only and touched no maize record; the Phase 4 re-seed returned
**200 (already seeded)** for all 13 POSTs, and the live
`GET /dss/decision-support` matched `dss_per_crop.json` exactly.

**The scope of "confirmed" — read this before writing the sentence.**
`AgriProfit_Chapter4.md` is not present in this repository or on the Desktop
(see §9.1). "Unchanged" therefore means *unchanged against the seed script and
the live endpoint*, verified figure by figure. It is **not** a diff against the
chapter text, which no phase of this work was able to read.

The marketable basis is ₦41.67/kg against ₦35/kg harvested — a 19% difference,
and the one the drying module exists to expose. **Only the harvested basis is
rendered anywhere in the application** (see §7 and §9.5).

---

## 6 · Bioprocess summary endpoint

`GET /api/v1/bioprocess/summary`, saved verbatim as
`docs/ch4-data/bioprocess_summary.json`:

```json
{
  "crops": [
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

**One crop only.** Cassava and tomato are absent by design — neither has a
drying run, which is exactly why they were seeded that way (cassava exercises
the marketable-mass fallback, tomato the no-yield path).

`total_water_removed_kg` is **14.08**, not the 16.0 a naive mass difference
would give (100 − 84). It is a water balance, not a mass difference — corrected
in commit `8690289`, and the discrepancy is the point: dry matter is conserved,
so water removed is computed from the moisture contents, not from the change in
total mass.

`safe_storage_share: 1.0` — the single run finished below the crop's safe
storage moisture threshold.

**No screen calls this endpoint** — see §9.6.

---

## 7 · The drying sub-form

**It exists.** `frontend/src/features/farm-records/DryingFields.tsx` is present
(65 lines; in the coverage table above at 0%), alongside `DryingRunResult.tsx`
and `dryingParams.ts`.

Section 4.8.4 row 4 records that the Bioprocess option was **REMOVED** from the
log-entry form after it produced an unsatisfiable queued record. **That record is
now historical.** The option was re-added together with its parameter fields in
commit `856200a` (ticket 08 phase 6, this branch). Selecting "Post-harvest
drying" today reveals: drying method (Sun / Solar dryer / Mechanical / Ambient),
mass in, mass out, moisture in and moisture out (both % wet basis), drying time,
and an optional air temperature; the Amount label gains "— 0 is fine for sun
drying".

`buildDryingParams` mirrors the backend validator client-side, so the
unsatisfiable queued record the chapter describes **cannot recur**: an invalid
payload is rejected before it can reach IndexedDB. `dryingParams.ts` is the
best-covered frontend module after `sync.ts` — 92.85% statements, 94.44%
branches, 100% functions and lines.

**The part that is still API-only.** There is **no readings input** on the form.
The Newton *k* hint in the result panel reads "Page fit needs 3+ intermediate
readings", and the form cannot supply them. The Page drying model is therefore
computed by the backend but **unreachable from the interface** — the seed posts
readings directly. For that sub-behaviour the chapter's sentence stands: *the
Page-model fit is exercised through the API rather than through the interface.*
That sentence applies to the readings and the Page model only, not to the drying
module as a whole, which now has a working form and a working result panel.

---

## 8 · Screenshot run-sheet

Reproduced from `docs/ch4-data/screenshot-runsheet.md`. Verified against the
running stack (`agrip-db-1`, `agrip-backend-1`, `agrip-frontend-1`,
`agrip-frontend-prod-1` all up) and the live API on 2026-08-19.

### Prepared state

The seed was re-run: all 13 POSTs returned **200 (already seeded)**, `13
operational logs, 13 financial transactions`. Live `GET /dss/decision-support`
matches `dss_per_crop.json` exactly. **Nothing needs re-seeding.** If the ledger
has been reset since:

```
python backend/scripts/seed_bioprocess_demo.py
```

**Origin `http://localhost:5173`** (dev) for the whole pass — it runs no service
worker, so a stale cached response cannot be photographed by mistake.
`http://localhost:4173` is the production PWA build, needed only for the
offline-with-cached-reads variant in 4.10.

**Before shot 1.** If the browser holds a token for another farm, sign out
(header, top right) and log in as `demo-bioprocess-v2@test.example` /
`demo-bioprocess-pw`. Window at **1440×900** for shots 1–10; **360 px** only at
step 11.

### Capture order — one pass

**1 · 4.1 Dashboard, post-cleanup.** `http://localhost:5173/`, no command.
Expect Net Profit **₦12.8K**, Gross Revenue **₦223.6K**, Operating Cost
**₦210.8K**, Profit Margin **5.7%** (from `GET /ledger/summary`). The
post-cleanup evidence in frame: six nav items only (no USSD/WhatsApp section),
no field-performance table, no YoY deltas or sparklines on the KPI tiles.

**2 · 4.3 Per-crop gross margin and ranking.** Same page, scroll to **Decision
support**. Three rows in rank order: **Cassava +₦84.2K**, **Maize +₦41.5K**,
**Tomato −₦112.9K** (tomato carries the alert accent; its line reads "Unit cost
— no yield recorded yet"). No numeric rank badge — the artefact is ordering plus
colouring.

**3 · 4.5 Break-even in the past tense.** Same card, same frame or a crop of it.
Cassava: "**Break-even was 993.7 kg at the price you got**". Maize:
"**Break-even was 7.8 kg at the price you got**" — matching the chapter's 7.8 kg.
Tomato has no break-even line at all, which is itself the shot for the null
path.

**4 · 4.4 Unit cost on both bases, maize — NOT REACHABLE IN THE UI.** See §9.5.
Capture instead, while the dashboard is still open: DevTools → Network →
`decision-support` → Response pane (both fields side by side), or the raw file
`docs/ch4-data/dss_per_crop.json`.

**5 · 4.6 Model metrics with the disclosure visible.**
`http://localhost:5173/dss`, scroll to **Model quality**. Renders without
running a prediction. Expect R² **0.9762**, MAE **0.2414 t/ha**, and the amber
box "**What these figures measure** … representative synthetic data … Trained on
**6,000** generated samples."

**6 · 4.7 Model info, untrained state.**

```
docker exec agrip-backend-1 mv /code/app/ml/models/model_meta.json /tmp/
```

Reload `/dss` → "**The model has not been trained yet.**" plus "No accuracy
figures exist until it has been fitted." `GET /dss/model` keys purely off the
existence of the meta sidecar; there is no service-worker cache on that route
and no restart is needed. **Do not press Run Prediction during this shot** —
`latest_model.joblib` is still present, so a forecast would succeed and the two
panels would contradict each other. Restore immediately after, then reload and
confirm the metrics are back:

```
docker exec agrip-backend-1 mv /tmp/model_meta.json /code/app/ml/models/
```

**7 · 4.2 Log-entry form with Bioprocess selected.**
`http://localhost:5173/records` → **Log activity** → Activity = **"Post-harvest
drying"**. See §7 for what this now shows and why row 4 of 4.8.4 is historical.

**8 · 4.13 Drying result panel — it exists.** Fill that same form and save. Use
**Crop = Rice, Amount = 0** — *not maize*: a maize run would add to marketable
mass and break the 100 kg / 84 kg / ₦3,500 figures Section 4.3.2 depends on.
Suggested values: mass in 60, mass out 50, moisture 22 → 13, time 8 h. On save
the form is replaced by the result panel: water removed, drying rate, process
loss (against the dry-matter-balance prediction), dry matter, moisture ratio,
Newton *k*, and a green safe-storage chip (rice threshold 14% wb). This
temporarily adds a fourth "rice" row (₦0 margin) to the decision-support panel,
which is why shots 1–3 come first. Step 10 removes it again.

**9 · 4.8 Reversal confirmation dialogue.** Still on `/records`. Click
**Reverse** on the **rice drying** row just created — **never on a seeded row**.
Dialog: "**Correct this record?**", the explanatory paragraph ("nothing is
deleted"), the record identified by activity/description/amount/date, "A
correcting entry cannot itself be corrected", buttons "Keep as it is" / "Post
correcting entry".

**10 · 4.9 Original and contra together.** Confirm **Post correcting entry**.
The list refetches: the original row is struck through with a "**Reversed**"
pill; the contra row is tinted and pilled "**Correction of #\<id\>**", described
"Reversal of log #\<id\>". Both fit in one frame. *Caveat for the chapter:*
`GET /ledger/logs` has no `ORDER BY`, so adjacency is observed, not guaranteed —
in practice the pair is the last two rows. Afterwards the rice bucket disappears
from decision support entirely (reversed drying runs are excluded from
marketable mass, and both money sides net to zero), so the ledger is back to the
three seeded crops. Reload `/` to confirm the KPIs read ₦12.8K / ₦223.6K /
₦210.8K again.

**11 · 4.12 360 px, no horizontal overflow.** DevTools device toolbar →
**360×800**, on `/records` (the widest content, now 15 rows). Expect the sidebar
gone with a hamburger in the header, every grid collapsed to one column, and the
table scrolling **inside** its own container
(`.table-scroll > table { min-width: 640px }`) while `main` keeps
`overflow-x: hidden` — the page itself does not scroll sideways. Worth a second
and third frame on `/` and `/dss` at the same width.

### Group B — backend unreachable. Capture last, together.

**12 · 4.10 Offline pending-sync indicator.** Return to **desktop width first**:
the indicator lives in the sidebar footer, which at 360 px is inside the drawer.

Two variants, which do **not** show the same thing:

- **DevTools → Network → Offline** (flips `navigator.onLine`): the sidebar shows
  **both** "Offline · showing saved data" **and** "⏳ 1 pending sync". *This is
  the shot the chapter wants.*
- **`docker compose stop backend` alone**: `isOnline` derives from
  `navigator.onLine`, which stays true, so **no offline chip appears**. The POST
  fails, the record queues, the form says "Network error — saved offline. Will
  retry when connected." and only "⏳ 1 pending sync" shows. **The application
  cannot distinguish a stopped backend from being online** — a genuine finding,
  worth its own frame beside the DevTools one.

Procedure: go offline → `/records` → Log activity → Other, description "Offline
queue demo", amount 500 → Save → screenshot the sidebar footer.

**Clean up before reconnecting:** DevTools → Application → IndexedDB → delete
the queued record. Otherwise it flushes on reconnect and lands as a real ₦500
expense under "Unspecified", adding a fourth DSS row and moving the dashboard
totals. If it does flush, reverse it from `/records`. If the container was
stopped: `docker compose start backend`.

Also worth photographing here: **reload the page while offline on 5173**. The
summary fetch fails, the summary stays zero, and the dashboard renders the
first-run **onboarding screen** rather than the KPI row — a fetch failure
presented as an empty farm. On `4173` the service worker serves the cached
summary and the real figures survive the reload. A clean two-frame finding.

### States that cannot be reached, stated plainly

| Shot | Status |
|---|---|
| 4.4 both unit-cost bases | **Absent from the UI.** Computed, returned by the API, rendered nowhere. |
| Page drying-model fit | **Unreachable from the form** — no readings input; backend only. |
| `/bioprocess/summary` | **No screen calls it.** Endpoint and typed client method exist, zero consumers. |
| 4.7 untrained model | Reachable only by removing the meta sidecar — not a state the app can enter on its own once the container has booted (`ensure_model` trains on startup). |
| 4.10 offline chip via stopped backend | **Not reachable** — requires `navigator.onLine` false. |

---

## 9 · What could NOT be produced, and why

### 9.1 The chapter itself was never read

`AgriProfit_Chapter4.md` **does not exist** in this repository or anywhere on
the Desktop. `find` over both returns only `AGENT_PROMPT_chapter4_gaps.md`. The
repo carries `AgriProfit_Chapters_1-3.docx`,
`AgriProfit_Chapters_1-3_corrected.docx`, `AgriProfit_Evaluation_Pack.docx` and
`AgriProfit_Viva_Prep.docx` — no Chapter Four.

Consequence, and it conditions everything above: **no phase of this work
verified anything against the chapter text.** Every reference to "Section 4.2.3",
"Section 4.3.2", "row 4 of Section 4.8.4" and "the chapter states 7.8 kg" comes
from the excerpts quoted in the agent prompt, not from the chapter. §5's
"confirmed unchanged" is confirmed against the seed script and the live
endpoint. **Whoever writes the prose must do that diff against the chapter
themselves.**

### 9.2 Evaluators 2 and 3

Not producible by an agent — they need two other people, roughly 25 minutes
each. The run-sheet exists (`usabilitysessionrunsheet.md`). Chapter Four
currently stands at **one evaluator honestly reported.**

The decision rule in 4.8.1 is correct and should not be softened: a single
evaluator honestly reported is a limitation; three reported without three is
misconduct. Do not split the difference. If the sessions do happen, capture
**during** the session rather than after: tasks completed, mean ease, duration,
heuristic compliance, **the ten individual SUS item responses rather than only
the total**, and every issue with the severity that evaluator assigned.
Photograph the sheets before they leave the room.

### 9.3 Row 10, the undiagnosed export defect

Not reconstructable. It depends on one memory only the user holds: what was
being exported and what came out wrong. If the answer is yes, write it down and
it replaces the row. If no, it stays **recorded-and-undiagnosed**, which is
honest and which the chapter already turns into a methodological finding about
instrument retention. **A reconstructed defect is a fabricated result even when
it feels like a memory** — nothing was invented for this row.

### 9.4 The screenshots themselves

None of the twelve figures were captured. Phase 4 prepared and verified the
states and the capture order; the pass itself is a human task, as scoped. §8 is
a run-sheet, not evidence that any shot was taken.

### 9.5 Shot 4.4 — both unit-cost bases, as a UI artefact

`unit_cost_per_kg_marketable` = **41.666666666666664** is computed in
`dss_service.py` and returned by the endpoint, but **no frontend component reads
it — the field is not present in `frontend/src/types/domain.ts` at all**.
`DecisionSupport.tsx` renders only `unit_cost_of_production` → "Unit cost of
production ₦35/kg". The investor report shows the single basis too. The
screenshot the chapter asks for cannot be taken; the DevTools Network pane or
`dss_per_crop.json` is the only artefact available. **Both bases exist as data,
never as interface. That absence is the finding, and the chapter should carry it
as one rather than describing a screen that does not exist.**

### 9.6 `/bioprocess/summary` has no consumer

The endpoint exists (`GET /api/v1/bioprocess/summary`, 100% covered), a typed
client method `bioprocessService.getSummary` exists, and **nothing calls it**.
The output in §6 was obtained by querying the API directly. There is no screen
to screenshot.

### 9.7 The Page drying-model fit is unreachable from the interface

The result panel's Newton *k* hint reads "Page fit needs 3+ intermediate
readings" and the form has **no readings input**. The backend computes the Page
model; the seed posts readings directly. No UI evidence for that path can be
produced.

### 9.8 There is no `rank` field to report

Section 3 of this brief asks for rank as a per-crop field. The API does not
return one — ranking is expressed purely as array order, and the UI shows no
rank badge. The rank column in §3 is array position, added by me, and is not a
measured value. **The chapter must not cite a rank field.**

### 9.9 A single unambiguous null case for tomato

Two of the four documented null cases hold simultaneously (§4.2). Which one
"fired" is a short-circuit artefact of a single conjunction, not a property of
the data. The evaluation order can be reported truthfully, but it cannot be
reduced to one case without misrepresenting the code.

### 9.10 A single authoritative backend coverage number

The repo has no coverage configuration, so the figure depends on the invocation:
**91%** with `--cov=backend/app`, **95%** with bare `--cov`, which counts the
test files. 91% is quoted throughout with the reason shown, but no committed
config makes that the project's canonical figure — a future run will disagree
with the chapter unless the flag is stated alongside it.

### 9.11 No component-render coverage exists to report

Every `.tsx` file in the frontend is at 0%. The 10.33% figure is real and needs
no asterisk, but it means Chapter Four has **no automated evidence for any
rendered screen** — every UI claim in the chapter rests on the screenshots in §8
and on manual verification, not on tests.

### 9.12 The seeded amounts have no citable source

Every cassava and tomato figure is a rate × quantity using mid-range 2024–25
Nigerian smallholder rates (₦3,000/person-day labour, ₦1,040/kg NPK, ₦940/L
petrol, 9.4 t/ha fresh cassava). These are **reasoned estimates from published
ranges, not a single citable dataset**, and commit `b1987f5` states each one so
it can be challenged. If Chapter Four presents the demo farm's economics as
realistic, it must say this. Nothing was tuned toward a round margin or a
particular ranking.

### 9.13 Not attempted, and deliberately so

Row 4 of Section 4.8.4 warned against re-adding the drying sub-form without
telling you. It was already re-added in `856200a`, earlier on this branch, and
§7 reports that rather than reverting it. No Alembic migration was created and
no dependency was added beyond `@vitest/coverage-v8@4.1.10`, which was necessary
to produce any frontend coverage figure at all.

---

## Branch log

`git log --oneline main..HEAD` (branch `feat/bioprocess-drying`, 31 commits):

```
e3bb674 docs(ch4): add the screenshot run-sheet for Phase 4
ec00162 test(frontend): measure coverage, and take the sync queue to 100%
d2f45af test(sync): cover the offline write queue's flush, three-strike and retry paths
ab7a0da docs(ch4): capture the DSS, bioprocess and model responses for Chapter Four
b1987f5 feat(seed): add a profitable and a loss-making crop to the demo farm
e833667 chore(repo): drop the unused design mockups, add the cleanup analysis
856200a feat(bioprocess): capture drying runs and show their metrics (ticket 08 phase 6)
59554cc perf(frontend): code-split the routes and the dashboard charts
73176dc refactor(frontend): extract the nav module and clear the lint backlog
d254e2a fix(backend): replace deprecated SQLAlchemy and FastAPI APIs
8690289 fix(bioprocess): water_removed_kg is a water balance, not a mass difference
dd8ebac test(bioprocess,dss): discriminating water-balance fixture; cover GET /dss/model
ef847f0 docs: chapter correction redline for Chapters 1-3
69d1aca feat(dss): surface model quality metrics on the prediction page
7bcadd5 feat(dss): rank crops by margin, add retrospective break-even yield
b6e2ddb feat(ui): responsive layout, and remove the USSD/WhatsApp placeholders
fbdadca fix(dss): omit empty crop buckets from decision support
d63d0ca docs: date the measurement set 17 August throughout
99676a3 docs: add limitations, progress summary and the Objective 4 evaluation strands
13f95a6 docs(perf): re-measure against the c16924e build, supersede the 15 Aug set
c16924e fix(ui,dss): remove unsupported claims, add reversal UI, group yield by unit
f51af98 docs(perf): settle service-worker attribution with a driven-browser probe
31616b4 docs(perf): commit raw Lighthouse artifacts + measurement README
b86ccdf fix(bioprocess): coherent demo (whole harvest dried) + document the assumption
fed6b07 fix(bioprocess): seed script used a reserved .local email, rejected by EmailStr
6992d1c feat(bioprocess): DSS coupling — marketable-mass cost + reversal netting (phase 5)
5fe711e feat(bioprocess): read + aggregate endpoints, seed script (phase 4)
0046b43 feat(bioprocess): pure drying-engineering service, tests-first (phase 3)
25b0684 feat(bioprocess): DryingParams/DryingReading schema with edge validation (phase 2)
3bfc6c9 chore(bioprocess): move ticket spec into .scratch under version control
85a9b2b docs(bioprocess): domain terms + ADR for drying in extra_data (phase 1)
```
