# Thesis evidence freeze — 2026-08-25

The implementation state from which thesis screenshots, figures and results are
to be produced. Development stops here.

Every figure below was produced by running the command named beside it, against
the tagged state, after the verification-artifact cleanup recorded in
`docs/DATA_CLEANUP_2026-08-25.md`.

---

## 1. Repository identity

| | |
| --- | --- |
| Branch | `feat/partial-budget-parity` |
| Tag | **`thesis-evidence-freeze-2026-08-25`** (annotated) |
| Implementation commit | `59a6286a1ecb26acdacdc95abc62d902c58d9b00` |
| Commit subject | `chore(freeze): post-audit remediation and thesis evidence-freeze state` |
| Commit date | Tue 25 Aug 2026 21:31:55 +0900 |
| Commit size | 43 files changed, 6506 insertions(+), 66 deletions(-) |
| Working tree | **Clean**, except four deliberately excluded paths (§1.2) |

Cite the **tag**, not the branch: the branch may move, the tag will not.

### 1.1 A note on the tag's commit

`59a6286` is the commit carrying the verified implementation — all source,
tests, migration and documentation. The tag itself sits on the immediately
following documentation-only commit, which adds nothing but this report (the
report cannot state its own commit's hash before that commit exists). The two
are identical in every source file:

```
git diff 59a6286 thesis-evidence-freeze-2026-08-25 -- backend/ frontend/    # empty
```

Either commit reproduces every test figure in §2.

### 1.2 Deliberately excluded from the commit

`git status --short` at the freeze reports exactly these four untracked paths,
and nothing else:

```
?? AGENT_PROMPT_chapter4_gaps.md
?? AGENT_PROMPT_thesis_conformance.md
?? "Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf"
?? docs/print/
```

None is remediation, its tests, its migration, its documentation or its evidence
record. Two are agent prompt scripts, one is a departmental guideline supplied as
input, and `docs/print/` holds thesis chapter exports (`Thesis_Ch1-3.docx`,
`Thesis_Ch1-3.pdf`) that this work is under instruction not to touch. They are
left in the working tree, uncommitted, on purpose.

One item **was** committed that is not remediation, and is named here rather
than slipped in: `CLAUDE.md` gains 73 lines of agent working rules written
during this cycle.

---

## 2. Test identity

All five commands run from the repository root unless stated, against the tagged
state.

| Check | Command | Result |
| --- | --- | --- |
| Backend suite | `python -m pytest backend/tests -q` | **190 passed, 0 failed, 0 skipped**, 1 warning, 44.22 s |
| Backend coverage | `python -m pytest backend/tests -q --cov=backend/app --cov-report=term` | **93%** — 1286 statements, **91 missed** |
| Frontend suite | `cd frontend && npm run test` | **9 files, 89 tests, 89 passed, 0 failed** |
| TypeScript | `cd frontend && npx tsc -b --force` | **exit 0**, no diagnostics |
| ESLint | `cd frontend && npx eslint .` | **exit 0**, 0 errors, 0 warnings |
| Production build | `cd frontend && npm run build` | **built in 6.86 s**, no errors; precache **21 entries, 859.67 KiB**; `dist/` 959 KB |

The single backend warning is `StarletteDeprecationWarning` raised inside the
installed FastAPI package's own `testclient` import (`httpx` → `httpx2`), not by
this repository's code.

### 2.1 Difference from the previously reported figures

The previous report quoted 185 backend tests, 92% coverage, 1,286 statements /
98 missed, and 82 frontend tests. Every difference is accounted for by the two
test modules added in this phase; **no application code changed**.

| Figure | Previously | At freeze | Cause |
| --- | ---: | ---: | --- |
| Backend tests | 185 | **190** | `backend/tests/test_concurrency.py` — 5 tests |
| Frontend tests | 82 | **89** | `frontend/src/lib/dbUpgrade.test.ts` — 7 tests |
| Frontend test files | 8 | **9** | same file |
| Backend statements | 1,286 | **1,286** | unchanged — no application code added |
| Backend missed | 98 | **91** | the 7 statements are all in `ledger_service.py`, whose `IntegrityError` recovery path had never been executed by a test before `test_concurrency.py` |
| Backend coverage | 92% | **93%** | consequence of the line above |

`ledger_service.py` moves 86% → **98%**; its one remaining missed statement is
line 123. No coverage was chased for its own sake.

### 2.2 Backend modules below 100%

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

Everything else is at 100%, including `schemas.py` (170), `models.py` (77),
`dss_service.py` (162), `enterprise_service.py` (72), `bioprocess_service.py`
(68), `share_service.py` (32), `auth_service.py` (22), `equipment_service.py`
(27), and every endpoint module except `dss.py`.

### 2.3 Frontend test files

| File | Tests |
| --- | ---: |
| `src/features/farm-records/dryingParams.test.ts` | 20 |
| `src/lib/queueOwner.test.ts` | 16 |
| `src/lib/sync.test.ts` | 15 |
| `src/features/dss/partialBudget.test.ts` | 15 |
| `src/features/farm-records/cropOptions.test.ts` | 8 |
| `src/lib/dbUpgrade.test.ts` | 7 |
| `src/lib/cacheInvalidation.test.tsx` | 5 |
| `src/features/auth/AuthProvider.test.tsx` | 2 |
| `src/lib/apiCache.test.ts` | 1 |
| **Total** | **89** |

Frontend coverage (`npm run test:coverage`, denominator = every file under
`src`): statements **33.48%** (378/1129), branches 25.55% (220/861), functions
24.34% (93/382), lines 33.69% (338/1003). The headline is low because the React
page and form layer has no component tests; the logic modules are covered —
`lib/db.ts`, `lib/sync.ts`, `lib/queueOwner.ts`, `lib/authToken.ts`,
`features/dss/partialBudget.ts`, `features/farm-records/cropOptions.ts` and
three DSS panels are all at 100%.

---

## 3. Implemented and verified

Only functionality supported by an automated test or an explicit live check
appears here. Each entry names what proves it.

| Capability | Proof |
| --- | --- |
| **Cross-farm `client_id` handling** — two farms may hold the same offline key; neither sees the other's row, neither request 500s | `test_same_client_id_in_two_farms_creates_two_records`, `test_cross_farm_client_id_does_not_leak_the_other_farms_row`, `test_a_null_client_id_is_exempt_from_the_composite_constraint`; migration `e6a2b4c7d130` |
| **Same-farm idempotency, sequential** — a replay returns the same row as 200, with exactly one log and one transaction stored | `test_idempotent_log_creation`, `test_farm_scoped_idempotency_still_holds_after_the_constraint_change` |
| **Same-farm idempotency, concurrent** — the loser of the race gets the winner's row with `created=False`, its flushed transaction rolled back rather than double-booked; the endpoint answers **200, not 500**; a non-replay integrity error still raises; two unstubbed threads racing one key book exactly one record | `backend/tests/test_concurrency.py`, 5 tests, file-backed SQLite with two real connections. The threaded case was run 10× consecutively with no flake |
| **Offline queue identity isolation** — the queue is partitioned by an owner key from the token's `sub`; every read path uses the `[ownerKey+status]` index | `queueOwner.test.ts` (16), `sync.test.ts` (15); `lib/queueOwner.ts` and `lib/sync.ts` at 100% statements |
| **Logout queue cleanup** — only the signing-out account's rows are deleted, before the token is cleared; a no-op when signed out; never blocks logout | `sync.test.ts` logout-cleanup block; `dbUpgrade.test.ts` "purges the migrated rows on logout, by owner" |
| **IndexedDB v1 → v2 migration** — a genuine v1 database (v1's own schema string, `verno === 1` asserted) opened by the shipped v2 module: all rows survive with payload intact, `ownerKey` is attributed, `ownerKey` and `[ownerKey+status]` are queryable, migrated rows then flush through the real `sync.ts` | `frontend/src/lib/dbUpgrade.test.ts`, 7 tests. Negative control: breaking the upgrade hook fails 4 of the 7 |
| **Mechanization schema behaviour** — `cost_subtype` validated against a closed taxonomy and the only field that moves a derived figure; `equipment_id`/`hours_used` validated, persisted, read by nothing, and surviving a read-back unchanged | `test_mechanization_params_are_captured_and_round_trip_intact`, `test_mechanization_omitting_the_capture_only_fields_is_accepted`, `test_mechanization_hours_used_out_of_range_rejected`, `test_mechanization_unrecognised_cost_subtype_rejected`, `test_non_mechanization_log_keeps_arbitrary_extra_data`; classified in `docs/adr/0003` |
| **Bioprocess drying model and readings** — process-loss and clean-balance fixtures, exact Page-model fit, insufficient and out-of-range readings, wet↔dry basis round-trip, safe-storage lookup, water balance vs mass difference | `test_bioprocess_service.py` (11); `bioprocess_service.py` at 100% |
| **Drying input validation** — every malformed run rejected as **422 at the schema edge, never 500** | 8 API tests (`mass_out > mass_in`, final moisture not below initial, non-positive mass, moisture out of range, non-increasing readings, band violations) plus 20 client-side tests in `dryingParams.test.ts` mirroring the same rules |
| **Drying arithmetic and API outputs** — detail/summary access control, cross-farm 404, reversal exclusion, per-crop aggregation | `test_bioprocess_detail_*`, `test_bioprocess_summary_*` |
| **Yield-baseline panel** — three seasons required, one high and one low discarded, ties discard one instance not all, mixed units null *with a reason*, season count reported in every branch | 6 API tests + 4 service tests; `YieldBaselinePanel.tsx` at 100% statements |
| **Crop selection logic** — the farm's recorded crops and the predictor's are merged, deduped across case and whitespace, the null crop dropped rather than shown as "Unspecified", one failed source falls back to the other, list sorted stably | `cropOptions.test.ts` (8); `cropOptions.ts` at 100% |
| **Enterprise economics** — classification and coverage, depreciation overlay (a zero rate counts as *unrated*, never a zero charge), proportional allocation, both break-even prices with the cash price provably strictly lower, sensitivity matrix, operating-expense ratio, partial budget signed both ways | `test_enterprise_service.py` (40 collected); `enterprise_service.py` at 100%; `EnterpriseEconomics.tsx` at 94.28% |
| **Offline/backend partial-budget parity** — both implementations agree against one shared fixture, including that an exact zero is not returned as negative zero | `partialBudget.test.ts` (15) and the backend `test_parity_*` block |
| **DSS ledger-derived outputs** — per-crop ranking, alphabetical tie-breaks, break-even yield and each null case, reversal netting, drying-aware unit costs, every degenerate crop case | `dss_service.py` at 100% with the `test_dss_*` API block |
| **Cache invalidation on write** — log writes, queue flushes, equipment creation, maintenance logging and reversals each invalidate the cached derived reads | `cacheInvalidation.test.tsx` (5) |
| **Live database state after cleanup** — verification farms and logs 1076–1078 gone; every seeded/demo record unchanged | Direct SQL, recorded in `docs/DATA_CLEANUP_2026-08-25.md` §4; backend answers `GET /` 200 and unauthenticated `GET /api/v1/ledger/logs` 401, with no error in its log since the deletion |

---

## 4. Implemented but visually / manually verified only

**Do not describe anything in this section as automatically tested.**

| Component | Status |
| --- | --- |
| **`frontend/src/features/farm-records/DryingCurveChart.tsx`** | **0% coverage, no automated test.** Its visual rendering correctness is established by manual inspection only. |

The distinction matters and must be preserved in the thesis:

**Verified automatically**
- the drying calculation and model arithmetic (`bioprocess_service.py`, 100%);
- `dryingParams.ts` — the client-side rules, 94.33% across 20 tests;
- the backend drying service and its fixtures;
- the API drying outputs (detail, summary, validation, reversal handling).

**Not verified automatically**
- the visual rendering correctness of `DryingCurveChart.tsx`.

The chart may be manually inspected and screenshotted for the thesis. The thesis
**must not** state that the chart component itself has automated test coverage.
No chart tests were added; adding them was explicitly out of scope for this task.

Two further components in the same position, for completeness: the untested page
and form layer generally — `FarmRecordCreateForm.tsx` (0/61),
`FarmRecordsPage.tsx` (0/60), `DryingFields.tsx` (0/26), `DryingRunResult.tsx`
(0/34), `Login.tsx` (0/28), `DSSPredictPage.tsx` (0/40), the investor pages and
the app shell — and `useCropOptions.ts` (0/16), the hook wrapping the fully
tested `cropOptions.ts`.

---

## 5. Known data-state limitations

The live database (`agrip-db-1`, database `agriprofit`) at the freeze: **14
farms, 13 users, 109 operational logs, 109 financial transactions, 3 equipment,
1 maintenance log, 10 share tokens**; `max(operational_logs.id)` = 1075.

1. **Eleven unidentified exploratory farms remain, and are to be left alone.**
   `Madlabs Farm` (3), `Sunrise Farm` (4), `lead farm` (5), `Zelle Farm` (19),
   `Dash Check Farm` (20), `Unit Check Farm` (21), `Empty Bucket Farm` (22),
   `Sun Dry Farm` (23), `Beeper Farms` (24), `Break Even Farm` (25) and
   `London Farm` (27) — development leftovers from July–August holding 3–9 logs
   each. Their origin cannot be reliably attributed to any single identified
   run, which is precisely why they were **not** deleted: unlike the two
   `Verify Farm` records, deleting them would be deletion on an assumption.
   **Do not delete, rename, reseed or otherwise "clean up" these farms.**
   `Legacy Farm` (1, 34 logs) is the pre-auth backfill and is not in this
   category.

2. **Two farms are both named `Demo Farm`** — ids **17** and **26**.
   - **Farm 26 carries the seeded demonstration data** (28 logs: the bioprocess
     and enterprise-economics seed). Every Chapter Four figure is read from it.
   - **Farm 17 does not carry the seeded demonstration data** (2 logs).

3. **For thesis demonstrations, sign in as the known seeded farm (26) and
   screenshot its own views.** Do not rely on a farm-list screenshot to
   establish which farm is which — the list is ambiguous by name and contains
   the exploratory farms above.

4. **`hours_used` is sparsely populated** — 3 of 8 seeded mechanisation logs
   (`equipment_id` on 5). Any machine-hour figure computed from today's data
   would be a total over an unknown fraction of actual machine use. See
   `docs/adr/0003`.

5. **The yield model is trained on synthetic data**, not on farm records. Every
   forecast in the evidence inherits that.

---

## 6. Known technical limitations

The two verification gaps this phase was commissioned to close — the Dexie v1→v2
upgrade test and the same-farm concurrency test — are **resolved** (§3) and are
not listed here. What follows is what genuinely remains.

### 6.1 Application defects

1. **Per-crop decision support does not net reversals.** Farm-wide P&L nets
   correctly; the per-crop breakdown and the investor report reusing it do not.
   After reversing a crop expense the crop still shows the reversed cost and a
   phantom "Unspecified" cost appears. Totals stay right; the per-crop
   comparison is misleading after any reversal.
2. **Monetary and quantity fields are unbounded.** `amount`, `purchase_price`
   and `cost` are unconstrained floats; a negative or absurdly large amount is
   accepted and distorts the P&L. (`depreciation_rate` *is* bounded.)
3. **Equipment cannot be corrected.** No PATCH/PUT on `/equipment/{id}` and no
   edit surface. A mistyped depreciation rate is permanent and silently biases
   the overlay, allocated fixed cost and both break-even prices.
4. **A mistaken reversal cannot be rolled back** — only compensated by an
   unlinked entry, leaving an audit trail that is truthful but not
   self-explanatory.
5. **Stale-revalidation window in the service worker — UNVERIFIED**, reasoned
   from the handler's ordering, never reproduced. Listed as a candidate, not a
   confirmed defect.

### 6.2 Testing and verification gaps

1. **The yield model is not validated.** `ml/train.py` 42% and `ml/dataset.py`
   36% are 63 of the 91 missed backend statements. Nothing asserts the
   synthetic data's distribution, the fitted model's quality, or run-to-run
   reproducibility. The suite proves a model exists and that the endpoint
   validates inputs and returns a forecast — nothing about accuracy.
2. **No component tests for the page and form layer**, including
   `DryingCurveChart.tsx` (§4).
3. **`apiClient.ts` (53%) and `logs.ts` (47%)** — the interceptor and error
   paths are the uncovered half.
4. **The v1→v2 upgrade is proven against `fake-indexeddb`, not a browser.**
   Dexie's version machinery, the upgrade callback, the object stores,
   transactions and indexes are all real; browser-specific storage eviction,
   quota behaviour and vendor IDB bugs are out of its reach. Stated in the test
   file's own header.
5. **The concurrency tests run on SQLite.** The deterministic ones force the
   pre-check to miss — which is what makes the `IntegrityError` branch execute
   on every run — while the unstubbed two-thread test covers the genuine
   interleaving without being able to guarantee which path it takes. Postgres's
   behaviour under the same race is inferred from the equivalent constraint,
   not measured.
6. **No end-to-end browser test** of the offline→online transition, the service
   worker lifecycle, or the PWA install path.
7. **No independent security review**, and no load, stress or soak testing.

### 6.3 Documentation and evidence gaps

1. **`TODO(cite)` in `schemas.py`** — the cost-behaviour taxonomy still needs an
   agricultural-economics or extension enterprise-budget citation.
2. **ADR-0003 has not been reconciled against the chapter text.** The
   capture-only classification is recorded in the ADR and `LIMITATIONS.md`, but
   no chapter has been checked for a claim of machine-hour or utilisation
   analysis. No thesis chapter was read or altered in this work.
3. **"Tamper-evident" wording.** Immutability here is audit-trail discipline,
   not cryptographic. Chapters using "tamper-evident" should read
   *audit-trailed*; not yet reconciled.

### 6.4 Thesis validation gaps

1. **No field trial and no real farmer data.** Every figure derives from seeded
   demo records on one farm.
2. **No user evaluation** — no usability study, no task-completion measurement,
   no comparison against the paper-based practice the work is positioned
   against.
3. **The DSS recommendations are unvalidated as agronomic advice.** The
   arithmetic is verified; whether following it improves an outcome is untested
   and, on synthetic training data, untestable here.
4. **Objective 3's data boundary is proven by tests, not by an independent
   security assessment.**
5. **No deployment evidence.** The system runs under `docker compose` on one
   developer machine — no managed hosting, TLS, backup/recovery, secret
   management or observability.

---

## 7. Thesis evidence rule

**The tagged commit `thesis-evidence-freeze-2026-08-25` is the implementation
state from which thesis screenshots and results are to be produced.**

- Every screenshot, figure, table and measured result quoted in the thesis must
  come from this tagged state, and from the live database in the condition
  described in §5 — signed in as the seeded demonstration farm, **farm 26**.
- Any claim of automated verification must trace to §3. Anything in §4 is
  manually inspected and must be described as such.
- Reproduce the figures with:

  ```
  python -m pytest backend/tests -q --cov=backend/app --cov-report=term
  cd frontend && npm run test && npx tsc -b --force && npm run lint && npm run build
  ```

- **No further commits are to be made on top of this tag** unless a genuine
  defect is discovered. If one is, fix it, re-run all six checks, and move the
  tag deliberately — do not let the evidence and the code drift apart silently.

Development stops here. The next phase is thesis evidence collection against
this exact tagged state.
