# Thesis reporting state — reconnaissance

Read-only survey of the repository and its existing documentation, compiled
2026-08-25 for the Chapter 4/5 reporting phase and **reconciled 2026-08-29
against the new thesis baseline**. Nothing here is new evidence: every figure is
a pointer to an artefact already committed. Where a number is quoted it is
because a committed artefact contains it, and the artefact is named.

**Nothing in this report should be cited directly. Cite the source artefact.**

> ## Reconciliation notice — 2026-08-29
>
> This document was written when the 25 August freeze was the reporting
> baseline. It is not. **The thesis baseline is
> `78a68c292205acdcac1a52f977fbea31b6e8495e` on `main`**, and the authoritative
> evidence document is **`docs/EVIDENCE_FREEZE_2026-08-29.md`**.
>
> Four things this document previously asserted are corrected below rather than
> deleted, because each of them, left standing, regenerates a false claim:
>
> 1. **Development did not stop at the freeze.** A production-hardening branch
>    was merged on 29 August. §1 said development was stopped; §9's drift check
>    (`git diff --stat thesis-evidence-freeze-2026-08-25 HEAD` empty) was true of
>    `acb97e4` on 26 August and is **false now** — the diff against `78a68c2` is
>    large and deliberate.
> 2. **The test and coverage figures moved** (190 → 422 collected, 93% → 96%,
>    89 → 148 frontend). §3 and §7 are updated.
> 3. **The B-01 reversal finding was a false positive** (§5). Per-crop decision
>    support nets reversals and did so at the freeze commit as well.
> 4. **"No production deployment" is now too blunt** (§10). A production
>    deployment *path* exists and was exercised; a deployment does not.
>
> History is not rewritten here. Where a statement was true of the 25 August
> state it is retained and dated, with the current state stated beside it.

---

## 0. What already exists (read these first)

The evidence work is already done. This report is an index over it, not a
replacement for it.

| Document | What it is | Authority |
| --- | --- | --- |
| `docs/EVIDENCE_FREEZE_2026-08-29.md` | The **current** evidence state at the baseline `78a68c2`: repo identity, test identity, the B-01 adjudication, live production-stack / RBAC / share-token / throttling / backup-restore verification, the open limitation list, the evidence rule | **Primary. Supersedes everything else on current figures, defects and limitations.** |
| `docs/EVIDENCE_FREEZE_2026-08-25.md` | The 25 August freeze report, left **immutable** as the dated historical record | Historical only. **Do not cite for current figures.** Its §6.1.1 item 1 is a recorded false positive; its §2 figures are superseded |
| `docs/HARDENING_CHANGELOG.md` | What the production-hardening work changed between the freeze and the baseline | Primary for the freeze→baseline delta |
| `docs/EVIDENCE.md` | The command behind every figure quoted on the branch, plus mutation/negative-control runs | Primary for provenance |
| `docs/STATE_REPORT_2026-08-25.md` (2,755 lines) | Read-only pre-freeze audit: implementation state per subsystem, live endpoint output, doc-vs-code discrepancies (§9), closing lists (§10), `CANNOT DETERMINE` (§10 tail) | Primary for subsystem detail |
| `LIMITATIONS.md` (8 sections + Future Work) | Draft limitations chapter | Primary for Ch5 |
| `docs/perf/README.md` + 26 raw Lighthouse artefacts | Frontend performance strand, raw and unedited | Primary for perf figures |
| `performancebenchmarking.md` | Write-up of the perf strand (§3.8.x) | Derived from `docs/perf/` |
| `hostingcostanalysis.md` | Cost strand, measured footprint + published pricing | Primary for cost figures |
| `docs/ch4-data/DATA_PACK.md` + 4 JSON files | Chapter 4 data pack | **Superseded and marked as such** — see §7 |
| `docs/adr/0001-0003` | Three decision records | Primary for design-decision justification |
| `docs/DATA_CLEANUP_2026-08-25.md` | What was deleted from the live DB and what was not | Primary for DB state |
| `PROGRESS.md`, `CONTEXT.md`, `PRD.md`, `STRUCTURE.md` | Project-level narrative and structure | Narrative only — **not evidence** |
| `usabilitysessionrunsheet.md` | Facilitator **script** for usability sessions | **A plan, not results.** See §10 |

---

## 1. Current implementation status

- **Corrected 2026-08-29.** This section previously read "development is stopped
  at a declared freeze", quoting the 25 August freeze §7. That was true on
  25–26 August. It is not true now: a production-hardening branch was developed
  and merged into `main` on 29 August as `78a68c2`, adding role-based
  authorization, login throttling, share-token expiry and revocation, credential
  scrubbing, monetary and quantity bounds, equipment correction, a migration
  test suite, forecast-reproducibility tests, and a production deployment
  composition with backup and restore tooling. **Development stopped at
  `78a68c2`**, which is the thesis baseline.
- The system is a working end-to-end application (FastAPI + SQLAlchemy +
  PostgreSQL, Alembic-managed; React + TypeScript PWA; Dockerised), not a
  prototype or mockup.
- `PROGRESS.md` §5 describes the pre-freeze state and has not been re-verified
  against the baseline; treat it as narrative, not evidence.
- The two verification gaps the last work cycle was commissioned to close (the
  Dexie v1→v2 upgrade test and the same-farm concurrency test) are **closed**,
  and remain closed at the baseline.

## 2. Major implemented features relevant to the thesis

Mapped from `PROGRESS.md` §2 and confirmed against the freeze report §3.

1. **Offline-first operational logbook** — IndexedDB queue, automatic sync on
   reconnect, `client_id` idempotency guard.
2. **Financial ledger engine** — operational logs map automatically into a
   single-entry ledger; per-crop revenue/expense; P&L with monthly breakdown and
   CSV export.
3. **Ledger integrity** — soft-immutable records; deletes blocked (405);
   corrections via auditable category-preserving reversal with `reverses_id`;
   double-reversal and cross-farm tampering rejected.
4. **Two-tier DSS** — deterministic tier (unit cost of production, per-crop gross
   margin, break-even yield, both break-even prices, sensitivity matrix,
   operating-expense ratio, partial budget) computed from the farm's own ledger;
   predictive tier (RandomForest yield forecast with a confidence band derived
   from tree spread).
5. **Enterprise economics** — cost-behaviour classification, derived fixed-cost
   overlay with depreciation, proportional allocation.
6. **Bioprocess drying** — Page/Newton model fit, wet↔dry basis conversion, water
   balance, safe-storage lookup, per-crop aggregation, drying-aware unit costs.
7. **Identity and per-farm data boundary** — JWT + bcrypt; every query farm-scoped;
   cross-farm read returns 404.
8. **Investor/stakeholder sharing** — tokenised read-only link, tokens SHA-256
   hashed at rest.
9. **Mechanization tracker** — equipment, maintenance logs, depreciation rate.
   `equipment_id` / `hours_used` are **capture-only** (ADR-0003) — see §5.

## 3. Tests and verification evidence

**All figures below are from `docs/EVIDENCE_FREEZE_2026-08-29.md` §3, measured
at the baseline `78a68c2`.** The 25 August figures they replace are kept in the
row beneath each, dated, so a reader meeting the old number elsewhere can place
it.

| Check | Command | Result at `78a68c2` | At the 25 Aug freeze |
| --- | --- | --- | --- |
| Backend suite | `python -m pytest backend/tests -q` | **422 collected; 418 passed, 4 skipped, 0 failed**, 279.89 s | 190 passed, 0 skipped |
| Backend migration chain | `MIGRATION_TEST_DATABASE_URL=… pytest backend/tests/test_migrations.py -v` | **12 passed, 0 skipped**, against PostgreSQL 15.18 | did not exist |
| Backend coverage | same `--cov=backend/app --cov-report=term` | **96%** (1,594 statements, 66 missed) | 93% (1,286 / 91) |
| Frontend suite | `cd frontend && npm run test` | **13 files, 148 tests**, all passed | 9 files, 89 tests |
| Frontend coverage | `npm run test:coverage` | **43.18%** statements (558 / 1,292) | 33.48% |
| TypeScript | `npx tsc -b --force` | exit 0 | exit 0 |
| ESLint | `npx eslint .` | exit 0, 0 errors, 0 warnings | same |
| Production build | `npm run build` | see §7 — **re-measured 29 Aug**; the 6.86 s / 21-entry / 859.67 KiB figures are the freeze's and must not be quoted as the baseline's | built 6.86 s; precache 21 entries / 859.67 KiB; `dist/` 959 KB |

- The **4 skipped** backend cases are the migration tests requiring a real
  PostgreSQL server. Supplied with one they execute and pass, as row 2 records.
  Report as "418 passed with 4 skipped locally; 422 passing when a database is
  supplied" — never as "422 passed" without that clause.
- **Count collected cases, not `def test_`.** Six backend modules parameterise;
  `test_enterprise_service.py` defines 32 functions that expand to 40 collected
  cases. The 422 total is composed of collected cases. `grep -c "^def test_"`
  undercounts six files.
- The freeze→baseline movement is **entirely additive**: nine new backend
  modules and four new frontend files. The four backend modules that existed at
  the freeze collect exactly the same 190 cases at the baseline
  (`test_api.py` 134, `test_enterprise_service.py` 40,
  `test_bioprocess_service.py` 11, `test_concurrency.py` 5), so no earlier
  verification was removed, weakened or renumbered.
- Frontend coverage remains low because the React page/form layer has no
  component tests. The **logic** modules are at or near 100%
  (`lib/db.ts`, `lib/sync.ts`, `lib/queueOwner.ts`, `lib/authToken.ts`,
  `features/dss/partialBudget.ts`, `features/farm-records/cropOptions.ts`, the
  record-bounds rules, three DSS panels; `dryingParams.ts` at 94.33%). Quote
  both numbers or neither.
- The frontend suite is **not timing-robust under machine contention**: run
  concurrently with the backend suite one dashboard test exceeded the 5,000 ms
  default timeout; alone the file passes in 2.93 s and the suite passes 148/148
  (29 Aug freeze §3.4). Contention, not a defect — but worth one sentence.
- Per-capability proof (which test proves which claim) is tabulated in the
  25 August freeze §3 (17 rows) and extended by the 29 August freeze §3.6–§3.11.
  **Any claim of automated verification in the thesis must trace to one of
  those.**
- Per-module backend coverage below 100% is listed in the 29 August freeze §3.1.
- **Do not write "CI is green."** The workflow is defined and readable, but no
  GitHub Actions run result for `78a68c2` was retrievable and none is recorded
  in the repository. Its jobs' substance was executed locally instead; cite it
  that way.
- **Negative controls exist.** `docs/EVIDENCE.md` records mutation runs proving
  the tests are load-bearing: breaking the cache purge → 5 failed / 0 passed;
  breaking the Dexie upgrade hook → 4 of 7 fail; the partial-budget parity
  fixture fails when it should. This is unusually strong evidence and is worth
  reporting.
- The one backend warning is a `StarletteDeprecationWarning` raised inside the
  installed FastAPI package, not by this repository's code.

## 4. Documented / live / manual verification

- **Live endpoint output** captured in `STATE_REPORT` §6; live database contents
  in §5.
- **Live DB state after cleanup** verified by direct SQL, recorded in
  `docs/DATA_CLEANUP_2026-08-25.md` §4.
- **Frontend performance** — Lighthouse 13.4.1, headless Chrome, mobile
  emulation (412 × 823 @ DPR 1.75), `simulate` (Lantern) throttling, target
  `http://localhost:4173/` (`vite preview` on the production build, so the
  service worker is active). Same method on both dates; **two measurement sets
  now exist and must never be mixed**:
  - **2026-08-29, commit `78a68c2` — the baseline set, and the one to report.**
    5 cold slow-3G CLI runs, 5 cold slow-4G CLI runs, 3 user-flow iterations
    each containing a cold **and** a warm navigation. Medians: cold slow-3G
    FCP/LCP/SI **5661.2 ms**, TBT 10.5, perf **65**; cold slow-4G FCP **1709.9
    ms**, LCP 1859.9, TBT 9.0, perf **99**; warm flow navigation FCP **70.6 ms**,
    LCP **1612.0 ms**, TBT 0, perf 100. Cold transfer **139,245 B over 8
    requests**; warm transfer **127 B over 7** — the whole shell at 0 B, the
    127 B being `pwa-192x192.png`, which is the manifest icon the precache omits.
    CLS 0 throughout. `benchmarkIndex` 1406–1996.
  - **2026-08-17, commit `c16924e` — superseded.** Medians: cold slow-3G 7674.4
    ms / perf 57; cold slow-4G 2317.7 ms / perf 95; warm FCP ≈ 105–122 ms;
    cold transfer 243,724 B over 7 requests. `benchmarkIndex` 425–1654. Quote
    only with its date and commit, and only as the earlier build.
  - Service-worker attribution is settled by a driven-browser probe
    (`offline-probe.mjs`, exits 0 on PASS), not by the timings.
- **Manual-only:** `DryingCurveChart.tsx` — 0% coverage, no automated test;
  visual correctness established by inspection only (freeze §4).
- **Screenshots** are to be taken per `docs/ch4-data/screenshot-runsheet.md`,
  signed in as **farm 26**.

## 5. Important limitations and known deviations

Full text in `LIMITATIONS.md` and freeze §§5–6. The ones that most constrain what
Chapter 4 may say:

**Application defects — adjudicated at the baseline (29 Aug freeze §5)**

The five entries that stood here were the 25 August freeze §6.1 list. Three no
longer stand, and the reason differs in each case. All five are kept, with their
disposition, because the old list is quoted in other documents.

1. ~~Per-crop decision support does not net reversals; a phantom "Unspecified"
   cost appears.~~ **FALSE — never a defect (B-01 = NETTED).** Settled by
   execution at both `59a6286` and `78a68c2`: reversing a ₦25,000 crop expense
   moved that crop's expenses 35,000 → 10,000 and its unit cost 2,916.67 →
   833.33, with no `Unspecified` bucket at any point; the investor report
   returned the same netted figures unauthenticated. The capability was
   introduced by `6992d1c` on 16 August, nine days before the freeze, and the
   freeze's own §3 already listed reversal netting as verified — §3 and §6.1.1 of
   that document contradict each other and §3 is the correct half. **Chapter 4/5
   must report this as a withdrawn finding, not as a fix.**
2. ~~`amount`, `purchase_price` and `cost` are unbounded floats.~~ **CLOSED by
   `78a68c2`** — `Money` / `Quantity` at the schema edge (`ge=0`, `le=1e9` /
   `1e6`, `allow_inf_nan=False`), 32 collected tests, live 422s for negative,
   over-cap, `Infinity` and `NaN`.
3. ~~Equipment cannot be corrected.~~ **CLOSED by `78a68c2`** —
   `PATCH /equipment/{id}` (migration `b9e5f30c74a1`), 20 collected tests,
   partial and farm-scoped, out-of-range rate refused, `updated_at` stamped only
   on a real change.
4. A mistaken reversal cannot be rolled back, only compensated. **STILL OPEN.**
5. A stale-revalidation window in the service worker is **reasoned, never
   reproduced** — a candidate, not a confirmed defect. **STILL OPEN, still
   unverified.**

**Also closed by `78a68c2`** (each was an absence rather than a defect, and each
is now a capability Chapter 4 may report): no authorization model → 3 roles / 12
permissions with permission checked before scope; no rate limiting → per-account
and per-address login budgets; share tokens never expiring and logged in
cleartext → 90-day expiry, revocation, hash-at-rest, three-logger scrubbing;
`POST /dss/train` callable by any authenticated user → granted to no role and
disabled by config; unpinned requirements → pinned; no migration executed by any
test → 12/12 against PostgreSQL 15.18; no production deployment configuration →
`docker-compose.prod.yml` built, started and probed, with backup and restore
rehearsed.

**Data-state (re-established by direct query at the baseline, 29 Aug freeze §4)**
- Live DB: 14 farms, 13 users, 109 operational logs, 109 financial transactions,
  3 equipment, 1 maintenance log, 10 share tokens, `alembic_version`
  `b9e5f30c74a1`, 0 unpaired operational logs. Identical to the freeze census —
  but quotable because it was re-queried, not inherited.
- **Two farms are both named `Demo Farm`.** Farm **26** carries the seeded
  demonstration data (28 logs); farm 17 does not (2 logs). Every Chapter 4 figure
  is read from farm 26. Do not use a farm-list screenshot to identify farms.
- Eleven unidentified exploratory farms remain and are to be **left alone**.
- `hours_used` is populated on 3 of 8 seeded mechanisation logs.
- The yield model is trained on **synthetic data**; every forecast inherits that.

**Naming / wording deviations**
- "Tamper-evident" in the chapters should read **audit-trailed** — immutability
  here is application-layer discipline, not cryptographic. Not yet reconciled.
- `TODO(cite)` remains in `schemas.py` (cost-behaviour taxonomy) and on the
  safe-storage moisture table (FAO / NSPRI / IITA guidance). Both need real citations.
- **ADR-0003 has not been reconciled against the chapter text** — no chapter has
  been checked for a claim of machine-hour or utilisation analysis. Open action
  for the reporting phase.

## 6. Architecture / components relevant to reporting

Detail in `STRUCTURE.md`; subsystem state in `STATE_REPORT` §§3, 4, 7.

- **Backend** `backend/app/` — `api/endpoints/` (auth, ledger, reports, dss,
  bioprocess, equipment, share), `services/` (ledger, dss, enterprise,
  bioprocess, reports, share, auth, equipment), `models/`, `schemas/`,
  `ml/` (dataset, train, predict), `core/security.py`; Alembic under
  `backend/alembic/versions/` (relevant late migration: `e6a2b4c7d130`,
  farm-scoped `client_id` uniqueness).
- **Frontend** `frontend/src/` — `features/` (farm-records, dss, dashboard, auth,
  investor), `lib/` (db, sync, queueOwner, authToken, apiCache, apiClient),
  PWA service worker + Workbox precache.
- **Deployment** — `docker-compose.yml`: `agrip-backend-1`, `agrip-db-1`,
  `frontend-prod`. Single developer machine only.
- **ADRs** — 0001 bioprocess drying parameters in `extra_data`; 0002 derived
  fixed-cost overlay and temporary domain assumptions; 0003 `equipment_id` /
  `hours_used` are capture-only.

## 7. Metrics / results that ARE supported by evidence

Safe to report, with the named source.

| Result | Source |
| --- | --- |
| **422 collected backend cases — 418 passed, 4 skipped locally, 0 failed; 96% coverage, 1,594 stmts / 66 missed** | 29 Aug freeze §3.1 |
| **12/12 migration tests against PostgreSQL 15.18**, 0 skipped | 29 Aug freeze §3.3 |
| **148 frontend tests across 13 files; 43.18% statement coverage** (32.41% branch, 36.16% function, 43.00% line) | 29 Aug freeze §3.4 |
| Per-module backend coverage list | 29 Aug freeze §3.1 |
| Per-file collected counts, all 13 backend files | 29 Aug freeze §3.2 |
| tsc / eslint clean; **build 13.45 s; precache 22 entries, 866.74 KiB; `dist/` 967 KB** (re-measured 29 Aug at the baseline) | Chapter 4 Table 4.3 |
| **Lighthouse at the baseline, 29 Aug 2026 / `78a68c2`:** cold slow-3G FCP/LCP/SI 5,661.2 ms, TBT 10.5, perf **65**; cold slow-4G FCP 1,709.9 ms, LCP 1,859.9 ms, perf **99**; warm FCP 70.6 ms, LCP 1,612.0 ms, TBT 0, perf **100**; CLS 0 throughout; `benchmarkIndex` 1406–1996 | Chapter 4 Table 4.22 |
| **Bundle at the baseline: 139,245 B transferred over 8 requests cold; 127 B over 7 warm** (the 127 B is `pwa-192x192.png`, absent from the precache); entry chunk 400.07 KB raw / 130.03 KB gzip | Chapter 4 §4.10 |
| *Superseded, quote only with its date and commit:* 17 Aug 2026 / `c16924e` — cold slow-3G perf 57, cold slow-4G perf 95, warm FCP ~105–122 ms, single JS chunk 243,724 B over 7 requests | `docs/perf/README.md` |
| Live production stack: 7 live checks passing (SPA served, readiness from the backend, `/api` prefix intact, register→login→`/auth/me` as owner, SPA fallback, no host DB port, both app containers non-root) | 29 Aug freeze §3.7 |
| Live RBAC matrix; 403 body naming only the missing permission; `POST /dss/train` 403 for an owner | 29 Aug freeze §3.10 |
| Share-token lifecycle live: 90-day expiry to the second, revoked and unknown both 404, token unusable as a bearer credential, raw token absent from all three logs | 29 Aug freeze §3.8 |
| Login throttling live: 10 × 401 then 429 with `Retry-After: 896`, message naming no account; counters cleared by a restart | 29 Aug freeze §3.9 |
| Input bounds and equipment correction live: −1e6, 2e9, `Infinity`, `NaN` each 422; PATCH stamps `updated_at` only on a real change; DELETE 405 | 29 Aug freeze §3.11 |
| Backup/restore rehearsal: 28,164-byte archive, 8 tables with data, every restored row count matching, `alembic_version` at chain head `b9e5f30c74a1`, 0 unpaired logs, live DB untouched | 29 Aug freeze §3.12 |
| **B-01 = NETTED**: reversing ₦25,000 moves crop expenses 35,000 → 10,000 and unit cost 2,916.67 → 833.33, no `Unspecified` bucket, at **both** `59a6286` and `78a68c2`; investor report inherits it | 29 Aug freeze §2 |
| Forecast metrics **re-derived, not read**: R² 0.976204, MAE 0.241393, **RMSE 0.488334 t/ha**, agreeing with `model_baseline.json` to six decimal places; dataset fingerprint `sha256 a461b884…` stable across two environments | 29 Aug freeze §3.5 |
| *Superseded:* 190 backend tests, 93% coverage, 1,286 stmts / 91 missed; 89 frontend tests across 9 files at 33.48%; build 6.86 s / precache 21 entries / 859.67 KiB / `dist/` 959 KB | 25 Aug freeze §2 — **historical only** |
| Estimated hosting cost **$15.40 / month ≈ ₦20,950** (2 GB tier $12 + snapshots $2.40 + domain $1.00 + Let's Encrypt $0) | `hostingcostanalysis.md` §6 |
| Measured container footprint subtotal **178.9–202.8 MiB** | `hostingcostanalysis.md` §2 |
| Yield model: Pipeline(OneHotEncoder + RandomForestRegressor), 200 estimators, 6,000 synthetic samples, 5 crops, plus feature importances. **Take the metrics from the 29 Aug freeze §3.5 row above, not from this JSON** — it predates the reproducibility work and records no RMSE | `docs/ch4-data/model_info.json` |
| Maize DSS: revenue ₦45,000, expenses ₦3,500, gross margin ₦41,500, yield 100 kg, marketable 84 kg, **unit cost ₦35.00/kg harvested, ₦41.67/kg marketable**, break-even yield 7.78 kg | `docs/EVIDENCE.md` seed-idempotency block; `docs/ch4-data/dss_per_crop.json` |
| Cassava: revenue ₦178,600, expenses ₦94,400, 1,880 kg, break-even yield 993.68 kg. Tomato: revenue 0, expenses ₦112,900, break-even **null** | `docs/ch4-data/dss_break_even.json` |
| Maize drying: 1 run, 100 kg in, 84 kg marketable, 14.08 kg water removed, mean rate 1.408 kg/h, Newton k 0.0802 (SOLAR_DRYER), safe-storage share 1.0 | `docs/ch4-data/bioprocess_summary.json` |
| Seed is idempotent — figures bit-identical across a re-run (md5 `1850df22069facec23e86032275c659f` on both captures) | `docs/EVIDENCE.md` |
| Scope figures: `backend/tests/` +2,194 insertions / −4 deletions on the branch; no migration, no `ml/` change, no new dependency in the enterprise range | `docs/EVIDENCE.md` Scope figures |

**Caveats that must travel with those numbers:**
- R² 0.976204 / MAE 0.241393 / RMSE 0.488334 are **in-distribution on synthetic
  data**. They are *reproducible* — that is a property of the pipeline, and it is
  established. They are not a claim about real-farm accuracy; the model is
  unvalidated against any real observation. Do not let "reproducible" be read as
  "accurate".
- Lighthouse `benchmarkIndex` varied 425–1654 on 17 Aug and 1406–1996 on 29 Aug.
  **TBT and the composite performance score move with host speed**; no
  difference in either between measurement dates may be attributed to code. Only
  the network-bound metrics (FCP, LCP, SI) and the byte counts compare across
  sets. Within a set the warm-against-cold contrast is internally controlled and
  sound.
- The Lighthouse figures are **simulated (Lantern) throttling against localhost
  on one developer machine**, on both dates. They are a model of a degraded
  network, not a measurement of a real one, and no figure in the strand was
  obtained on a real device over a real Nigerian connection.
- Hosting cost is **estimated, not incurred** — no production deployment exists,
  only a production deployment path that has been exercised.
- `docs/ch4-data/DATA_PACK.md` is **superseded** (measured 2026-08-19 at
  `e3bb674`: 91 tests, 91% coverage, 1,043 statements) and says so in its own
  header. Do not quote its test/coverage figures; its JSON siblings remain valid
  for the DSS / bioprocess / model values above.

## 8. Existing documentation relevant to the thesis

Beyond §0: `AgriProfit_Chapters_1-3.docx` and `_corrected.docx`,
`Thesis_Ch1-3.docx`, `docs/print/Thesis_Ch1-3.{docx,pdf}` (chapter exports —
under instruction not to touch), `AgriProfit_Evaluation_Pack.docx`,
`AgriProfit_Viva_Prep.docx`, `Updated B.Tech Final Project Guideline for
2025_2026_v1.pdf` (departmental guideline, untracked input),
`UNUSED_FILES_ANALYSIS.md`, `.scratch/` tickets, `docs/agents/` process docs.

`docs/THESIS_MASTER_INSTRUCTION.md` exists but is **empty (0 bytes)**.

`STATE_REPORT` §9 lists documentation-versus-code discrepancies — read it before
quoting any figure out of `PROGRESS.md`, `CONTEXT.md` or `PRD.md`.

## 9. Reporting baseline — CORRECTED 2026-08-29

| | |
| --- | --- |
| **Baseline commit (cite this)** | **`78a68c292205acdcac1a52f977fbea31b6e8495e`** |
| Commit subject | `Merge pull request #1 from DEWA-Empr/harden/production-readiness` |
| Branch | `main`, `0 0` against `origin/main` |
| Commit date | Sat 29 Aug 2026 06:12:55 +0900 |
| Working tree | clean for all tracked files (untracked paths listed in the 29 Aug freeze §1.1) |
| Evidence document | `docs/EVIDENCE_FREEZE_2026-08-29.md` |

**The previous baseline, retained as history.** Tag
`thesis-evidence-freeze-2026-08-25` (annotated), implementation commit
`59a6286`, tag commit `acb97e4` (documentation-only), branch
`feat/partial-budget-parity`, dated Tue 25 Aug 2026 21:31:55 +0900. `59a6286`
and the tag are identical in every source file.

**The drift check in this section is superseded, and the correction matters.**
This report previously recorded that
`git diff --stat thesis-evidence-freeze-2026-08-25 HEAD -- backend/ frontend/`
was **empty**. That was true on 26 August, when `HEAD` was `acb97e4`. It is
**false now**: the production-hardening branch was merged on 29 August, so the
diff between the freeze tag and `78a68c2` is large and intentional — nine new
backend test modules, new application code for authorization, rate limiting,
credential scrubbing, share-token expiry, equipment correction and input bounds,
a migration, and a production deployment composition with backup and restore
scripts. Anyone re-running that command today will get a long diff, and that is
correct, not a sign of accidental drift. `docs/HARDENING_CHANGELOG.md` records
what changed.

**Cite the baseline commit, not the tag and not the branch name.** Every
screenshot, figure, table and measured result must come from `78a68c2`, with the
live database in the condition described in the 29 Aug freeze §4, signed in as
**farm 26**.

> **SUPERSEDED IN PART — 7 September 2026.** The reporting baseline for test
> figures, for the thirteen screenshots in `Screenshots/` and for all frontend
> behaviour is now commit **`598eab0`**
> (`598eab0a02533e9692332d92382d42f16fc9e346`), recorded in
> `docs/EVIDENCE_FREEZE_2026-09-07.md`. The screenshots were captured against
> that state and do **not** reproduce from `78a68c2`. The **performance figures
> remain at `78a68c2` and were not re-measured**; cite `78a68c2` for those and
> `598eab0` for everything else. The database condition and the farm 26 sign-in
> above are unchanged.

Reproduce with:

```
python -m pytest backend/tests -q --cov=backend/app --cov-report=term
python -m pytest backend/tests --collect-only -q
cd frontend && npm run test && npm run test:coverage && npx tsc -b --force && npm run lint && npm run build
python -m pytest backend/tests/test_reproducibility.py -q
```

And, with Docker available, the parts CI would otherwise own — the migration
chain against real PostgreSQL, the production stack, and the backup/restore
rehearsal — per the 29 Aug freeze §7.

Development stopped at `78a68c2`. No further commits unless a genuine defect is
found; if one is, fix it, re-run every check above, and re-establish the
baseline deliberately.

## 10. Claims that must NOT be made

Each is unsupported by anything in this repository.

**On validation**
1. **No claim of yield-model accuracy on real farms.** Nothing asserts the
   synthetic data's realism or the fitted model's real-world quality. At the
   baseline `ml/train.py` (47%) and `ml/dataset.py` (82%) are 37 of the 66
   missed backend statements. The suite proves a model exists, that the endpoint
   validates inputs and returns a forecast, and — this part **has** changed —
   that the pipeline is **seed-deterministic and reproducible**: the metrics
   re-derive to six decimal places and the dataset fingerprint is stable across
   two environments (18 tests). Reproducibility is a property of the procedure.
   It is not accuracy, and the two must not be conflated in either direction:
   do not claim field accuracy, and do not repeat the withdrawn claim that the
   pipeline is non-reproducible or that RMSE is unavailable — RMSE is
   **0.488334 t/ha**.
2. **No claim that the DSS recommendations are agronomically sound.** The
   arithmetic is verified; whether following the advice improves an outcome is untested.
3. **No claim of a field trial or of real farmer data.** Every figure derives
   from seeded demo records on one farm.
4. **No claim of a usability study, task-completion measurement, SUS score,
   heuristic-evaluation findings, or comparison against paper-based practice.**
   `usabilitysessionrunsheet.md` is a facilitator **script**; no session results
   exist anywhere in the repository.

**On verification**
5. **Do not say `DryingCurveChart.tsx` has automated test coverage.** It is 0%,
   manually inspected only (freeze §4). Same for the page/form layer:
   `FarmRecordCreateForm.tsx`, `FarmRecordsPage.tsx`, `DryingFields.tsx`,
   `DryingRunResult.tsx`, `Login.tsx`, `DSSPredictPage.tsx`, the investor pages,
   the app shell, and `useCropOptions.ts`.
6. **Do not claim browser-verified IndexedDB migration.** The v1→v2 upgrade is
   proven against `fake-indexeddb`; browser storage eviction, quota behaviour and
   vendor IDB bugs are out of its reach.
7. **Do not claim Postgres concurrency behaviour was measured.** The concurrency
   tests run on SQLite; Postgres is inferred from the equivalent constraint.
8. **Do not claim end-to-end browser testing** of the offline→online transition,
   the service-worker lifecycle, or the PWA install path. None exists.
9. **Do not claim an independent security review, penetration test, threat
   model, or load, stress or soak testing.** None was performed. Objective 3's
   data boundary is proven by tests **and by live probing of the running
   production stack** — which is stronger than "tests only" was, and is still
   not an independent assessment.

**On deployment and operations**
10. **Do not claim a production deployment — and do not claim the blanket
    absence either.** Both errors are now available and both are wrong. What is
    true: a production composition builds, starts and was probed live; TLS is
    configured via an optional Caddy edge whose config renders; secrets are
    enforced by a startup guard with nothing committed; backup and restore were
    rehearsed end to end against real PostgreSQL; the migration chain was
    executed against PostgreSQL 15.18. What is false: that any instance serves
    real users, that a departmental host runs it, that a certificate was ever
    issued for a real domain, that production observability exists (it does not
    — no metrics, no tracing, no alerting), or that production-scale performance
    is known. Hosting cost is estimated, not incurred. The formula to use is
    **"an exercised deployment path"**, never "deployed".
11. **Do not present the Lighthouse figures as production or real-network
    behaviour.** Single developer machine against localhost, simulated (Lantern)
    network and CPU throttling — on both measurement dates. Quote the 29 August
    baseline set; quote the 17 August set only with its date and commit.
11a. **Do not write "CI is green."** The workflow is defined and its jobs are
    readable, but no run result for `78a68c2` is retrievable or recorded. Its
    substance was executed locally; cite it that way.

**On wording and arithmetic**
12. **Do not write "tamper-evident"** where "audit-trailed" is meant.
    Immutability is application-layer, not cryptographic.
13. **REVERSED 2026-08-29 — the per-crop DSS figures ARE reversal-correct.**
    This item previously said the opposite, citing the 25 August freeze §6.1.1.
    That finding is a false positive; see §5 above and the 29 August freeze §2.
    The prohibition now runs the other way: **do not claim, anywhere, that
    per-crop decision support fails to net reversals, that a phantom
    `Unspecified` bucket appears, or that the investor report inherits such a
    defect.** Do not claim either that `78a68c2` fixed reversal netting — the
    behaviour predates the freeze by nine days and the baseline merely confirms
    it.
13a. **Do not repeat any of the other closed findings as live.** Specifically:
    the yield baseline is reachable (the panel is mounted in the
    enterprise-economics view); the crop list is assembled at run time from the
    farm's own crops merged with the model's, not hard-coded; drying readings
    can be entered through the form; RMSE exists; the pipeline is reproducible;
    money and quantity fields are bounded; equipment is correctable; a
    deployment path, a backup/restore procedure, secret enforcement, RBAC,
    share-token lifecycle controls and login throttling all exist.
14. **Do not claim machine-hour or utilisation analysis.** `equipment_id` and
    `hours_used` are capture-only (ADR-0003), and `hours_used` is populated on 3
    of 8 seeded mechanisation logs.
15. **Do not quote the superseded `DATA_PACK.md` test figures** (91 tests, 91%,
    1,043 statements), nor its statement that the drying form has no readings
    input — both are stale. The same applies to the 25 August freeze's figures
    (190 / 93% / 89) and to this report's own pre-reconciliation figures: quote
    the baseline set from `docs/EVIDENCE_FREEZE_2026-08-29.md`.
17. **Do not upgrade "implemented" or "verified" into "validated in practice."**
    Implemented = present in the system. Verified = supported by a named test,
    command or reproducible check. Validated in practice = demonstrated with
    real users, in field conditions, or in production operation. Nothing in this
    project reaches the third level. The distinction is load-bearing for
    security, usability, forecasting, production deployment and performance.
16. **Do not attribute the cost-behaviour taxonomy or the safe-storage moisture
    ceilings to a source.** Both still carry `TODO(cite)`.
