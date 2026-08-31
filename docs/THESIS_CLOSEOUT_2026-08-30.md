# Thesis closeout report — 30 August 2026

**Purpose.** Establish the final evidence baseline for submission, audit Chapter
Three against the implementation that actually exists, and specify exactly what
Chapter Four may claim and what must be captured to support it.

**Freeze observed.** No application code, test, threshold, model or algorithm was
touched in producing this report. Every command run was read-only or a test
execution. Several stale claims and two live defects in the chapter text were
found; none was fixed.

**What this adds to what already exists.** `docs/EVIDENCE_FREEZE_2026-08-29.md`
is the authoritative measurement document and this report does not replace it.
This report adds (a) independent re-verification of the headline figures one day
later, (b) the Chapter Three audit, which no document had performed, (c) the
Chapter Four evidence map, and (d) a screenshot plan built against the *current*
interface rather than the 19 August one.

---

## 1. Submission baseline

| | |
|---|---|
| **Branch** | `main` |
| **Commit** | `78a68c292205acdcac1a52f977fbea31b6e8495e` |
| **Commit subject** | `Merge pull request #1 from DEWA-Empr/harden/production-readiness` |
| **Commit date** | Sat 29 Aug 2026 06:12:55 +0900 |
| **Working tree** | **Clean for all application code.** Two tracked documentation files are modified and uncommitted; twelve untracked paths exist. Neither set changes a byte of `backend/app`, `backend/tests`, `frontend/src`, `backend/alembic` or any configuration. |
| **Verification date** | 30 Aug 2026 |

### 1.1 Uncommitted tracked changes — documentation only

| File | What changed | Bearing on evidence |
|---|---|---|
| `LIMITATIONS.md` | Rewritten against the 29 Aug freeze: §1 deployment, §2 throttling and RBAC, §3 input bounds / equipment correction / the reversal-netting retraction, §7 performance, §8 verification figures, §9 future-work renumbering | **This is the corrected text and should be committed before submission.** The committed version still carries the 93% / 190 / 89 figures and the false reversal defect. |
| `docs/perf/README.md` | SUPERSEDED banner pointing at `docs/perf/2026-08-29/` | Should be committed. Without it the 17 Aug figures read as current. |

**Recommendation.** Commit these two documentation edits together with the
untracked evidence artefacts as one `docs:` commit. It changes no measured
figure, so the Chapter Four evidence baseline remains `78a68c2` either way.
State it in the thesis as "commit `78a68c2`, with its accompanying documentation
set".

### 1.2 Untracked paths, excluded from the implementation baseline

`.gemini/`, `claude/Thesis_Ch4-5_DRAFT.md`, `AGENT_PROMPT_chapter4_gaps.md`,
`AGENT_PROMPT_thesis_conformance.md`, `MERGE_AUDIT.md`,
`docs/CH4_LOCATION_MAP.md`, `docs/EVIDENCE_FREEZE_2026-08-29.md`,
`docs/THESIS_REPORTING_STATE.md`, `docs/perf/2026-08-29/`, `docs/print/`,
`Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf`, and this file.

`docs/perf/2026-08-29/` and `docs/EVIDENCE_FREEZE_2026-08-29.md` are **evidence
artefacts Chapter Four will cite and must be committed.** The rest is working
material.

### 1.3 Were existing thesis figures produced from an older commit?

**Yes — all of them.** Chapter Four §4.1 states in terms: *"the annotated Git tag
`thesis-evidence-freeze-2026-08-25`, whose implementation commit is `59a6286`
… Development stopped at that tag."* Development did not stop at that tag; a
production-hardening branch was merged on 29 August. **Every quantitative claim
in the current Chapter Four text is measured at `59a6286` and must be
re-sourced.** The performance figures are older still — commit `c16924e`,
17 August.

### 1.4 Existing evidence documents, and their standing

| Document | Standing |
|---|---|
| `docs/EVIDENCE_FREEZE_2026-08-29.md` | **AUTHORITATIVE.** Every Chapter 4–5 figure traces here. |
| `docs/perf/2026-08-29/README.md` | **AUTHORITATIVE** for performance. |
| `backend/app/ml/model_baseline.json` + `docs/REPRODUCIBILITY.md` | **AUTHORITATIVE** for ML metrics. |
| `LIMITATIONS.md` (working-tree version) | **AUTHORITATIVE** for limitations. |
| `hostingcostanalysis.md` | **AUTHORITATIVE for cost**, with two stale figures — §4 register rows C-09, C-10. |
| `docs/HARDENING_CHANGELOG.md` | Authoritative delta record of what the merge superseded. |
| `docs/EVIDENCE_FREEZE_2026-08-25.md` | **HISTORICAL ONLY.** Immutable. Contains one recorded false positive (its own §3 contradicts its §6.1.1). |
| `docs/STATE_REPORT_2026-08-25.md` | **HISTORICAL ONLY.** Source of that false positive. |
| `docs/ch4-data/DATA_PACK.md` | **SUPERSEDED** (19 Aug, `e3bb674`). Self-labelled. |
| `docs/ch4-data/screenshot-runsheet.md` | **SUPERSEDED.** Three of its findings are now false — §4 rows C-11 to C-13. |
| `docs/ch4-data/*.json` | **STALE — a three-crop snapshot of a five-crop farm.** The per-crop maize, cassava and tomato rows remain valid; **no farm-wide total is**. |
| `docs/CH4_LOCATION_MAP.md` | File paths and claim boundaries serviceable; §D figures superseded; its own §A2 and §A4 partly overtaken. |
| `performancebenchmarking.md` | **SUPERSEDED** (17 Aug, `c16924e`). |
| `docs/perf/README.md` (17 Aug set) | **HISTORICAL ONLY**, once the banner is committed. |
| `claude/Thesis_Ch4-5_DRAFT.md` | Working draft against the 25 Aug freeze. Stale throughout. |
| `Thesis_Ch1-5.docx` | **The chapter text. Stale or false in fourteen identified places — §4.** |

---

## 2. Authoritative Chapter 4 evidence baseline

Everything in this section is a figure Chapter Four may quote. Anything not here
is not evidence.

### 2.1 Backend

| Quantity | Value | Source |
|---|---|---|
| Tests collected | **422** | re-verified 30 Aug (§3.1) |
| Passed | **418** | freeze §3.1 |
| Skipped | **4** — PostgreSQL-only migration tests | freeze §3.1 |
| Failed | **0** | freeze §3.1 |
| Statement coverage | **96%** | freeze §3.1, re-verified 30 Aug |
| Statements / missed | **1,594 / 66** | freeze §3.1 |
| Coverage kind | **statement, not branch.** `--cov-branch` is not enabled anywhere in the repository | freeze §3.1 |
| The 4 skips, executed for real | **12/12 passed against PostgreSQL 15.18** | freeze §3.3 |

Per-file collected counts (freeze §3.2): `test_api.py` 134,
`test_authorization.py` 74, `test_enterprise_service.py` 40,
`test_input_validation.py` 32, `test_workflows.py` 21,
`test_equipment_correction.py` 20, `test_logging_safety.py` 20,
`test_rate_limit.py` 19, `test_reproducibility.py` 18,
`test_share_lifecycle.py` 16, `test_migrations.py` 12,
`test_bioprocess_service.py` 11, `test_concurrency.py` 5.

**Quote collected counts, never `grep -c "^def test_"`.** Six modules
parameterise; a function count reads 355 and understates the suite by 67.

Modules below 100%: `ml/train.py` 47%, `models/database.py` 64%, `ml/dataset.py`
82%, `api/endpoints/dss.py` 90%, `ml/predict.py` 91%, `core/security.py` 93%,
`main.py` 94%, `services/reports_service.py` 94%, `services/auth_service.py`
98%, `services/ledger_service.py` 98%. Everything else is at 100%, including
`dss_service.py`, `enterprise_service.py`, `bioprocess_service.py`,
`share_service.py`, `equipment_service.py`, `core/roles.py`,
`core/rate_limit.py`, `core/logging_safety.py`, `schemas.py` and `models.py`.

### 2.2 Frontend

| Quantity | Value | Source |
|---|---|---|
| Test files | **13** | re-verified 30 Aug (§3.2) |
| Tests | **148** | re-verified 30 Aug |
| Result | **148 passed on an uncontended machine** | freeze §3.4; contention independently reproduced 30 Aug (§3.2) |
| Statement coverage | **43.18%** (558 / 1,292) | freeze §3.4 |
| Branch / function / line | 32.41% (318/981) · 36.16% (149/412) · 43.00% (492/1,144) | freeze §3.4 |
| Coverage denominator | **the whole of `src`**, including page and form components with no tests at all | freeze §3.4 |

Untested by design at this stage: `FarmRecordsPage.tsx`,
`FarmRecordCreateForm.tsx`, `DSSPredictPage.tsx`, `InvestorsPage.tsx`,
`PublicInvestorReport.tsx`, `ReportsPage.tsx`, `Login.tsx`,
`DryingCurveChart.tsx`, the hooks. Tested logic modules are high:
`dryingParams.ts` 94.33%, `EnterpriseEconomics.tsx` 94.28%, and
`BreakEvenPricePanel.tsx`, `CostStructurePanel.tsx`, `YieldBaselinePanel.tsx`
and `EmptyState.tsx` at 100%.

**The backend and frontend coverage figures must be quoted together or not at
all.** Quoting 96% alone misrepresents the system.

### 2.3 ML / forecasting

| Quantity | Value |
|---|---|
| Model type | `Pipeline(OneHotEncoder + RandomForestRegressor)`, `n_estimators=200`, `random_state=42` |
| Dataset origin | **Synthetic.** `backend/app/ml/dataset.generate`, 6,000 samples, `seed=42` |
| Real farmer records used in training | **None. Zero.** |
| Split | `test_size=0.2`, `split_random_state=42` |
| R² | **0.9762** (measured 0.976204) |
| MAE | **0.2414 t/ha** (measured 0.241393) |
| RMSE | **0.4883 t/ha** (measured 0.488334) |
| Dataset fingerprint | `sha256 a461b884afc9fafda953ff90cc2f75eb0d8608f2e58ad9d206fc215d7b6ba5bf` |
| Reproducibility | Re-derived by regenerating the dataset and refitting, not read from the sidecar. Agreement to **six decimal places**. `test_reproducibility.py` — 18 passed |
| Cross-environment | Agreement recorded across Python 3.14.5 and 3.11.15 with differing pandas patch versions; the binding packages are scikit-learn and numpy |

**Mandatory disclosure.** R² 0.9762 is an **in-distribution** figure measuring
how well a Random Forest recovers a relationship a parameterised generator was
written to produce. It is evidence that the machine-learning pipeline is
correctly implemented end to end. It is **not** evidence about Nigerian yields,
and the model **does not learn from any farm's records**.

**RMSE now exists.** The `[PLACEHOLDER]` in Chapter Four §4.9 must be filled with
**0.4883 t/ha**, and Chapter Three §3.6.5's "may additionally be reported"
becomes "is additionally reported".

### 2.4 Performance

**Source: `docs/perf/2026-08-29/README.md`. The 17 August set is superseded.**

| Condition | FCP | LCP | SI | TBT | TTI | CLS | score |
|---|---|---|---|---|---|---|---|
| Cold, slow-3G (median of 5) | **5661.2** | 5661.2 | 5661.2 | 10.5 | 5727.6 | 0 | 65 |
| Cold, slow-4G (median of 5) | **1709.9** | 1859.9 | 1709.9 | 9.0 | 1943.8 | 0 | 99 |
| Warm, slow-3G (median of 3 flows) | **70.6** | 1612.0 | — | 0 | — | 0 | 100 |

| | |
|---|---|
| Tool | Lighthouse **13.4.1**, headless Chrome |
| Commit | **`78a68c2`** — the baseline |
| Target | `http://localhost:4173/` — `vite preview` on the production build, so the service worker is active |
| Form factor | Mobile, 412 × 823 @ DPR 1.75 |
| Throttling | **Simulated (Lantern)**, constant 4× CPU. Slow-3G 400 ms / 400 Kbps; slow-4G 150 ms / 1638.4 Kbps |
| Runs | **5 cold CLI runs per condition, plus 3 flow iterations** each containing a cold and a warm navigation. **Medians reported**, individual runs tabulated |
| Cold transfer | **139,245 B over 8 requests**, every run |
| Warm transfer | **127 B over 7 requests** |
| Entry chunk | 400.07 KB raw / **130.03 KB gzipped**; charting code 262.12 KB / 82.07 KB gzip, loaded separately |
| Host benchmark index | 1406–1996 |
| Internal control | The flow harness's own cold navigation reproduces the CLI cold median to within ~3 ms |

**Two rules that must travel with these numbers.**

1. **Score and TBT are not comparable with the 17 August set**, because the host
   benchmark index differed (425–1654 then, 1406–1996 now). Only the
   network-bound metrics and the byte counts compare. This specifically rules
   out reading the cold slow-3G TBT movement (121.0 → 10.5 ms) as a code effect.
2. This is **simulated throttling against localhost on one developer machine** —
   a model of a degraded network, not a measurement of a real one.

Comparable movement against 17 August (`c16924e`): cold transfer
243,724 B → **139,245 B** (−43%); cold slow-3G FCP 7674.4 → **5661.2 ms**
(−26%); cold slow-4G FCP 2317.7 → **1709.9 ms** (−26%); warm FCP
116.4 → **70.6 ms**; warm LCP 1613.8 → **1612.0 ms** (unchanged, because it was
never network-bound). Route-level code-splitting removed 104,479 bytes from the
first load.

The 127 warm bytes are `pwa-192x192.png`, the manifest icon, absent from the
Workbox precache. That is the §4.10.4 defect, now confirmed **by measurement**
rather than by reading the precache listing.

### 2.5 Hosting economics

| | |
|---|---|
| Estimated total | **$15.40 / month ≈ ₦20,950 / month** |
| Composition | Instance $12.00 (₦16,327) + snapshot backups $2.40 (₦3,265) + domain $1.00 (₦1,361) + TLS $0.00 |
| Reference instance | 2 GB RAM / 50 GB SSD commodity tier (DigitalOcean Basic or Amazon Lightsail 2 GB) |
| Conversion basis | **CBN ₦1,360.58 = US$1, as at 12 August 2026.** Parallel market ₦1,425 on 13 Aug 2026, so naira figures are indicative rather than exact |
| Measured footprint | Backend 145.5–161.5 MiB, PostgreSQL 33.4–41.3 MiB, **subtotal 178.9–202.8 MiB**, across two container instances differing by ~11% |
| Not measured | The static PWA server (not running during sampling) and the OS / container runtime. **The total is part-measured and part-assumed, and must be described as such** |
| Sampling caveat | Seven single-shot samples across a 14.2 s startup window at a mean 2.37 s interval; the widest 4.11 s gap falls across the steepest part of the climb, so **145.5 MiB is a lower bound on the startup peak**, not the peak |
| Cost per farm | ₦419 at 50 farms · ₦210 at 100 · ₦105 at 200 · ₦42 at 500 — **reasoned, not load-tested** |
| Startup cost | 8.57 s from restart to accepting traffic, driven by the train-on-boot step. An availability cost, not a memory cost |

**Status: estimated, not incurred.** No provider was contacted, no quotation
obtained; prices are list prices captured on a single date, exclusive of tax and
of committed-use discount. **The `[CONFIRM — re-check provider pricing pages]`
placeholder in §4.11 is still open** and must be resolved or the retrieval date
restated before submission.

### 2.6 Enterprise economics — implemented calculations and endpoints

All present, all at 100% statement coverage in `enterprise_service.py`:

| Calculation | Endpoint |
|---|---|
| Cost structure and classification coverage | `GET /api/v1/dss/cost-structure` |
| Dual break-even price (cash / total) | `GET /api/v1/dss/break-even-price` |
| Yield sensitivity matrix | `GET /api/v1/dss/sensitivity` |
| Partial budget | `POST /api/v1/dss/partial-budget` |
| Olympic-average yield baseline | `GET /api/v1/dss/yield-baseline` |
| Per-crop margin, unit cost (both bases), retrospective break-even yield | `GET /api/v1/dss/decision-support` |

**All six are now reachable in the interface.** See §4 rows C-11 to C-13, which
retract two "implemented but unreachable" findings the chapter currently carries.

### 2.7 Security, deployment and operations — verified live at the baseline

Freeze §3.7–§3.13. **Chapter Four has no section reporting any of this**, and it
is the largest body of unreported verified evidence in the project. See §7 and
§10.

| Area | Result |
|---|---|
| Production stack | 3 services healthy; 7 of 7 live checks pass; both application containers non-root (backend uid 1000, frontend uid 101); the database publishes no host port |
| Share-token lifecycle | 90-day expiry verified to the second; unauthenticated report 200; token presented as a bearer credential → **401**; after revoke → **404**; unknown token → **404**, identical, so no existence oracle |
| Log scrubbing | Raw token absent from all three logs. nginx redacts; application middleware and uvicorn write a stable 12-hex non-reversible fingerprint that still correlates requests |
| Login throttling | 10 failures → 401; the 11th → **429** carrying `Retry-After: 896`; budget exactly 10 failures per 900 s; the refusal names no account, so it confirms no email |
| RBAC | Live matrix over 3 roles / 12 permissions; the 403 body names only the missing permission; `POST /dss/train` as **owner** → **403** |
| Input bounds | −1,000,000 / 2,000,000,000 / `Infinity` / `NaN` each → **422**; a valid amount → 201 |
| Equipment correction | `PATCH` → 200 with `updated_at` stamped; **a no-op PATCH leaves `updated_at` unchanged**, so a non-correction is not recorded; out-of-range rate → 422 |
| Ledger immutability | `DELETE /ledger/logs/1` → **405** |
| Backup / restore | Executed with the project's own scripts: 28,164-byte dump, 8 tables with data, every row count matched on restore, `alembic_version` = `b9e5f30c74a1`, **0 unpaired operational logs**, live database untouched, scratch database dropped |
| Migration chain | 9 revisions, single head `b9e5f30c74a1`, both directions on every revision; 12/12 against PostgreSQL 15.18 including the schema-versus-models drift check and a rollback-and-reapply |
| Configuration | Prod compose renders from `.env.example` alone; `--profile edge` renders; no `SECRET_KEY` literal committed; no tracked `.env` |

### 2.8 Live database census (freeze §4)

farms **14** · users **13** · operational_logs **109** ·
financial_transactions **109** · equipment **3** · maintenance_logs **1** ·
share_tokens **10** · `alembic_version` **`b9e5f30c74a1`** ·
**unpaired operational logs 0**.

The 109 / 109 correspondence is the paired-write invariant visible in the data,
and it is the single most quotable structural result in the thesis.

---

## 3. Commands and results — this verification, 30 August 2026

Run at `78a68c2` with the working tree as described in §1. These are
re-verifications of the freeze, not a new measurement set.

### 3.1 Backend collection

```
$ python -m pytest backend/tests/ --collect-only -q
422 tests collected in 0.92s
```

**Confirms the 422 figure exactly.**

### 3.2 Frontend suite — and an independent reproduction of the timing defect

```
$ cd frontend && npm run test
 Test Files  1 failed | 12 passed (13)
      Tests  1 failed | 147 passed (148)
   Duration  82.71s
```

The failure was `src/features/dashboard/dashboardAccess.test.tsx`. Run alone:

```
$ npx vitest run dashboardAccess
 Test Files  1 passed (1)
      Tests  5 passed (5)
   Duration  3.33s
```

**Finding.** The freeze recorded this as a one-off observed under concurrent
execution with the backend suite. It has now recurred on a second day, on a
machine running no concurrent backend suite. **It is reproducible enough to be
reported as a property of the suite rather than as an anomaly.** The file passes
in 3.33 s alone and times out against Vitest's 5,000 ms default in the full run.
This is a **test-harness** limitation, not an application defect — but the
honest form of the claim is "148 tests, of which one is not timing-robust in a
full-suite run", not "148 passed".

**Total count and file count confirmed: 13 files, 148 tests.**

### 3.3 Backend coverage

```
python -m pytest backend/tests/ -q --cov=backend/app --cov-report=term
```

Re-run on 30 August. **418 passed, 4 skipped, 0 failed, 96%, 1,594 statements, 66 missed, 284.49 s** — exact agreement with the freeze on every figure. Full output in §12.1.

### 3.4 Code-level verifications performed (read-only)

| Question | Command / file | Answer |
|---|---|---|
| Does a USSD/SMS webhook exist? | `grep -rniE "ussd\|sms\|whatsapp\|webhook\|twilio\|africastalking" backend/app frontend/src` | **No.** Two comment lines in `frontend/src/app/navigation.tsx` recording that the nav section was *removed*. No route, no parser, no sender mapping, no test. |
| Is marketable unit cost rendered? | `DecisionSupport.tsx:48,84-87`; `types/domain.ts:141-142` | **Yes**, since `2a282ba`. |
| Is the yield baseline reachable? | `EnterpriseEconomics.tsx:9,49,152` | **Yes** — `YieldBaselinePanel` is mounted. |
| Is the crop list still hard-coded? | `useCropOptions.ts`, `cropOptions.ts`, `FarmRecordCreateForm.tsx:79` | **No** — merged at runtime from two API sources. |
| Does the drying form take readings? | `DryingFields.tsx:79-137`, `dryingParams.ts:24-26,72-84` | **Yes** — repeatable optional readings, plus `DryingCurveChart.tsx`. |
| Is `/bioprocess/summary` consumed? | `grep -rn "getSummary" frontend/src` | **No.** `bioprocessService.getSummary` exists in `apiClient.ts:171` and is called by nothing. |
| Is there equipment-correction UI? | `EquipmentPage.tsx:43` | **Yes** — a partial PATCH sending only changed fields. |
| Is there member-management UI? | `grep -rn "members" frontend/src` | **No.** `POST/PATCH /auth/members` are API-only. |
| Is offline read-caching enabled? | `frontend/vite.config.ts:50-68` | **Yes** — `StaleWhileRevalidate` over `ledger`, `reports` and five named `dss` reads; 64 entries, 7 days; `/dss/model` and `/dss/predict` deliberately excluded. |
| Are equipment id and hours captured on a log? | `models.py`, `dss_service.py`, `enterprise_service.py` | **Captured and validated, consumed by no service.** |

---

## 4. Contradiction and stale-figure register

Every conflict found between the chapter text, the planning material and the
baseline. **No figure below was chosen silently.**

### 4.1 Test and coverage figures

| ID | Metric | Old figure / source | New figure / source | Baseline decision | Reason |
|---|---|---|---|---|---|
| C-01 | Backend tests | 190 passed / 0 skipped — Ch4 §4.3.1, §4.13, §4.15; `LIMITATIONS.md` (committed) | **422 collected, 418 passed, 4 skipped, 0 failed** — freeze §3.1, re-verified 30 Aug | **422 / 418 / 4 / 0** | The 190 figure is measured at `59a6286`. Nine test modules were added by the merge. The four pre-existing modules still collect exactly 190, so nothing was weakened — the increase is entirely additive. |
| C-02 | Backend coverage | 93%, 1,286 statements, 91 missed — Ch4 §4.3.1 | **96%, 1,594 statements, 66 missed** — freeze §3.1 | **96% / 1,594 / 66** | Same cause. Both are statement coverage. |
| C-03 | Frontend tests | 89 tests in 9 files — Ch4 §4.3.1 | **148 tests in 13 files** — freeze §3.4, re-verified 30 Aug | **148 / 13** | Four frontend test files added by the merge. |
| C-04 | Frontend coverage | 33.48% statements (378 / 1,129) — Ch4 §4.3.2 | **43.18% (558 / 1,292)** — freeze §3.4 | **43.18% (558 / 1,292)** | Same measurement method, same `src`-wide denominator; more tested code. |
| C-05 | Reconciliation table (Ch4 Table 4.7) | 185 → 190 backend, 82 → 89 frontend, cause `test_concurrency.py` and `dbUpgrade.test.ts` | The reconciliation that now matters is **190 → 422** and **89 → 148** | **Rewrite Table 4.7 entirely** | The table reconciles two superseded states against each other. Keeping it would document a comparison no reader needs while omitting the one they do. |
| C-06 | Backend module coverage list | `dss.py` 93%, `security.py` 93%, three modules under 80% — Ch4 §4.3.2 | `dss.py` **90%**, `security.py` **93%**, **one** module under 80% (`ml/train.py` 47%) — freeze §3.1 | **Freeze §3.1 list** | `ml/dataset.py` rose 36% → 82%; `models/database.py` unchanged at 64%. |
| C-07 | Test counting method | Ch4 quotes numbers of tests without stating the method | Freeze §3.2 establishes **collected**, and shows six modules parameterise | **Always quote pytest collected counts**, and say so | `grep -c "^def test_"` yields 355 and undercounts six files. |

### 4.2 Correctness claims

| ID | Metric | Old figure / source | New figure / source | Baseline decision | Reason |
|---|---|---|---|---|---|
| C-08 | Per-crop reversal netting | **"The per-crop decision-support breakdown does not net reversals … a phantom 'Unspecified' cost appears"** — Ch4 §4.6.4; freeze-25 §6.1.1; `LIMITATIONS.md` (committed) | **It does net reversals, and did so at the freeze commit too** — freeze-29 §2, adjudicated by execution at both `59a6286` and `78a68c2` | **NETTED. Delete Ch4 §4.6.4 as a defect section.** | Reversing ₦25,000 moved that crop's expenses 35,000 → 10,000 and its unit cost ₦2,916.67 → ₦833.33, with no `Unspecified` bucket at any point. The investor report returned the same netted figures unauthenticated. Five named tests pin it; the capability was introduced by `6992d1c` nine days before the freeze. `docs/EVIDENCE_FREEZE_2026-08-25.md` §3 already listed reversal netting as implemented — the document contradicted itself and §3 was the correct half. **Chapter Four should explain the false positive as a methodological finding rather than pretend the passage never existed.** |
| C-09 | ML artefact reproducibility | **"the artefact is not reproducible from the repository … regenerating it would produce different figures, because the training data is synthesised afresh"** — Ch4 §4.9 | **Fully reproducible.** `seed=42`, fixed split seed, `sha256 a461b884…` dataset fingerprint, six-decimal agreement on re-derivation, 18 reproducibility tests, cross-environment record | **Reproducible. Rewrite §4.9's second qualification.** | The claim was true before `model_baseline.json` and the seeding work landed. It is now false, and it understates the project's own rigour. |
| C-10 | RMSE | `[PLACEHOLDER]` — Ch4 §4.9 | **0.4883 t/ha** (measured 0.488334) | **0.4883 t/ha** | Measured and recorded; tolerance ±0.0005. |

### 4.3 Performance and cost

| ID | Metric | Old figure / source | New figure / source | Baseline decision | Reason |
|---|---|---|---|---|---|
| C-11 | Performance set | 17 Aug 2026 at `c16924e`, pre-code-splitting; cold slow-3G LCP 7.68 s, transfer 243,724 B, warm FCP 116.4 ms — Ch4 §4.10; `performancebenchmarking.md`; `docs/perf/README.md` | **29 Aug 2026 at `78a68c2`**: cold slow-3G FCP/LCP **5661.2 ms**, transfer **139,245 B / 8 req**, warm FCP **70.6 ms**, warm LCP **1612.0 ms**, warm transfer **127 B** — `docs/perf/2026-08-29/README.md` | **The 29 August set.** | The 17 Aug set measures a build the thesis does not submit. Ch4 §4.10.3 already flags this as a confound and says the direction is "likely favourable"; it is now **measured**, so the hedge should be replaced with the figure. |
| C-12 | Score / TBT comparison | Ch4 §4.10 compares scores across measurement dates | Host benchmark index differed: 425–1654 (17 Aug) vs 1406–1996 (29 Aug) | **Do not compare score or TBT across dates.** Compare only network-bound metrics and byte counts | Lighthouse's composite score and TBT are CPU-sensitive; FCP/LCP/SI under Lantern `simulate` are largely insulated. |
| C-13 | Bundle size in the cost analysis | "The application bundle is 243,534 bytes" — `hostingcostanalysis.md` §4 | **139,245 B transferred over 8 requests** (entry chunk 400.07 KB raw / 130.03 KB gzip) | **139,245 B** | Pre-code-splitting figure. The bandwidth **conclusion** is unaffected — egress remains immaterial — so only the number changes, not the argument. |
| C-14 | Precache size | "21 entries totalling 859.67 KiB" — Ch4 §4.10.3 | Not re-measured on 29 Aug; the 29 Aug set measures *transfer*, not precache | **Do not quote the precache figure as a baseline figure.** Either re-measure or attribute it to `59a6286` | It was measured at the freeze tag, not at `78a68c2`. |

### 4.4 Reachability claims in the chapter's functional inventory

These are the highest-risk rows in Chapter Four: each asserts a *negative* about
the built system, and three of them are now false.

| ID | Claim | Source | Verified at baseline | Baseline decision |
|---|---|---|---|---|
| C-15 | "Olympic-average yield baseline — **implemented, not reachable**. No interface component fetches it" | Ch4 Table 4.2 row 11 | **FALSE.** `EnterpriseEconomics.tsx:49` calls `dssService.getYieldBaseline()` and renders `YieldBaselinePanel` at line 152 | **Reachable. Delete row 11 or restate as reachable.** |
| C-16 | "Cowpea and tomato … **not reachable in the interface**. The entry form carries a hard-coded crop list" | Ch4 Table 4.2 row 12 | **FALSE.** `useCropOptions.ts` merges the recorded-crop and predictor-crop sources at runtime; `FarmRecordCreateForm.tsx:79` consumes it | **Reachable. Delete row 12 or restate.** |
| C-17 | "Both unit-cost bases … **absent from the UI**. Computed, returned by the API, rendered nowhere" | `screenshot-runsheet.md` shot 4 and its closing table; `CH4_LOCATION_MAP.md` | **FALSE.** `DecisionSupport.tsx:84-87` renders "Unit cost ₦…/kg marketable" beside the harvested figure, since `2a282ba` | **Rendered. The runsheet's shot 4 is obsolete — the state is now screenshottable.** |
| C-18 | "The drying form has **no readings input**, so the Page model is unreachable from the interface" | `screenshot-runsheet.md` shots 7 and 8 | **FALSE.** `DryingFields.tsx:79-137` provides repeatable optional readings rows; `dryingParams.ts` validates them client-side; `DryingCurveChart.tsx` plots them | **Reachable. The Page-model fit is screenshottable.** |
| C-19 | "Per-operation equipment attribution and machine hours — **captured, not consumed**" | Ch4 Table 4.2 row 13 | **TRUE.** `equipment_id` and `hours_used` are validated and persisted; no service reads them; no cost-per-hour, utilisation or machine-rate figure exists | **Keep. This row is correct and is a genuine finding.** |
| C-20 | "`/bioprocess/summary` — **no screen calls it**" | `screenshot-runsheet.md` closing table | **TRUE.** `bioprocessService.getSummary` (`apiClient.ts:171`) has zero callers | **Keep.** |

### 4.5 Demonstration-data figures

| ID | Metric | Old figure / source | New figure / source | Baseline decision | Reason |
|---|---|---|---|---|---|
| C-21 | Demo farm crop set | "the three seeded crops" (cassava, maize, tomato); farm-wide totals ₦223,600 / ₦210,800 / ₦12,800 | **Five crops** — cassava 6, cowpea 11, maize 2, sorghum 4, tomato 5 = **28 logs** — `seed_bioprocess_demo.py` | **Five crops. Do not quote any farm-wide total from `dss_per_crop.json`.** | `6f926a5` added cowpea and sorghum plus two equipment records, before the freeze tag. Farm-wide totals moved; per-crop rows did not. |
| C-22 | Maize row | ₦45,000 revenue / ₦3,500 expenses / GM ₦41,500 / 100 kg / 84 kg marketable / ₦35.00 harvested / ₦41.666666666666664 marketable / break-even 7.777… kg | Unchanged | **VALID — quote freely** | `6f926a5` was verified bit-identical on the maize row and its diff touches nothing there. These figures are load-bearing across Chapters 4 and 5. |
| C-23 | Maize break-even price (total) | ₦41.666666666666664 | **₦42.36767852721509** for `break_even_price_TOTAL`; `break_even_price_CASH` unchanged at ₦41.666666666666664 | **Both, distinguished** | The farm now owns a depreciating asset and maize takes ₦58.88 of the farm-wide overlay. Neither figure is in the JSON captures. |
| C-24 | Break-even nomenclature | `dss_break_even.json` `_source`: "no separate break-even route exists" | Break-even **yield** is a field inside `/dss/decision-support`; break-even **price** has its own route `GET /api/v1/dss/break-even-price` | **Keep the two distinct throughout Chapter Four** | Break-even yield is retrospective, in kg, deterministic tier. Break-even price is dual cash/total, in ₦/kg, enterprise tier. |
| C-25 | Endpoint module naming | "(auth, ledger, reports, dss, bioprocess, equipment, **share**)" — `THESIS_REPORTING_STATE.md` §6 | There is no `share.py`. The module is **`backend/app/api/endpoints/investor.py`**; `share_service.py` is the service behind it | **`investor.py`** | Verified against `backend/app/api/router.py`. |

### 4.6 Baseline identity

| ID | Metric | Old figure / source | New figure / source | Baseline decision | Reason |
|---|---|---|---|---|---|
| C-26 | The reporting baseline | "tag `thesis-evidence-freeze-2026-08-25`, implementation commit `59a6286` … **Development stopped at that tag**" — Ch4 §4.1 | **`78a68c292205acdcac1a52f977fbea31b6e8495e` on `main`**, 29 Aug 2026 | **`78a68c2`** | Development did not stop; the hardening branch merged four days later. Every §4.1 figure and both reproduction commands must be re-stated against `78a68c2`. |
| C-27 | CI status | Chapter and drafts risk "CI is green" | **No CI run result was retrievable for `78a68c2`**, and none is recorded in the repository | **Never write "CI is green."** Cite the jobs' substance as executed locally (freeze §3.3, §3.6, §3.7, §3.13) | `gh` is not installed on the verification machine, and no run artefact exists in-repo. The workflow is *defined*; its result is not *observed*. |

---

## 5. Chapter Three — implementation alignment audit

Verified against the code at `78a68c2`.

### 5.1 Functional requirements (§3.3.1)

| Chapter 3 claim | Code verification | Status | Required correction |
|---|---|---|---|
| "record farm operations and their associated costs as **paired entries**" | `ledger_service`, one commit per pair; live census 109 logs / 109 transactions, **0 unpaired** | **IMPLEMENTED** | None. This is the strongest claim in the chapter. |
| "compute profit-and-loss and gross-margin metrics" | `GET /reports/pnl`, `/pnl/monthly`, `/pnl.csv`; `GET /dss/decision-support` | **IMPLEMENTED** | None. |
| "track equipment, maintenance, and depreciation" | `equipment.py` (5 routes incl. `PATCH`), `MaintenanceLog`, depreciation overlay in `enterprise_service` | **IMPLEMENTED** | Add that depreciation is a **derived report-time overlay, never posted to the ledger** — a design decision Chapter Four reports as a result and Chapter Three does not mention. |
| "deterministic decision-support metrics (unit cost of production and per-crop gross margin) from real records" | `dss_service.py`, 100% covered | **IMPLEMENTED** | **Understated.** The tier also produces unit cost on **two** bases, retrospective break-even yield, ranking, and — through the enterprise layer — cost structure, dual break-even price, sensitivity, partial budget and yield baseline. §3.6.5(a) names two of nine. |
| "provide an optional yield forecast" | `POST /dss/predict`, RandomForest, confidence band from tree spread | **IMPLEMENTED** | None. |
| "authenticate users and confine each user's data to their own farm" | `auth_service`, bcrypt, JWT; every query farm-scoped; cross-farm read → 404 | **IMPLEMENTED** | None, but see §5.5 — the chapter omits RBAC entirely. |
| "allow a farmer to grant a bank or investor a **read-only** view of standardised reports" | `investor.py`: mint / list / revoke / public report; token hashed at rest; 90-day expiry | **IMPLEMENTED** | Add expiry. Chapter Three describes the token as revocable but not as expiring. |

### 5.2 Non-functional requirements (§3.3.2)

| Chapter 3 claim | Code verification | Status | Required correction |
|---|---|---|---|
| (a) "Low-bandwidth, mobile-first operation" | Code-split PWA; 139,245 B cold / 127 B warm; slow-4G score 99 | **IMPLEMENTED**, measured | None. |
| (b) "Offline data capture … synchronised, without loss or duplication" | Dexie queue, `client_id` idempotency, `[ownerKey+status]` index, 3-attempt retry, logout purge | **PARTIALLY IMPLEMENTED** | Two boundaries must be stated: offline **writes** cover the record-creation path only, not every write surface; and the whole offline behaviour is verified against `fake-indexeddb` and stand-ins under Vitest, **never in a driven browser**. |
| (c) "Security and data isolation" | Farm scoping on every path; bcrypt; RBAC; throttling | **IMPLEMENTED** | None. |
| (d) "Accessibility for low-specification devices and **feature phones**: data entry must be possible through channels that do not presuppose a smartphone" | **No such channel exists in the codebase.** See §5.4 | **NOT IMPLEMENTED** | This NFR is not met. It must be restated as a design requirement that the current release does not satisfy. |
| (e) "Computational feasibility … modest server hosting" | 178.9–202.8 MiB measured across two containers; fits a 2 GB commodity instance | **IMPLEMENTED**, measured | Note that two footprint components were not measured. |

### 5.3 Architecture and data model (§3.4, §3.5)

| Chapter 3 claim | Code verification | Status | Required correction |
|---|---|---|---|
| "client–server architecture … mobile-first PWA client and a backend API service" | React/Vite PWA + FastAPI; three-container compose | **IMPLEMENTED** | None. |
| "schema … managed through versioned migrations" | Alembic, 9 revisions, single head `b9e5f30c74a1`, both directions everywhere, executed against PostgreSQL 15.18 | **IMPLEMENTED** | None — and this is now backed by a 12-test suite Chapter Three could cite. |
| "An Operational Log … automatically and atomically paired with a corresponding Financial Transaction … enforced at the write layer" | `ledger_service`; `financial_transaction_id` FK; census 109/109 | **IMPLEMENTED** | None. |
| "The financial ledger is **single-entry**" | `transaction_type` + `category`, no double-entry pairing | **IMPLEMENTED** | None — correctly and honestly stated. |
| **Table 3.1 — principal entities**: Operational Log, Financial Transaction, Equipment, Maintenance Log, Farm/User | Code also has **`ShareToken`** as a first-class table, a **`crop`** column on `OperationalLog`, **`extra_data` JSON** carrying drying parameters, **`reverses_id`** for contra entries, **`client_id`** for idempotency, and **`role`** on `User` | **IMPLEMENTED DIFFERENTLY FROM CHAPTER 3** | Table 3.1 is incomplete. Add `ShareToken` at minimum; the sharing mechanism of §3.6.7 has no entity in the data model as written. Mention `crop`, `reverses_id` and `client_id` in prose — Chapter Four's per-crop analysis, reversal analysis and idempotency results all depend on columns Chapter Three never introduces. |
| **Ledger immutability and reversal** | `DELETE` → 405; contra entry linked by `reverses_id`; double reversal refused; `ReverseConfirmDialog` in the UI | **NOT DESCRIBED IN CHAPTER 3** | §3.6.2 describes the ledger engine but never states that records are soft-immutable and corrected by contra entry. This is a central design decision and a Chapter Four result. **Add it to §3.6.2.** |

### 5.4 Module design (§3.6)

| Chapter 3 claim | Code verification | Status | Required correction |
|---|---|---|---|
| §3.6.1 "records entered without connectivity are queued in a local browser database and synchronised … Synchronisation is idempotent: each queued record carries a client-generated identifier" | `db.ts`, `sync.ts`, `queueOwner.ts`; `client_id` idempotency farm-scoped; verified sequentially and under a genuine two-thread race | **IMPLEMENTED** | None for the write path. |
| §3.6.1 "retrieval of previously stored data assumes connectivity **unless runtime caching of read endpoints is enabled, which is identified as a planned enhancement**" | `vite.config.ts:50-68`: `StaleWhileRevalidate` over `ledger`, `reports` and five named `dss` reads; 64 entries / 7 days; purged on write and on auth change; `/dss/model` and `/dss/predict` deliberately excluded | **IMPLEMENTED DIFFERENTLY FROM CHAPTER 3** | **The chapter understates the system.** Offline *reads* are implemented in the production service worker. Rewrite as built, and state the exclusions and the purge-on-write design — the exclusion of `/dss/model` and `/dss/predict` for tenant reasons is a design result worth a sentence. |
| §3.6.2 Financial ledger engine as "the translation layer that creates the paired Financial Transaction" | `ledger_service.py`, 98% covered | **IMPLEMENTED** | Add immutability/reversal (§5.3 above). |
| §3.6.3 Reporting: "overall, per-category, and monthly … standardised, **exportable** reports" | `/pnl`, `/pnl/monthly`, `/pnl.csv` | **IMPLEMENTED** | Say **CSV**. There is no PDF export, and "exportable reports" invites the assumption of one. |
| §3.6.4 "records mechanisation usage and fuel as operational entries tagged with the mechanisation activity category" | Implemented; cost subtype validated against a closed taxonomy | **IMPLEMENTED** | None. |
| §3.6.4 "A direct per-machine association between an individual operation and a specific equipment item is identified as a **future refinement**" | `equipment_id` and `hours_used` **are** accepted, validated, persisted and read back on an operational log — but **read by no service** | **IMPLEMENTED DIFFERENTLY FROM CHAPTER 3** | The association exists in the data model; what does not exist is any *use* of it. Restate as: the association is **captured but not costed** — no cost-per-hour, utilisation or machine-rate figure is produced anywhere. This is exactly Chapter Four Table 4.2 row 13, and the two chapters currently disagree. |
| §3.6.5 Two-tier DSS; Tier 1 deterministic on real records; Tier 2 Random Forest on synthetic data, not learning from farm usage | Both tiers present; `MODEL_TRAIN` granted to no role; training disabled by config | **IMPLEMENTED** | Tier 1 is understated (§5.1). Add that retraining is **unreachable over the API for every role** — a stronger and more defensible statement of the synthetic-data disclosure than the chapter currently makes. |
| §3.6.5 "R² and MAE; **RMSE … may additionally be reported**" | R² 0.9762, MAE 0.2414, **RMSE 0.4883**, all reproducible to six decimals | **IMPLEMENTED** | Change "may additionally be reported" to "is additionally reported". |
| §3.6.6 "Authentication issues a signed token upon login, with passwords stored only in hashed form. Every read and write … scoped to the authenticated user's farm" | JWT; bcrypt `$2b$`; farm scoping on every path | **IMPLEMENTED** | **Materially understated.** The chapter describes authentication with no authorisation model. The system has 3 roles over 12 permissions, endpoints ask for a permission rather than a role, permission is checked **before** scope so a refusal is never an existence oracle, and owner-only member management exists. **Chapter Three must describe RBAC, or Chapter Four will report a capability the methodology never designed.** |
| §3.6.7 "revocable, opaque token … read-only … cannot be used to write data or to reach any other farm" | All true, verified live; **plus** stored only as a hash, 90-day expiry, cannot be exchanged for a session (401), unknown/revoked/expired all resolve to one identical 404, and the raw token is scrubbed from all three logs | **IMPLEMENTED** | Understated. Add expiry, hashing at rest, and the single-404 design. |
| §3.6.8 "An inbound webhook accepts a message consisting of a sender identifier and a short structured text, parses it into an activity and amount, and creates a paired Operational Log and Financial Transaction through the same ledger service … The channel is designed to be gateway-agnostic, **so that it can be exercised through simulated inbound-message payloads independently of any carrier**" | **Nothing exists.** No route, no webhook, no parser, no sender→farm mapping, no test, no schema. The only trace in the codebase is a comment in `frontend/src/app/navigation.tsx` recording that the USSD/SMS and WhatsApp nav entries were **removed** because "neither had a backend of any kind" | **NOT IMPLEMENTED** | **This is the single most serious overclaim in Chapter Three.** The present-tense description reads as built, and the sentence about simulated payloads asserts a demonstrability that does not exist. Rewrite the whole subsection as *designed but not implemented*, in the future/conditional, and state plainly that no part of the channel — not even a simulated harness — was built. Then reconcile NFR (d), Objective 1's inclusive-entry claim, and any Chapter Five statement that rests on it. |
| **Post-harvest drying / bioprocess** — Page and Newton fitting, wet↔dry basis conversion, water balance, safe-storage lookup, per-crop aggregation, drying-aware unit costs | `bioprocess_service.py` (100% covered), `bioprocess.py` endpoints, `DryingFields`/`DryingRunResult`/`DryingCurveChart` | **NOT DESCRIBED IN CHAPTER 3** | Chapter Four devotes §4.8 to it and calls it "the engineering contribution". **Chapter Three has no module for it at all.** Add §3.6.x describing the design, including the drying → marketable-mass → unit-cost coupling. Without it, Chapter Four reports a subsystem the methodology never specified. |
| **Enterprise economics** — cost-behaviour classification, depreciation overlay, proportional fixed-cost allocation, dual break-even price, sensitivity matrix, partial budget, yield baseline, operating-expense ratio | `enterprise_service.py` (100% covered), five endpoints, `EnterpriseEconomics.tsx` and four panels | **NOT DESCRIBED IN CHAPTER 3** | Chapter Four devotes §4.7 to it. **Add it to §3.6.5 or as its own subsection.** |
| **Rate limiting** | `core/rate_limit.py`, two budgets (per account, per address), registration and public report separately capped, 19 tests, live 429 | **NOT DESCRIBED IN CHAPTER 3** | Add one sentence to §3.7. |
| **Production deployment and operations** | `docker-compose.prod.yml`, nginx image, Caddy edge profile, `ops/backup.sh` / `ops/restore.sh`, readiness probe | **NOT DESCRIBED IN CHAPTER 3** | Optional, but if Chapter Four reports the deployment verification (§7 recommends it), Chapter Three should name the deployment design. |

### 5.5 Security design (§3.7)

| Chapter 3 claim | Code verification | Status | Required correction |
|---|---|---|---|
| "authenticated access with hashed credentials; strict per-farm data isolation on every data path; scoped, revocable, read-only tokens that cannot escalate to write access or cross farm boundaries" | All three verified live at the baseline | **IMPLEMENTED** | Add: role-based authorisation; login throttling; input bounds at the schema edge; share-token expiry and hashing at rest; credential scrubbing across three loggers; retraining granted to no role. **Six verified security capabilities are absent from the security design section.** |

### 5.6 Evaluation methodology (§3.8)

| Chapter 3 claim | Code / evidence verification | Status | Required correction |
|---|---|---|---|
| §3.8.1 Functional verification by automated suite plus manual walkthroughs; DSS arithmetic asserted against hand-computed values; offline idempotency asserted | 422 backend + 148 frontend collected cases; hand-computed DSS assertions present; idempotency tested sequentially and under a two-thread race | **EXECUTED** | None. |
| §3.8.2 Lighthouse against the production build, mobile emulation, throttling, several runs, median reported | 5 cold runs per condition + 3 flows, medians, at `78a68c2` | **EXECUTED** | None. State that throttling is **simulated (Lantern)** against **localhost**, not a real network — the chapter says "network throttling applied to approximate a slow mobile connection", which is true but should name the method. |
| §3.8.3 Desk-based hosting-cost analysis on published pricing, labelled an estimate | `hostingcostanalysis.md`, footprint measured | **EXECUTED** | None. Resolve the `[CONFIRM]` placeholder. |
| §3.8.4 "Usability is evaluated through an expert heuristic evaluation combined with a standardised usability questionnaire … Three to five evaluators … each evaluator additionally completes the ten-item SUS" | **The instruments exist; no session was run.** No scored SUS forms, no filled heuristic checklists, no session notes, no participant records | **NOT IMPLEMENTED (not executed)** | **Chapter Three presents this among "the evaluation actually undertaken".** It was not undertaken. Either move it to §3.8.5 as designed future work, or keep it in place with an explicit statement that the instruments were prepared and the study was not run. Objective 4 is **partly met** and both chapters must say so consistently. |
| §3.8.5 Designed field evaluation, explicitly future work | Not executed, correctly labelled | **Correctly stated** | None. |

### 5.7 Overclaim summary — Chapter Three

1. **§3.6.8 USSD/SMS channel — not implemented in any form.** Highest severity.
2. **§3.3.2(d) feature-phone NFR — not met.** Follows from 1.
3. **§3.8.4 usability evaluation — presented as undertaken, not undertaken.**
4. **§3.6.4 machine-equipment association — described as future work; actually captured but not costed.** (Understates, then contradicts Chapter Four.)
5. **§3.6.1 offline reads — described as a planned enhancement; actually built.** (Understates.)
6. **§3.6.5 Tier 1 — described as two metrics; actually nine.** (Understates.)
7. **§3.6.6 / §3.7 — no authorisation model described; RBAC, throttling, input bounds, token expiry, log scrubbing all exist.** (Understates.)
8. **§3.6 — no module for post-harvest drying or enterprise economics**, both of which carry their own Chapter Four sections.
9. **Table 3.1 — omits `ShareToken`**, the entity behind §3.6.7.
10. **§3.6.2 — omits ledger immutability and the contra-entry correction model.**

Items 1–3 are overclaims and must be corrected. Items 4–10 are underclaims or
omissions: they cost the thesis credit and, worse, leave Chapter Four reporting
results for capabilities the methodology never specified.

---

## 6. Chapter Four evidence map

Against the existing chapter structure. **"Verified?" means: verified at
`78a68c2`.**

| Ch4 section / claim | Evidence source | Verified? | Screenshot? | Table? | Notes |
|---|---|---|---|---|---|
| **4.1** Reporting baseline is `59a6286`, "development stopped at that tag" | — | **NO — FALSE** | — | — | Rewrite to `78a68c2`. Both reproduction commands must be restated. C-26. |
| **4.2.1** Three-container composition; layered backend; six authenticated routes + one public | `docker-compose.yml`, `router.tsx`, `App.tsx:45` | YES | No | No | Public route is `/investor/:token`. |
| **4.2.1** Census 14/13/109/109/3/1/10, 0 unpaired | Freeze §4, re-queried 29 Aug | YES | No | **Yes — T1** | Quotable; re-established by query, not inherited. |
| **4.2.2** Table 4.2 rows 1–10 (capabilities implemented and reachable) | Code + freeze §3 | YES | See §7 | Yes | Keep. |
| **4.2.2** Row 11 yield baseline "not reachable" | `EnterpriseEconomics.tsx:49,152` | **NO — FALSE** | — | — | C-15. Delete or restate. |
| **4.2.2** Row 12 crops "not reachable" | `useCropOptions.ts` | **NO — FALSE** | — | — | C-16. Delete or restate. |
| **4.2.2** Row 13 equipment attribution "captured, not consumed" | Code | YES | No | Yes | C-19. Keep — a genuine finding. |
| **4.3.1** 190 / 93% / 89 in 9 files | — | **NO — SUPERSEDED** | No | **Yes — T2** | 422/418/4/0, 96%, 1,594/66, 148 in 13. C-01–C-04. |
| **4.3.2** Coverage distribution; frontend 33.48% | Freeze §3.1, §3.4 | **NO — SUPERSEDED** | No | **Yes — T3** | 43.18% (558/1,292). C-04, C-06. |
| **4.3.3** Capability-to-proof mapping | `backend/tests/`, `frontend/src/**/*.test.*` | Partly | No | **Yes — T4** | Must be re-derived over the nine new backend modules and four new frontend files. |
| **4.3.4** Table 4.7 reconciliation 185→190 / 82→89 | — | **NO — OBSOLETE** | No | **Yes — T5** | Rewrite as 190→422 and 89→148, with the additive-only argument. C-05. |
| **4.4** Negative-control testing (3 experiments) | `docs/EVIDENCE.md`, the neutered-purge runs | YES (at `59a6286`) | No | Yes | The controls concern frontend cache logic the merge did not change. **Re-run or attribute to `59a6286` explicitly.** |
| **4.5.1** Components verified visually only | Code + coverage report | YES | No | Yes | The list shrinks slightly: several panels now carry tests. Re-derive from the 29 Aug coverage output. |
| **4.5.2** Live system verification — every endpoint 200 | Freeze §3.7–§3.11 | YES, and **far more strongly than the chapter claims** | No | Yes | The chapter reports "every endpoint returned 200". The baseline has a full live security matrix. Expand. |
| **4.5.3** Service-worker attribution by driven browser | `performancebenchmarking.md` §1 (17 Aug, `c16924e`) | Partly — **at the old commit** | **Yes — S12** | No | Offline navigation returned 200 with the SW flag set. Either re-run at `78a68c2` or attribute by date and commit. |
| **4.6.1** Per-crop gross margin and ranking | `GET /dss/decision-support` | YES | **Yes — S05** | **Yes — T6** | **Five crops, not three.** No `rank` field exists; the artefact is ordering plus profit/alert colouring. C-21. |
| **4.6.2** Unit cost on two bases; maize ₦35.00 / ₦41.67 | `dss_service.py`; live response | YES | **Yes — S05** | **Yes — T7** | **Now visible in the UI.** C-17, C-22. |
| **4.6.3** Retrospective break-even yield; maize 7.8 kg; four null cases | Live response; four named tests | YES | **Yes — S05** | Yes | C-22, C-24. |
| **4.6.4** "A stated defect: per-crop DSS does not net reversals" | — | **NO — FALSE** | — | — | **C-08. Delete as a defect. Replace with the false-positive methodology finding.** |
| **4.7.1** Cost structure; 11.75% unclassified at farm level; maize 100% | `GET /dss/cost-structure` | YES (at capture) | **Yes — S07** | **Yes — T8** | Re-capture: the farm now holds five crops and two equipment records. |
| **4.7.2** Depreciation overlay; never posted to the ledger; unrated count; zero-base undefined | `enterprise_service.py`; ADR | YES | **Yes — S07** | Yes | Design result, well evidenced. |
| **4.7.3** Dual break-even price and sensitivity | `GET /dss/break-even-price`, `/sensitivity` | YES | **Yes — S07** | **Yes — T9** | Cowpea is the legible crop, not maize. C-23. |
| **4.7.4** Partial budget, two implementations agreeing on eight hand-computed cases | `enterprise_service.py` + offline client implementation | YES | **Yes — S08** | Yes | Strong result; keep. |
| **4.7.5** Yield baseline (Olympic average) | `GET /dss/yield-baseline` | YES | **Yes — S07** | Yes | **Now reachable.** C-15. |
| **4.8.1** Verification by designed fixture — Page and Newton parameters recovered exactly | `test_bioprocess_service.py` (11) | YES | No | **Yes — T10** | |
| **4.8.2** Seeded maize run: 100 kg @ 25% → 84 kg @ 13%; dry matter 75.0 kg; predicted 86.21 kg vs observed 84 kg | Live `GET /bioprocess/{id}` | YES | **Yes — S09** | **Yes — T11** | Load-bearing. Do not alter. |
| **4.8.3** Drying input validation — every malformed run 422, never 500; 8 API + 20 client tests | `test_api.py`, `dryingParams.test.ts` | YES | **Yes — S10** | Yes | |
| **4.8.4** Coupling to the ledger; drying cost posts through the same paired write | `dss_service.py` marketable-mass coupling | YES | **Yes — S05 + S09** | No | The ₦35.00 → ₦41.67 chain. |
| **4.9** R² 0.9762, MAE 0.2414, RMSE `[PLACEHOLDER]` | `model_baseline.json`; freeze §3.5 | YES | **Yes — S11** | **Yes — T12** | **Fill RMSE 0.4883.** C-10. |
| **4.9** "The artefact is not reproducible from the repository" | — | **NO — FALSE** | — | — | **C-09. Rewrite.** Six-decimal reproduction, dataset fingerprint, 18 tests. |
| **4.9** Synthetic-data disclosure and three UI display states | `dataset.py`; DSS page | YES | **Yes — S11** | No | The disclosure text must be visible in the screenshot. |
| **4.10.1–2** Lighthouse method and principal finding | `docs/perf/2026-08-29/` | **Method YES, figures SUPERSEDED** | No | **Yes — T13** | Replace the whole figure set. C-11. |
| **4.10.3** "Characterises an earlier build … direction likely favourable" | — | **SUPERSEDED** | — | — | It has now been measured. Replace the hedge with the number, and keep the host-speed caveat. C-11, C-12. |
| **4.10.4** Precache defect — the manifest icon | `docs/perf/2026-08-29/README.md` | **YES — now confirmed by measurement** | No | No | 127 B over 7 requests on the warm navigation. Upgrade from "found by reading the precache listing" to "confirmed by measurement". |
| **4.11.1** Measured footprint 178.9–202.8 MiB | `hostingcostanalysis.md` §2 | YES | No | **Yes — T14** | Two components unmeasured; the 145.5 MiB peak is a lower bound. |
| **4.11.2** Correction: the ML tier is not the cost driver | `hostingcostanalysis.md` §3 | YES | No | No | Good methodological result; keep. |
| **4.11.3** $15.40 ≈ ₦20,950/month | `hostingcostanalysis.md` §6 | YES (estimate) | No | **Yes — T15** | Resolve `[CONFIRM]`. |
| **4.11.4** Cost per farm at scale | §7 | **Reasoned, not measured** | No | Yes | Must be labelled as reasoned. |
| **4.12** Usability | — | **NO VERIFIED EVIDENCE — DO NOT CLAIM AS RESULT** | No | No | The instruments exist; no completed instrument of any kind exists. Report the absence. |
| **4.13** Objectives table | §4.3–4.11 | Partly | No | **Yes — T16** | Objective 4 row cites 190/93%/89 — restate. Objective 4 is **partly met**. |
| **4.14** Limitations of the results | §9 of this report | YES | No | **Yes — T17** | Replace with the register in §9. |
| **NEW — security and authorisation results** | Freeze §3.8–§3.11 | YES | **Yes — S13, S14** | **Yes — T18** | **The largest gap.** Nothing in Chapter Four reports RBAC, throttling, token lifecycle, log scrubbing or input bounds. See §10. |
| **NEW — deployment and recovery results** | Freeze §3.7, §3.12, §3.13 | YES | No | **Yes — T19** | 7/7 live checks; backup/restore rehearsal with every row count matched. |
| **NEW — migration chain against PostgreSQL** | Freeze §3.3 | YES | No | Yes | 12/12, drift check, rollback-and-reapply. Answers the freeze's own §6.2 finding. |

### 6.1 Claims with no verified evidence

Each of these must be stated as **NO VERIFIED EVIDENCE — DO NOT CLAIM AS
RESULT**:

- Any usability figure, SUS score, heuristic-severity count or evaluator finding.
- Any field-trial, farmer-feedback or real-farm-data result.
- Any load, stress, soak or concurrency-at-scale result.
- Any PostgreSQL concurrency result (measured on SQLite; PostgreSQL inferred).
- Any independent security review, penetration test or threat-model result.
- Any statement that CI passed for `78a68c2`.
- Any production-deployment, real-domain-TLS or real-user result.
- Any claim that the service-worker stale-revalidation window is or is not a real
  defect (reasoned from handler ordering; never reproduced).
- Any browser-verified offline behaviour beyond the single driven-browser
  attribution probe at `c16924e`.
- Any machine-hour, utilisation or cost-per-hour figure.
- Any field-predictive accuracy claim for the yield model.

---

## 7. Screenshot and figure capture plan

### 7.1 Preparation — do this once, before any capture

```
docker compose up -d db backend frontend
python backend/scripts/seed_bioprocess_demo.py
```

The seed is idempotent (fixed `client_id` per log), so re-running is safe. It
creates or reuses **farm "Demo Farm"**, user **`demo-bioprocess-v2@test.example`**
/ **`demo-bioprocess-pw`**, with **28 operational logs across five crops**
(cassava 6, cowpea 11, maize 2, sorghum 4, tomato 5) and **two equipment
records, one rated and one unrated**, so the depreciation overlay is visibly
partial.

**Capture origin: `http://localhost:5173` (dev)** for everything except S12.
The dev server runs **no service worker**, so a stale cached response cannot be
photographed by mistake. `http://localhost:4173` is the production PWA build and
is needed only for the offline pair.

**Window 1440 × 900** for all shots except S15 (360 × 800).

**If the browser holds a token for another farm, sign out first.** The live
database holds 14 farms and two share the name "Demo Farm" — **never use a
farm-list view to establish which farm is which.**

**Do not touch the maize rows.** The 100 kg, 84 kg, ₦3,500, ₦45,000, ₦35.00 and
₦41.67 figures are quoted across Chapters 4 and 5. Any drying run added for
demonstration must use a **different crop** (rice) and be reversed afterwards.

### 7.2 The plan

Priority: **E** essential · **R** recommended · **O** optional.

| ID | System area | Navigation / action | Required visible state | Thesis purpose | Proposed caption | Priority |
|---|---|---|---|---|---|---|
| **S01** | Authenticated dashboard | Sign in as the demo user; land on `/` | KPI row populated — net profit, gross revenue, operating cost, profit margin; the P&L chart and cost breakdown rendered; the six-item sidebar; the account label in the header | Demonstrates that authentication gates a populated, integrated overview. **One figure covers authentication and the dashboard together** — do not spend a second figure on a login form. | *Figure 4.x: The authenticated dashboard for the demonstration farm, showing the integrated financial overview computed from 28 paired operational and financial records.* | **E** |
| **S02** | Login screen | `/` signed out | The login form only | Only if Chapter Four discusses the authentication *interface* as a result. It does not currently. | *Figure 4.x: The authentication screen.* | **O — skip unless §4.5.1 needs it** |
| **S03** | Farm records — list | `/records` | 28 rows visible with activity type, description, crop, amount, date; the paired financial amount on each row | Demonstrates structured operational record keeping at volume, and the paired write visible per row | *Figure 4.x: The operational logbook, each entry carrying the financial transaction posted with it in the same commit.* | **E** |
| **S04** | Operational record creation | `/records` → **Log activity** → fill a real entry (Activity = Fertiliser application, Crop = Maize, description, amount, date) — **capture the filled form before saving** | Every field populated with realistic values; the crop dropdown open or showing a selected crop from the runtime-merged list | Demonstrates the entry path and the input→record chain. **Capture the form filled, not empty.** | *Figure 4.x: Recording a farm operation. The entry posts the operational log and its paired financial transaction in a single transaction.* | **E** |
| **S05** | Decision support — Tier 1 | `/` → scroll to the **Decision support** card | **All five crops** in gross-margin order; cassava and maize positive, tomato and sorghum negative; the alert accent on the loss-makers; **both unit-cost bases on maize (₦35.00/kg harvested and ₦41.67/kg marketable)**; maize break-even "was 7.8 kg at the price you got"; tomato's null break-even shown as withheld, not as zero | **The single most important figure in the thesis.** It shows input context (a real ledger) and output (ranked margins, dual unit cost, break-even) in one frame, and it demonstrates the withholding-a-figure design principle. | *Figure 4.x: Deterministic decision support computed from the live ledger — per-crop gross margin and ranking, unit cost of production on both a harvested and a marketable basis, and retrospective break-even yield. Figures are withheld rather than defaulted where the inputs do not support them.* | **E** |
| **S06** | Profit and loss | `/reports` | Populated P&L — income, expenses by category, net result; the monthly breakdown; the CSV export control visible | Directly demonstrates the core objective: records converted into a profitability statement | *Figure 4.x: The profit-and-loss statement aggregated from the paired ledger, with the monthly breakdown and CSV export.* | **E** |
| **S07** | Enterprise economics | `/dss` → scroll to the **Enterprise economics** section; select **cowpea** | Cost structure with classification coverage; the depreciation overlay showing the **unrated equipment count**; **both break-even prices** (cash and total) on cowpea; the sensitivity matrix; the yield-baseline panel | Demonstrates the enterprise tier as a whole, and the partial-overlay honesty (an unrated asset is counted, not charged as zero). Cowpea, not maize, is the crop on which the dual price and sensitivity are legible. | *Figure 4.x: Enterprise-economics analysis for cowpea — cost structure with classification coverage, the derived depreciation overlay, dual break-even price on a cash and a total-cost basis, and the yield-sensitivity matrix.* | **E** |
| **S08** | Partial budget | `/dss` → **Partial budget** form → enter a change and submit | Inputs and the computed result in one frame — added costs, added returns, reduced costs, reduced returns, net change | Demonstrates the second, independent implementation of the partial budget (client and server agree on eight hand-computed cases) | *Figure 4.x: Partial-budget analysis of a proposed change, computed identically by the offline client and the server.* | **R** |
| **S09** | Drying / bioprocess — result | `/records` → **Log activity** → Activity = **Post-harvest drying**, **Crop = Rice**, Amount = 0, mass in 60 → out 50, moisture 22% → 13%, time 8 h, **and add three intermediate readings**; save | The result panel: water removed, drying rate, process loss against the dry-matter prediction, dry matter, moisture ratio, **the Newton k and the Page fit** (unlocked by three readings), the **drying curve chart**, and the **green safe-storage chip** (rice threshold 14% wb) | **The distinctive subsystem, and the engineering contribution.** Shows input → computed output, including the Page fit that older planning material wrongly recorded as unreachable. | *Figure 4.x: A recorded drying run and its computed result — water balance, process loss against the dry-matter prediction, fitted Newton and Page parameters from the intermediate readings, the drying curve, and the safe-storage verdict for the crop.* | **E** |
| **S10** | Drying input validation | Same form; enter **outlet mass greater than inlet mass** (e.g. in 50, out 60) and attempt to save | The client-side refusal message, before any request is sent | Demonstrates that the client mirrors the backend validator, so an unsatisfiable record cannot be queued offline | *Figure 4.x: Client-side validation of a physically impossible drying run, mirroring the server's rule so an invalid record is never queued.* | **R** |
| **S11** | ML forecast | `/dss` → enter rainfall, fertiliser, soil pH, crop → **Run prediction**; then scroll to **Model quality** | **Both in one frame if possible**: the filled inputs with the resulting forecast and its confidence band; and R² **0.9762**, MAE **0.2414 t/ha**, with the amber **"What these figures measure … representative synthetic data … Trained on 6,000 generated samples"** disclosure **legible** | Demonstrates Tier 2. **The disclosure must be readable in the figure** — that is the point of including it. | *Figure 4.x: The optional yield forecast with its model-quality panel. The disclosure shown in the interface states that the model is trained on synthetic data and does not learn from any farm's records.* | **R** |
| **S12** | Offline — cached reads | **On `http://localhost:4173`** (production build, service worker active): load `/`, then DevTools → Network → **Offline**, then **reload** | The dashboard rendering **real figures** from the service-worker cache while offline, with the sidebar showing "Offline · showing saved data" | Demonstrates the low-bandwidth claim in its operative form. **Pair with the honest counter-case below.** | *Figure 4.x: The production build serving previously cached reads while offline.* | **R** |
| **S13** | Offline — the counter-case | Same offline state, **on `http://localhost:5173`** (no service worker): reload `/` | The dashboard falling back to the first-run onboarding screen — a fetch failure presented as an empty farm | **An honest finding, and it belongs beside S12.** Without the service worker there is no offline read, and the failure mode is misleading rather than explicit. | *Figure 4.x: The same reload without the service worker. The read fails and the interface presents an empty farm rather than an error — a finding reported in Section 4.14.* | **R** |
| **S14** | Offline — queued write | Desktop width, DevTools → Network → **Offline** → `/records` → Log activity → Other, "Offline queue demo", ₦500 → Save → capture the **sidebar footer** | **Both** "Offline · showing saved data" **and** "⏳ 1 pending sync" | Demonstrates offline write queuing. **The caption must not imply that all writes work offline** — only the record-creation path queues. | *Figure 4.x: An operation recorded while offline, queued locally for synchronisation. Offline write support covers the record-creation path.* | **R** |
| **S15** | Reversal — dialogue and result | `/records` → **Reverse** on the **rice drying row created in S09** (never a seeded row) → capture the confirmation dialogue → confirm → capture the original and contra rows together | Dialogue: "Correct this record?", "nothing is deleted", "A correcting entry cannot itself be corrected". After: the original struck through with a **Reversed** pill, the contra tinted and pilled **Correction of #\<id\>** | Demonstrates the immutability-plus-contra correction model, which Chapter Three should describe and Chapter Four reports | *Figure 4.x: Correcting a record. The original is preserved and marked reversed; a linked contra entry is posted beside it.* | **E** |
| **S16** | Investor sharing — owner view | `/investors` → mint a link | The links list with label, creation date and **expiry date**; a revoke control. **Redact the token** — crop or blur all but the first four characters | Demonstrates the stakeholder-sharing mechanism and its bounds | *Figure 4.x: Minting a revocable, expiring read-only investor link. The token is redacted in this figure.* | **R** |
| **S17** | Investor sharing — recipient view | `/investor/<token>` in a **private window with no session** | The public report rendering the farm's standardised P&L and yield summary, with **no navigation, no entry controls and no session** | Demonstrates that a stakeholder can read without an account and cannot write | *Figure 4.x: The investor report as a bank or investor sees it — read-only, reached by token, with no account and no write surface.* | **R** |
| **S18** | RBAC refusal | Sign in as a **worker** (create one via `POST /auth/members` as owner) → attempt `/reports` | The refusal naming only the missing permission: *"Your role (worker) does not permit finance:read."* — and the sidebar with the finance items **absent** | Demonstrates the authorisation boundary and that a refusal is not an existence oracle. **Only capture if Chapter Four gains the security section §10 recommends.** | *Figure 4.x: Role-based authorisation. A worker's navigation omits the finance screens, and a direct request names the missing permission and nothing else.* | **R (E if §4.x security is added)** |
| **S19** | Equipment and maintenance | `/equipment` | Both seeded assets — one rated, one unrated; a maintenance entry; the correction (PATCH) control visible | Demonstrates equipment tracking and the correction path that closed a recorded defect. **One figure, not several.** | *Figure 4.x: Equipment records, including an unrated asset that the depreciation overlay counts but does not charge, and the correction path added in the hardening cycle.* | **R** |
| **S20** | Mobile layout | DevTools device toolbar **360 × 800** on `/records` | The sidebar replaced by a hamburger; grids collapsed to one column; the table scrolling **inside** its own container while the page does not scroll sideways | Evidences the mobile-first non-functional requirement | *Figure 4.x: The interface at 360 px. Wide content scrolls within its own container; the page does not scroll horizontally.* | **R** |
| **S21** | Untrained-model state | `docker exec agrip-backend-1 mv /code/app/ml/models/model_meta.json /tmp/` → reload `/dss` → **restore immediately** | "The model has not been trained yet." plus "No accuracy figures exist until it has been fitted." | Demonstrates the third display state — the design decision not to render an untrained model as R² 0.0000 | *Figure 4.x: The model-quality panel with no trained model. The absence is stated rather than rendered as a zero score.* | **O** |

### 7.3 Clean-up, mandatory

1. **Reverse the rice drying run from S09** (this is S15, so the two are already
   paired). After reversal the rice bucket disappears from decision support
   entirely — reversed drying runs are excluded from marketable mass and both
   money sides net to zero.
2. **Delete the queued offline record from S14** before reconnecting: DevTools →
   Application → IndexedDB → delete the row. Otherwise it flushes on reconnect
   and lands as a real ₦500 expense under "Unspecified", adding a sixth
   decision-support row and moving every dashboard total. If it does flush,
   reverse it from `/records`.
3. **Deactivate or remove the S18 worker account** if it was created only for the
   figure.
4. **Restore `model_meta.json`** immediately after S21 and confirm the metrics
   return.
5. **Re-load `/` and confirm the KPI row matches the pre-capture state** before
   quoting any figure from it.

### 7.4 Quality rules for every capture

- Realistic but non-sensitive demonstration data only; no real farmer, no real
  bank, no real personal detail.
- The page must be **populated**. An empty form is captured only where the input
  process itself is the subject (S04, S10).
- Capture the state **after** the meaningful interaction, not the page merely
  existing.
- **Redact** share tokens, JWTs, passwords and any sensitive URL. Crop rather
  than paint over, where cropping does not change the meaning.
- Consistent zoom and window size across the set (1440 × 900, except S20).
- Crop only for clarity. **Never edit a figure in a way that changes what it
  evidences** — do not retouch a number, hide a warning, or remove an empty
  state.
- Every figure gets a caption stating what is demonstrated, not what is shown.
- Prefer **input/action → populated state → output** over "here is a page".

### 7.5 States that cannot be captured — state the absence, do not stage it

| State | Status |
|---|---|
| `GET /bioprocess/summary` in the interface | **No screen calls it.** The endpoint and a typed client method exist with zero consumers. Report as a finding; do not screenshot a JSON response and present it as an interface. |
| Machine-hour or utilisation analysis | **Does not exist anywhere in the platform.** |
| Member/role management interface | **API-only.** No screen exists. S18 shows the *effect* of a role, not its administration. |
| A USSD or SMS entry channel | **Does not exist.** No route, no parser, no simulated harness. |
| Offline chip via a stopped backend | **Not reachable.** `isOnline` derives from `navigator.onLine`, which stays true; the application cannot distinguish a stopped backend from being online. This is itself a finding — report it in prose beside S13/S14. |
| Any usability session | **Never held.** |
| A production deployment | **Does not exist.** |

---

## 8. Recommended Chapter Four tables

| ID | Table | Content | Source |
|---|---|---|---|
| **T1** | Live database census | 14 / 13 / 109 / 109 / 3 / 1 / 10, `alembic_version` `b9e5f30c74a1`, **0 unpaired** | Freeze §4 |
| **T2** | Suite identity | Collected 422, passed 418, skipped 4, failed 0; coverage 96%, 1,594 / 66; frontend 13 files / 148 tests / 43.18% | Freeze §3.1, §3.4 |
| **T3** | Coverage distribution | The ten backend modules below 100%, with statements and misses; the frontend tested-versus-untested split | Freeze §3.1, §3.4 |
| **T4** | Capability-to-proof mapping | Each capability → the named tests that pin it → collected count | `backend/tests/`, re-derived |
| **T5** | Figure reconciliation | 190 → 422 backend, 89 → 148 frontend, 93% → 96%, 33.48% → 43.18%; cause: nine backend and four frontend test modules; **the four pre-existing backend modules still collect exactly 190** | Freeze §3.1–§3.4 |
| **T6** | Per-crop decision support | Five crops: revenue, expenses, gross margin, rank order | Live `GET /dss/decision-support` |
| **T7** | Unit cost on two bases | Per crop: harvested basis, marketable basis, difference; maize ₦35.00 / ₦41.67 / 19%; cowpea's ₦63.40 gap; cassava's withheld marketable figure | Live response |
| **T8** | Cost structure and classification coverage | Per crop and farm-wide: variable, semi-variable, fixed, unclassified; 11.75% unclassified at farm level; maize 100% | `GET /dss/cost-structure` |
| **T9** | Dual break-even price and sensitivity | Cowpea: cash and total price; the sensitivity matrix at 75–125% of baseline yield | `GET /dss/break-even-price`, `/sensitivity` |
| **T10** | Drying-model fixture recovery | Designed Page and Newton parameters versus recovered values | `test_bioprocess_service.py` |
| **T11** | The seeded maize drying run | 100 kg @ 25% wb → 84 kg @ 13% wb; dry matter 75.0 kg; predicted 86.21 kg; observed 84 kg; process loss; the resulting ₦41.67/kg | Live `GET /bioprocess/{id}` |
| **T12** | Model evaluation | Estimator, n=6,000, seed 42, split 0.2/42; **R² 0.9762, MAE 0.2414 t/ha, RMSE 0.4883 t/ha**; dataset `sha256 a461b884…`; measured-versus-recorded agreement to six decimals | `model_baseline.json`, freeze §3.5 |
| **T13** | Performance | Cold slow-3G, cold slow-4G, warm; FCP / LCP / SI / TBT / TTI / CLS / score / benchmark index; medians of 5 and 3; cold 139,245 B / 8 req, warm 127 B / 7 req | `docs/perf/2026-08-29/README.md` |
| **T14** | Measured resource footprint | Backend 145.5–161.5 MiB, PostgreSQL 33.4–41.3 MiB, subtotal 178.9–202.8 MiB, two components unmeasured | `hostingcostanalysis.md` §2 |
| **T15** | Estimated monthly cost | Instance / backups / domain / TLS → $15.40 ≈ ₦20,950, at CBN ₦1,360.58 as at 12 Aug 2026 | `hostingcostanalysis.md` §6 |
| **T16** | Results against objectives | Four objectives × evidence × evidence class × verdict. **Objective 4: partly met** | §4.13, restated |
| **T17** | Verified limitations | The register in §9 | This report |
| **T18** | **NEW — security and authorisation verification** | The live RBAC matrix; the throttling result; the share-token lifecycle table; the log-scrubbing observation; the input-bounds results | Freeze §3.8–§3.11 |
| **T19** | **NEW — deployment and recovery verification** | The 7 production-stack checks; the backup/restore row-count comparison; the migration chain result | Freeze §3.3, §3.7, §3.12, §3.13 |

---

## 9. Verified limitations register

Class: **IL** implementation limitation · **EL** evaluation limitation ·
**FW** future work · **OOS** out-of-scope feature.

| # | Limitation | Class | Code / evidence | Thesis implication | Chapter |
|---|---|---|---|---|---|
| 1 | **No production deployment.** A production *path* exists and was built, started and probed; no instance serves real users | IL | Freeze §3.7, §3.13 | Hosting cost is estimated, not incurred. No real-network figure may be claimed | 4 (§4.11), 5 |
| 2 | **No TLS certificate for a real domain.** The Caddy edge is configured and renders; automatic issuance has never run against a real hostname | IL | Freeze §3.13 | Bounds the "secure deployment" claim | 5 |
| 3 | **No independent security assessment** — no external review, no penetration test, no threat model | EL | Freeze §5.3 | The security results are internal verification, not assurance | 4 (§4.x), 5 |
| 4 | **No field trial and no real farm data.** Every figure derives from seeded or synthetic records | EL | Freeze §6 | Bounds every result in Chapter Four | 4 (§4.14), 5 |
| 5 | **The forecast tier trains on synthetic data** and does not learn from any user's records | IL | `dataset.py`, §2.3 | R² 0.9762 is in-distribution and says nothing about Nigerian farms | 4 (§4.9), 5 |
| 6 | **No usability evaluation and no SUS score.** The instrument pack exists; the study was not run | EL | §5.6 | **Objective 4 is partly met.** Chapter Three §3.8.4 must be reconciled | 3, 4 (§4.12), 5 |
| 7 | **No load, stress or soak testing** | EL | Freeze §5.3 | The tenancy and cost-per-farm figures are reasoned, not measured | 4 (§4.11.4), 5 |
| 8 | **No end-to-end browser testing.** Offline and service-worker behaviour is verified against stand-ins (`fake-indexeddb`, a stand-in Cache Storage) and one driven-browser probe at an older commit | EL | `sync.test.ts`, `cacheInvalidation.test.tsx` | Bounds every offline claim | 4 (§4.5), 5 |
| 9 | **Backend tests run on SQLite** while production runs PostgreSQL. Only the migration chain is executed against PostgreSQL | EL | Freeze §3.3 | Dialect behaviour at scale is unverified | 4, 5 |
| 10 | **Concurrency is measured on SQLite** and inferred for PostgreSQL | EL | `test_concurrency.py` | The idempotency-under-race result is real but dialect-bounded | 4, 5 |
| 11 | **No production observability** — no metrics, tracing or alerting; container logs to stdout only | IL | `LIMITATIONS.md` §1 | A named prerequisite for deployment | 5 |
| 12 | **Single-host design.** Rate-limit counters are in-process: they do not span replicas and do not survive a restart — **both observed** | IL | Freeze §3.9 | The throttling result is correct and bounded. Naming the residual is stronger than claiming the control | 4 (§4.x), 5 |
| 13 | **No token revocation within a token's lifetime**, no refresh tokens, no password reset, no email verification, no MFA | IL | `LIMITATIONS.md` §2 | Bounds the identity claim | 5 |
| 14 | **The frontend suite is not timing-robust under load.** `dashboardAccess.test.tsx` exceeds Vitest's 5,000 ms default in a full run and passes in ~3 s alone. **Observed on two separate days** | EL | §3.2 of this report | Quote "148 tests, one of which is not timing-robust in a full-suite run". A harness limitation, not an application defect | 4 (§4.3), 5 |
| 15 | **A mistaken reversal cannot itself be rolled back** — only compensated by a new unlinked entry | IL | `LIMITATIONS.md` §3 | The audit trail is truthful but not self-explanatory to a lay reader | 4, 5 |
| 16 | **The service-worker stale-revalidation window is UNVERIFIED.** Reasoned from handler ordering in `vite.config.ts:33-49`; never reproduced, provoked or observed | IL | `vite.config.ts` | **Must be reported as a hypothesis, not a defect.** The Phase-6b tests model only the serve half and cannot speak to it | 4, 5 |
| 17 | **The manifest icon is absent from the Workbox precache** — 127 B still transfers on a warm load | IL | `docs/perf/2026-08-29/README.md` | A real, small, measured defect. Report it; it strengthens the chapter | 4 (§4.10.4) |
| 18 | **Per-operation equipment attribution is captured but not costed.** `equipment_id` and `hours_used` are validated and persisted, read by no service | IL | §3.4 of this report | **No machine-hour, utilisation or cost-per-hour figure exists.** `hours_used` is populated on three of eight seeded mechanisation logs, so any rate would be over an unknown fraction of use | 3 (§3.6.4), 4 (T4.2 row 13), 5 |
| 19 | **`GET /bioprocess/summary` has no consumer.** Endpoint and typed client method exist; zero callers | IL | `apiClient.ts:171` | Report as built-but-unreachable | 4 (§4.2.2) |
| 20 | **No USSD/SMS/feature-phone channel of any kind.** No route, no parser, no sender mapping, no simulated harness | OOS→FW | §3.4 of this report | **Chapter Three §3.6.8 and NFR (d) must be rewritten.** Objective 1's inclusive-entry claim rests partly on this and must be re-scoped | 3, 4, 5 |
| 21 | **Two components of the hosting footprint were not measured**, and the 145.5 MiB startup peak is a lower bound from a 4.11 s sampling gap | EL | `hostingcostanalysis.md` §2 | The total is part-measured, part-assumed, and must say so | 4 (§4.11.1) |
| 22 | **Performance is simulated (Lantern) throttling against localhost on one developer machine.** Score and TBT are not comparable across measurement dates | EL | `docs/perf/2026-08-29/README.md` | A model of a degraded network, not a measurement of one | 4 (§4.10), 5 |
| 23 | **The single-entry ledger is not double-entry** and has no cryptographic tamper-evidence | IL (deliberate) | `LIMITATIONS.md` §3 | Correctly stated in Chapter Three; keep it stated | 3, 5 |
| 24 | **No CI run result is recorded for the baseline commit.** The workflow is defined; its jobs' substance was executed locally | EL | Freeze §7 | **Never write "CI is green."** | 4 |
| 25 | **A defect read out of code without being reproduced is not a defect.** The 25 August audit's per-crop reversal finding was a false positive that survived into three documents and the chapter text | EL (method) | Freeze §2 | **This is a genuine methodological finding and belongs in Chapter Four or Five as one.** Do not quietly delete the passage | 4 (§4.6.4 replacement), 5 |

---

## 10. Recommended Chapter Four structure

The existing structure is sound. Three changes: re-source every figure, delete
one false section, and add the security/deployment strand that is currently
unreported.

| § | Section | Change |
|---|---|---|
| 4.1 | Introduction and reporting baseline | **Rewrite.** Baseline `78a68c2`, 29 Aug 2026. New reproduction commands. State that the evidence document is `docs/EVIDENCE_FREEZE_2026-08-29.md`. |
| 4.2 | The implemented system | **Amend.** Keep 4.2.1 and the census. In Table 4.2, delete or restate rows 11 and 12 (now reachable); keep row 13; **add rows for authorisation, throttling, share-token expiry, input bounds and equipment correction**, which the merge added and the table does not list. |
| 4.3 | Functional verification: automated test evidence | **Re-source entirely.** 422/418/4/0, 96%, 1,594/66; 148 in 13 files at 43.18%. Rewrite Table 4.7's reconciliation as 190→422 / 89→148 with the additive-only argument. Add the timing-robustness note. |
| 4.4 | Negative-control testing | **Keep, re-attributed.** Either re-run at `78a68c2` or say plainly that the controls were run at `59a6286` against frontend cache logic the merge did not change. |
| 4.5 | Manually inspected evidence | **Amend.** Re-derive the untested-component list from the 29 Aug coverage output. Insert the figures from §7. Re-attribute the driven-browser probe by date and commit. |
| 4.6 | Decision support from the live ledger | **Amend.** Five crops, not three. Both unit-cost bases are now *rendered*, so the "absent from the UI" finding goes. **Delete §4.6.4** and replace it with §4.6.4 *"A recorded defect that was not one"* — the false-positive methodology finding (limitation 25). |
| 4.7 | Enterprise economics | **Re-capture** against the five-crop farm. Yield baseline is now reachable. |
| 4.8 | Post-harvest drying | **Amend.** The Page fit is now reachable from the interface; the readings input exists. Otherwise sound. |
| 4.9 | Yield-forecast model evaluation on synthetic data | **Amend.** Fill RMSE **0.4883 t/ha**. **Delete the "not reproducible from the repository" qualification** and replace it with the reproducibility evidence — dataset fingerprint, six-decimal agreement, 18 tests, cross-environment record. Keep every word of the synthetic-data disclosure. |
| 4.10 | Performance | **Replace the figure set** with the 29 August measurements. Replace §4.10.3's "likely favourable" hedge with the measured −43% / −26%. Keep the host-speed caveat as a stated non-comparability. Upgrade §4.10.4 from a reading of the precache listing to a measured 127 B. |
| 4.11 | Hosting-cost analysis | **Keep.** Correct the bundle-size figure. **Resolve the `[CONFIRM]` placeholder** or restate the retrieval date. |
| **4.12** | **NEW — Security, authorisation and deployment verification** | **Add.** The live RBAC matrix; login throttling with `Retry-After`; the share-token lifecycle (expiry, revocation, the single 404, the 401 on bearer use); credential scrubbing across three loggers; input bounds; equipment correction with the no-op case; the 7 production-stack checks; the backup/restore rehearsal; the migration chain against PostgreSQL 15.18. **This is the largest body of verified, unreported evidence in the project, and it is the direct answer to Objective 3.** |
| 4.13 | Usability evaluation | **Keep as written.** The absence is reported honestly and the section is drafted to receive real data. |
| 4.14 | Results against the objectives | **Re-source.** Objective 4 row must carry 422/96%/148 and read **partly met**. Objective 3 gains the new §4.12. |
| 4.15 | Limitations of the results | **Replace** with §9 of this report. |
| 4.16 | Summary | **Re-source** every figure. |

---

## 11. Claims that must NOT appear in the thesis

Evidence does not support any of these at `78a68c2`.

**False — the evidence positively contradicts them:**

1. "Per-crop decision support does not net reversals" / "a phantom `Unspecified`
   cost appears after a reversal". **Reproduced false at two commits.**
2. "Development stopped at the 25 August freeze tag."
3. "190 backend tests" / "93% backend coverage" / "1,286 statements" /
   "89 frontend tests in 9 files" / "33.48% frontend coverage" — as *current*
   figures.
4. "The model artefact is not reproducible from the repository" / "regenerating
   it would produce different figures."
5. "The Olympic-average yield baseline is implemented but not reachable."
6. "Cowpea and tomato cannot be entered through the form."
7. "Both unit-cost bases are computed but rendered nowhere."
8. "The drying form has no readings input, so the Page model is unreachable."
9. "There is no rate limiting" / "monetary fields are unbounded" / "equipment
   cannot be corrected" / "share tokens never expire" / "the share token is
   logged in cleartext" / "`POST /dss/train` is callable by any authenticated
   user" — **all closed at the baseline.**
10. Any farm-wide total quoted from `docs/ch4-data/dss_per_crop.json` (a
    three-crop capture of a five-crop farm).

**Unsupported — no evidence exists either way:**

11. Any SUS score, usability finding, heuristic-severity rating, evaluator count
    or session result.
12. Any field-trial, farmer-feedback, adoption or real-farm-data result.
13. Any load, stress, soak or throughput figure; any concurrency result for
    PostgreSQL.
14. Any independent security-review or penetration-test finding.
15. **"CI is green"** or any statement about a CI run for `78a68c2`.
16. Any production-deployment, real-user, real-domain-TLS or uptime claim.
17. Any claim that the yield model predicts real Nigerian yields, or that it
    learns or improves from farm usage.
18. Any machine-hour, utilisation, cost-per-hour or machine-rate figure.
19. Any claim that offline behaviour was verified in a browser beyond the single
    driven-browser attribution probe at `c16924e`.
20. Any claim that "all writes work offline" — only the record-creation path
    queues.
21. Any statement that the service-worker stale-revalidation window **is** a
    defect. It is a hypothesis reasoned from handler ordering and has never been
    reproduced. (Equally: do not claim it is *not* a defect.)
22. Any performance score or TBT comparison across the 17 and 29 August
    measurement sets.
23. Any statement that the hosting footprint total is fully measured.
24. Any statement that the platform provides a USSD, SMS or WhatsApp entry
    channel, or that such a channel can be exercised through simulated payloads.
25. Any claim of a drying "verdict" or storage-safety capability beyond what the
    implementation actually computes.

---

## 12. Appendix — re-verification run, 30 August 2026

```
$ cd "C:/Users/DELL/Desktop/Agri P"
$ git rev-parse HEAD
78a68c292205acdcac1a52f977fbea31b6e8495e

$ git status --porcelain | grep -v '^??'
 M LIMITATIONS.md
 M docs/perf/README.md

$ git diff --stat HEAD -- backend frontend
(empty — no application code differs from the baseline commit)

$ python -m pytest backend/tests/ --collect-only -q
422 tests collected in 0.92s

$ cd frontend && npm run test
 Test Files  1 failed | 12 passed (13)
      Tests  1 failed | 147 passed (148)
   Duration  82.71s
   (failure: src/features/dashboard/dashboardAccess.test.tsx — 5000 ms timeout)

$ npx vitest run dashboardAccess
 Test Files  1 passed (1)
      Tests  5 passed (5)
   Duration  3.33s
```

Backend coverage re-run result: see §12.1.

### 12.1 Backend coverage, 30 August 2026

```
$ python -m pytest backend/tests/ -q --cov=backend/app --cov-report=term
(paths shown with forward slashes; pytest-cov prints them with \ on Windows)

backend/app/services/bioprocess_service.py         68      0    100%
backend/app/services/dss_service.py               162      0    100%
backend/app/services/enterprise_service.py         72      0    100%
backend/app/services/equipment_service.py          40      0    100%
backend/app/services/ledger_service.py             56      1     98%
backend/app/services/reports_service.py            68      4     94%
backend/app/services/share_service.py              36      0    100%
backend/app/services/auth_service.py               63      1     98%
backend/app/core/rate_limit.py                     48      0    100%
backend/app/core/roles.py                          29      0    100%
backend/app/core/security.py                       30      2     93%
backend/app/main.py                                78      5     94%
backend/app/ml/dataset.py                          50      9     82%
backend/app/ml/predict.py                          46      4     91%
backend/app/ml/train.py                            53     28     47%
backend/app/models/database.py                     11      4     64%
backend/app/models/models.py                       81      0    100%
backend/app/schemas/schemas.py                    194      0    100%
----------------------------------------------------------------
TOTAL                                            1594     66     96%
418 passed, 4 skipped, 1 warning in 284.49s (0:04:44)
```

**Exact agreement with `docs/EVIDENCE_FREEZE_2026-08-29.md` §3.1** on every
figure: 418 passed, 4 skipped, 0 failed, 96%, 1,594 statements, 66 missed, and
the same ten modules below 100%. The evidence baseline is confirmed independently
one day later.
