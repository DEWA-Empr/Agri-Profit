# Evidence freeze — 2026-08-25

The state the repository and the live database are in as thesis evidence
collection begins. Every figure below was produced by running the command named
beside it, after the verification-artifact cleanup recorded in
`docs/DATA_CLEANUP_2026-08-25.md`.

No application behaviour was changed to produce this report. The changes made in
this phase are: two new test modules, one ADR, two documentation additions, one
test-only devDependency, and a nine-line docstring correction. They are itemised
in §1.3.

---

## 1. Repository

### 1.1 Branch and commit

| | |
| --- | --- |
| Branch | `feat/partial-budget-parity` |
| HEAD | `09bcc32f19a235289d8bcba61dc124c8c35032da` |
| Main branch | `main` |
| Tags | none |

### 1.2 Latest commits

```
09bcc32 docs(evidence): state the baseline the "no new dependency" item is read against
7e3e798 docs(evidence): record the command behind every figure quoted on this branch
330f1d9 test(dss): prove offline and backend partial budgets agree via a shared fixture
1337787 chore(git): add .gitattributes so line endings stop churning
e8c60c6 refactor(cache): move the reversal purge into the client, test it, write the race down
```

### 1.3 Working tree: **NOT clean**

This is the single thing standing between the current state and a true freeze.
`HEAD` (`09bcc32`) does **not** contain the remediation work; all of it is
uncommitted. 27 tracked files are modified and 18 paths are untracked
(`git diff --stat`: **27 files changed, 1180 insertions(+), 66 deletions(-)**,
excluding untracked files).

Untracked source and test files that the passing results below depend on:

| Path | Added by |
| --- | --- |
| `backend/alembic/versions/e6a2b4c7d130_scope_client_id_uniqueness_to_farm.py` | remediation |
| `frontend/src/lib/queueOwner.ts`, `queueOwner.test.ts` | remediation |
| `frontend/src/features/dss/components/YieldBaselinePanel.tsx` | remediation |
| `frontend/src/features/farm-records/DryingCurveChart.tsx` | remediation |
| `frontend/src/features/farm-records/cropOptions.ts`, `cropOptions.test.ts`, `useCropOptions.ts` | remediation |
| `backend/tests/test_concurrency.py` | **this phase** (§2.2) |
| `frontend/src/lib/dbUpgrade.test.ts` | **this phase** (§2.1) |
| `docs/adr/0003-mechanization-equipment-id-and-hours-used-are-capture-only.md` | **this phase** (§3) |
| `docs/DATA_CLEANUP_2026-08-25.md` | **this phase** (§4) |
| `docs/STATE_REPORT_2026-08-25.md`, `docs/EVIDENCE_FREEZE_2026-08-25.md` | audit / this file |

Changes made in **this phase** to tracked files, in full:

| File | Change |
| --- | --- |
| `frontend/package.json`, `package-lock.json` | `fake-indexeddb@6.2.5` added as a **devDependency**. Test-only; it is not imported by any `src/` module that ships, so the production bundle is unaffected (§5.4 confirms the built size). |
| `backend/app/schemas/schemas.py` | `MechanizationParams` docstring: points at ADR-0003, and corrects a miscount — the seed populates `equipment_id` on five mechanisation logs and `hours_used` on three, not "both fields on five". No code change. |
| `LIMITATIONS.md` | New §3 paragraph recording machine-hour costing as a scope boundary. |

A commit was **not** made; committing was not requested, and the tree is
reported as found.

---

## 2. Backend

### 2.1 Tests

`python -m pytest backend/tests -q --cov=backend/app --cov-report=term`

**190 passed, 0 failed, 0 skipped, 1 warning, 47.29 s.**

The one warning is `StarletteDeprecationWarning` from FastAPI's own
`testclient` import (`httpx` → `httpx2`); it is raised inside the installed
FastAPI package, not by this repository's code.

Collected tests per module:

| Module | Collected |
| --- | --- |
| `backend/tests/test_api.py` | 134 |
| `backend/tests/test_enterprise_service.py` | 40 |
| `backend/tests/test_bioprocess_service.py` | 11 |
| `backend/tests/test_concurrency.py` | **5** (new) |
| **Total** | **190** |

(Collected counts exceed `def test_` counts because several tests are
parametrised.)

### 2.2 Coverage

**93%** — **1286 statements, 91 missed, 1195 covered.**

Modules at less than 100%:

| Module | Stmts | Miss | Cover | Missed lines |
| --- | ---: | ---: | ---: | --- |
| `app/ml/dataset.py` | 50 | 32 | 36% | 75-88, 93-103, 116-121, 125-129 |
| `app/ml/train.py` | 53 | 31 | 42% | 36-45, 53-64, 69-105, 116-117, 121-123 |
| `app/main.py` | 48 | 6 | 88% | 33-35, 70-71, 82 |
| `app/models/database.py` | 11 | 4 | 64% | 11-15 |
| `app/ml/predict.py` | 46 | 4 | 91% | 31, 44, 59-60 |
| `app/services/reports_service.py` | 68 | 4 | 94% | 90-91, 109, 112 |
| `app/api/deps.py` | 20 | 3 | 85% | 37-38, 41 |
| `app/api/endpoints/dss.py` | 46 | 3 | 93% | 45-47 |
| `app/core/security.py` | 30 | 2 | 93% | 36-38 |
| `app/api/endpoints/auth.py` | 21 | 1 | 95% | 40 |
| `app/services/ledger_service.py` | 56 | 1 | 98% | 123 |

Every other module — including `schemas.py` (170), `models.py` (77),
`dss_service.py` (162), `enterprise_service.py` (72), `bioprocess_service.py`
(68), `share_service.py` (32), `auth_service.py` (22), `equipment_service.py`
(27) and all six endpoint modules bar `dss.py` — is at **100%**.

### 2.3 Which of those misses materially matter

**Materially uncovered — 63 of the 91 misses, and the honest weak point:**

- `app/ml/train.py` (31) and `app/ml/dataset.py` (32) together are two thirds of
  all missed statements. These are the synthetic-data generator and the
  RandomForest training routine. They execute on every application start
  (`ensure_dss_model` runs in the startup hook, and the API tests depend on a
  trained model existing), so they are *exercised* — but by a startup side
  effect, not by an assertion. **No test asserts anything about the training
  data's distribution, the model's fitted quality, or reproducibility across
  runs.** Chapter Four should not claim the yield model is validated by this
  suite; what the suite proves is that a trained model exists and that the
  prediction endpoint validates its inputs and returns a forecast.

**Not materially uncovered — 28 misses, each a defensive or environment branch:**

- `models/database.py:11-15` — the Postgres/SQLite `DATABASE_URL` branch. Tests
  run on in-memory SQLite by construction, so the production branch is not
  reachable from them.
- `main.py:33-35, 70-71, 82` — CORS/startup configuration and the last-resort
  `Exception` handler's logging lines. The handler's *behaviour* is asserted
  elsewhere; these are the log statement and the branch taken only on an
  unexpected exception.
- `ledger_service.py:123` — `ConflictError` for reversing a log that has **no**
  paired financial transaction. Unreachable through the API: every app-created
  log is paired by construction (`create_operational_log` writes both). It is a
  guard against a hand-edited database row.
- `reports_service.py:90-91` — the December→January rollover inside the P&L
  month window; `109`/`112` — the `timestamp is None` and out-of-window skips.
- `deps.py:37-38, 41`, `security.py:36-38`, `auth.py:40` — malformed/expired
  token branches; the 401 outcomes are asserted at the API level.
- `dss.py:45-47` — the "no model trained" 503 branch, unreachable while the
  startup hook trains one (documented in `test_dss_predict_rejects_malformed_payload`).
- `predict.py:31, 44, 59-60` — missing-artifact and unknown-crop guards.

---

## 3. Frontend

### 3.1 Tests

`npm run test` (`vitest run`) — **9 test files, 89 tests, 89 passed, 0 failed**,
12.14 s.

| Test file | Tests |
| --- | ---: |
| `src/features/farm-records/dryingParams.test.ts` | 20 |
| `src/lib/queueOwner.test.ts` | 16 |
| `src/lib/sync.test.ts` | 15 |
| `src/features/dss/partialBudget.test.ts` | 15 |
| `src/features/farm-records/cropOptions.test.ts` | 8 |
| `src/lib/dbUpgrade.test.ts` | **7** (new) |
| `src/lib/cacheInvalidation.test.tsx` | 5 |
| `src/features/auth/AuthProvider.test.tsx` | 2 |
| `src/lib/apiCache.test.ts` | 1 |
| **Total** | **89** |

### 3.2 Coverage

`npm run test:coverage`. The denominator is every file under `src`, tested or
not (`vitest.config.ts` sets `coverage.include` deliberately, so this is not the
flattering "files a test happened to import" figure).

| Metric | Covered / Total | % |
| --- | --- | ---: |
| Statements | 378 / 1129 | **33.48** |
| Branches | 220 / 861 | 25.55 |
| Functions | 93 / 382 | 24.34 |
| Lines | 338 / 1003 | 33.69 |

The low headline is React page and form components with no component tests. The
logic modules are the covered ones:

| Module | Statements | % |
| --- | --- | ---: |
| `lib/db.ts` | 10/10 | **100** (was 0 — no test imported it before `dbUpgrade.test.ts`) |
| `lib/sync.ts` | 39/39 | 100 |
| `lib/queueOwner.ts` | 14/14 | 100 |
| `lib/authToken.ts` | 7/7 | 100 |
| `features/dss/partialBudget.ts` | 4/4 | 100 |
| `features/farm-records/cropOptions.ts` | 12/12 | 100 |
| `features/dss/components/YieldBaselinePanel.tsx` | 9/9 | 100 |
| `features/dss/components/CostStructurePanel.tsx` | 7/7 | 100 |
| `features/dss/components/BreakEvenPricePanel.tsx` | 8/8 | 100 |
| `features/farm-records/dryingParams.ts` | 50/53 | 94.33 |
| `features/dss/components/EnterpriseEconomics.tsx` | 33/35 | 94.28 |
| `features/dss/components/SensitivityTable.tsx` | 9/10 | 90 |
| `features/auth/AuthProvider.tsx` | 21/24 | 87.5 |
| `lib/apiClient.ts` | 35/66 | 53.03 |
| `lib/logs.ts` | 8/17 | 47.05 |
| `features/dss/components/PartialBudgetForm.tsx` | 16/44 | 36.36 |
| `features/farm-records/DryingCurveChart.tsx` | 0/7 | **0** |
| `features/farm-records/DryingFields.tsx` | 0/26 | 0 |
| `features/farm-records/FarmRecordCreateForm.tsx` | 0/61 | 0 |
| `features/farm-records/useCropOptions.ts` | 0/16 | 0 |

Coverage was not optimised for its own sake; the only change is the genuine
`db.ts` 0% → 100%, which is a by-product of testing the upgrade, not the point
of it.

### 3.3 TypeScript

`npx tsc -b --force` — **exit 0, no diagnostics.**

`tsconfig.app.json` sets `include: ["src"]` with no `exclude`, so the new
`src/lib/dbUpgrade.test.ts` is inside the type-checked project, not skipped.

### 3.4 ESLint

`npm run lint` (`eslint .`) — **exit 0, 0 errors, 0 warnings.**

### 3.5 Production build

`npm run build` (`tsc -b && vite build`) — **built in 2.77 s**, no errors.

| | |
| --- | --- |
| `dist/` total | **959 KB** |
| JS + CSS assets | 893 KB |
| Service-worker precache | **21 entries, 859.67 KiB** |

Largest chunks (raw / gzip):

| Chunk | Raw | Gzip |
| --- | ---: | ---: |
| `index-BbrkA7Cc.js` | 398.38 kB | 129.50 kB |
| `CategoricalChart-tX9TLfC1.js` | 262.12 kB | 82.07 kB |
| `CartesianChart-BGFkcYXT.js` | 54.01 kB | 14.02 kB |
| `DSSPredictPage-p4UK0c-o.js` | 34.01 kB | 8.86 kB |
| `FarmRecordsPage-CioM6Hl8.js` | 27.76 kB | 8.21 kB |
| `index-BTa7PcTv.css` | 2.56 kB | 0.92 kB |

The two chart chunks are Recharts, code-split and loaded only by the pages that
draw. PWA generation succeeded (`dist/sw.js`, `dist/workbox-1320db52.js`).

---

## 4. Verified functionality

Each item states what is proven and by what. Where a claim is narrower than the
feature's name suggests, it says so.

**Cross-farm `client_id` handling — CONFIRMED.** Two farms may hold the same
offline key; neither sees the other's row and neither request 500s. Migration
`e6a2b4c7d130` scopes the constraint to `UNIQUE(farm_id, client_id)`.
`test_same_client_id_in_two_farms_creates_two_records`,
`test_cross_farm_client_id_does_not_leak_the_other_farms_row`,
`test_a_null_client_id_is_exempt_from_the_composite_constraint`.

**Same-farm idempotency — CONFIRMED, including under the race.** A sequential
replay returns the same row as 200 with exactly one log and one transaction
stored (`test_idempotent_log_creation`). The concurrent case is now covered by
`backend/tests/test_concurrency.py` (5 tests, file-backed SQLite so two sessions
hold two real connections): the unique constraint is proven live before anything
else is asserted; the loser of the race receives the winner's row with
`created=False`, its flushed `FinancialTransaction` rolled back rather than
double-booked; the endpoint answers **200, not 500**; an integrity error that is
*not* a same-farm replay still raises, so the handler is a recovery and not a
blanket swallow; and two real threads racing one key, with nothing stubbed,
book exactly one record. The threaded case was run 10 times consecutively with
no flake.

**Offline queue identity isolation — CONFIRMED.** The IndexedDB queue is
partitioned by an owner key derived from the token's `sub`, and every read path
uses the `[ownerKey+status]` compound index. `queueOwner.test.ts` (16 tests)
covers the derivation including every case that must return null;
`sync.test.ts` (15) covers the flush, the three-attempt give-up and the retry
under two accounts. `lib/queueOwner.ts` and `lib/sync.ts` are at 100% statement
coverage. Note the deliberate non-guarantee: the key is **not** authorisation —
it is an unverified local partition label, and the server authenticates every
POST regardless.

**Logout queue cleanup — CONFIRMED.** `purgeQueueForCurrentOwner` deletes only
the signed-in account's rows, is a no-op when signed out, and never blocks
logout on failure. Covered in `sync.test.ts` and again in `dbUpgrade.test.ts`
against a real IndexedDB, where rows migrated from v1 are shown to be reachable
by the purge rather than stranded outside it. This **does** discard unsent work;
that is the recorded trade, not a defect.

**IndexedDB v1 → v2 migration — CONFIRMED (new).** `src/lib/dbUpgrade.test.ts`
writes a genuine v1 database using v1's own schema string, asserts `verno === 1`,
then opens it with the shipped v2 module and asserts: all three rows survive with
`clientId`, `status`, `failCount`, `createdAt` and `payload` intact; `ownerKey`
is populated on all of them including the exhausted-retry row; `ownerKey` and
`[ownerKey+status]` exist and are *queryable* as indexes; the migrated rows then
flush through the real `sync.ts` and the failed one is still recoverable via
Retry. The signed-out path — where rows are unattributable and are deliberately
cleared — is pinned as the documented data loss it is, and an empty v1 and a
fresh v2 install are covered so the upgrade tests cannot pass by accident.
Negative control: breaking the upgrade hook fails 4 of the 7 tests.

**Mechanization schema behaviour — CONFIRMED, and formally classified.**
`cost_subtype` is validated against a closed taxonomy and is the only one of the
three fields that moves a derived figure. `equipment_id` and `hours_used` are
**capture-only metadata** — validated (`0 < hours_used ≤ 1000`), persisted, read
by nothing — now recorded as a decision in
`docs/adr/0003-mechanization-equipment-id-and-hours-used-are-capture-only.md` and
as a scope boundary in `LIMITATIONS.md` §3. Round-trip is proven, not assumed:
`test_mechanization_params_are_captured_and_round_trip_intact` asserts both
fields survive a **read-back** and that neither name appears anywhere in the
derived cost-structure response. `test_mechanization_omitting_the_capture_only_fields_is_accepted`,
`test_mechanization_hours_used_out_of_range_rejected`,
`test_mechanization_unrecognised_cost_subtype_rejected` and
`test_non_mechanization_log_keeps_arbitrary_extra_data` fix the edges. Nothing
was deleted and no economics were invented.

**Bioprocess drying readings — CONFIRMED.** `test_bioprocess_service.py` (11)
covers the maize process-loss fixture, the rice clean-balance fixture, exact
Page-fit recovery, insufficient and out-of-range readings, wet↔dry basis
round-trip, safe-storage lookup for known and unknown crops, the process-loss
warning flag, and that `water_removed_kg` is a water balance rather than a mass
difference. Eight API tests reject the malformed cases (mass out > mass in,
final moisture not below initial, non-positive mass, moisture out of range,
non-increasing readings) as **422 at the schema edge, never 500**, and four more
cover detail/summary access control and reversal exclusion.

**Drying curve — PARTIALLY CONFIRMED. Read this one carefully.** The
*arithmetic* behind the curve is well covered: `dryingParams.ts` at 94.33% with
20 tests, and the Page-model fit in `bioprocess_service.py` at 100%. The
*component* that draws it, `DryingCurveChart.tsx`, has **0% coverage and no
test**. Its correctness rests on visual inspection only. Chapter Four may claim
the drying model and its fitted parameters are verified; it must not claim the
chart rendering is.

**Yield-baseline panel — CONFIRMED.** `YieldBaselinePanel.tsx` is at 100%
statement coverage, and six API tests plus four service tests cover the
Olympic-average rule end to end: three seasons required, one high and one low
discarded, ties handled by discarding one instance rather than all, mixed units
returning null *with a reason*, the season count distinguishing the two kinds of
null, and a crop with no yield still reported.

**Crop selection — CONFIRMED at the logic layer.** `cropOptions.ts` is at 100%
with 8 tests: crops the farm has recorded are offered even when the model has
never seen them, predictor crops stay selectable, duplicates are merged across
case and whitespace, the null crop is dropped rather than shown as
"Unspecified", one failed source falls back to the other, and the list is sorted
so it does not reorder between loads. The hook that wires it into the page,
`useCropOptions.ts`, is untested (0%).

**Enterprise economics — CONFIRMED.** `enterprise_service.py` at 100% with 40
collected tests covering classification and coverage, the depreciation overlay
(including that a zero rate counts as *unrated* rather than as a zero charge),
proportional allocation, both break-even prices with the cash price provably
strictly lower, the yield-sensitivity matrix, the operating-expense ratio, and
the partial budget signed in both directions. Offline/backend partial-budget
parity is proven against a shared fixture on both sides (`partialBudget.test.ts`,
15 tests; `test_parity_*` on the backend), including that an exact zero is not
returned as negative zero. `EnterpriseEconomics.tsx` is at 94.28%.

**DSS outputs — CONFIRMED for the ledger-derived figures; NOT validated for the
ML forecast.** `dss_service.py` is at 100%, with API tests covering per-crop
ranking, alphabetical tie-breaks, break-even yield and each of its null cases,
reversal netting, drying-aware unit costs, and every degenerate crop case
(zero margin, zero cost, fully reversed, yield-only). The **model** side is
different: `test_dss_predict_returns_forecast` proves a well-formed request
returns a forecast and `test_dss_predict_rejects_malformed_payload` proves a
malformed one is a 422 — but no test asserts anything about the forecast's
accuracy, and the training code is 42%/36% covered (§2.3). The model is trained
on synthetic data.

---

## 5. Live database after cleanup

Full detail in `docs/DATA_CLEANUP_2026-08-25.md`. Summary: ten rows removed —
farms 28/29 (`Verify Farm A`, `Verify Farm B`), users 27/28, operational logs
1076/1077/1078 and their three paired financial transactions. All were created
by the 2026-08-25 verification run and referenced by nothing else (both
dependency queries returned zero rows).

After: 14 farms, 13 users, 109 operational logs, 109 financial transactions, 3
equipment, 1 maintenance log, 10 share tokens. `max(operational_logs.id)` is now
1075. Per-farm log counts are byte-identical to the pre-deletion snapshot for
every surviving farm — farm 26 (`Demo Farm`, the source of Chapter Four figures)
still holds all 28 of its logs and farm 1 (`Legacy Farm`) all 34. The backend
answers `GET /` with 200 and rejects an unauthenticated
`GET /api/v1/ledger/logs` with 401; its log shows no error since the deletion.

Nothing was reseeded and no migration was run.

---

## 6. Remaining limitations

Five separate categories. An item appears in exactly one.

### 6.1 Application defects

Behaviour that is wrong, not merely absent.

1. **Per-crop decision support does not net reversals.** Farm-wide P&L nets
   correctly; the per-crop breakdown and the investor report that reuses it do
   not. After reversing a crop expense, the crop still shows the reversed cost
   *and* a phantom "Unspecified" cost appears. Totals stay right; the per-crop
   comparison — the view a farmer would actually use to choose between crops —
   is misleading after any reversal. (`LIMITATIONS.md` §3.)
2. **Monetary and quantity fields are unbounded.** `amount`, `purchase_price`
   and `cost` are unconstrained floats. A negative amount and an absurdly large
   amount are accepted and persisted rather than rejected as 422, and both
   distort the P&L. (`depreciation_rate` *is* bounded, `0 < rate ≤ 100`.)
3. **Equipment cannot be corrected.** No PATCH/PUT on `/equipment/{id}` and no
   edit surface. A mistyped depreciation rate is permanent and silently biases
   the overlay, the allocated fixed cost and both break-even prices for that
   farm, with no route to fix it short of direct database access. Unlike the
   ledger, this is a missing write path rather than a deliberate immutability
   choice.
4. **A mistaken reversal cannot be rolled back.** Correct, in that it prevents
   over-correction — but the only remedy is an unlinked compensating entry, and
   the resulting audit trail is truthful without being self-explanatory.
5. **Stale-revalidation window in the service worker — UNVERIFIED, reasoned from
   the handler's ordering.** A `StaleWhileRevalidate` revalidation begun before
   `purgeApiReadCache()` can complete after it and repopulate the cache with a
   pre-mutation body. This has never been reproduced or observed, and the Phase
   6b tests model only the serve half of the handler, so they cannot speak to it
   either way. It is listed as a defect candidate, not a confirmed defect, and it
   should be reproduced before it is described as a bug.

### 6.2 Testing / verification gaps

Behaviour that may well be correct but is not proven here.

1. **The yield model is not validated.** `ml/train.py` 42% and `ml/dataset.py`
   36% — 63 of 91 missed backend statements. Nothing asserts the synthetic data's
   distribution, the fitted model's quality, or run-to-run reproducibility. The
   suite proves a model exists and that the endpoint validates inputs and returns
   a forecast; it proves nothing about accuracy.
2. **No component tests for the form and page layer.** Frontend statement
   coverage is 33.48% because `FarmRecordCreateForm.tsx` (0/61),
   `FarmRecordsPage.tsx` (0/60), `DryingFields.tsx` (0/26),
   `DryingRunResult.tsx` (0/34), `Login.tsx` (0/28), `DSSPredictPage.tsx` (0/40),
   the investor pages and the whole app shell have none.
3. **`DryingCurveChart.tsx` is untested** (0/7). The curve's arithmetic is
   covered; its rendering is not.
4. **`useCropOptions.ts` is untested** (0/16), though the `cropOptions.ts` logic
   it wraps is at 100%.
5. **`apiClient.ts` (53%) and `logs.ts` (47%)** — the interceptor and error paths
   are the uncovered half.
6. **The v1→v2 upgrade is proven against `fake-indexeddb`, not a browser.** It
   is a spec implementation, so Dexie's version machinery, the upgrade callback,
   the object stores, transactions and indexes are all real — but browser-specific
   storage eviction, quota behaviour and vendor IDB bugs are out of its reach.
   Stated in the test file's own header.
7. **The concurrent-race tests run on SQLite**, and the deterministic ones force
   the pre-check to miss rather than winning a real thread interleaving. The
   forced miss is what makes the `IntegrityError` branch execute on every run;
   the unstubbed two-thread test covers the genuine interleaving but cannot
   guarantee which path it takes. Postgres's behaviour under the same race is
   inferred from the equivalent constraint, not measured.
8. **No end-to-end browser test** of the offline→online transition, the service
   worker lifecycle, or the PWA install path.
9. **No independent security review**, and no load or performance testing.

### 6.3 Data-quality issues

1. **`hours_used` is optional and sparsely populated** — 3 of 8 seeded
   mechanisation logs. Any future machine-hour rate computed from today's data
   would be a total over an unknown fraction of actual machine use. Recorded in
   ADR-0003 as a reason not to build one yet.
2. **The live database carries accumulated exploratory farms.** 14 farms remain,
   of which `Madlabs Farm`, `Sunrise Farm`, `lead farm`, `Zelle Farm`,
   `Dash Check Farm`, `Unit Check Farm`, `Empty Bucket Farm`, `Sun Dry Farm`,
   `Beeper Farms`, `Break Even Farm` and `London Farm` are development leftovers
   from July–August, holding 3–9 logs each. They were **not** removed: unlike the
   two `Verify Farm` records they are not attributable to a single identified
   verification run, and deleting on a guess is worse than leaving them. They do
   not affect any Chapter Four figure, which is read from farm 26 (`Demo Farm`).
   If screenshots would show a farm list, this needs a decision first.
3. **Two farms are both named `Demo Farm`** (ids 17 and 26). Only 26 carries the
   bioprocess/enterprise seed. A screenshot must be unambiguous about which.
4. **The yield model is trained on synthetic data**, not on farm records. This is
   a stated design decision for a cold start, but every forecast in the evidence
   inherits it.

### 6.4 Documentation / evidence gaps

1. **The working tree is uncommitted** (§1.3). `HEAD` does not contain the
   remediation, the new tests, ADR-0003 or the cleanup record. Every result in
   this report describes the working tree, and a reader who checks out `09bcc32`
   will not reproduce them. This is the highest-priority item on the list.
2. **`TODO(cite)` in `schemas.py`** — the cost-behaviour taxonomy (variable
   scales with output, fixed does not) still needs an agricultural-economics or
   extension enterprise-budget citation. "The taxonomy was supplied" is not a
   citation, as the comment itself says.
3. **ADR-0003 needs to reach the chapter text.** The capture-only classification
   is now recorded in the ADR and `LIMITATIONS.md`, but no chapter has been
   checked for a claim of machine-hour or utilisation analysis. No thesis
   chapter was read or altered in this phase.
4. **"Tamper-evident" wording.** Immutability here is audit-trail discipline, not
   cryptographic. Earlier chapters or stakeholder copy using "tamper-evident"
   should read *audit-trailed*. Flagged in `LIMITATIONS.md` §3; not yet
   reconciled against the chapters.
5. **No tags and no frozen commit hash** to cite as "the evaluated version".

### 6.5 Thesis validation gaps

Claims the artifact cannot support on its own, whatever the code does.

1. **No field trial and no real farmer data.** Every figure derives from seeded
   demo records on one farm. There is no evidence of usability, adoption, or
   accuracy against actual outcomes.
2. **No user evaluation** — no usability study, no task-completion measurement,
   no comparison against the paper-based practice the work is positioned against.
3. **The DSS recommendations are unvalidated as agronomic advice.** The
   arithmetic is verified; whether following it improves a farmer's outcome is
   untested and, on synthetic training data, untestable here.
4. **Objective 3's data-boundary claim is proven by tests, not by an independent
   security assessment.** Farm scoping is asserted at every endpoint and the
   cross-tenant cases pass, but no third party has attempted to breach it.
5. **No deployment evidence.** The system runs under `docker compose` on one
   developer machine. There is no managed hosting, TLS, backup/recovery, secret
   management or observability story, so nothing supports a claim about
   behaviour in the field.

---

## 7. Status

The two verification gaps named for this phase are closed with real tests, the
`equipment_id`/`hours_used` question is formally settled as capture-only in
ADR-0003, and the verification artifacts are out of the live database with the
seeded records provably untouched. Backend 190/190, frontend 89/89, TypeScript
clean, ESLint clean, production build clean.

The one thing that prevents this being a true freeze is §6.4 item 1: none of it
is committed.
