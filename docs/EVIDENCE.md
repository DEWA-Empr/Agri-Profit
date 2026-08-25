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
| Fixture H (endpoint layer): **32 passed, 96 deselected** | `python -m pytest backend/tests/test_api.py -q -k "enterprise or mechanis"` |
| Full backend suite: **179 passed** | `python -m pytest backend/tests -q` |
| `enterprise_service.py` **72 stmts, 0 miss, 100%** | `python -m pytest backend/tests --cov=backend/app --cov-report=term` |
| Overall backend coverage **TOTAL 1285 stmts, 98 miss, 92%** | same command as above |
| Full frontend suite: **41 passed, 6 files** | `cd frontend && npx vitest run` |
| Parity block alone: **40 passed** backend / **15 passed** frontend | `python -m pytest backend/tests/test_enterprise_service.py -q` · `cd frontend && npx vitest run src/features/dss/partialBudget.test.ts` |
| Type check clean (exit 0) | `cd frontend && npx tsc -b` |
| Lint clean (exit 0) | `cd frontend && npx eslint .` |

## Scope figures

| Figure | Command |
|---|---|
| No Alembic migration on the branch | `git diff --stat main...HEAD -- backend/alembic/versions/ alembic/versions/` (empty) |
| Nothing under `backend/app/ml/` modified | `git diff --stat main...HEAD -- backend/app/ml/` (empty) |
| `backend/tests/` additions **2194 insertions, 4 deletions** | `git diff --stat main...HEAD -- backend/tests/` |
| The 4 deletions are an HS256 comment rewrite, not enterprise economics | `git log --oneline -S "Flip the final signature character" main...HEAD -- backend/tests/` → `8690289 fix(bioprocess): water_removed_kg is a water balance…` |
| Dependency changes on the branch: `pytest-cov`, `@vitest/coverage-v8` | `git diff main...HEAD -- backend/requirements.txt frontend/package.json` · attributed by `git log --oneline main...HEAD -- backend/requirements.txt frontend/package.json` → `ec00162`, `0046b43` |
| Parity commit adds no dependency, migration or `ml/` change | `git show --stat 330f1d9 -- backend/requirements.txt frontend/package.json backend/app/ml/ backend/alembic/` (empty) |

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
