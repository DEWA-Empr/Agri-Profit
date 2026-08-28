# Evidence — the read-cache invalidation tests actually test the cache

This file records how the Phase 6b/6c cache-invalidation tests were verified to
be **load-bearing**, and how to repeat that verification. It exists because the
strongest claim this work makes — *these tests fail if the purge stops working* —
is not visible in the test output when everything passes, and was until now only
demonstrated in a transcript.

Everything below is a procedure to re-run, not a result to take on trust.

## Provenance

| | |
|---|---|
| **Subject** | `frontend/src/lib/cacheInvalidation.test.tsx` — five tests, one per farm-scoped write path |
| **Under test** | `purgeApiReadCache()` in `frontend/src/lib/apiCache.ts`, and the call sites that invoke it |
| **Runner** | Vitest **4.1.10**, `win32-x64`, `node v24.15.0` |
| **Working directory** | `frontend/` |
| **Commit at time of run** | Phase 6c working tree, on `feat/enterprise-economics` (parent `d82419d`) |
| **Date of run** | 2026-08-25 |

## Why a mutation test and not a spy

`expect(purgeApiReadCache).toHaveBeenCalled()` proves a function ran. It passes
just as happily when the purge deletes nothing, which is the exact bug class
these tests exist to close. So each test instead seeds a **real** cache entry
through a stand-in service worker, performs the write, and re-reads — asserting
on the **value** that comes back.

The verification below confirms that: with the purge neutered, every one of the
five fails on a value or on rendered text, and none fails on a call count.

## The edit

Replace the body of `purgeApiReadCache` in `frontend/src/lib/apiCache.ts` with a
no-op. The signature and the export are unchanged, so every call site still
resolves and still awaits — only the deletion stops happening:

```ts
export async function purgeApiReadCache(): Promise<void> {
  void API_READ_CACHE;
  return;
}
```

For reference, the real body it replaces:

```ts
export async function purgeApiReadCache(): Promise<void> {
  if (typeof caches === 'undefined') return; // no Cache Storage (e.g. dev/SSR)
  try {
    await caches.delete(API_READ_CACHE);
  } catch {
    // Best-effort: a failure here must never block login/logout.
  }
}
```

`void API_READ_CACHE;` is there only to keep the now-unused import from failing
lint during the experiment. **Revert the file afterwards** — the no-op must not
be committed.

## The command

```
cd frontend
npx vitest run src/lib/cacheInvalidation.test.tsx
```

## Expected result: 5 failed, 0 passed

```
 ❯ src/lib/cacheInvalidation.test.tsx (5 tests | 5 failed)
```

Each failure, with the value asserted and where the stale value comes from:

| # | Write path | Failure message | Asserted | Received (stale) | Why the stale value is that |
|---|---|---|---|---|---|
| 1 | Online log save (`saveOperationalLog` → `ledgerService.createLog`) | `AssertionError: expected +0 to be 3500 // Object.is equality` | `3500` | `0` | The DSS read cached before the ₦3,500 fertiliser log was written |
| 2 | Offline queue flush (`flushPendingLogs`) | `AssertionError: expected +0 to be 5500 // Object.is equality` | `5500` | `0` | The DSS read cached before either queued log (₦3,500 + ₦2,000) was flushed |
| 3 | Equipment create (`EquipmentPage`) | `AssertionError: expected ' Enterprise economicsEverything below…' to contain '2 of your 3 assets have no depreciati…'` | rendered text `2 of your 3 assets have no depreciation rate recorded` | the panel still renders `1 of your 2 assets has no depreciation rate recorded` | The break-even read cached before the third, unrated asset was added |
| 4 | Maintenance log (`MaintenancePanel`) | `AssertionError: expected +0 to be 12000 // Object.is equality` | `12000` | `0` | The cost-structure read cached before the ₦12,000 gearbox service |
| 5 | Reversal (`ledgerService.reverseLog`) | `AssertionError: expected 5500 to be 2000 // Object.is equality` | `2000` | `5500` | The DSS read cached before the ₦3,500 log was reversed; ₦2,000 survives it |

Note the shape of #5: unlike #1, #2 and #4 its stale value is **not** zero. The
two logs (₦3,500 and ₦2,000) are both written before the seeding read, so the
cached figure is ₦5,500 and the correct figure is ₦2,000. A cache that survived
the reversal reads ₦5,500; a ledger that lost the second log would read ₦0.
Only a purge plus a correctly-netted contra produces ₦2,000.

Note also the shape of #3: it fails on rendered text rather than on a number,
because the thing that goes stale for a user there is a sentence.

## What this does and does not establish

**Does:** that all five tests depend on `purgeApiReadCache` doing real work, and
that each one's assertion moves when the cache is stale.

**Does not:** anything about the background-revalidation half of
StaleWhileRevalidate. The harness models only the serve half (a cache hit wins).
The revalidation race is written up beside the `runtimeCaching` block in
`frontend/vite.config.ts` — it is reasoned from the handler's ordering, has not
been observed, and is not addressed by these tests.

## Where the purge lives (Phase 6c)

The invariant, for anyone re-running the above and wondering why a component no
longer purges: **mutating `ledgerService` methods purge; components do not.**
`createLog` and `reverseLog` each purge on 2xx and on the status codes that mean
the server's state already moved (409 for both; 404 additionally for
`reverseLog`).

Two declared exceptions, because they do not route through the ledger client and
call `purgeApiReadCache` directly:

| File | Line |
|---|---|
| `frontend/src/features/equipment/EquipmentPage.tsx` | `51` |
| `frontend/src/features/equipment/components/MaintenancePanel.tsx` | `53` |

(Import lines are `4` in both files. Verify with
`grep -n "purgeApiReadCache" frontend/src/features/equipment/EquipmentPage.tsx frontend/src/features/equipment/components/MaintenancePanel.tsx`.)

---

# Evidence — the partial-budget parity fixture actually fails when it should

`frontend/src/features/dss/partialBudget.ts` is a second implementation of
`backend/app/services/enterprise_service.partial_budget`. Both files asserted in
prose that they must agree and nothing executed both and compared; the two
suites shared seven cases and not one input tuple. A term added to one
implementation left both suites green.

`frontend/src/fixtures/partial_budget_parity.json` (cases **PB-1..PB-8**, all
values hand-computed and never regenerated from either implementation) is now
read verbatim by both `backend/tests/test_enterprise_service.py` and
`frontend/src/features/dss/partialBudget.test.ts`. Both implementations agreed
with all eight on the first run — no divergence was found.

Note that **A-H and PB-1..PB-8 are two disjoint sets**, not two names for one
set: A-G are the enterprise-economics fixtures in `test_enterprise_service.py`,
H is the rejection/isolation set in `test_api.py`, and PB-1..PB-8 are the parity
cases. (Register finding P1-04.)

## Why the failure runs exist

A parity test that skips, catches, or defaults when it cannot find its input is
indistinguishable from no parity test at all — the exact condition the fixture
exists to end. So the fixture read is uncaught in both suites, and that claim is
verified rather than asserted: three ways of breaking the fixture, each run
against both suites, six runs. **The fixture is restored and unmodified in the
commit** (md5 `68b2549054fb6f06325fcd15c18c6f3b` before and after).

## The commands

The backend suite needs **no `DATABASE_URL`, no Docker and no Postgres**. Every
database-touching fixture in `backend/tests/conftest.py` is function-scoped and
`Base.metadata.create_all` runs only inside `db`; these cases request none of
them. Run from the repository root:

```
python -m pytest backend/tests/test_enterprise_service.py -q
cd frontend && npx vitest run src/features/dss/partialBudget.test.ts
```

Green baseline: **40 passed** (backend, 29 pre-existing + 11 new) and
**15 passed** (frontend, 4 pre-existing + 11 new).

## The six runs

| # | Break | Suite | Failure |
|---|---|---|---|
| 1a | `mv …/partial_budget_parity.json …/partial_budget_parity.json.renamed` | backend | `FileNotFoundError: [Errno 2] No such file or directory: 'C:\Users\DELL\Desktop\Agri P\frontend\src\fixtures\partial_budget_parity.json'` — collection error, `Interrupted: 1 error during collection` |
| 1b | same | frontend | Vite fails to resolve the import at transform time: `Failed to resolve import "../../fixtures/partial_budget_parity.json"`, pointing at line 3 of `partialBudget.test.ts`. `Test Files 1 failed (1) / Tests no tests` |
| 2a | truncate to the first 400 bytes (invalid JSON) | backend | `json.decoder.JSONDecodeError: Unterminated string starting at: line 7 column 13 (char 277)` — collection error |
| 2b | same | frontend | `Error: EOF while parsing a string at line 7 column 135`. `Test Files 1 failed (1) / Tests no tests` |
| 3a | `"case_count": 8` → `9`, cases left at 8 | backend | `AssertionError: partial_budget_parity.json: case_count is 9 but cases has 8 entries` / `assert 9 == 8` in `test_parity_fixture_is_internally_consistent`. `1 failed, 39 passed` |
| 3b | same | frontend | `AssertionError: partial_budget_parity.json: case_count is 9 but cases has 8 entries: expected 9 to be 8 // Object.is equality`. `Tests 1 failed \| 14 passed (15)` |

Runs 1 and 2 fail at **import/collection** time in both suites, before any test
body executes — which is the point: there is no code path in which a missing or
malformed fixture yields a green run. Run 3 is the truncated-but-parseable case,
which import-time failure cannot catch, so it is caught by comparing the file's
own `case_count` against `len(cases)` and both against a constant declared in
each test file.

## What this does and does not establish

**Does:** that both implementations of the partial budget produce the same net
change for eight hand-computed tuples, including a negative result (PB-1, sign
asserted separately from magnitude), an exact zero that is not negative zero
(PB-3), kobo precision at `rel=1e-9` (PB-7), and a cross-pair transposition trap
(PB-8). And that the fixture cannot go missing, malformed, or silently shrink
without failing both suites.

**Does not:** anything about the endpoint layer, serialisation, or the offline
substitution logic that decides *which* implementation runs. It compares two
pure functions. It also cannot establish that both are wrong in the same way —
only that hand-computed expectations, which no implementation generated,
disagree with neither.

## Two findings recorded here, deliberately NOT changed by this ticket

1. **`conftest.py` imports the database module at collection time.**
   `backend/tests/conftest.py:8-9` imports `backend.app.main`, which reaches
   `backend/app/models/database.py:5`, `engine = create_engine(settings.database_url)`,
   evaluated at import for every test in the directory. It only parses the URL
   and imports the driver — it does not connect — so the default
   `postgresql://…@localhost/agriprofit` plus an installed psycopg2 is enough
   and pure numeric tests run with no database. But it does mean a pure test
   cannot be collected without a parseable URL and an importable driver. Out of
   scope here.
2. **The `run-backend-tests-locally` note is stale.** It says a SQLite
   `DATABASE_URL` must be set or psycopg2 fails to import. Both halves are wrong
   on this machine: psycopg2 2.9.12 is installed, and
   `env -u DATABASE_URL python -m pytest backend/tests/test_enterprise_service.py -q`
   passes, while `DATABASE_URL=sqlite` *breaks* the run with
   `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from given URL
   string`. Correcting that note is not in this ticket.

---

# Evidence — the command behind every figure quoted for the branch

Run from the repository root unless stated. No `DATABASE_URL` is required (see
the finding above). Figures are as of 2026-08-25 on `feat/partial-budget-parity`.

## Test and coverage figures

| Figure | Command |
|---|---|
| Fixtures A–G: **11 passed, 29 deselected** | `python -m pytest backend/tests/test_enterprise_service.py -v -k "fixture_a or fixture_b or fixture_c or fixture_d or fixture_e or fixture_f or fixture_g"` |
| Fixture H (endpoint layer): **39 passed, 95 deselected** | `python -m pytest backend/tests/test_api.py -q -k "enterprise or mechanization"` |
| Full backend suite: **185 passed** | `python -m pytest backend/tests -q` |
| `enterprise_service.py` **72 stmts, 0 miss, 100%** | `python -m pytest backend/tests --cov=backend/app --cov-report=term` |
| Overall backend coverage **TOTAL 1286 stmts, 98 miss, 92%** | same command as above |
| Full frontend suite: **82 passed, 8 files** | `cd frontend && npx vitest run` |
| Parity block alone: **40 passed** backend / **15 passed** frontend | `python -m pytest backend/tests/test_enterprise_service.py -q` · `cd frontend && npx vitest run src/features/dss/partialBudget.test.ts` |
| Type check clean (exit 0) | `cd frontend && npx tsc -b` |
| Lint clean (exit 0) | `cd frontend && npx eslint .` |

> **These are the enterprise-economics phase's figures, not the frozen ones.**
> Re-running the commands today gives higher counts: the evidence-freeze phase
> added 5 backend tests (`backend/tests/test_concurrency.py`) and 7 frontend
> tests (`frontend/src/lib/dbUpgrade.test.ts`), taking the suites to **190
> backend / 89 frontend** and coverage to **93% (1,286 statements, 91 missed)**.
> The table is left as captured because it is a dated measurement paired with
> the command that produced it. The frozen figures are in
> `docs/EVIDENCE_FREEZE_2026-08-25.md`.

### Correction: the Fixture H command used a token that matched nothing

The row above previously read **32 passed, 96 deselected** from:

```
python -m pytest backend/tests/test_api.py -q -k "enterprise or mechanis"
```

`mechanis` matches **no test**. pytest's `-k` does not substring-match the way
that expression assumed, so the second clause contributed nothing and the
command selected only the 32 `enterprise*` tests — while appearing to cover the
mechanisation schema tests as well. Measured on this machine:

```
$ python -m pytest backend/tests/test_api.py -q -k "enterprise"
32 passed, 102 deselected

$ python -m pytest backend/tests/test_api.py -q -k "mechanization"
6 passed, 128 deselected

$ python -m pytest backend/tests/test_api.py -q -k "mechanis"
134 deselected
```

The tests always passed; what was wrong was the recorded command and therefore
what the figure was understood to cover. `mechanization` in full selects the six
it was meant to, and the union is 39 (two names match both clauses).

## Scope figures

| Figure | Command |
|---|---|
| No Alembic migration on the branch | `git diff --stat main...HEAD -- backend/alembic/versions/ alembic/versions/` (empty) |
| Nothing under `backend/app/ml/` modified | `git diff --stat main...HEAD -- backend/app/ml/` (empty) |
| `backend/tests/` additions **2194 insertions, 4 deletions** | `git diff --stat main...HEAD -- backend/tests/` |
| The 4 deletions are an HS256 comment rewrite, not enterprise economics | `git log --oneline -S "Flip the final signature character" main...HEAD -- backend/tests/` → `8690289 fix(bioprocess): water_removed_kg is a water balance…` |
| **No dependency added by the enterprise-economics work** | `git diff --stat 502dced..94e554a -- backend/requirements.txt frontend/package.json frontend/package-lock.json` (empty) |
| Dependency changes on the branch as a whole: `pytest-cov`, `@vitest/coverage-v8` | `git diff main...HEAD -- backend/requirements.txt frontend/package.json` · attributed by `git log --oneline main...HEAD -- backend/requirements.txt frontend/package.json` → `ec00162`, `0046b43` |
| Parity commit adds no dependency, migration or `ml/` change | `git show --stat 330f1d9 -- backend/requirements.txt frontend/package.json backend/app/ml/ backend/alembic/` (empty) |

### On the baseline for "no new dependency"

The enterprise-economics DoD item **"No new Python or JavaScript dependency"**
is read against that ticket's own commit range, `502dced..94e554a` (eleven
commits), where it is clean — not against `main`, where the branch does add
`pytest-cov` and `@vitest/coverage-v8`.

That is not a loosening. The two packages **predate** the range: `pytest-cov`
arrives in `0046b43` (bioprocess phase 3) and `@vitest/coverage-v8` in `ec00162`
(frontend coverage), each closed under its own ticket. And they are load-bearing
for two other items in the same DoD — without `pytest-cov` the coverage figures
cannot be produced at all:

```
$ python -m pytest backend/tests/test_enterprise_service.py -p no:cov --cov=backend/app
ERROR: python -m pytest: error: unrecognized arguments: --cov=backend/app
```

`main` carries neither package (`requirements.txt` ends `pytest / httpx`;
`package.json` has no `test:coverage` script), so coverage is not measurable on
`main` at all. Read against `main`, the DoD's items "enterprise_service.py at
100% coverage", "overall backend coverage not below the current 91%" and "no new
dependency" cannot all hold at once. The DoD settles its own intent by saying
**"the current 91%"** — a figure that could only have been measured with
`pytest-cov` already installed. The tooling is assumed present, not forbidden.

## Seed idempotency — the maize figures are bit-identical

The maize figures **₦35.00/kg harvested** and **₦41.67/kg marketable** are quoted
in a defended chapter, so the multi-crop seed must not move them. With the stack
up (`docker compose up -d`, containers `agrip-backend-1` and `agrip-db-1`),
captured before and after a re-run of the seed:

```
python backend/scripts/seed_bioprocess_demo.py
```

Read back with `GET /api/v1/dss/decision-support` as
`demo-bioprocess-v2@test.example`, selecting the maize crop object:

```json
{ "crop": "maize", "expenses": 3500.0, "revenue": 45000.0,
  "gross_margin": 41500.0, "yield_quantity": 100.0,
  "marketable_mass_kg": 84.0,
  "unit_cost_of_production": 35.0,
  "unit_cost_per_kg_marketable": 41.666666666666664,
  "break_even_yield": 7.777777777777778 }
```

Byte-identical before and after (md5 `1850df22069facec23e86032275c659f` on both
captures; `diff` reports no differences). The seed reported
`28 operational logs, 28 financial transactions, 2 equipment` with every log
returning **HTTP 200** rather than 201 — the ledger's `client_id` idempotency
returning existing rows instead of duplicating them.

## Where the marketable unit cost is visible

`frontend/src/features/dashboard/components/DecisionSupport.tsx:85` renders
`Unit cost {nairaExact(marketableCost)}/kg marketable` beside the harvest-unit
figure, guarded at line 82 so a crop with no drying run (and therefore no
marketable mass) falls back rather than rendering a null. The two break-even
prices carry the same `/kg marketable` suffix at
`frontend/src/features/dss/components/BreakEvenPricePanel.tsx:29`.

---

# Evidence — the post-audit remediation, and that its tests are load-bearing

Work carried out on 2026-08-25 against the findings in
`docs/STATE_REPORT_2026-08-25.md`. Every claim below is a command to re-run, not
a result to take on trust. Run from the repository root unless stated.

## Baseline, before and after

| Figure | Before (state report) | After remediation | At freeze |
|---|---|---|---|
| Backend tests | 179 passed | 185 passed | **190 passed** |
| Backend statements / missed / coverage | 1,285 / 98 / 92% | 1,286 / 98 / 92% | **1,286 / 91 / 93%** |
| Frontend test files / tests | 6 / 41 | 8 / 82 | **9 / 89** |
| Frontend entry bundle | 406,941 B raw · 130,365 B gzip | see §"Bundle" below | 398.38 kB raw · 129.50 kB gzip |

The "At freeze" column is the evidence-freeze phase: `test_concurrency.py` (5
backend) and `dbUpgrade.test.ts` (7 frontend). The 7 statements that leave the
missed count are all in `ledger_service.py`, which goes 86% → 98% because the
concurrency tests are the first to execute its `IntegrityError` recovery path.
No application code changed between the middle column and the right one.

Commands: `python -m pytest backend/tests -q`,
`python -m pytest backend/tests --cov=backend/app --cov-report=term`,
`cd frontend && npx vitest run`.

## 1. The offline write queue is identity-scoped (state report §9.13)

`frontend/src/lib/queueOwner.ts` derives an owner key from the token's `sub`
claim; `PendingLog` gains `ownerKey`; every queue read goes through the
`[ownerKey+status]` compound index added in Dexie schema v2; and
`purgeQueueForCurrentOwner()` runs on logout **before** the token is cleared.

### That the tests fail when the scope is removed

Two independent mutations, each run against `src/lib/sync.test.ts`.

**Mutation A — ignore the owner on every read.** Replace the body of
`ownerScopedRows` in `frontend/src/lib/sync.ts` with an unscoped query:

```ts
function ownerScopedRows(status: 'pending' | 'failed') {
  const owner = currentOwnerKey();
  void owner;
  return db.pendingLogs.where('status').equals(status) as never;
}
```

```
cd frontend && npx vitest run src/lib/sync.test.ts
→ Tests  8 failed | 7 passed (15)
```

Among the failures is `never flushes another account's queued write`. **Read
this mutation narrowly**: the in-memory stand-in for the Dexie table implements
only the owner-scoped query shapes, so seven of those eight failures are the
mock refusing an unsupported shape rather than an assertion about ownership.
Mutation B is the clean one.

**Mutation B — neuter only the logout purge.** Replace the body of
`purgeQueueForCurrentOwner()` with `void owner; return;`:

```
cd frontend && npx vitest run src/lib/sync.test.ts
→ Tests  2 failed | 13 passed (15)
```

```
× logout cleanup > drops the signed-in account's queued writes and nobody else's
× logout cleanup > a write queued before logout is not flushed after a different account logs in
```

Nothing else moves, which is the point: the remaining thirteen — including
`survives the purge failing: the row is still inert for the next account` — hold
on the owner scope alone. The purge and the scope are independent protections
and the suite distinguishes them.

**The file is restored in the commit.** `git diff` on `frontend/src/lib/sync.ts`
shows the scoped implementation, not either mutation.

### What this does and does not establish

**Does:** that a row belonging to one owner key is never POSTed, retried,
counted or deleted while another owner key is signed in; that logout removes the
departing account's rows and only theirs; and that the exact reported sequence
(queue offline → sign out → another account signs in → connectivity returns)
sends nothing.

**Does not:** anything about a real IndexedDB. `sync.test.ts` runs against an
in-memory stand-in implementing the query shapes `sync.ts` uses, so the Dexie v2
`.upgrade()` that attributes or drops pre-existing v1 rows is **not** exercised
by any test — it needs a real IndexedDB and a database that already holds v1
data. It is reasoned, commented in `lib/db.ts`, and unverified.

`src/lib/queueOwner.test.ts` (16 cases) covers the key derivation itself,
including base64url payloads, a numeric `sub`, and the six malformed-token cases
that must return null rather than a key that would match somebody's rows.

## 2. `client_id` uniqueness is farm-scoped (state report §9.14)

Migration `e6a2b4c7d130` replaces the global unique index on `client_id` with
`UNIQUE(farm_id, client_id)` and restores a plain index. The model carries the
matching `__table_args__`. `ledger_service` is unchanged apart from its comment:
the recovery lookup it already performed is now the only case the constraint can
reject.

### That the tests fail against the old constraint

Restore the pre-migration model — `client_id = Column(String, unique=True,
nullable=True, index=True)` and delete the `UniqueConstraint` from
`__table_args__` — then:

```
python -m pytest backend/tests/test_api.py -q -k "client_id or idempot"
```

```
E  sqlite3.IntegrityError: UNIQUE constraint failed: operational_logs.client_id
E  sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: operational_logs.client_id
```

That IntegrityError is the 500: in the application it escapes
`ledger_service.create_operational_log`'s bare `raise` and lands on the
catch-all handler at `backend/app/main.py:67`. Restored, the same command gives
**5 passed, 127 deselected**.

### Applied to the live database

```
$ docker compose up -d --build backend        # migrations run on startup
$ docker exec agrip-db-1 psql -U postgres -d agriprofit -t \
    -c "SELECT version_num FROM alembic_version;"
 e6a2b4c7d130

$ docker exec agrip-db-1 psql -U postgres -d agriprofit \
    -c "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
        WHERE conrelid='operational_logs'::regclass AND contype='u';"
 uq_operational_logs_farm_client | UNIQUE (farm_id, client_id)
```

The index on `client_id` is now non-unique (`\d operational_logs`). No row was
touched: the composite constraint is strictly weaker than the global one, so
nothing existing can violate it.

### What this does and does not establish

**Does:** that two farms may hold the same `client_id`, that each sees only its
own row with its own amount, that same-farm idempotent replay still returns 200
with the original id, and that NULL `client_id` remains exempt.

**Does not:** anything about the concurrent same-farm race that the
`except IntegrityError` branch exists for. That path is still uncovered
(`ledger_service.py` lines 57–73 are among its 8 missed statements) and still
needs two simultaneous requests to provoke.

## 3. Drying readings, the drying curve, and the yield baseline

`buildDryingParams` now validates and carries `readings`, mirroring
`DryingReading`'s bounds and the three readings clauses of
`_check_physical_consistency`; `DryingFields` collects them; `DryingCurveChart`
plots them. Ten new cases in
`frontend/src/features/farm-records/dryingParams.test.ts` cover the band edges
(inclusive), strictly-increasing time, the half-filled row, and the blank row
that must be dropped rather than rejected.

The chart plots **measured points only** — the run's start, the readings, and
its final moisture, all off `GET /bioprocess/{id}`. The fitted Newton and Page
curves are deliberately not drawn: drawing them would mean a second
implementation of the kinetics in the browser, which is the failure this file
already documents for the partial budget.

`YieldBaselinePanel` renders `GET /dss/yield-baseline`, which had been
implemented, tested and service-worker-cached with no interface reading it.

### Not verified

No test renders `DryingFields`, `DryingCurveChart` or `YieldBaselinePanel`.
There is no component-test harness for them in this project, and the state
report already records every panel on the DSS and records screens as
implemented-but-not-verified. Their inputs are covered — `buildDryingParams` for
the form, the endpoint tests for the panel's data — and the components
themselves are covered by inspection and by the live probe in §5.

## 4. Crop options come from the API (state report §7.4)

`frontend/src/features/farm-records/cropOptions.ts` merges the farm's own
recorded crops (`/dss/decision-support`) with the predictor's
(`/dss/model`), normalised to trimmed lower case, deduped and sorted; the form
adds an "Another crop…" free-text option so a crop neither source knows can
still be entered. `cropOptions.test.ts` (8 cases) pins the merge, including the
reported case: cowpea and tomato are offered because the farm recorded them,
even though the model never saw them.

`useCropOptions` uses `Promise.allSettled`, so one failed request narrows the
list rather than emptying it. Nothing tests the hook itself.

## 5. Bundle

```
cd frontend && npm run build
```

Sizes measured directly, not from Vite's report:

```
stat -c%s frontend/dist/assets/<entry>.js
gzip -9 -c frontend/dist/assets/<entry>.js | wc -c
```

The current filenames, byte sizes and the whole-`dist` total are in the
completion report for this work; the hashes change on every content change, so
quoting a filename here would go stale on the next build.
