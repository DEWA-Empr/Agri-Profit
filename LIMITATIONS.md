# Limitations and Future Work

This chapter records, honestly, what AGRI-PROFIT does **not** do in its current
form. The system was built to demonstrate a specific thesis — that unifying a
Nigerian smallholder's operational records with a financial ledger yields
profitability analysis and stakeholder-ready reporting on affordable,
low-bandwidth hardware — and it meets that objective within a deliberately narrow
scope. The purpose of this chapter is to draw the boundary of that scope
precisely, so that the contribution is neither over-claimed nor mistaken for a
production system, and to set out the concrete work each limitation implies.

The limitations below are grouped by concern. Several were surfaced or confirmed
by a structured pre-defense audit of the running system; where a limitation was
measured rather than merely reasoned about, the measurement is stated. All
performance figures are from a **local Docker development environment** on a
single developer machine and make no claim about production or real-network
behaviour.

**Baseline.** This document describes commit
`78a68c292205acdcac1a52f977fbea31b6e8495e` on `main` (29 August 2026), the
thesis baseline. Every figure and every open/closed judgement here traces to
`docs/EVIDENCE_FREEZE_2026-08-29.md`, which supersedes the 25 August freeze.
Where a limitation recorded in an earlier revision of this file has since been
closed, or was found never to have been real, the entry is rewritten to describe
the current state rather than deleted, so that a reader who meets the old text
elsewhere can see what became of it.

---

## 1. Scope and Deployment

**No production deployment — but a production deployment path that has been
exercised.** This entry previously recorded a blanket absence. That is no longer
accurate, and the distinction now matters: a deployment *path* exists and has
been built, started and probed; a *deployment* does not exist.

Exercised at the baseline (`docs/EVIDENCE_FREEZE_2026-08-29.md` §3.7, §3.12,
§3.13): `docker-compose.prod.yml` builds and starts with all three services
healthy; the frontend is served by nginx and proxies the API with its path
intact; migrations are applied on startup; liveness and readiness probes answer
from the application rather than from the page shell; both application
containers run unprivileged (backend uid 1000, frontend uid 101) and the
database publishes no host port; the signing-key guard (`core/config.py`)
refuses to boot outside `dev`/`test` with the public default `SECRET_KEY`, no
`SECRET_KEY` literal is committed and no `.env` is tracked; an optional Caddy
edge supplies automatic TLS under the `edge` profile and its configuration
renders; and `ops/backup.sh` / `ops/restore.sh` were run end to end against a
real PostgreSQL 15 server, restoring into a scratch database beside the live one
with every row count matching and the paired-write invariant intact.

What does **not** exist: no instance serves real users, no departmental host
runs this software, no TLS certificate has ever been issued for a real domain
(automatic issuance has never run against a real hostname), and there is **no
production observability** — no metrics, no tracing, no alerting; container logs
to stdout are the whole of it. There is no managed database service and no
point-in-time recovery: what exists is a scripted dump and restore. The backup
rehearsal verifies the mechanism against seeded data; it is not a restore of a
production backup, and the standing requirement of a monthly rehearsal against
real data is unaffected by it. Hosting cost is therefore estimated, not
incurred.

**Single-instance assumptions.** The offline-sync idempotency, the DSS
train-on-boot step, and the in-process model cache all assume one backend
instance. Running multiple replicas would require externalising the model
artifact and revisiting the startup training hook.

**Manual-entry scope.** Consistent with the PRD, the platform integrates no
external data feeds. Weather APIs, soil-moisture and satellite imagery, live
commodity prices, and CAN-bus machinery telemetry are all out of scope; every
record is entered by a human. The decision-support outputs are therefore only as
current and complete as the farmer's data-entry discipline.

## 2. Identity, Authentication, and Access Control

**No token revocation within its lifetime.** Access is granted by a stateless
JWT with a fixed 24-hour lifetime (`access_token_expire_minutes`). There is no
server-side session store and no deny-list, so a token cannot be invalidated
before it expires — "logging out" clears the token on the client only. A leaked
token remains valid until expiry. There is also no refresh-token mechanism; when
a token expires the user simply re-authenticates (the frontend's 401 interceptor
drops cleanly to the login screen, so expiry is handled without a broken state,
but it is a re-login rather than a silent refresh).

**No account recovery.** There is no password-reset or email-verification flow.
A user who forgets their password has no self-service path back into their
account. This is a known gap, deferred deliberately to keep the identity surface
small for the thesis.

**Login throttling exists; its counters are in-process.** This entry previously
recorded the absence of any throttling. Authentication is now throttled
(`core/rate_limit.py`, 19 tests): failed logins are counted on two independent
budgets, per account and per client address; registration and the public report
are separately capped; successes are not counted and clear the account budget;
and the refusal names no account, so it confirms no email. Verified live at the
baseline — ten failures returned 401 and the eleventh returned 429 carrying
`Retry-After: 896`, on a budget of exactly 10 failures per 900 s.

The **residual** limitation is the mechanism rather than its absence: the
counters are held in process. They do not span replicas and do not survive a
restart — both observed directly, a backend restart clearing the counters and
the account signing in immediately. On a single-instance deployment that is
acceptable; on a replicated one it is not, and a shared store would be required.
There is still no CAPTCHA and no account lockout beyond the time budget.

What the current design *does* get right, and what should be preserved in any
hardening, is the **per-farm data boundary**: every domain query is scoped to the
authenticated user's `farm_id`, and a cross-tenant read resolves to a 404 rather
than leaking existence. The pre-defense audit exercised this boundary across the
ledger, reports, equipment, DSS, and share-link surfaces with a second account's
token and found no cross-tenant access. Passwords are stored only as bcrypt
(`$2b$`) hashes.

**Authorization within a farm is role-based, and share links are bounded.**
Neither was true when this document was first written, and both bear directly on
the stakeholder-sharing objective. Three roles — owner, manager, worker — sit
over a twelve-permission table (`core/roles.py`, 74 collected tests); endpoints
ask for a permission rather than for a role; and permission is checked **before**
scope, so a refusal never doubles as an existence oracle. Model retraining is
granted to no role and is additionally disabled by configuration — an owner
calling `POST /dss/train` receives 403. Share links expire (90 days, verified to
the second), are revocable, are stored only as a hash, cannot be exchanged for a
session, and resolve unknown, revoked and expired tokens to one identical 404.
The raw token is scrubbed from all three logs that record the request: nginx
writes a redaction, while the application middleware and uvicorn's access log
write a stable non-reversible fingerprint that still correlates requests. What
remains open is stated above and below — no revocation within a token's
lifetime, no refresh, no reset, no second factor, and no independent security
assessment of any of it.

## 3. Data Integrity and the Ledger Model

**Single-entry, not double-entry.** The ledger records each transaction once,
tagged as a debit (expense) or credit (revenue); it does not enforce
double-entry invariants (no balancing counter-account, no trial-balance
guarantee). This is appropriate for the target user — a smallholder tracking cash
in and cash out — but it means the ledger cannot, by construction, self-detect a
posting error the way a balanced double-entry system can.

**Immutability is a discipline, not a cryptographic guarantee.** Records are
never edited or deleted; a mistake is corrected by a *reversal* — a new
category-preserving contra entry linked to the original, leaving both visible in
the audit trail (see `CONTEXT.md` and migration `d5c1f0a9b8e2`). Deletes are
refused with a 405. This gives *soft* immutability and a clean audit history, and
it is genuinely useful. It is **not**, however, tamper-evident in the
cryptographic sense: there is no hash-chaining, signing, or append-only log that
would let an auditor detect out-of-band modification of the database itself. Any
language in earlier chapters or stakeholder-facing copy describing reports as
"tamper-evident" should be read as *audit-trailed*, not cryptographically
verifiable. Closing that gap is future work (see §7).

**The reversal-of-reversal terminal case.** A reversal is itself a record and so
cannot be reversed (guarded with a 409), and an already-reversed entry cannot be
reversed twice. This correctly prevents over-correction, but it also means a
*mistaken* reversal cannot be rolled back through the system — it can only be
compensated by posting a new, unlinked manual entry in the opposite direction.
The audit trail then shows the original, the erroneous reversal, and the
compensating entry, which is truthful but not self-explanatory to a lay reader.

**Monetary and quantity inputs are bounded — closed.** This entry previously
recorded `amount`, `purchase_price` and `cost` as unconstrained floats through
which a negative or absurdly large value could reach the P&L. They are now
constrained at the schema edge by the `Money` and `Quantity` types (`ge=0`,
`le=1e9` and `le=1e6` respectively, `allow_inf_nan=False`), covered by 32
collected tests in `test_input_validation.py`, and confirmed live against the
running production stack: −1,000,000, 2,000,000,000, `Infinity` and `NaN` are
each refused with a renderable 422 rather than a server error, while a valid
amount is accepted with 201. `depreciation_rate` remains bounded to
0 < rate <= 100. The residual limitation is one of kind rather than of range: a
bound rejects the impossible, not the merely wrong, so a plausible but mistaken
amount is still accepted and must be corrected by reversal.

**An equipment record can now be corrected — closed.** This entry previously
recorded equipment as create-and-read only, so that a mistyped depreciation rate
silently biased the depreciation overlay, the allocated fixed cost and both
break-even prices with no route to fix it short of database access.
`PATCH /equipment/{id}` now exists (migration `b9e5f30c74a1`, 20 collected tests
in `test_equipment_correction.py`): the update is partial and farm-scoped, an
out-of-range rate is refused with 422, and the correction timestamp is stamped
**only when a value actually changes**, so a no-op PATCH is not recorded as a
correction. All three behaviours were confirmed live at the baseline. The
distinction from the ledger is unchanged and deliberate: equipment is not a
financial record, so it carries a correction timestamp rather than a contra
entry.

**Mechanisation records machine use but does not cost it.** A mechanisation log
may carry `equipment_id` and `hours_used` alongside its `cost_subtype`. Only
`cost_subtype` drives a figure — it selects the cost-behaviour bucket. The other
two are *capture-only*: validated (`0 < hours_used <= 1000`), persisted, and read
by nothing. This is a deliberate scope boundary rather than a defect, recorded in
`docs/adr/0003`: no machine-hour rate, utilisation figure or cost-per-hour metric
is defined anywhere in this platform's specifications, and inventing one would
put uncited arithmetic underneath cost-structure and break-even numbers the
thesis defends. The consequence is that the system can answer "what did
mechanisation cost, and was that cost fixed or variable?" but cannot answer "what
does an hour of tractor time cost?" — and no chapter should claim otherwise.
Machine-hour costing is future work, and it needs a cited method before it needs
code. `hours_used` is also optional on every write, so any rate built from
today's data would be computed over an unknown fraction of actual machine use.

**Per-crop decision support DOES net reversals — the entry that stood here was a
false positive.** This section previously reported that the per-crop breakdown,
and the investor report that reuses it, failed to net reversals and produced a
phantom "Unspecified" bucket after a crop expense was reversed. That report was
wrong at the commit it described. It is corrected here rather than deleted,
because it was carried into several project documents and repeated in the thesis
interpretation, and because the contrary text survives in the 25 August freeze
as an immutable historical record.

The behaviour was settled by execution rather than by reading code
(`docs/EVIDENCE_FREEZE_2026-08-29.md` §2). Reversing a ₦25,000 crop expense
moved that crop's expenses from ₦35,000 to ₦10,000 and its unit cost of
production from ₦2,916.67 to ₦833.33, with no `Unspecified` bucket present
before or after; the investor report, fetched unauthenticated with a live share
token, returned the same netted figures. The reproduction was run **both** at the
25 August freeze implementation commit (`59a6286`) and at the baseline
(`78a68c2`) and returned identical results, so the capability predates the
freeze: `6992d1c` (16 August 2026) introduced it, nine days before.
`dss_service.py` attributes a contra to its original's crop
(`crop = crop_by_id.get(log.reverses_id) or UNSPECIFIED`) and excludes reversed
yield quantities from the unit-cost denominator. Five named tests pin the
behaviour, including one asserting specifically that no `Unspecified` bucket
appears, and the service stands at 100% statement coverage.

The chronology to carry is therefore: reversal netting existed; the 25 August
audit recorded a contrary finding that contradicted that same document's own
"implemented and verified" table; adjudication on 29 August reproduced the
behaviour and established that the per-crop figures net reversals; and the
baseline **confirms** already-existing behaviour rather than fixing anything.

## 4. Decision Support System

**The forecast tier is trained on synthetic data.** The Tier-2 RandomForest
yield model is trained on a representative *synthetic* dataset
(`ml/dataset.py` — Gaussian rainfall and pH optima, a saturating fertilizer
response, crop-specific ceilings), not on any farm's real history. It is offered
as a plausible starting point while a farm accumulates records, and the interface
is honest about this. Its predictions therefore reflect the modelled agronomy of
the synthetic generator, not observed local reality, and its reported accuracy
(high R² on held-out synthetic data) is an in-distribution figure that does not
transfer to a claim about real Nigerian farms. The model does not learn from the
user's own records in this release, and there is no pipeline to retrain on real
data once enough of it exists.

**The deterministic tier is only as good as the inputs.** Tier 1 (unit cost of
production and per-crop gross margin) is computed transparently from the real
ledger, which is its strength — no black box. But it inherits the data-entry
limitation directly: unrecorded costs or yields simply do not appear, and unit
cost is reported as undefined (never a fabricated zero) when a crop has no
recorded yield quantity. The system cannot distinguish "genuinely zero" from "not
entered."

## 5. Offline and Connectivity Behaviour

**Offline writes cover the quick-capture path only.** The offline-first queue
(IndexedDB via Dexie, flushed on reconnection with a `client_id` idempotency key)
is wired to the dashboard quick-log form. It reliably queues an entry when the
device is offline or the request fails, shows a pending-sync indicator, and
offers a retry for entries that exhaust their attempts — the audit found no silent
loss on this path. Not every form in the application is offline-capable to the
same degree, and the sync model is idempotent-replay, not a full conflict-resolving
CRDT: it assumes a single author per device and does not merge concurrent edits.

**The offline queue is identity-scoped, and cleared on logout.** This was
previously a stated limitation: the queue carried no identity, so on a shared
browser an entry queued by one account could be flushed under the next account's
token and land in the wrong farm, and unsynced entries containing financial
amounts persisted after sign-out. Both are now closed. Every queued row is
stamped with an owner key derived from the token's subject (`lib/queueOwner`),
and the flush, the retry, the pending count and the failed count all read
through a compound `[ownerKey+status]` index — so one account's rows are inert
for every other, and are not drained when nobody is signed in. Logout purges the
departing account's rows before clearing the token. The two protections are
independent on purpose: the purge is best-effort and fire-and-forget, so the
scope has to hold on its own if it never lands, and a regression test asserts
exactly that. Purging does discard unsent work — a deliberate trade, since the
alternative is leaving one farm's records readable in a shared browser's
IndexedDB after its owner has left it; the pending count is on screen in the
sidebar while it is non-zero. Rows written by the previous, unscoped version are
attributed to the signed-in account on upgrade, or dropped if there is none,
because an unattributable row is precisely what the defect flushed.

**Cached reads are purged coarsely.** Offline *reads* are served from a
service-worker cache of authenticated GET responses. Because the cache is keyed
by URL and ignores the Authorization header, it is purged wholesale on every
login and logout so that one farm's cached data can never be served to another
account. This is correct but coarse: it discards a farm's own cache on
re-authentication rather than partitioning per identity, so the first post-login
reads are always uncached.

## 6. Alternative Channels

**USSD, SMS, and WhatsApp entry are absent, not simulated.** This section
previously said the build presented them as interface simulations. It does not:
the ACCESS navigation section carrying them was removed in `b6e2ddb` because
neither had a backend behind it, and `frontend/src/app/navigation.tsx` records
that every remaining entry is a built feature. The same paragraph credited the
ambition to the PRD; `PRD.md` contains no mention of USSD, SMS or WhatsApp, so
that attribution is withdrawn rather than repeated. There is no telecom
aggregator, USSD gateway or WhatsApp Business API connection, and no interface
standing in for one. A production channel — with its session management,
character-set limits and per-message billing — remains out of scope.

## 7. Performance and Scale

None of the following was optimised; the figures are descriptive, measured
locally against a seeded 600-record farm, and are reported so the evaluation is
grounded rather than aspirational.

- **N+1 query on the ledger list.** Listing operational logs serialises each
  row's paired financial transaction via a lazy relationship, so one request for
  a 100-row page issued roughly 100 additional per-row lookups (measured: ~106
  transaction reads for a single request), giving a p50 of ~127 ms versus ~14 ms
  for the whole-farm P&L aggregate. Eager-loading the relationship would remove
  this; it is the single clearest performance fix.
- **Aggregate queries are healthy but the join is unindexed.** The P&L
  aggregation executes in under 1 ms in-database at 600 rows using an index on
  `farm_id`, but joins `operational_logs` by a sequential scan because
  `financial_transaction_id` is unindexed — trivial now, worth an index before the
  data grows.
- **The entry bundle is still large, though no longer monolithic.** The
  production build was one ~245 KB-gzip chunk; every route is now `React.lazy`-
  loaded, and the two recharts-backed dashboard charts are lazy again inside
  their page. Measured at the baseline: the entry chunk is 400.07 KB raw and
  **130.03 KB gzipped**, with the 262.12 KB / 82.07 KB-gzip charting code
  arriving separately and only where it is used, so a cold first load transfers
  **139,245 bytes over 8 requests** against 243,724 over 7 before the split. What
  remains is the entry chunk itself (React, router, axios, Dexie), which no
  amount of route splitting reduces — trimming it further means removing or
  replacing a dependency, not deferring one.
- **Performance figures were re-measured at the baseline** (29 August 2026,
  commit `78a68c2`; raw artefacts in `docs/perf/2026-08-29/`), so they
  characterise the submitted build. They remain **simulated (Lantern) throttling
  against localhost on one developer machine** — a model of a degraded network,
  not a measurement of a real one. Composite score and total blocking time are
  **not comparable** between the 17 and 29 August sets, because the host
  benchmark index differed (425–1654 against 1406–1996); only the network-bound
  metrics and byte counts compare.
- **No load, stress, or soak testing** was performed, and the test suite runs
  against SQLite while production uses PostgreSQL, so dialect-specific behaviour
  at scale is unverified (the reporting code deliberately avoids dialect-specific
  date SQL to keep the two consistent). The one exception is the **migration
  chain**, which is executed against a real PostgreSQL 15 server — 12 of 12
  tests passing, including the schema-versus-models drift check and a
  rollback-and-reapply of the newest revision. Concurrency behaviour remains
  measured on SQLite and inferred for PostgreSQL.

## 8. Verification and Assurance

At the baseline, automated backend statement coverage is **96%** — 1,594
statements, 66 missed — across **422 collected backend cases** (418 passed, 4
skipped locally, 0 failed), alongside **148 frontend tests** in 13 files at
**43.18%** statement coverage. These figures supersede the 93% / 190 / 89 set
recorded here previously, which was measured at the 25 August freeze; the
increase is entirely additive — nine new backend modules and four new frontend
files — and the four backend modules that existed at the freeze collect exactly
the same 190 cases at the baseline, so no earlier verification was weakened.
Test counts are pytest **collected** cases, not counts of `def test_`: six
modules parameterise, so a function count understates them.

Coverage remains concentrated on the business logic. Every module that serves a
request is at or near 100%, including `dss_service`, `enterprise_service`,
`bioprocess_service`, `share_service`, `equipment_service`, `core/roles`,
`core/rate_limit`, `core/logging_safety`, the schemas and the models. The
modules below 100% are `ml/train.py` (47%), `models/database.py` (64%),
`ml/dataset.py` (82%), `api/endpoints/dss.py` (90%), `ml/predict.py` (91%),
`core/security.py` (93%), `main.py` (94%), `services/reports_service.py` (94%),
`services/auth_service.py` (98%) and `services/ledger_service.py` (98%) — the
shortfall concentrated in the offline machine-learning command-line paths, which
means the training pipeline is the least-verified part of the backend. The
figures are statement coverage, not branch coverage; `--cov-branch` is not used.
The frontend figure is low because the React page and form layer has no
component tests at all; the logic modules are at or near 100%. Quote both
numbers or neither.

The frontend suite is **not timing-robust under machine contention**: run
concurrently with the backend suite, one dashboard test exceeded the 5,000 ms
default timeout; run alone the file passes in 2.93 s and the full suite passes
148/148. That is contention against a default timeout rather than a defect, and
it is recorded because it will recur on a loaded machine.

There is no end-to-end browser-automation suite — offline behaviour and the
service-worker cache lifecycle are verified by unit tests against stand-ins
(a stand-in Cache Storage in `cacheInvalidation.test.tsx`, an in-memory Dexie
table in `sync.test.ts`), by API-level probing, and by a single driven-browser
attribution probe, not by an automated browser suite. There is **no independent
security review, penetration test or threat model**, and no load, stress or soak
testing. A CI workflow is defined and its jobs' substance has been executed
locally, but no CI run result is recorded for the baseline commit, so nothing in
this project should be described as "CI is green".

The read-only state audit of 25 August 2026 (`docs/STATE_REPORT_2026-08-25.md`)
did find defects, and this section previously claimed otherwise. Two were
cross-tenant or data-integrity issues and both are now fixed: the offline write
queue was not identity-scoped (Section 5 above), and `client_id` uniqueness was
global while idempotency was farm-scoped, so a cross-farm collision returned an
unhandled HTTP 500 (Section 3 above). That audit also produced one
**false positive** — the per-crop reversal-netting finding adjudicated in
Section 3 above — which is itself a limitation of the method: a defect read out
of code without being reproduced is not a defect until it is reproduced. The
absence of further findings is scoped to what the audit exercised and is not a
substitute for external review.

---

## Future Work

The limitations above map onto a concrete, prioritised programme of work. The
first group are small corrections that harden the present contribution; the
second are larger capabilities that extend it.

**Near-term hardening (small, well-scoped):**

Items 1 to 3 of this list are **done** at the baseline and are retained, struck
through in substance, so that the programme reads as a record rather than as an
outstanding list.

1. ~~Constrain monetary and quantity inputs at the schema edge~~ — **done**
   (`Money` / `Quantity`, 32 collected tests, live 422s; §3).
2. ~~Extend reversal-aware netting into the per-crop decision-support and
   investor aggregations~~ — **withdrawn: there was nothing to fix.** The
   netting already existed and the finding that prompted this item was a false
   positive (§3).
3. ~~Scope or clear the offline write queue on authentication change~~ — **done**
   (`lib/queueOwner`, compound `[ownerKey+status]` index, logout purge; §5).
4. Eager-load the financial transaction in the ledger list and add an index on
   `operational_logs.financial_transaction_id` (§7). **Still open** — measured at
   an earlier state and not re-measured at the baseline.
5. Trim the frontend entry chunk itself — route-level code-splitting is done
   (§7), so the remaining win is dependency-level, not structural.
6. Replace the in-process rate-limit counters with a shared store, so throttling
   survives a restart and spans replicas (§2).

**Medium-term platform maturity:**

7. Identity hardening: refresh tokens with rotation, server-side revocation and
   a password-reset flow (§2). Login rate-limiting, which stood in this item, is
   **done**.
8. Cryptographic tamper-evidence for the ledger — an append-only, hash-chained
   audit log — to make "verifiable" a technical guarantee rather than a
   discipline, which is also the honest foundation for the blockchain-backed
   provenance ledger the PRD defers (§3).
9. Per-identity partitioning of the offline read cache instead of wholesale purge
   (§5), and broadening offline write support beyond the quick-log path.
10. **Perform** the deployment the path now supports: run the production
    composition on a real host, issue a certificate for a real domain, and add
    the observability that is genuinely absent — metrics, tracing and alerting
    (§1). The composition, the TLS edge, the secret guards and the backup and
    restore scripts exist and have been exercised; what remains is doing it for
    real, plus a monthly restore rehearsal against real data.
11. An end-to-end browser test suite covering the offline/online transition and
    the cache lifecycle; an independent security review and penetration test;
    load, stress and soak testing; and concurrency measured on PostgreSQL rather
    than inferred from SQLite (§7, §8).

**Longer-term capability (per the PRD's stated intent, not present scope):**

12. Retrain the yield model on the farm's own accumulated records once enough
    history exists, replacing the synthetic-data starting point (§4). The
    pipeline itself is seed-deterministic and reproducible; what is missing is
    real data, not procedural integrity.
13. External data integration — weather, soil and satellite feeds, and live
    commodity pricing — to enrich decision support (§1, §4).
14. Live low-end channels (USSD/SMS/WhatsApp) via a telecom aggregator (§6).
15. Blockchain-backed supply-chain provenance, building on the hash-chained
    ledger of item 8 (§3).

Taken together, these items describe the distance between a focused thesis
artifact that demonstrably works within its scope and a system ready for
Nigerian farmers in the field. Naming that distance precisely is itself part of
the contribution: it establishes what has been shown, what remains assumed, and
what must be built next.
