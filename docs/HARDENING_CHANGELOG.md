# Production-hardening cycle — 2026-08-27

What changed, and — more importantly — **which earlier documents it supersedes**.

Several defects recorded in `LIMITATIONS.md`, in
`docs/EVIDENCE_FREEZE_2026-08-25.md` §6, and in the Chapter 4/5 draft are now
fixed. Those documents are **not edited here**: they are thesis material and
belong to their author. This file is the delta, so nothing is silently
contradicted and no chapter is quietly rewritten.

**The thesis evidence tag is untouched.** All of this work sits on
`harden/production-readiness`, branched from `acb97e4`. The tag
`thesis-evidence-freeze-2026-08-25` still points at `acb97e4`, so every figure
Chapter 4 quotes remains reproducible by checking it out. No Chapter 4 figure is
invalidated by anything below.

---

## 1. Previously documented defects that are now fixed

Cross-reference these before quoting either document.

| Recorded as | Where | Status |
|---|---|---|
| "Monetary and quantity fields are unbounded" | Freeze §6.1.2, Ch4 §4.14 | **FIXED.** `schemas.Money` / `schemas.Quantity`. Also closed two worse cases the record did not mention — see §2 |
| "Equipment cannot be corrected" | Freeze §6.1.3, Ch4 §4.14 | **FIXED.** `PATCH /equipment/{id}`, partial, farm-scoped, stamped with `updated_at` |
| "No independent security review, and no load, stress or soak testing" | Freeze §6.2.7 | **PARTIALLY ADDRESSED.** Still no independent review and no load testing. Security *boundaries* now have a dedicated regression suite and a CI job |
| "The concurrency tests run on SQLite … Postgres inferred, not measured" | Freeze §6.2.5 | **UNCHANGED** for concurrency. The *migration* chain is now executed against real PostgreSQL in CI |
| "Per-crop decision support does not net reversals" | Freeze §6.1.1, `LIMITATIONS.md:138`, Ch4 §4.6.4 | **WAS ALREADY FIXED BEFORE THE FREEZE** — by `6992d1c`, an ancestor of the freeze commit. This entry was stale when written. Four named tests pin it; `test_workflows.py` now also asserts it end to end |

## 2. Defects found during this cycle that no document recorded

Each was demonstrated against the running API before being fixed.

| Defect | Severity | Consequence |
|---|---|---|
| **A negative debit inflated profit.** Sign is carried by `transaction_type`, so a debit of −1,000,000 was an expense that *added* to margin. A farm with ₦50,000 revenue and that one entry reported a gross margin of ₦1,050,000 | **Critical** | Every other integrity control protects an entry's *history*; none protected its *value*. A P&L shown to a lender could be inflated without leaving a mark — which is the exact claim the sharing feature exists to support |
| **`Infinity` was accepted and stored** (HTTP 201). Gross margin became `null`, and because the ledger cannot delete, the farm's P&L could not be repaired through the API at all. `NaN` reached the database as an unhandled 500 | **Critical** | Permanent, unrecoverable corruption of a farm's financial position |
| **Rejecting a non-finite value produced a 500, not a 422** — FastAPI's error body echoes the offending input and `json.dumps` cannot encode `inf`. A correctly rejected value still gave the wrong answer | High | Surfaced while fixing the above |
| **The share token was logged in cleartext.** `GET /share/report/{token}` carries the whole credential in its path and the middleware logged the path verbatim | **High** | Every investor view wrote a working, unexpiring link into stdout, and thence into container logs and their backups |
| **`POST /dss/train` was callable by any authenticated user** | High | It rewrites the single model artefact every farm's forecast is served from — a cross-tenant side effect on shared state |
| **No rate limiting anywhere** | High | Passwords guessable as fast as bcrypt would answer; the database fillable by a loop |
| **Share tokens never expired** | Medium | A link handed over for one loan assessment stayed live until somebody remembered to revoke it |
| **No test executed a migration** | Medium | `conftest.py` uses `create_all`; a broken migration would keep CI green and fail on the next deployment |
| **`requirements.txt` had no version pins** | Medium | The "frozen" evidence state was not environmentally reproducible |

## 3. What is new

- **Authorization.** Three roles derived from the PRD's personas
  (`core/roles.py`), enforced server-side on every route. Farm scoping is
  unchanged and unweakened — a permission is only ever the right to act on your
  *own* farm.
- **Farm membership.** Owner-only endpoints to add members and set roles, so the
  role model is reachable rather than decorative. Deactivation replaces
  deletion and takes effect on the member's next request.
- **Readiness probe.** `/health/ready` reports the database; `/health` stays a
  pure liveness check so a database hiccup cannot cause a restart loop.
- **Production composition** (`docker-compose.prod.yml`), an nginx-served
  frontend image, an optional automatic-HTTPS edge, and backup/restore tooling.
- **Documentation:** `README.md`, `docs/DEPLOYMENT.md`, `docs/OPERATIONS.md`,
  `docs/REPRODUCIBILITY.md`.

## 4. Corrections the thesis text will need

Not applied here. Listed so they are not missed.

1. **Ch4 §4.14 "Application defects" drops from five to two.** Unbounded
   monetary fields and un-correctable equipment are fixed. The stale reversal
   entry was never true at the freeze. What remains: a mistaken reversal cannot
   itself be rolled back, and the unverified stale-revalidation window in the
   service worker.
2. **Ch4 §4.9's reproducibility reservation is wrong as written.** It says
   re-running training "would produce different figures, because the training
   data is synthesised afresh". The pipeline is seed-deterministic end to end
   and a fresh draw is identical to the cached data — now asserted by test. The
   true limitations are narrower: the fitted artefact is untracked, and the
   environment was unpinned (the second is now addressed).
3. **RMSE is available.** 0.4883 t/ha, measured under the environment recorded
   in `backend/app/ml/model_baseline.json`. Ch4 §4.9 holds a placeholder for it.
   Re-derive it in whichever environment the thesis pins before quoting.
4. **Objective 3's evidence is stronger than the draft claims** — the boundary
   now has a dedicated regression suite covering unauthenticated access, role
   boundaries, cross-farm isolation, privilege escalation attempts, token
   handling and sensitive logging. It is still not an *independent* security
   assessment, and that limitation stands as written.
5. **`docs/EVIDENCE_FREEZE_2026-08-25.md` §1.2** lists four untracked paths "and
   nothing else"; there are now more. Either update it or note it as describing
   the tag rather than the working tree.

## 5. What this cycle did **not** do

- No SMS, WhatsApp, USSD or telephony work. Out of scope and unchanged.
- No Kubernetes, service mesh, multi-region deployment or distributed tracing.
- No rewrite of any working subsystem. The offline queue, sync and idempotency,
  DSS arithmetic, enterprise economics, drying model, reversal handling, cache
  invalidation and investor sharing are all untouched except where a bound or a
  permission was added around them — and 397 of the 402 backend tests that pass
  now are the same tests, unchanged, that passed before.
- No independent security review, no load or soak testing, no field trial, no
  user evaluation.
- ~~No restore executed against a real database.~~ **Closed 2026-08-28.** Docker
  and PostgreSQL 15 were available in a later session; `ops/backup.sh` and
  `ops/restore.sh` were run end to end against the `docker-compose.prod.yml`
  `db` service. Every row count matched the source, `alembic_version` restored
  to the chain head, the paired-write invariant held at 0 unpaired logs, and the
  live database was untouched. See `docs/OPERATIONS.md` §3 for the recorded
  result. The mechanism is verified; the monthly rehearsal against real data is
  still the standing requirement.
