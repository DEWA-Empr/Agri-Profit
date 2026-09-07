# Thesis evidence freeze — 2026-08-29

**This is the current evidence state. It supersedes
`docs/EVIDENCE_FREEZE_2026-08-25.md` for every figure, every verification claim
and every defect list.**

The 25 August document remains in the repository unedited, as the dated
historical record of what was believed and measured at the freeze tag. It is not
wrong to cite it *as history*. It must not be cited for current figures, and one
of its findings is now demonstrably false (§2).

Everything below was **executed on 29 August 2026** against the commit named in
§1. Nothing here is copied from an earlier document. Where a figure could be
established by running a command, the command was run and is quoted.

---

## 0. Why this document exists

Chapters 4 and 5 were drawing on two incompatible evidence states: the
25 August freeze (`59a6286` / tag `thesis-evidence-freeze-2026-08-25`) and the
29 August production-hardening merge (`78a68c2`). Test counts, coverage, the
defect list and the limitations differ between them, and mixing the two produces
a thesis that contradicts itself.

**From this point, Chapters 4–5 are generated from this document alone.**

---

## 1. Repository identity

> **SUPERSEDED IN PART — 7 September 2026.** The reporting baseline for the test
> figures, for the thirteen screenshots in `Screenshots/` and for all frontend
> behaviour is now commit **`598eab0`**
> (`598eab0a02533e9692332d92382d42f16fc9e346`), recorded in
> `docs/EVIDENCE_FREEZE_2026-09-07.md`. The screenshots were captured against
> that state and do **not** reproduce from the commit named in this section.
> The **performance figures in this document remain measured at `78a68c2` and
> were not re-measured on 7 September** — they stand as recorded here and
> should still be cited to `78a68c2`. Everything this document records that the
> 7 September freeze does not name also still stands.

| | |
| --- | --- |
| Branch | `main` |
| Thesis baseline commit | `78a68c292205acdcac1a52f977fbea31b6e8495e` |
| Commit subject | `Merge pull request #1 from DEWA-Empr/harden/production-readiness` |
| Commit date | Sat 29 Aug 2026 06:12:55 +0900 |
| Remote | `main == origin/main` (0 ahead, 0 behind) |
| Working tree | **Clean for all tracked files** (10 untracked paths, §1.1) |
| Verification date | 29 Aug 2026, 08:45–09:00 +0900 (2026-08-28T23:45Z–23:58Z) |

```
git rev-parse HEAD                        # 78a68c292205acdcac1a52f977fbea31b6e8495e
git rev-list --left-right --count main...origin/main   # 0    0
git status --porcelain | grep -v '^??'    # empty
```

### 1.1 Untracked paths, excluded from the baseline

`.gemini/`, `GEMINI.md`, `AGENT_PROMPT_chapter4_gaps.md`,
`AGENT_PROMPT_thesis_conformance.md`, `MERGE_AUDIT.md`,
`docs/CH4_LOCATION_MAP.md`, `docs/THESIS_MASTER_INSTRUCTION.md`,
`docs/THESIS_REPORTING_STATE.md`, `docs/print/`,
`Updated B.Tech Final Project Guideline for 2025_2026_v1.pdf`.

Thesis prose (`*.docx`) is gitignored by repository policy and is not part of the
implementation baseline.

### 1.2 Verification environment

| | |
| --- | --- |
| OS | Windows 11 (10.0.22621.4317) |
| Python | 3.14.5 |
| Node / npm | v24.15.0 / 11.12.1 |
| Key packages | scikit-learn 1.9.0, numpy 2.4.6, pandas 3.0.3, FastAPI 0.137.0, SQLAlchemy 2.0.50, Alembic 1.18.5 |
| Docker | 29.7.2, Compose v5.4.0 |
| PostgreSQL (containers) | 15.18 |

---

## 2. B-01 adjudication — per-crop reversal netting

### `B-01 = NETTED`

**Per-crop decision-support figures DO net reversed expenses, and did so at the
25 August freeze state.** `EVIDENCE_FREEZE_2026-08-25.md` §6.1.1 item 1 and
`LIMITATIONS.md` §3 are **factually wrong at the commit they describe**.
`docs/HARDENING_CHANGELOG.md` §1, which called that entry "stale when written",
is correct.

### How it was settled

Not from documentation. A worktree was created at the freeze implementation
commit and the behaviour was executed:

```
git worktree add --detach <tmp> 59a6286
# seed maize expense 25,000 + maize expense 10,000 + maize yield 40,000/12 bags
# reverse the 25,000
# GET /api/v1/dss/decision-support
```

**Result at `59a6286` (the freeze implementation commit):**

| | Before reversal | After reversing ₦25,000 |
|---|---|---|
| maize expenses | 35,000.0 | **10,000.0** |
| maize revenue | 40,000.0 | 40,000.0 |
| maize `unit_cost_of_production` | 2,916.67 | **833.33** |
| buckets present | `['maize']` | `['maize']` |
| `Unspecified` bucket | absent | **absent** |

The reversed amount left the crop. No phantom `Unspecified` bucket appeared.
The unit cost was recomputed rather than left stale.

**The investor report inherits it.** Freeze §6.1.1 also indicts "the investor
report reusing it". Minting a share link at the same commit and fetching
`GET /api/v1/share/report/{token}` unauthenticated returned maize expenses
`10,000.0`, `Unspecified` absent.

**Identical at the baseline.** The same reproduction at `78a68c2` returns the
same figures.

### Supporting evidence

1. **Implementation.** `backend/app/services/dss_service.py` in
   `get_decision_support` attributes a contra to its original's crop:
   `crop = crop_by_id.get(log.reverses_id) or UNSPECIFIED`, with `reversed_ids`
   computed up front to drop reversed yield quantities from the unit-cost
   denominator.
2. **The test freeze §3 refers to.**
   `backend/tests/test_api.py::test_dss_reversed_crop_expense_no_unspecified_bucket`
   — its own comment reads "no phantom 'Unspecified' bucket". Four sibling tests
   pin the rest: `test_dss_reversed_yield_restores_quantity_and_unit_cost`,
   `test_dss_reversed_only_drying_run_no_division_error`,
   `test_dss_fully_reversed_crop_is_omitted`,
   `test_dss_break_even_reflects_reversal`. **All five pass at `59a6286`.**
3. **Provenance.** `6992d1c` (16 Aug 2026,
   `feat(bioprocess): DSS coupling — marketable-mass cost + reversal netting (phase 5)`)
   is an ancestor of `59a6286`. The capability predates the freeze by nine days.
4. **Freeze §3 already claimed it.** The freeze's own "Implemented and verified"
   table lists "reversal netting" under DSS ledger-derived outputs. §3 and §6.1.1
   of that document contradict each other; §3 is the correct half.

### Consequence for the thesis

Any statement in Chapter 4 or 5 that per-crop decision support fails to net
reversals — including a "stated defect" section built around it — is false and
must be removed, not softened. This includes the claim that a phantom
`Unspecified` cost appears after a reversal.

---

## 3. Verification record — commands and results

### 3.1 Backend test suite and coverage

```
python -m pytest backend/tests/ -q --cov=backend/app --cov-report=term
```

| | |
|---|---|
| Collected | **422** |
| Passed | **418** |
| Skipped | **4** (PostgreSQL-only migration tests — closed separately, §3.3) |
| Failed | 0 |
| Statement coverage | **96%** |
| Statements / missed | **1,594 / 66** |
| Duration | 279.89 s |

Coverage is **statement** coverage. `--cov-branch` is not used.

**Modules below 100%:** `ml/train.py` 47%, `models/database.py` 64%,
`ml/dataset.py` 82%, `api/endpoints/dss.py` 90%, `ml/predict.py` 91%,
`core/security.py` 93%, `main.py` 94%, `services/reports_service.py` 94%,
`services/auth_service.py` 98%, `services/ledger_service.py` 98%.

Everything else is at 100%, including `dss_service.py`, `enterprise_service.py`,
`bioprocess_service.py`, `share_service.py`, `equipment_service.py`,
`core/roles.py`, `core/rate_limit.py`, `core/logging_safety.py`, `schemas.py`
and `models.py`.

### 3.2 Per-file test counts — collected, not grepped

```
python -m pytest backend/tests/ --collect-only -q          # 422 tests collected
python -m pytest backend/tests/<file> --collect-only -q
```

| File | Collected | `def test_` | Parametrised |
|---|---|---|---|
| `test_api.py` | **134** | 120 | yes |
| `test_authorization.py` | **74** | 42 | yes |
| `test_enterprise_service.py` | **40** | 32 | yes |
| `test_input_validation.py` | **32** | 27 | yes |
| `test_workflows.py` | 21 | 21 | no |
| `test_equipment_correction.py` | **20** | 15 | yes |
| `test_logging_safety.py` | 20 | 20 | no |
| `test_rate_limit.py` | 19 | 19 | no |
| `test_reproducibility.py` | 18 | 18 | no |
| `test_share_lifecycle.py` | **16** | 13 | yes |
| `test_migrations.py` | 12 | 12 | no |
| `test_bioprocess_service.py` | 11 | 11 | no |
| `test_concurrency.py` | 5 | 5 | no |
| **Total** | **422** | 355 | |

> **The 40-versus-32 discrepancy is resolved.** `test_enterprise_service.py`
> defines **32** test functions which pytest expands to **40** collected cases
> via two `@pytest.mark.parametrize` decorators. Both numbers are correct;
> they measure different things. **Quote collected counts** — that is what the
> 422 total and every headline figure is counted in. Six files are affected;
> any per-file count taken with `grep -c "^def test_"` undercounts them.

### 3.3 Migration chain — executed against real PostgreSQL

The four tests that skip locally were **run for real**, closing the gap:

```
docker run -d --name agrip-verify-pg -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=agriprofit_migrations \
  -p 55432:5432 postgres:15
MIGRATION_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:55432/agriprofit_migrations \
DATABASE_URL=postgresql://postgres:postgres@localhost:55432/agriprofit_migrations \
  python -m pytest backend/tests/test_migrations.py -v
```

**Result: 12 passed, 0 skipped, 6.19 s, against PostgreSQL 15.18.**

All twelve, including the four that require a real server:

- `test_migrations_run_from_an_empty_database_to_head`
- `test_the_migrated_schema_matches_the_models` — the schema-vs-models drift check
- `test_the_newest_migration_can_be_rolled_back_and_reapplied`
- `test_the_application_can_read_and_write_the_migrated_schema`

The chain is 9 revisions, single head `b9e5f30c74a1`, every revision defining
both directions.

### 3.4 Frontend

```
cd frontend && npm run test
cd frontend && npm run test:coverage
```

| | |
|---|---|
| Test files | **13 passed** |
| Tests | **148 passed**, 0 failed |
| Statement coverage | **43.18%** (558 / 1,292) |
| Branch coverage | 32.41% (318 / 981) |
| Function coverage | 36.16% (149 / 412) |
| Line coverage | 43.00% (492 / 1,144) |

Frontend coverage is low because it is measured over the whole of `src`,
including page and form components with no tests at all
(`FarmRecordsPage.tsx`, `FarmRecordCreateForm.tsx`, `DSSPredictPage.tsx`,
`InvestorsPage.tsx`, `PublicInvestorReport.tsx`, `ReportsPage.tsx`,
`Login.tsx`, `DryingCurveChart.tsx`, the hooks). The tested logic modules are
high: `dryingParams.ts` 94.33%, `EnterpriseEconomics.tsx` 94.28%, and
`BreakEvenPricePanel.tsx`, `CostStructurePanel.tsx`, `YieldBaselinePanel.tsx`
and `EmptyState.tsx` at 100%.

> A prior run of the full frontend suite executed **concurrently with the
> backend suite** produced one failure:
> `dashboardAccess.test.tsx > "still shows the real figures when the summary is
> allowed"` timed out at the 5,000 ms default after 23,061 ms. Re-run alone the
> file passes in 2.93 s, and the full suite passes 148/148. This is machine
> contention against a default timeout, not a defect — but the suite is not
> timing-robust under load, which is worth one sentence in Chapter 5.

### 3.5 Forecast model — metrics measured, not read

The metrics were **re-derived** by regenerating the dataset and refitting, not
by reading `model_baseline.json`:

```python
df = dataset.generate()                      # seed=42, 6000 samples
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = train._build_estimator(200, 42); model.fit(X_train, y_train)
```

| Metric | Measured 29 Aug | Recorded in `model_baseline.json` | Tolerance |
|---|---|---|---|
| R² | **0.976204** | 0.9762 | ±0.0005 |
| MAE | **0.241393 t/ha** | 0.2414 | ±0.0005 |
| **RMSE** | **0.488334 t/ha** | **0.4883** | ±0.0005 |

Agreement is to **six decimal places**, not merely within tolerance.

```
python -m pytest backend/tests/test_reproducibility.py -q     # 18 passed
```

`model_baseline.json` additionally records agreement across two environments
differing in Python minor version (3.14.5 recording vs 3.11.15 deployment
image) and pandas patch version, with a byte-identical dataset fingerprint
(`sha256 a461b884…`). The binding packages are scikit-learn and numpy.

**RMSE exists and is reproducible. Any placeholder for it in Chapter 4 §4.9
should be filled with 0.4883 t/ha.**

### 3.6 Security and correctness suites

```
python -m pytest backend/tests/test_authorization.py backend/tests/test_logging_safety.py \
  backend/tests/test_rate_limit.py backend/tests/test_share_lifecycle.py \
  backend/tests/test_input_validation.py -q
```
**161 passed** (the CI `security` job's exact grouping), 127.32 s.

```
python -m pytest backend/tests/test_equipment_correction.py backend/tests/test_reproducibility.py -q
```
**38 passed**, 23.76 s.

### 3.7 Production stack — built, started and exercised

The real `docker-compose.prod.yml` was built and run
(`up -d --build`, project `agripverify`). All three services reported
**healthy**. Every assertion below is a live HTTP result, not a CI definition.

| # | Check | Result |
|---|---|---|
| 1 | `GET /` serves the app | `text/html` — PASS |
| 2 | `GET /health/ready` reaches the **backend**, not the SPA fallback | `{"status":"ready","checks":{"database":"ok"}}` — PASS |
| 3 | `GET /api/v1/ledger/logs` reaches the backend with the `/api` prefix intact | `application/json` — PASS |
| 4 | Register → login → `GET /auth/me` | `role=owner` — PASS |
| 5 | Unknown path reaches the SPA, not the API | `text/html` — PASS |
| 6 | Database publishes no host port | `db 5432/tcp` (network only) — PASS |
| 7 | Both app containers non-root | `backend uid=1000`, `frontend uid=101` — PASS |

### 3.8 Share-token lifecycle and log scrubbing — live

| Check | Result |
|---|---|
| Minted link carries an expiry | minted `2026-08-28T23:54:40Z`, `expires_at 2026-11-26T23:54:40Z` — exactly 90 days |
| Investor report reachable by token, unauthenticated | 200, `farm_name` present — PASS |
| Share token used as a bearer credential | **HTTP 401** — PASS (no escalation) |
| Raw token present in any container log | **absent from all three** — PASS |
| After revoke | **HTTP 404** — PASS |
| Unknown token | **HTTP 404** — identical verdict, no oracle |

All three loggers scrub, and the scrubbed forms were observed directly:

```
frontend-1  | "GET /api/v1/share/report/[redacted] HTTP/1.1" 200 592          <- nginx
backend-1   | INFO: [agriprofit] GET /api/v1/share/report/[redacted]:3e36f866b7a1 -> 200 (29.2ms)
backend-1   | INFO: 172.19.0.4 - "GET /api/v1/share/report/[redacted]:3e36f866b7a1 HTTP/1.1" 200 OK   <- uvicorn
```

nginx redacts; the application middleware and uvicorn's access log both carry a
stable 12-hex fingerprint that correlates requests without being reversible.

### 3.9 Login throttling — live

Eleven consecutive failed logins against one account:

```
attempts  1–10 -> HTTP 401
attempt  11    -> HTTP 429   retry-after: 896
body: {"detail":"Too many requests. Please wait and try again."}
```

The account budget is exactly 10 failures per 900 s, the 429 carries
`Retry-After`, and the message **names no account**, so it confirms no email.

A backend restart cleared the counters and login succeeded immediately —
confirming the documented limitation that in-process counters do not survive a
restart and do not span replicas.

### 3.10 RBAC — live, on the running stack

| Endpoint | worker | manager |
|---|---|---|
| `GET /reports/pnl` | **403** | 200 |
| `GET /dss/decision-support` | **403** | 200 |
| `GET /ledger/summary` | **403** | 200 |
| `GET /equipment/` | **403** | 200 |
| `GET /ledger/logs` | **200** | 200 |
| `POST /share/links` | **403** | **403** (owner-only) |
| `GET /auth/members` | **403** | — |

The 403 body names the missing permission and nothing else:
`{"detail":"Your role (worker) does not permit finance:read."}`

`POST /dss/train` as **owner** → **403**. Retraining is unreachable over the API
for every role.

### 3.11 Input validation, equipment correction, immutability — live

| Check | Result |
|---|---|
| Negative amount (−1,000,000) | **422** |
| Over-cap amount (2,000,000,000) | **422** |
| `Infinity` | **422** |
| `NaN` | **422** |
| Valid amount | 201 |
| `PATCH /equipment/1` rate 10.0 → 12.5 | 200, `updated_at` stamped `2026-08-28T23:57:33.913229Z` |
| No-op `PATCH` with the same value | `updated_at` **unchanged** — a non-correction is not recorded |
| `PATCH` rate 0 (out of range) | **422** |
| `DELETE /ledger/logs/1` | **405** |

### 3.12 Backup and restore rehearsal — executed

Run with the project's own scripts against the live production stack:

```
sh ops/backup.sh
sh ops/restore.sh backups/agriprofit-20260828T235648Z.dump
```

Backup: **28,164 bytes, 8 tables with data**, archive verified readable by
`pg_restore --list` without touching a database.

| Check | Source | Restored | Match |
|---|---|---|---|
| `farms` | 3 | 3 | ✔ |
| `users` | 4 | 4 | ✔ |
| `operational_logs` | 5 | 5 | ✔ |
| `financial_transactions` | 5 | 5 | ✔ |
| `equipment` | 1 | 1 | ✔ |
| `share_tokens` | 1 | 1 | ✔ |
| `alembic_version` | — | **`b9e5f30c74a1`** (chain head) | ✔ |
| Unpaired operational logs | — | **0** | ✔ |
| Live `agriprofit` database | untouched | — | ✔ |
| Scratch database afterwards | dropped | — | ✔ |

This verifies **the mechanism**, against seeded data, on 29 August 2026. It is
not a restore of a production backup, because there is no production deployment.
The monthly rehearsal against real data remains a standing requirement.

### 3.13 Production configuration checks

| Check | Result |
|---|---|
| `docker-compose.prod.yml` renders with only `.env.example` values, no profile | PASS |
| `--profile edge` renders when selected | PASS |
| Database publishes no host port in the prod file | PASS |
| `ops/backup.sh` and `ops/restore.sh` parse (`sh -n`) | PASS |
| No `SECRET_KEY` literal committed | PASS |
| No tracked `.env` | PASS |

---

## 4. Live database census — re-established

Queried directly on 29 Aug 2026, not quoted from the 25 August document:

```
docker start agrip-db-1
docker exec agrip-db-1 psql -U postgres -d agriprofit -tAc "..."
```

| Table | Rows |
|---|---|
| `farms` | **14** |
| `users` | **13** |
| `operational_logs` | **109** |
| `financial_transactions` | **109** |
| `equipment` | **3** |
| `maintenance_logs` | **1** |
| `share_tokens` | **10** |
| `alembic_version` | **`b9e5f30c74a1`** |
| Unpaired operational logs | **0** |

These are identical to the post-cleanup figures in
`docs/DATA_CLEANUP_2026-08-25.md` §4. The census is therefore **still current** —
but it is quotable now because it was re-established by query, not inherited.
The container was returned to its stopped state and nothing was written.

---

## 5. Findings from the 25 August freeze — current status

### 5.1 Closed by `78a68c2`

| Freeze finding | Status at baseline | Evidence |
|---|---|---|
| §6.1.2 Monetary and quantity fields unbounded | **CLOSED** | `schemas.Money` / `Quantity`, `ge=0`, `le=1e9` / `1e6`, `allow_inf_nan=False`; 32 collected tests; live 422s (§3.11) |
| §6.1.3 Equipment cannot be corrected | **CLOSED** | `PATCH /equipment/{id}`, migration `b9e5f30c74a1`, 20 collected tests, live PATCH (§3.11) |
| §6.2 No test executes a migration | **CLOSED** | 12/12 against PostgreSQL 15.18 (§3.3) |
| No rate limiting | **CLOSED** | `core/rate_limit.py`, 19 tests, live 429 with `Retry-After` (§3.9) |
| Share tokens never expire | **CLOSED** | `expires_at`, migration `f7b3c2d94e15`, live 90-day expiry (§3.8) |
| Share token logged in cleartext | **CLOSED** | three-logger scrubbing observed live (§3.8) |
| `POST /dss/train` callable by any authenticated user | **CLOSED** | `Permission.MODEL_TRAIN` granted to no role + config flag; live 403 for owner (§3.10) |
| `requirements.txt` unpinned | **CLOSED** | pinned; cross-environment reproduction (§3.5) |
| No production deployment configuration | **CLOSED** | `docker-compose.prod.yml`, nginx image, Caddy edge, backup/restore; built and exercised (§3.7, §3.12) |
| No authorization model | **CLOSED** | 3 roles / 12 permissions, 74 collected tests, live matrix (§3.10) |

### 5.2 Factually wrong at the commit it described

| Freeze finding | Adjudication |
|---|---|
| §6.1.1 "Per-crop decision support does not net reversals" | **FALSE at `59a6286`.** See §2. Netting worked, no `Unspecified` bucket appeared, and the investor report inherited the correct behaviour. |

### 5.3 Still open at `78a68c2`

| Finding | Status |
|---|---|
| §6.1.4 A mistaken reversal cannot itself be rolled back | **OPEN** — only compensable by an unlinked entry |
| §6.1.5 Service-worker stale-revalidation window | **OPEN, still UNVERIFIED** — reasoned from handler ordering in `vite.config.ts`, never reproduced |
| §6.2 No independent security review or penetration test | **OPEN** |
| §6.2 No load, stress or soak testing | **OPEN** |
| §6.2 Concurrency measured on SQLite, not PostgreSQL | **OPEN** — `test_concurrency.py` uses file-backed SQLite with two real connections; PostgreSQL behaviour is inferred |
| §6.4 No field trial, no real farmer data | **OPEN** |
| §6.4 No usability evaluation, no SUS score | **OPEN** |
| §4 `DryingCurveChart.tsx` and the page/form layer at 0% coverage | **OPEN** — manual inspection only |
| No end-to-end browser suite | **OPEN** |

---

## 6. Limitations that remain open — the complete list

These must survive into Chapter 5 unchanged in substance:

1. **No production deployment.** A production *configuration* exists and has been
   built, started and exercised locally (§3.7). No instance serves real users.
2. **No TLS certificate issued for a real departmental domain.** The Caddy edge
   is configured and its config renders; automatic issuance has never run
   against a real hostname.
3. **No independent security assessment** — no external review, no penetration
   test, no threat model.
4. **No field trial and no real farm data.** Every figure derives from seeded or
   synthetic records.
5. **The forecast tier is trained on synthetic data** and does not learn from any
   user's records. R² 0.9762 is an in-distribution figure against the
   generator's own response surface, not a statement about Nigerian farms.
6. **No usability evaluation and no SUS score.** The instrument pack exists; the
   study was not run. Objective 4 is **partly met**.
7. **No load, stress or soak testing.**
8. **No end-to-end browser testing.** Offline and service-worker behaviour is
   verified against stand-ins.
9. **Backend tests run on SQLite** while production runs PostgreSQL. Only the
   migration chain is executed against PostgreSQL.
10. **Concurrency is measured on SQLite.**
11. **No production observability** — no metrics, tracing or alerting; container
    logs to stdout only.
12. **Single-host design.** Rate-limit counters are in-process: they do not span
    replicas and do not survive a restart (both observed, §3.9).
13. **No token revocation within a token's lifetime**, no refresh tokens, no
    password reset, no email verification, no MFA.
14. **Lighthouse performance figures are stale.** They were measured on
    2026-08-17 at commit `c16924e` against `vite preview` on localhost, on one
    developer machine whose benchmark index varied 425–1654 across runs. They
    were **not** re-run at `78a68c2` and were **not** measured against the
    deployable nginx image. Either re-run them or label them by their commit.
15. **The frontend suite is not timing-robust under machine contention** (§3.4).
16. **A mistaken reversal cannot be rolled back** (§5.3).
17. **The service-worker stale-revalidation window is unverified** (§5.3).

---

## 7. Thesis evidence rule

**The commit `78a68c292205acdcac1a52f977fbea31b6e8495e` on `main` is the
implementation state from which all Chapter 4 and Chapter 5 results are to be
produced.**

- Every quantitative claim in Chapters 4–5 must trace to a numbered subsection of
  §3 or §4 of this document.
- Do **not** mix figures from `EVIDENCE_FREEZE_2026-08-25.md` with figures from
  this document. The 25 August test counts (190 backend / 93% / 89 frontend) and
  coverage figures are superseded and must not appear as current.
- **Do not write "CI is green."** The workflow at `.github/workflows/ci.yml` is
  defined and every job's assertions are readable, but no GitHub Actions run
  result for `78a68c2` was retrievable during this verification (`gh` is not
  installed on the verification machine) and none is recorded in the repository.
  The jobs' substance has instead been executed locally — §3.3, §3.6, §3.7,
  §3.13 — and should be cited that way.
- Anything not verified here is **not** evidence. In particular: no usability
  result, no SUS score, no field data, no production deployment, no
  load test, no independent security assessment.

Reproduce the core figures with:

```
python -m pytest backend/tests/ -q --cov=backend/app --cov-report=term
python -m pytest backend/tests/ --collect-only -q
cd frontend && npm run test && npm run test:coverage
python -m pytest backend/tests/test_reproducibility.py -q
```

And, with Docker available, the parts CI would otherwise own:

```
# migration chain against real PostgreSQL
docker run -d --name pg -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=agriprofit_migrations -p 55432:5432 postgres:15
MIGRATION_TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:55432/agriprofit_migrations \
  python -m pytest backend/tests/test_migrations.py -v

# production stack
cp .env.example .env    # fill SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL
docker compose -f docker-compose.prod.yml up -d --build
sh ops/backup.sh && sh ops/restore.sh backups/<stamp>.dump
```
