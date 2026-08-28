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

---

## 1. Scope and Deployment

**Local-only deployment.** The application runs as a Docker Compose stack
(PostgreSQL, FastAPI backend, Vite/React frontend) on a single machine. It has
never been deployed to a production host. Consequently there is no TLS
termination, no managed database backup or point-in-time recovery, no horizontal
scaling, no process supervision beyond Docker's restart policy, and no
observability stack (metrics, tracing, alerting) beyond structured request
logging to stdout. The signing-key guard (`core/config.py`) refuses to boot
outside `dev`/`test` with the public default `SECRET_KEY`, which is the correct
first step, but a real deployment would additionally require secret management,
network hardening, and an operations runbook that this project does not provide.

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

**No rate limiting or brute-force protection.** Neither the login endpoint nor
any other route is throttled. An attacker can attempt unlimited credential
guesses. Bcrypt's per-attempt cost raises the price of an online attack, but the
absence of lockout, throttling, or CAPTCHA is a real weakness for any
internet-facing deployment.

What the current design *does* get right, and what should be preserved in any
hardening, is the **per-farm data boundary**: every domain query is scoped to the
authenticated user's `farm_id`, and a cross-tenant read resolves to a 404 rather
than leaking existence. The pre-defense audit exercised this boundary across the
ledger, reports, equipment, DSS, and share-link surfaces with a second account's
token and found no cross-tenant access. Passwords are stored only as bcrypt
(`$2b$`) hashes.

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

**Numeric input validation is incomplete.** The schema validates enums, email
format, password length, and the DSS model's input bounds, and no endpoint was
observed to return a 500 on malformed input during the audit. However, monetary
and quantity fields (`amount`, `purchase_price`, `cost`) are
unconstrained floats (`depreciation_rate` is now bounded to 0 < rate <= 100): the audit confirmed that a negative amount and an
absurdly large amount are currently accepted and persisted rather than rejected
with a 422. Such values distort the P&L. Adding lower/upper bounds at the schema
edge is a small, well-understood fix and is listed as near-term future work.

**An equipment record cannot be corrected.** Equipment is create-and-read only:
there is no PATCH or PUT on `/equipment/{id}` and no edit surface anywhere in
the interface. A depreciation rate — or a purchase price or date — entered
wrongly is permanent, and because the rate drives the depreciation overlay, the
allocated fixed cost and both break-even prices, a mistyped rate silently biases
every derived cost figure for that farm with no route to fix it short of direct
database access. Unlike the ledger, where immutability is a deliberate design
choice serviced by reversal, this is simply a missing write path: equipment is
not a financial record and has no audit reason to be append-only.

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

**Per-crop decision support does not yet net reversals.** The farm-wide P&L and
its top-line figures correctly subtract a reversal from the pile its category
feeds (ticket 10b). The *per-crop* decision-support breakdown, and the investor
report that reuses it, do **not** apply the same netting: because a reversal log
carries no crop, the audit confirmed that after reversing a crop expense the
original crop still shows the reversed cost while a phantom "Unspecified" cost
appears. The overall figures remain correct; the per-crop comparison — the view a
farmer would use to choose between crops — is misleading after any reversal. This
is a correctness limitation of the present release, remedied by extending the
reversal-aware aggregation into the per-crop service.

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
  their page, which brings first paint down to a ~132 KB-gzip entry chunk with
  the 82 KB charting code arriving separately and only where it is used. What
  remains is the entry chunk itself (React, router, axios, Dexie), which no
  amount of route splitting reduces — trimming it further means removing or
  replacing a dependency, not deferring one.
- **No load, stress, or soak testing** was performed, and the test suite runs
  against SQLite while production uses PostgreSQL, so dialect-specific behaviour
  at scale is unverified (the reporting code deliberately avoids dialect-specific
  date SQL to keep the two consistent).

## 8. Verification and Assurance

Automated backend statement coverage is **93%** — 1,286 statements, 91 missed —
across **190 backend tests**, alongside **89 frontend tests** in 9 files. Coverage
is concentrated on the business logic: every service except `ledger_service`
(98%) and `reports_service` (94%) is at 100%, as are the schemas, the models and
five of the seven endpoint modules. Three modules sit below 80% and are the
untested remainder: `ml/dataset.py` (36%), `ml/train.py` (42%) and
`models/database.py` (64%) — the ML data-generation and training command-line
paths, and engine construction. The figures are statement coverage, not branch
coverage; `--cov-branch` is not used.

There is no end-to-end browser-automation suite — offline behaviour and the
service-worker cache lifecycle are verified by unit tests against stand-ins
(a stand-in Cache Storage in `cacheInvalidation.test.tsx`, an in-memory Dexie
table in `sync.test.ts`) and by API-level probing, not by a driven browser. There
is no independent security penetration test beyond the internal audits.

The read-only state audit of 25 August 2026 (`docs/STATE_REPORT_2026-08-25.md`)
did find defects, and this section previously claimed otherwise. Two were
cross-tenant or data-integrity issues and both are now fixed: the offline write
queue was not identity-scoped (Section 5 above), and `client_id` uniqueness was
global while idempotency was farm-scoped, so a cross-farm collision returned an
unhandled HTTP 500 (Section 3 above). The absence of further findings is scoped
to what the audit exercised and is not a substitute for external review.

---

## Future Work

The limitations above map onto a concrete, prioritised programme of work. The
first group are small corrections that harden the present contribution; the
second are larger capabilities that extend it.

**Near-term hardening (small, well-scoped):**

1. Constrain monetary and quantity inputs (`amount`, `purchase_price`,
   `depreciation_rate`, `cost`) with non-negative and sane upper bounds at the
   schema edge (§3).
2. Extend reversal-aware netting into the per-crop decision-support and investor
   aggregations, attributing a contra to its original's crop (§3).
3. Scope or clear the offline write queue on authentication change (§5).
4. Eager-load the financial transaction in the ledger list and add an index on
   `operational_logs.financial_transaction_id` (§7).
5. Trim the frontend entry chunk itself — route-level code-splitting is done
   (§7), so the remaining win is dependency-level, not structural.

**Medium-term platform maturity:**

6. Identity hardening: refresh tokens with rotation, server-side revocation, a
   password-reset flow, and login rate-limiting (§2).
7. Cryptographic tamper-evidence for the ledger — an append-only, hash-chained
   audit log — to make "verifiable" a technical guarantee rather than a
   discipline, which is also the honest foundation for the blockchain-backed
   provenance ledger the PRD defers (§3).
8. Per-identity partitioning of the offline read cache instead of wholesale purge
   (§5), and broadening offline write support beyond the quick-log path.
9. A production deployment story: managed hosting, TLS, database backup and
   recovery, secret management, and observability (§1).
10. An end-to-end browser test suite covering the offline/online transition and
    the cache lifecycle, plus an independent security review (§8).

**Longer-term capability (per the PRD's stated intent, not present scope):**

11. Retrain the yield model on the farm's own accumulated records once enough
    history exists, replacing the synthetic-data starting point (§4).
12. External data integration — weather, soil and satellite feeds, and live
    commodity pricing — to enrich decision support (§1, §4).
13. Live low-end channels (USSD/SMS/WhatsApp) via a telecom aggregator (§6).
14. Blockchain-backed supply-chain provenance, building on the hash-chained
    ledger of item 7 (§3).

Taken together, these items describe the distance between a focused thesis
artifact that demonstrably works within its scope and a system ready for
Nigerian farmers in the field. Naming that distance precisely is itself part of
the contribution: it establishes what has been shown, what remains assumed, and
what must be built next.
