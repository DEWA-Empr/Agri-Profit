<!-- Extracted from Thesis_Ch1-5.docx (26 Aug 2026 merged submission document).
     Chapters Four and Five only; the reference list is not included.
     Structure preserved; wording unaltered at extraction.
     The .docx remains the source of record. -->

# CHAPTER FOUR


# 4.0  RESULTS AND ANALYSIS


## 4.1 Introduction

This chapter reports what the implemented AGRI-PROFIT platform does, measured rather than asserted. It is organised around the four evaluation strands specified in Section 3.8 — functional verification (3.8.1), performance benchmarking (3.8.2), hosting-cost analysis (3.8.3) and usability evaluation (3.8.4) — together with three sections reporting the substantive analytical output of the system: the decision-support figures computed from a live ledger, the enterprise-economics figures derived from them, and the post-harvest drying analysis. Those three are reported in their own right because they are the outputs against which Objectives 2 and 3 are judged.

A reporting standard has been applied consistently throughout and is stated at the outset, because it shapes how every result in this chapter should be read. Each claim belongs to exactly one of four classes, and the class is visible wherever the claim is made:


**Table 4.1: The evidential classification applied throughout Chapter Four**


| Class | What it means | What may establish it |
|---|---|---|
| Implemented | The code exists and, where stated, is reachable by a user. | Source inspection and the deployed application. |
| Automatically verified | A named, passing automated test asserts the behaviour. | The test suites only. |
| Manually inspected | Observed by the researcher, or by a live probe against the running system; no automated test exists. | Live endpoint responses, direct SQL, driven-browser probes, visual inspection. |
| Numerical result | A measured or computed value with a named command or artefact behind it. | Test and coverage output, live API responses, committed measurement artefacts. |

Anything that fits none of these four classes is a limitation. It is reported as such in Section 4.14 and interpreted in Chapter Five, and it is not converted into a result. Where a quantity could not be obtained it is reported as absent or marked as a placeholder rather than filled with a plausible value. Several results in this chapter are consequently unflattering — a low frontend coverage figure, an untested page and form layer, a usability strand that cannot yet be reported, a defect found in the build during the performance measurement. These are reported as found, on the reasoning that a results chapter which lists only what succeeded is not a results chapter.

One further distinction cuts across the classification above and governs the wording of every claim in this chapter and the next. **Implemented** means the capability is present in the system. **Verified** means it is supported by a named test, command or reproducible check. **Validated in practice** means it has been demonstrated with real users, in field conditions, or in production operation. The first two are claimed in this chapter wherever the evidence supports them; the third is claimed nowhere, because no strand of this evaluation establishes it. The distinction matters most for security, usability, forecasting, production deployment and performance, each of which is implemented and in large part verified, and none of which is validated in practice.

The reporting baseline. Every figure, table and screenshot in this chapter is produced from a single implementation state: commit 78a68c292205acdcac1a52f977fbea31b6e8495e on the main branch, dated 29 August 2026, which is the merge of the production-hardening work into main. The working tree is clean for all tracked files and the branch matches its remote. This baseline supersedes the earlier evidence freeze of 25 August 2026, whose test counts, coverage figures and defect list no longer describe the submitted software; the earlier document is retained as a dated historical record and the full verification behind the present baseline is recorded in the project repository as the evidence freeze of 29 August 2026. Demonstration figures are read from the seeded demonstration farm, farm 26, signed in as its own user; the live database holds several other farms, and no figure in this chapter is read from any of them. Its census was re-established by direct query at the baseline rather than carried forward, and is unchanged. The commands that reproduce the whole of Section 4.3 are:

python -m pytest backend/tests -q --cov=backend/app --cov-report=term
python -m pytest backend/tests --collect-only -q
cd frontend && npm run test && npm run test:coverage && npx tsc -b --force && npm run lint && npm run build

Section 4.13 draws the strands together against the four objectives of Chapter One; Section 4.14 states the limitations of the results themselves. Discussion of what the results mean for the wider problem, and the recommendations that follow from them, are reserved for Chapter Five.


## 4.2 The Implemented System

This section reports what exists. No verification claim is attached to anything in it; verification is the subject of Sections 4.3 to 4.5. The separation is deliberate, because “the platform does X” and “the platform is proven to do X” are different statements, and conflating them is the most common way a results chapter overstates its evidence.


### 4.2.1 Deployed components

AGRI-PROFIT is a working end-to-end application rather than a prototype or a mockup. It runs as a three-container Docker composition: a FastAPI backend service, a PostgreSQL 15 database whose schema is managed by Alembic migrations, and a static server for the built Progressive Web Application. The backend is organised into an endpoint layer (authentication, ledger, reports, decision support, bioprocess, equipment and investor sharing), a service layer carrying the business logic (ledger, decision support, enterprise economics, bioprocess, reports, sharing, authentication and equipment), a model and schema layer, and a machine-learning package holding dataset generation, training and prediction. The frontend is organised by feature — farm records, decision support, dashboard, authentication and investor sharing — over a library layer providing the local database, the synchronisation queue, queue ownership, authentication token handling and the read cache, with a Workbox service worker and precache.

The application serves six authenticated routes — dashboard, records, reports, equipment, decision support and investors — and one unauthenticated public route for a shared investor report reached by token.

At the baseline the live database held 14 farms, 13 users, 109 operational logs, 109 financial transactions, 3 equipment records, 1 maintenance log and 10 share tokens, with the migration chain at its head revision and no unpaired operational log. These counts were re-established by direct query at the baseline commit, not quoted from the earlier freeze. The one-to-one correspondence between operational logs and financial transactions is not a coincidence of the sample: it is the paired-write invariant of Section 3.5 visible in the data, every operational record having posted its financial transaction in the same commit.


### 4.2.2 Functional inventory


**Table 4.2: Implemented capabilities and their reachability**


| # | Capability | Status |
|---|---|---|
| 1 | Offline-first operational logbook — local queue, automatic synchronisation on reconnect, client-generated identifier for idempotency | Implemented and reachable |
| 2 | Financial ledger engine — every operational log posts its paired transaction in one commit; per-crop revenue and expense; profit-and-loss with monthly breakdown and CSV export | Implemented and reachable |
| 3 | Ledger integrity — records are soft-immutable; deletion is refused with HTTP 405; corrections are made by category-preserving contra entry linked through reverses_id; double reversal and cross-farm tampering are rejected | Implemented and reachable |
| 4 | Deterministic decision support (Tier 1) — unit cost of production on two bases, per-crop gross margin and ranking, retrospective break-even yield, both break-even prices, sensitivity matrix, operating-expense ratio, partial budget | Implemented and reachable |
| 5 | Predictive decision support (Tier 2) — Random Forest yield forecast with a confidence band derived from the spread of the forest’s trees | Implemented and reachable |
| 6 | Enterprise economics — cost-behaviour classification at the schema edge, derived fixed-cost overlay with depreciation, proportional allocation of fixed cost to crops | Implemented and reachable |
| 7 | Post-harvest drying — Page and Newton model fitting, wet↔dry basis conversion, water balance, safe-storage lookup, per-crop aggregation, drying-aware unit costs | Implemented and reachable |
| 8 | Identity and per-farm data boundary — signed token authentication with hashed passwords; every query farm-scoped; a cross-farm read returns HTTP 404 | Implemented and reachable |
| 9 | Tokenised stakeholder sharing — revocable read-only link; tokens stored hashed at rest | Implemented and reachable |
| 10 | Mechanisation and equipment tracker — equipment, maintenance logs, depreciation rate | Implemented and reachable |
| 11 | Olympic-average yield baseline | Implemented and reachable. The panel is rendered inside the enterprise-economics view, and a null baseline is displayed as the backend’s own stated reason rather than as a dash. |
| 12 | Crop selection on the entry form | Implemented and reachable. The form’s options are assembled at run time from the union of the farm’s own recorded crops and the forecast model’s crops, normalised and deduplicated, so a crop that holds a ledger can always be entered. |
| 13 | Role-based access control within a farm | Implemented and reachable. Three roles — owner, manager, worker — over a twelve-permission table, enforced on every route, with the navigation and route guard following the same table. |
| 14 | Tokenised sharing controls | Implemented and reachable. Every minted link expires, links are revocable, only a hash is stored, and the raw token is scrubbed from every log that records the request. |
| 15 | Authentication throttling | Implemented. Failed logins are counted on two independent budgets, per account and per client address, and registration and the public report are separately capped. |
| 16 | Production deployment path | Implemented. A production composition with an nginx-served frontend, migration-on-startup, health and readiness probes, an optional automatic-TLS edge, and backup and restore tooling. |
| 17 | Per-operation equipment attribution and machine hours | Captured, not consumed. equipment_id and hours_used are validated and stored but read by no service. No cost-per-hour, utilisation or machine-rate figure exists anywhere in the platform. |

Item 17 is reported here rather than omitted because it is a genuine finding about the built system, and it bounds what this thesis may claim about mechanisation: the platform records mechanisation cost within the ledger and classifies it by behaviour, and it does not perform machine-hour or utilisation analysis. The classification decision is recorded in the project’s third architecture decision record. A further constraint on any such analysis is that hours_used is populated on only three of the eight seeded mechanisation logs, so a machine-hour total computed from today’s data would be a total over an unknown fraction of actual machine use.


## 4.3 Functional Verification: Automated Test Evidence

Section 3.8.1 specifies verification of the implemented functionality against the requirements of Chapter Three by means of an automated test suite. This section reports that strand. Every figure in it is measured at the baseline commit by the commands given in Section 4.1, and nothing in this section is drawn from any other source.


### 4.3.1 Suite identity and headline results


**Table 4.3: Verification results at the baseline commit**


| Check | Command | Result |
|---|---|---|
| Backend test suite | python -m pytest backend/tests -q | 422 collected; 418 passed, 0 failed, 4 skipped, 1 warning, 279.89 s |
| Backend migration chain | MIGRATION_TEST_DATABASE_URL=... python -m pytest backend/tests/test_migrations.py -v | 12 passed, 0 skipped, against PostgreSQL 15.18 |
| Backend statement coverage | python -m pytest backend/tests -q --cov=backend/app --cov-report=term | 96% — 1,594 statements, 66 missed |
| Frontend test suite | npm run test | 13 files, 148 tests, 148 passed, 0 failed |
| Frontend statement coverage | npm run test:coverage | 43.18% — 558 of 1,292 statements |
| TypeScript compilation | npx tsc -b --force | Exit 0, no diagnostics |
| Static analysis | npx eslint . | Exit 0, 0 errors, 0 warnings |
| Production build | npm run build | Built in 13.45 s, no errors; service-worker precache 22 entries, 866.74 KiB; dist/ 967 KB |

The four skipped backend cases are the migration tests that require a real PostgreSQL server; they are not skipped in substance. Provided with one, all twelve migration tests execute and pass, as the second row of Table 4.3 records, so the suite is reported as 418 passed with 4 skipped locally and 422 passed when a database is supplied. The suite runs against the real application rather than against mocks: the backend cases exercise the FastAPI application through its test client with a real database session, and the frontend cases exercise the shipped modules, including a genuine IndexedDB implementation. The single backend warning is a deprecation notice raised inside the installed FastAPI package’s own test-client import and not by any code in this repository; it is reported rather than suppressed.

The coverage measurement is statement coverage, not branch coverage. Branch measurement is not enabled and no coverage configuration in the repository turns it on. This is stated because “96% coverage” invites the question of which kind, and the honest answer is the weaker of the two.


### 4.3.2 Where the coverage sits

The headline percentage is less informative than its distribution. Of the 66 missed backend statements, 37 lie in two modules — the synthetic-data generator and the model-training script — which are the offline command-line paths of the machine-learning tier.


**Table 4.4: Backend modules below full statement coverage**


| Module | Statements | Missed | Coverage |
|---|---|---|---|
| ml/train.py | 53 | 28 | 47% |
| models/database.py | 11 | 4 | 64% |
| ml/dataset.py | 50 | 9 | 82% |
| api/deps.py | 29 | 3 | 90% |
| api/endpoints/dss.py | 50 | 5 | 90% |
| ml/predict.py | 46 | 4 | 91% |
| core/security.py | 30 | 2 | 93% |
| main.py | 78 | 5 | 94% |
| services/reports_service.py | 68 | 4 | 94% |
| services/auth_service.py | 63 | 1 | 98% |
| services/ledger_service.py | 56 | 1 | 98% |

Every other backend module with executable statements is at 100%, including the schema layer (194 statements), the data models (81), the decision-support service (162), the enterprise-economics service (72), the bioprocess service (68), the sharing service (36), the equipment service (40), the authorization table (29), the rate limiter (48), the credential-scrubbing module (42), the throttle layer (18) and every endpoint module except decision support. The eleven rows above are the complete set below 100%, taken from a coverage run at the baseline; the project's evidence record lists ten, omitting the dependency-injection module at 90%, and the eleven-row table is the one that reconciles to the 66 missed statements. That distribution is the substantive result: every module that serves a request is fully or almost fully covered, and the shortfall is concentrated in paths that are run manually. That is a defensible place for coverage to be thin, and it is nevertheless a real gap — it means the training pipeline is the least-verified part of the backend, which bears directly on how the model figures of Section 4.9 should be read.

The frontend figure must be quoted alongside the backend one or not at all. Measured over every file under src, frontend coverage is 43.18% of statements (558 of 1,292), 32.41% of branches, 36.16% of functions and 43.00% of lines. The headline is low because the React page and form layer has no component tests at all. The logic modules, by contrast, are fully or almost fully covered: the local database, the synchronisation queue, queue ownership, authentication token handling, the offline partial-budget implementation, the crop-option merge, the record-bounds rules and three decision-support panels are at or near 100% statements, and the drying-parameter rules stand at 94.33%.


**Table 4.5: Frontend test files at the baseline**


| File | Tests |
|---|---|
| features/farm-records/recordBounds.test.ts | 22 |
| features/farm-records/dryingParams.test.ts | 20 |
| app/routeAccess.test.tsx | 18 |
| lib/queueOwner.test.ts | 16 |
| features/dss/partialBudget.test.ts | 15 |
| lib/sync.test.ts | 15 |
| app/navigation.test.ts | 14 |
| features/farm-records/cropOptions.test.ts | 8 |
| lib/dbUpgrade.test.ts | 7 |
| features/dashboard/dashboardAccess.test.tsx | 5 |
| lib/cacheInvalidation.test.tsx | 5 |
| features/auth/AuthProvider.test.tsx | 2 |
| lib/apiCache.test.ts | 1 |
| Total | 148 |


### 4.3.3 Capability-to-proof mapping

The behaviours below are those on which the design argument of Chapter Three depends. Each is asserted by at least one named passing test. The mapping is given at the level of behaviour rather than of endpoint, because several of these behaviours are properties of the interaction between components rather than of any single one.


**Table 4.6: Behaviours verified by automated test, with the evidence for each**


| Behaviour verified | What is asserted | Proof |
|---|---|---|
| Cross-farm offline-key handling | Two farms may hold the same client-generated key; neither sees the other’s record and neither request fails with a server error | Three tests over the composite constraint, plus the migration that introduced it |
| Same-farm idempotency, sequential | Replaying a record returns the same row with HTTP 200, with exactly one log and one transaction stored | test_idempotent_log_creation; test_farm_scoped_idempotency_still_holds_after_the_constraint_change |
| Same-farm idempotency, concurrent | The loser of a race receives the winner’s row, its flushed transaction rolled back rather than double-booked; the endpoint answers 200, not 500; a non-replay integrity error still raises; two unstubbed threads racing one key book exactly one record | test_concurrency.py, 5 tests, file-backed SQLite with two real connections; the threaded case run ten times consecutively without a flake |
| Offline queue identity isolation | The queue is partitioned by an owner key derived from the token’s subject; every read path uses the compound owner-and-status index | queueOwner.test.ts (16) and sync.test.ts (15); both modules at 100% statements |
| Logout queue cleanup | Only the signing-out account’s rows are deleted, before the token is cleared; a no-op when signed out; never blocks logout | The logout-cleanup block of sync.test.ts; the by-owner purge case in dbUpgrade.test.ts |
| Local database migration | A genuine version-1 database, opened by the shipped version-2 module: all rows survive with payload intact, ownership is attributed, both indexes are queryable, and migrated rows then flush through the real synchronisation module | dbUpgrade.test.ts, 7 tests |
| Mechanisation schema behaviour | Cost subtype is validated against a closed taxonomy and is the only field that moves a derived figure; equipment identifier and hours are validated, persisted, read by nothing, and survive a read-back unchanged | Five schema and API tests |
| Drying model and readings | Process-loss and clean-balance fixtures, exact Page-model recovery, insufficient and out-of-range readings, wet↔dry basis round-trip, safe-storage lookup, water balance distinguished from mass difference | test_bioprocess_service.py (11); the service at 100% coverage |
| Drying input validation | Every malformed run is rejected as HTTP 422 at the schema edge, never 500 | 8 API tests plus 20 client-side tests mirroring the same rules |
| Drying arithmetic and API outputs | Detail and summary access control, cross-farm 404, exclusion of reversed runs, per-crop aggregation | The bioprocess detail and summary test blocks |
| Yield-baseline computation | Three seasons required; one high and one low discarded; ties discard one instance rather than all; mixed units return null with a stated reason; the season count is reported in every branch | 6 API tests and 4 service tests |
| Crop-selection logic | The farm’s recorded crops and the forecast model’s are merged, deduplicated across case and whitespace, the null crop dropped rather than displayed, one failed source falling back to the other, the list sorted stably | cropOptions.test.ts (8); the module at 100% |
| Enterprise economics | Classification and coverage, the depreciation overlay (a zero rate counting as unrated, never as a zero charge), proportional allocation, both break-even prices with the cash price provably strictly lower, the sensitivity matrix, the operating-expense ratio, and the partial budget signed both ways | test_enterprise_service.py (40); the service at 100% |
| Offline/backend partial-budget parity | Two independent implementations agree against one shared hand-computed fixture, including that an exact zero is not returned as negative zero | partialBudget.test.ts (15) and the backend parity block |
| Decision-support outputs | Per-crop ranking, alphabetical tie-breaks, break-even yield and each of its null cases, reversal netting at farm level, drying-aware unit costs, every degenerate crop case | The decision-support service at 100% with its API test block |
| Cache invalidation on write | Log writes, queue flushes, equipment creation, maintenance logging and reversals each invalidate the cached derived reads | cacheInvalidation.test.tsx (5) |
| Per-crop reversal netting | A reversed crop expense leaves the crop’s expenses and unit cost; no “Unspecified” bucket appears; a reversed yield’s quantity leaves the denominator; a fully reversed crop is omitted | Five named decision-support tests, and a direct reproduction against the running API |
| Role-based authorization | Three roles over a twelve-permission table; a worker is refused the farm’s financial picture, a manager may not disclose the farm, only an owner may manage members or mint a link; an unknown role receives no permission at all | test_authorization.py (74 collected) |
| Permission checked before scope | A caller lacking a permission is refused before the system reveals whether the named record exists, so a 403 never doubles as an existence oracle | test_permission_is_checked_before_scope |
| Share-token lifecycle | Every minted link expires; a link is revocable; only a hash is stored; unknown, revoked and expired tokens return one identical verdict so the endpoint is not an oracle; a share token cannot be used as a bearer credential and reaches no write path | test_share_lifecycle.py (16 collected) |
| Credential scrubbing in logs | The raw share token is replaced by a non-reversible fingerprint before any log line is written, and the query string is scrubbed wholesale | test_logging_safety.py (20) |
| Authentication throttling | Failed logins are counted on two independent budgets, per account and per client address; successes are not counted and clear the account budget; the refusal names no account | test_rate_limit.py (19) |
| Input bounds at the domain edge | Money and quantity are non-negative, capped and finite-checked; a non-finite value is refused with a renderable 422 rather than a server error | test_input_validation.py (32 collected) |
| Equipment correction | A partial, farm-scoped update; the correction timestamp is stamped only when a value actually changes; an out-of-range rate is refused | test_equipment_correction.py (20 collected) |
| Migration chain | The chain runs from an empty database to head, the migrated schema matches the models, the newest migration rolls back and reapplies, and the application reads and writes the migrated schema | test_migrations.py (12), executed against PostgreSQL 15.18 |
| Forecast reproducibility | The dataset generator and the training pipeline are seed-deterministic; the dataset fingerprint and the three metrics are stable across environments | test_reproducibility.py (18) |
| Model retraining is unreachable | Retraining rewrites the single artefact every farm’s forecast is served from; no role holds the permission and a configuration flag independently disables the route | test_model_training_over_the_api_is_refused_even_for_an_owner |


### 4.3.4 Movement against the previously reported figures

The figures reported at the evidence freeze of 25 August 2026 were 190 backend tests at 93% statement coverage over 1,286 statements with 91 missed, and 89 frontend tests across nine files at 33.48% statement coverage. Those figures are superseded. They are reconciled here rather than replaced silently, because a test count that moves without an explanation is not evidence.


**Table 4.7: Reconciliation of the test figures, freeze to baseline**


| Figure | At the 25 August freeze | At the baseline | Cause |
|---|---|---|---|
| Backend test files | 4 | 13 | Nine modules added by the production-hardening work |
| Backend tests collected | 190 | 422 | The nine new modules contribute exactly 232 cases |
| Backend statements | 1,286 | 1,594 | Authorization, rate limiting, credential scrubbing, share-token expiry, equipment correction and input bounds are new application code |
| Backend missed statements | 91 | 66 | Twenty-five previously unexercised statements are now covered, chiefly in the machine-learning and endpoint paths |
| Backend coverage | 93% | 96% | More code, and proportionally more of it tested |
| Frontend test files | 9 | 13 | recordBounds, routeAccess, navigation and dashboardAccess |
| Frontend tests | 89 | 148 | The four new files contribute 59 cases |
| Frontend statements | 1,129 | 1,292 | Role-aware navigation and route guarding are new code |
| Frontend coverage | 33.48% | 43.18% | The new modules are logic, and are tested |

Two properties of the reconciliation are worth stating because they bear on whether the earlier evidence is invalidated. First, the four test modules that existed at the freeze collect exactly the same 190 cases at the baseline: test_api.py 134, test_enterprise_service.py 40, test_bioprocess_service.py 11 and test_concurrency.py 5. No pre-existing test was removed, weakened or renumbered, so every behaviour verified at the freeze remains verified. Second, the entire increase is additive — nine new backend modules and four new frontend files covering authorization, input bounds, credential scrubbing, throttling, the share-token lifecycle, equipment correction, the migration chain, forecast reproducibility and role-aware routing.

One counting convention must be stated, because two defensible numbers exist for the same file. Test totals in this chapter are pytest collected cases, not counts of test functions. Six backend modules use parameterisation, so a function count understates them — test_enterprise_service.py, for instance, defines 32 functions that expand to 40 collected cases. The collected figure is used throughout because it is what the 422 total is composed of.


## 4.4 Negative-Control Testing

A passing test suite demonstrates that the behaviours somebody thought to test behave as specified. It is silent about whether those tests would notice if the behaviour broke. That distinction is not academic: an assertion that a purge function was called passes just as happily when the purge deletes nothing, which is the exact class of defect such a test exists to catch.

Three sets of mutation experiments were therefore run, in which the implementation was deliberately broken and the suite re-run to confirm it failed, and failed for the right reason. This is the strongest single piece of verification evidence in this chapter, and it is reported in full.


**Table 4.8: Negative-control (mutation) runs**


| # | What was broken | Suite | Outcome |
|---|---|---|---|
| 1 | The read-cache purge replaced with a no-op, its signature and export unchanged so that every call site still resolves and still awaits | Cache-invalidation suite | 5 failed, 0 passed. Every failure is on a value or on rendered text; none is on a call count |
| 2 | The local-database upgrade hook broken | Migration suite | 4 of 7 tests fail |
| 3a | The shared parity fixture renamed away | Both backend and frontend | Failure at collection and transform time, before any test body executes |
| 3b | The parity fixture truncated to invalid JSON | Both | Decode failure at collection and transform time |
| 3c | The fixture’s declared case count raised to 9 while its cases remained 8 | Both | The internal-consistency test fails in each suite: 1 failed, 39 passed (backend); 1 failed, 14 passed (frontend) |

Experiment 1 is the most informative. Each of the five tests seeds a real cache entry through a stand-in service worker, performs the write, and re-reads — so the assertion is on the value the user would see. With the purge neutered, the decision-support figure reads ₦0 where ₦3,500 is correct after a log write; ₦0 where ₦5,500 is correct after a queue flush; ₦0 where ₦12,000 is correct after a maintenance entry; a stale sentence about depreciation rates where a corrected one is expected after an equipment write; and — the discriminating case — ₦5,500 where ₦2,000 is correct after a reversal. That last figure matters because it is not zero: only a working purge combined with correctly netted contra accounting produces ₦2,000, whereas a surviving cache produces ₦5,500 and a lost record produces ₦0. The three outcomes are distinguishable, so the test can only pass for the right reason.

Experiment 3 establishes a different property: that the parity fixture cannot go missing, malformed or silently shorter without failing both suites. A parity test that skips or defaults when it cannot find its input is indistinguishable from no parity test at all, and runs 3a and 3b show that no such code path exists — the failure occurs before any test body runs. Run 3c covers the case import-time failure cannot catch, by comparing the file’s own declared case count against the number of cases present and both against a constant declared independently in each test file.

What the negative controls do not establish. They establish that these tests are load-bearing. They do not establish anything about behaviour the suites do not reach — in particular, the background-revalidation half of the service worker’s caching strategy, which is modelled in neither harness. That behaviour is reasoned from the handler’s ordering and has never been reproduced; it is reported in Section 4.14 as a candidate defect rather than a confirmed one. Nor can a parity run establish that two implementations are not wrong in the same way; it establishes only that hand-computed expectations, which neither implementation generated, disagree with neither.


## 4.5 Manually Inspected Evidence

This section reports evidence obtained by observation rather than by automated test. It is weaker evidence, and it is separated from Section 4.3 for that reason. It is nonetheless evidence, and reporting it separately is what allows Section 4.3 to be read as strictly as it is written.


### 4.5.1 Components verified visually only

The drying-curve chart component has no automated test and 0% coverage. Its visual rendering correctness is established by manual inspection alone, and no claim of automated coverage is made for it anywhere in this thesis. The distinction is material because the drying calculations the chart displays are fully covered: the bioprocess service is at 100%, the client-side drying rules are covered by 20 tests, and the drying API outputs — detail, summary, validation and reversal handling — are covered by the test block named in Table 4.6. What is not covered is the drawing of the picture.

The same status applies to the wider page and form layer, which is listed here so that no reader infers coverage from the presence of a screenshot: the record creation form, the records page, the drying entry fields, the drying result panel, the login page, the decision-support prediction page, the investor pages, the application shell, and the hook that wraps the fully tested crop-option module. All are implemented, all are reachable, and none is exercised by an automated test.

[INSERT VERIFIED RESULT HERE — figure numbers and captions for the interface screenshots. Screenshots are to be taken against the baseline commit, signed in as farm 26, following the project’s screenshot run-sheet. A farm-list screenshot must not be used to establish which farm is which, because two farms share the name “Demo Farm” and only farm 26 carries the seeded demonstration data.]


### 4.5.2 Live system verification

Every endpoint on which this chapter’s figures depend was exercised against the running stack and returned HTTP 200: the decision-support breakdown, the model information endpoint, the bioprocess summary and detail endpoints, and all five enterprise-economics routes. No probe returned a non-2xx response. The authenticated probes were performed as the seeded demonstration farm’s own user, and the responses are the source of every figure in Sections 4.6 to 4.9.

Two further live checks were performed and are reported because they bear on data integrity rather than on functionality. First, after the verification-artefact cleanup that preceded the freeze, the database state was confirmed by direct SQL: the transient verification farms and their logs were absent, and every seeded and demonstration record was unchanged. Second, the backend answered an unauthenticated request to a protected route with HTTP 401 and a root request with HTTP 200, with no error appearing in its log after the deletion.


### 4.5.3 Service-worker attribution by driven browser

A zero-byte network transfer establishes that a resource came from a cache; it does not establish which cache. Because the architectural claim under test concerns the service worker specifically — an ordinary browser HTTP cache would evidence nothing about the design — attribution was established directly by driving a real browser rather than inferred from timings.


**Table 4.9: Service-worker attribution probe**


| Check | Result |
|---|---|
| Page controlled by a service worker | True; the controller is the built service worker |
| Cache storage present | One cache, the Workbox precache |
| Bundle resolvable from cache | Hit, HTTP 200 |
| Full navigation with the network disconnected | HTTP 200, served from the service worker |
| Rendered result offline | The login screen rendered, with no console or page errors |

One qualification is recorded because it was encountered and resolved rather than assumed away. After the offline navigation the browser’s own connectivity flag reported the network as available, which taken at face value would have invalidated the test. Control requests to resources outside the precache, issued both before and after the navigation, were rejected with a disconnection error, as were requests to the backend. The network was therefore genuinely unreachable at the moment the navigation succeeded, and the connectivity flag is a known artefact of the emulation applied to a freshly created document.

This probe is the evidence for the offline claim in Section 4.10, and it is manually inspected evidence, not an automated test. No end-to-end browser test of the offline-to-online transition, the service-worker lifecycle or the installation path exists, and none is claimed.


### 4.5.4 Live verification against the production stack

The production composition was built and started for this chapter, and the checks below are live HTTP results against it rather than readings of a configuration file. They are reported as manually inspected evidence: each was executed once and observed, not asserted by a test that runs on every change.


**Table 4.10: Checks executed against the running production stack**


| Check | Observed |
|---|---|
| All services report healthy | Backend, database and frontend all healthy |
| The application is served | GET / returns HTML |
| Readiness answers from the backend, not the page shell | {"status":"ready","checks":{"database":"ok"}} |
| The API is reachable through the proxy with its path intact | GET /api/v1/ledger/logs returns JSON |
| An unknown path reaches the application, not the API | Returns HTML |
| Register, sign in, and read the authenticated identity | Role returned as owner |
| The database publishes no host port | Reachable on the internal network only |
| Both application containers run unprivileged | Backend uid 1000, frontend uid 101 |
| A worker is refused the farm's financial picture | 403 on the profit-and-loss, decision-support, summary and equipment routes; 200 on the farm's own log |
| Only an owner may disclose the farm | 403 on minting a share link, for both worker and manager |
| The refusal names the missing permission and nothing else | "Your role (worker) does not permit finance:read." |
| Model retraining is refused for every role | 403 for an owner |
| A minted share link carries an expiry | 90 days, to the second |
| A share token cannot be used as a bearer credential | 401 |
| A revoked link, and an unknown token, return one identical verdict | 404 in both cases |
| The raw share token reaches no log | Absent from the application, server and proxy logs alike |
| Monetary input is bounded and finite-checked | Negative, over-cap, infinity and not-a-number each refused with 422; a valid amount accepted |
| Equipment is correctable, and a non-correction is not recorded | Rate updated and timestamped; a repeat of the same value left the timestamp unchanged; an out-of-range rate refused with 422 |
| Deletion is refused | 405 |
| Failed logins are throttled | Ten refusals, then 429 with a retry interval and a message naming no account |

Two of these deserve comment because they are properties that a configuration review would not have established. The credential-scrubbing check was performed by minting a live token, fetching the report through the proxy, opening the corresponding application route, and then searching every container's log output for the raw token: it appears in none of them, while the scrubbed forms are present, the proxy writing a redaction and the application writing a stable non-reversible fingerprint that still allows two requests carrying the same link to be correlated. And the throttling check incidentally confirmed the documented limitation that the counters are held in process: restarting the backend cleared them and the account signed in immediately.


### 4.5.5 Backup and restore rehearsal

The backup and restore scripts were executed end to end against a real PostgreSQL 15 server holding seeded data — two tenant farms, four users across all three roles, five operational logs each paired to a financial transaction, one equipment record with a maintenance entry, and one share token.

The backup produced a 28,164-byte archive and verified it by reading its table of contents without restoring it, listing eight tables carrying data. The restore was run in its rehearsal mode, which restores into a scratch database beside the live one and drops it afterwards.


**Table 4.11: Restore rehearsal, source against restored**


| Check | Source | Restored |
|---|---|---|
| farms | 3 | 3 |
| users | 4 | 4 |
| operational_logs | 5 | 5 |
| financial_transactions | 5 | 5 |
| equipment | 1 | 1 |
| share_tokens | 1 | 1 |
| Schema version | — | At the migration chain head |
| Unpaired operational logs | — | 0 |
| The live database afterwards | Untouched | — |

The last two rows are the substantive ones. The restored database satisfies the platform's central integrity invariant — every operational log carries its financial transaction — and the live database was not written to, which is what makes the rehearsal safe to run on a schedule. This verifies the mechanism against seeded data. It is not a restore of a production backup, because there is no production deployment, and the standing requirement of a monthly rehearsal against real data is unaffected by it.


## 4.6 Decision-Support Results from the Live Ledger

Objective 2 concerns the conversion of recorded farm activity into decision-relevant financial information. The deterministic tier is exactly that conversion: it computes from the ledger the platform actually holds, with no model, no estimation and no external data. This section reports its output against the seeded demonstration farm at the baseline commit. Every figure is a live API response, and every one is traceable to the records that produced it.


### 4.6.1 Per-crop gross margin and ranking


**Table 4.12: Per-crop decision support, farm 26, at the baseline**


| Rank | Crop | Revenue (₦) | Expenses (₦) | Gross margin (₦) | Yield | Marketable mass |
|---|---|---|---|---|---|---|
| 1 | Cowpea | 624,950 | 267,700 | 357,250 | 480 kg | 431 kg |
| 2 | Cassava | 178,600 | 94,400 | 84,200 | 1,880 kg | — |
| 3 | Maize | 45,000 | 3,500 | 41,500 | 100 kg | 84 kg |
| 4 | Tomato | 0 | 112,900 | −112,900 | none | — |
| 5 | Sorghum | 0 | 119,950 | −119,950 | none | — |
|  | Farm total | 848,550 | 598,450 | 250,100 |  |  |

Four properties of this output matter to the argument, and each is pinned by a named test irrespective of the seeded amounts.

First, the ordering is computed rather than incidental. Crops are sorted by descending gross margin with alphabetical tie-breaking, and the test is constructed so that an alphabetical sort cannot pass it by coincidence. Note that the ranking is by margin, not by scale: cassava earns nearly four times maize’s revenue and returns roughly twice its margin, while maize returns ₦41,500 on ₦3,500 of recorded cost. Ranking and efficiency are different questions, and the platform answers the first.

Second, a loss is displayed as a loss. Tomato and sorghum carry recorded input costs and no sale, and both report negative margins rather than being suppressed or shown as zero. The loss-making enterprise is precisely the one a farmer most needs to see, and a system that quietly omits it would fail at the point of greatest value.

Third, the figures are the ledger, not a projection. Each is the sum of transactions carrying that crop’s category, with reversed pairs netted at farm level.

Fourth, the yield column is unit-aware. Where a crop’s harvests were recorded in incompatible units the platform returns a null rather than an arithmetically invalid sum. Farm 26 is unit-clean, so each crop here reports a single unit; the wider database is not, which is why the behaviour exists.


### 4.6.2 Unit cost of production on two bases

Unit cost is the figure most directly connected to the pricing decision a farmer faces at the farm gate. The platform computes it as attributed cost divided by output, and — this being the point at which the record-keeping layer meets the process-engineering layer — it distinguishes the mass that left the field from the mass that can actually be sold.


**Table 4.13: Unit cost of production, farm 26**


| Crop | Cost basis | Denominator | Unit cost | What it answers |
|---|---|---|---|---|
| Maize | Harvest (wet) mass | 100 kg | ₦35.00 / kg | What the crop cost to produce in the field |
| Maize | Marketable mass | 84 kg | ₦41.67 / kg | What each saleable kilogram must recover at the gate |
| Cowpea | Harvest (wet) mass | 480 kg | ₦557.71 / kg |  |
| Cowpea | Marketable mass | 431 kg | ₦621.11 / kg |  |
| Cassava | Harvest mass | 1,880 kg | ₦50.21 / kg | No drying run recorded, so no marketable basis exists |

The 19% difference between ₦35.00 and ₦41.67 is post-harvest mass reduction expressed in money. A farmer pricing against the wet-basis figure would be pricing against a mass that no longer exists and would under-recover by ₦6.67 on every kilogram sold. The same pattern appears on cowpea, where the two bases differ by ₦63.40 per kilogram.

Two reporting decisions inside those figures are themselves results. The marketable denominator is the mass actually weighed out, not the mass the dry-matter balance predicts. For the maize run those two differ: from 100 kg at 25% moisture the dry matter is 75.0 kg, which at 13% final moisture should weigh 86.21 kg, against 84 kg observed. Costing against the predicted 86.21 kg would give ₦40.60 per kilogram and would charge the farmer’s pricing decision with grain that never reached the store. Costing against the observed 84 kg is the conservative and correct choice, and it is the one the platform makes. And where no drying run exists, as with cassava, the marketable figure is withheld rather than defaulted to the harvest mass — the two are not the same quantity, and reporting one as the other would be a silent error.

The API returns these values at full floating-point precision — the marketable maize figure is 41.666666666666664 — and the interface formats to two decimal places. The ₦41.67 quoted throughout this thesis is that value rounded to the kobo, and the residual difference of roughly a third of a kobo is a display artefact rather than a discrepancy.


### 4.6.3 Retrospective break-even yield

Break-even yield reports the output at which a crop would have covered its recorded costs at the price actually achieved. It is deliberately retrospective, and the interface says so by rendering it in the past tense, because the platform holds no forward price forecast and must not imply one.


**Table 4.14: Retrospective break-even yield, farm 26**


| Crop | Recorded cost (₦) | Realised price (₦/kg) | Break-even yield | Actual yield |
|---|---|---|---|---|
| Maize | 3,500 | 450.00 | 7.78 kg | 100 kg |
| Cassava | 94,400 | 95.00 | 993.68 kg | 1,880 kg |
| Cowpea | 267,700 | 1,302.00 | 205.61 kg | 480 kg |
| Tomato | 112,900 | none realised | null | none |
| Sorghum | 119,950 | none realised | null | none |

The maize record covered its recorded cash costs within the first eight kilograms sold. The nulls are as informative as the numbers: where no sale has been recorded there is no realised price, and a break-even computed against a price that does not exist would be arithmetic dressed as advice. The figure is likewise withheld where no yield has been recorded, where the sale that established the price has since been reversed, and where no cost has been attributed to the crop — in that last case an arithmetically valid break-even of zero kilograms would communicate a false completeness to a user whose actual situation is that they have not recorded their costs. All four null cases are asserted by named tests.


### 4.6.4 A withdrawn defect report: per-crop reversal netting

One qualification must travel with Tables 4.12 to 4.14 and is stated here rather than deferred, because it affects how the figures are read.

An earlier draft of this chapter reported that the per-crop decision-support breakdown fails to net reversals, and that a phantom “Unspecified” cost appears after a crop expense is reversed. That report was incorrect, and it is withdrawn here — rather than quietly dropped — because it was carried in several project documents, repeated in the interpretation, and recorded in a dated evidence document that remains in the repository and that a reader may well encounter.

The behaviour was settled by execution rather than by reading. A crop expense of ₦25,000 was posted alongside a second expense of ₦10,000 and a yield of ₦40,000 over 12 bags; the first expense was then reversed and the decision-support endpoint queried. The crop’s expenses moved from ₦35,000 to ₦10,000, its unit cost of production was recomputed from ₦2,916.67 to ₦833.33, and no “Unspecified” bucket appeared. The investor report, which reuses the same aggregation, returned the same netted figures to an unauthenticated recipient holding only a share token.

The chronology matters, and it is not the chronology of a fix. The reproduction above was run at the 25 August evidence-freeze commit **and** at the baseline, and returned identical figures at both. Reversal netting therefore existed before the audit that reported it missing; the commit that introduced it is dated nine days before that audit; the audit's own summary table already listed reversal netting among the verified capabilities, so the document contradicted itself and the erroneous half was the defect list; and the adjudication reported here reproduced the behaviour and established the correct reading. **The baseline confirms behaviour that already existed. It did not fix anything, and this thesis does not claim that it did.** What the episode demonstrates is a methodological point that Chapter Five returns to: a defect read out of source code and never executed is a hypothesis, not a finding.

The mechanism is that a reversal carries no crop of its own, so the aggregation attributes the contra to the crop of the log it reverses, and separately excludes a reversed yield’s quantity from the unit-cost denominator. Five named tests pin the behaviour, including one asserting specifically that no “Unspecified” bucket appears, and the decision-support service stands at 100% statement coverage. The per-crop breakdown is therefore reversal-correct, on the same basis as the farm-wide statement.


## 4.7 Enterprise Economics Results

The enterprise-economics layer extends the deterministic tier from margin accounting to cost-behaviour analysis. All figures are live responses from farm 26 at the baseline commit.


### 4.7.1 Cost structure and classification coverage


**Table 4.15: Cost structure, farm 26**


| Bucket | Maize (₦) | Whole farm (₦) |
|---|---|---|
| Variable cost | 3,500 | 483,650 |
| Semi-variable cost | 0 | 26,500 |
| Recorded fixed cost | 0 | 18,000 |
| Unclassified cost | 0 | 70,300 |
| Total recorded cost | 3,500 | 598,450 |
| Cash cost (variable + semi-variable) | 3,500 | 510,150 |
| Classification coverage | 100% | 88.25% |
| Revenue | 45,000 | 848,550 |
| Cash operating cost | 3,500 | 580,450 |
| Operating-expense ratio | 7.78% | 68.40% |

Classification coverage is itself the substantive result. It states what proportion of recorded cost carries a cost subtype, and it is reported rather than hidden because every downstream figure inherits its incompleteness. At farm level 11.75% of recorded cost is unclassified — two mechanisation logs entered without cost parameters — and the platform reports that as unclassified rather than defaulting it into a bucket. An unclassified cost sits inside the total and outside the cash figure, so a reader can see exactly how much of the analysis rests on classified data. The maize enterprise, at 100% coverage, is the case where the figures can be read without that reservation.

The operating-expense ratio excludes the depreciation overlay of Section 4.7.2 and excludes any recorded depreciation charge, both of which are non-cash; it is a measure of how much of each naira of revenue is consumed by cash operating cost. Maize consumes 7.78 kobo in the naira; the farm as a whole consumes 68.40.


### 4.7.2 The depreciation overlay and fixed-cost allocation

Depreciation is computed as a derived overlay at report time and is never posted to the ledger. The reasoning is recorded in an architecture decision record and is worth restating because it is a design result rather than an arithmetic one: posting a synthetic depreciation row would require either an unpaired entry, which violates the paired-write invariant that the whole ledger design rests on, or a fabricated operational log describing an event that did not happen. Neither is acceptable in a ledger whose claim is that every row records something a farmer did. The overlay is therefore computed, transparent and recomputable, in the same way as every other derived figure on the platform.


**Table 4.16: Derived fixed-cost overlay, farm 26**


| Quantity | Value |
|---|---|
| Reporting period | 7.0 days, derived from the ledger span |
| Period fixed cost (depreciation overlay) | ₦10,068.49 |
| Equipment records | 2 |
| Equipment without a usable depreciation rate | 1 |
| Total direct cost, all crops (the allocation base) | ₦598,450 |
| Fixed cost allocated to maize | ₦58.88 |

Three properties are asserted by test. A zero depreciation rate counts as unrated and is reported in the unrated count, never as a zero charge — so a partial overlay is visible as partial rather than being read as a small true fixed cost. The allocation is proportional to direct cost and is computed farm-wide before any crop filter is applied, so the same figure cannot change according to how it was requested. And where the total direct cost is zero, every share and every allocation is undefined rather than being split evenly, on the reasoning that an even split invents an allocation base that does not exist.

Two simplifications ride along and are stated rather than hidden: the method is straight-line with no salvage value and no accumulated-depreciation floor, so an asset held past its implied life keeps charging and the overlay is an upper bound. The reporting window may also be pinned explicitly rather than derived, which is a reproducibility measure: a derived span widens every time a log is entered, and a figure quoted from a widening window cannot be re-derived afterwards.


### 4.7.3 Dual break-even price and yield sensitivity


**Table 4.17: Break-even price, maize, farm 26**


| Quantity | Value |
|---|---|
| Variable and semi-variable cost | ₦3,500.00 |
| Total recorded cost | ₦3,500.00 |
| Allocated fixed cost | ₦58.88 |
| Total cost | ₦3,558.88 |
| Marketable mass | 84 kg |
| Break-even price to cover cash cost | ₦41.67 / kg marketable |
| Break-even price to cover total cost | ₦42.37 / kg marketable |

Two prices are reported rather than one because they answer different questions: what the farmer must obtain this season to avoid a cash loss, and what must be obtained to cover the wear on the assets used as well. The cash price is provably strictly lower than the total price, which is asserted directly by test, including in the edge case of full classification coverage and no overlay. Both are withheld entirely where no marketable mass exists, because a price per kilogram of nothing is undefined.


**Table 4.18: Yield sensitivity matrix, maize, farm 26**


| Yield scenario | Marketable mass | Break-even price, cash | Break-even price, total |
|---|---|---|---|
| 75% of recorded | 63.0 kg | ₦55.56 / kg | ₦56.49 / kg |
| 90% | 75.6 kg | ₦46.30 / kg | ₦47.08 / kg |
| 100% (baseline) | 84.0 kg | ₦41.67 / kg | ₦42.37 / kg |
| 110% | 92.4 kg | ₦37.88 / kg | ₦38.52 / kg |
| 125% | 105.0 kg | ₦33.33 / kg | ₦33.89 / kg |

The matrix is labelled conditional in the response and in the interface, because every row other than the baseline describes a yield that did not occur. It answers the planning question the deterministic tier is otherwise silent on: how much the required price moves if the harvest disappoints. A quarter shortfall in marketable mass raises the cash break-even price by a third.


### 4.7.4 Partial budget and implementation parity

The partial-budget calculator evaluates a proposed change by four terms — added revenue, reduced cost, lost revenue and added cost — and returns the signed net change. A probe with added revenue ₦120,000, reduced cost ₦15,000, no lost revenue and added cost ₦90,000 returned benefits of ₦135,000 against costs of ₦90,000 for a net change of +₦45,000. The four inputs were chosen for the probe and are not seeded data; the route is stateless and wrote nothing.

The result of interest here is not the arithmetic but the parity. The partial budget is implemented twice — once in the backend service and once in the client, so that it remains available offline — and two implementations of the same formula are an invitation to divergence. Eight cases were hand-computed, placed in a single shared fixture read verbatim by both suites, and asserted against both implementations. They agreed on all eight on the first run; no divergence was found. The cases include a negative result whose sign is asserted separately from its magnitude, an exact zero that must not be returned as negative zero, kobo-level precision, and a transposition trap that swaps a pair of terms. The three fixture-mutation runs reported in Section 4.4 establish that the shared fixture cannot go missing or silently shrink without failing both suites.


### 4.7.5 Yield baseline

The Olympic-average yield baseline discards the highest and lowest season before averaging, and requires at least three seasons. Queried for maize on farm 26 it returns no Olympic average, a grand average of 100.0 kg, a season count of 1, and the stated reason that an Olympic average needs at least three seasons and this crop has one. That is the result: the demonstration farm holds a single season, and the platform says so rather than averaging what it has. The season count is reported in every branch of the response, including the branches that return no average, so that a null is never read without the count that explains it — one season and ten seasons are different reasons for the same null.

This endpoint is implemented and covered by ten tests — six at the API level and four at the service level — and it is reachable: the panel is rendered inside the enterprise-economics view, where a null Olympic average is displayed as the backend’s own stated reason rather than as a dash, precisely so that the three different nulls are not collapsed into one. An earlier draft of this chapter recorded the baseline as computed but invisible, which was true of an earlier build and is not true at the baseline; the reachability defect is withdrawn.


## 4.8 Post-Harvest Drying Results

The post-harvest module implements thin-layer drying kinetics: conversion between wet-basis and dry-basis moisture content, a dry-matter balance determining marketable output, a water balance, safe-storage assessment, and the fitting of two established thin-layer models to an observed moisture series. It carries the bioprocess engineering content of the platform.


### 4.8.1 Verification by designed fixture

A drying model can only be shown to be correct by recovering parameters known in advance, so the module is verified by hand-calculated fixture rather than by demonstration. Eleven service-level tests pass and the service stands at 100% statement coverage. The properties established are:

- (a)  Exact recovery of the Page model. The Page model, MR = exp(−k·tⁿ), is linearised by the double logarithm ln(−ln MR) = ln k + n·ln t and its parameters recovered by least-squares regression on that transform. The fixture is a moisture series constructed from a known Page curve with an initial moisture content of 30.0% wet basis, k = 0.30 and n = 0.75, sampled at five times — 1, 2, 4, 6 and 8 hours, giving 24.098299, 20.557042, 15.501120, 11.947665 and 9.326998% wet basis. The fit recovers n = 0.750000 and k = 0.300000 with a linear r² of 1.000000, using all five readings and dropping none. That establishes that the linearisation, the regression and the back-transformation from ln k to k are each correct — the whole of the fitting path. One implementation detail is asserted by the same fixture and is worth recording, because getting it wrong changes the answer without failing visibly: the moisture ratio is normalised against the stated initial moisture content, not against the first reading, and the fit runs on a dry basis. Normalising against the first reading, or fitting on a wet basis, returns approximately n = 0.805 and k = 0.218 — a plausible-looking result that is wrong.
- (b)  The water balance is not a mass difference. A dedicated fixture asserts that the mass of water removed and the process loss are distinct quantities and fails if they are ever made equal. The distinction is the specific error the module exists to prevent: water leaving the grain is the intended outcome of the process, whereas solid matter leaving the system is a loss.
- (c)  A clean-balance control. A second fixture is constructed so that observed outlet mass equals the mass the dry-matter balance predicts, giving zero process loss, which isolates the balance itself from the loss accounting layered on it.
- (d)  Insufficient and out-of-range readings. A fit is refused rather than attempted below three readings, and readings outside the physical moisture band are dropped.
- (e)  Safe storage is null, never false, for an unknown crop. An unrecognised crop has no threshold, and the platform reports the absence of a threshold rather than a negative verdict.
- (f)  Basis conversion round-trips. Wet-basis to dry-basis and back returns the original value.

### 4.8.2 The seeded drying run in full


**Table 4.19: Maize drying run, farm 26, as computed by the platform**


| Quantity | Value |
|---|---|
| Method | Solar dryer |
| Inlet mass | 100.0 kg at 25.0% moisture, wet basis |
| Outlet mass observed | 84.0 kg at 13.0% moisture, wet basis |
| Drying time | 10.0 h |
| Dry matter | 75.0 kg |
| Expected outlet mass from the dry-matter balance | 86.21 kg |
| Process loss | 2.21 kg (2.56%) — below the 5% data-quality threshold |
| Water removed (water balance) | 14.08 kg |
| Mean drying rate | 1.408 kg/h |
| Specific drying rate | 0.01877 kg water / kg dry matter / h |
| Moisture, dry basis | 33.33% → 14.94% |
| Moisture ratio, final | 0.4483 |
| Newton (Lewis) rate constant, k | 0.08023 h⁻¹ |
| Page model | n = 0.7956, k = 0.1316, linear r² = 0.9981 over 3 readings, 0 dropped |
| Safe-storage verdict | Safe, against the 13.0% wet-basis maize threshold |


**Table 4.20: Per-crop drying summary, farm 26**


| Crop | Runs | Mass in | Marketable mass | Water removed | Mean drying rate | Mean Newton k (solar dryer) | Safe-storage share |
|---|---|---|---|---|---|---|---|
| Cowpea | 1 | 480.0 kg | 431.0 kg | 36.84 kg | 2.631 kg/h | 0.03745 | 1.0 |
| Maize | 1 | 100.0 kg | 84.0 kg | 14.08 kg | 1.408 kg/h | 0.08023 | 1.0 |

The two runs are internally consistent in a way that is worth noting: the maize run, which removes a larger proportion of its initial moisture, returns a Newton rate constant roughly twice the cowpea run’s under the same drying method, and the cowpea run’s higher absolute drying rate reflects its larger batch rather than a faster process. Both are reported per crop rather than pooled, because a mean rate constant across crops with different initial moistures would not describe anything physical.

One reservation applies to the Page fit specifically. The fit requires intermediate time-and-moisture readings, and the readings on the seeded runs reported here were supplied by the seed script. The interface does capture them: the drying entry form provides an optional, repeatable time-and-moisture reading row, so a run entered by a user can carry the series the Page model needs, and a run entered without one is saved and has its Page fit correctly refused rather than attempted. What is therefore demonstrated in this section is the model fitted over a seeded series; a fit over a series captured through the interface is available but is not among the figures reported here.


### 4.8.3 Input validation

Every malformed drying submission is rejected at the schema edge with HTTP 422, and never with a server error. Eight API tests cover outlet mass exceeding inlet mass, a final moisture not below the initial, non-positive mass, moisture outside the physical range, readings not in strictly increasing time order, and readings outside the moisture band. Twenty client-side tests mirror the same rules in the browser, so an invalid run is refused before it is queued as well as after it is sent. This matters for the offline path in particular: a record that the API will always reject, but that the client accepts and queues, would retry forever.


### 4.8.4 Coupling to the financial ledger

The engineering significance of this module is not the kinetics in isolation — the models are long established — but that its output enters the financial record. A drying run is recorded as an operational activity like any other, so it posts its cost to the ledger through the same paired write as a fertiliser application, and its computed marketable output becomes the denominator of the unit-cost figure in Table 4.13. The chain from a moisture measurement to a price per marketable kilogram — 100 kg at 25% moisture, dried to 13%, weighed out at 84 kg, costed at ₦41.67 rather than ₦35.00 — is computed by the platform without manual intervention at any step. Access control and reversal handling travel with it: a drying run belonging to another farm returns HTTP 404, and a reversed run is excluded from the summary.


## 4.9 Yield-Forecast Model Evaluation on Synthetic Data

The predictive tier is a Random Forest regressor serving a yield estimate from agronomic inputs. Its reported quality is:


**Table 4.21: Yield model as served by the platform**


| Property | Value |
|---|---|
| Model | Pipeline (one-hot encoder + Random Forest regressor) |
| Estimators | 200 |
| Training samples | 6,000, synthetically generated |
| Features | Rainfall, fertiliser used, soil pH, crop |
| Crops | Maize, rice, sorghum, soybean, cassava |
| Target | Yield, t/ha |
| Coefficient of determination (R²) | 0.976204 |
| Mean absolute error (MAE) | 0.241393 t/ha |
| Root-mean-square error (RMSE) | 0.488334 t/ha |
| Feature importances | Crop 0.3445; rainfall 0.2845; soil pH 0.2479; fertiliser 0.1231 |
| Trained | 1 July 2026 |

These figures are an in-distribution result on synthetic data and nothing more. The training data was generated from a parameterised agronomic relationship and the model was then fitted to that generated data, so an R² of 0.9762 measures how well the Random Forest recovers a relationship that was constructed to be recoverable. It is evidence that the machine-learning pipeline is correctly implemented — that features are encoded, the model fitted, and predictions served end to end — and it is not evidence that the model predicts Nigerian smallholder yields. No claim of field-predictive accuracy is made anywhere in this thesis.

Two reservations bound the claim further, and one earlier reservation is withdrawn.

First, the model is not validated against any real data. The suite establishes that a model exists, that the endpoint validates its inputs, and that a forecast is returned with an interval; it establishes nothing about field accuracy. The two least-covered backend modules, at 47% and 82%, remain the training and data-generation paths, and they account for 37 of the 66 missed statements reported in Table 4.4.

Second, the fitted artefact itself is not under version control. The model is written to disk at first boot and is not committed, so the binary served at any moment is not the object a reader can inspect.

The reservation that the pipeline is not reproducible is withdrawn, because it is false. The pipeline is seed-deterministic end to end, and re-running it does not produce different figures. Regenerating the dataset from the generator with its recorded seed and refitting the estimator at the baseline reproduces R² 0.976204, MAE 0.241393 and RMSE 0.488334 — agreeing with the recorded baseline metrics to six decimal places rather than merely within the recorded tolerance of ±0.0005. The repository records a dataset fingerprint taken over the float64 bytes of the feature and target columns rather than over the formatted CSV text, so the check is insensitive to library formatting changes, and it identifies scikit-learn and numpy as the packages that actually move the metrics. The same three figures were obtained in two environments differing in Python minor version and pandas patch version. Eighteen tests assert this determinism.

RMSE is therefore reported, at 0.488334 t/ha, and Chapter Three’s statement that it "may additionally be reported" is superseded by its being reported.

What the platform does do with these figures is report them honestly in the interface. Three display states are distinguished: metrics unavailable while loading; an explicit statement that the model has not been trained, where that is the case; and the figures with their disclosure where a trained model exists. The untrained case is deliberately not rendered as R² 0.0000, because a zero reads to a user as a very poor model rather than as no model. All three states are asserted by test at the endpoint level, though the rendered states themselves are manually inspected only.


## 4.10 Performance Results

Section 3.8.2 specifies a Lighthouse audit of the production build under mobile emulation and network throttling.


### 4.10.1 Method and conditions

Lighthouse 13.4.1 was run in headless Chrome against the production build served by the `frontend-prod` container, which runs `vite preview` on the built bundle — the configuration in which the service worker is registered, as distinct from the development server, which registers none. Device emulation was a mobile profile at 412 × 823 with a device pixel ratio of 1.75, and throttling was Lighthouse’s simulated (Lantern) method throughout with a constant 4× CPU slowdown, so that differences between conditions are attributable to network characteristics alone. Five cold runs were performed per network condition and three user-flow iterations, each flow iteration containing a cold and a warm navigation. Medians are reported.

**The audit was re-run at the baseline commit for this chapter.** An earlier measurement set exists, taken on 17 August 2026 at commit `c16924e` against a build that predates route-level code-splitting; it is not the set reported here, and Section 4.10.3 reconciles the two rather than quoting them interchangeably. The figures in Table 4.22 were measured on **29 August 2026 against commit 78a68c2**, the baseline this whole chapter reports, by the same method and on the same machine as the earlier set. Both sets of raw artefacts — the reports, the flow script and the driven-browser probe — are retained with the project, so every figure below can be recomputed independently.


**Table 4.22: Lighthouse results at the baseline commit (medians, measured 29 August 2026 at `78a68c2`)**


| Condition | n | Score | FCP | LCP | Speed Index | TBT | Transfer | Requests |
|---|---|---|---|---|---|---|---|---|
| Slow 4G, 1.6 Mbps — cold | 5 | 99 | 1,709.9 ms | 1,859.9 ms | 1,709.9 ms | 9.0 ms | 139,245 B | 8 |
| Slow 3G, 0.4 Mbps — cold | 5 | 65 | 5,661.2 ms | 5,661.2 ms | 5,661.2 ms | 10.5 ms | 139,245 B | 8 |
| Slow 3G, 0.4 Mbps — warm | 3 | 100 | 70.6 ms | 1,612.0 ms | 70.6 ms | 0 ms | 127 B | 7 |
| Flow harness, cold navigation | 3 | 65 | 5,664.4 ms | 5,664.4 ms | 5,664.4 ms | 3.5 ms | 139,245 B | 8 |

Cumulative Layout Shift was 0 in every run and is omitted from the table.

The final row is an internal control rather than a fifth condition. The user-flow harness performs a cold navigation before its warm one, and that cold navigation independently reproduces the command-line cold figure to within about three milliseconds — which establishes that the two harnesses are comparable and that the warm measurement may legitimately be set against the command-line cold result.


### 4.10.2 The principal finding

Between the first and second navigation of the same flow, on an identical 0.4 Mbps simulated link, first paint fell from 5,664.4 ms to 70.6 ms — a factor of eighty — and network transfer fell from 139,245 bytes to 127. The service-worker precache serves the entire application shell from local storage, and this is proven rather than inferred by the driven-browser probe of Section 4.5.3: a full navigation with the network disconnected returned HTTP 200 and rendered the login screen.

The residual 127 bytes are worth naming precisely, because they are not noise. Every request that constitutes the application — the document, both JavaScript chunks, the stylesheet, the service-worker registration script and the web manifest — transferred **zero** bytes on the warm navigation. The single request that did not is `pwa-192x192.png`, the manifest icon, which is the defect reported in Section 4.10.4. The warm measurement therefore does double duty: it establishes that the shell is served entirely from the precache, and it independently confirms that exactly one declared asset is missing from that precache.

The finding must be stated with equal precision about what did not improve. Largest contentful paint in the warm run was 1,612.0 ms — a factor of 3.5, not eighty — and it is largest contentful paint rather than first paint that both weighs most heavily in the composite score and corresponds most closely to the moment a user considers the page usable. Reporting the warm result as “0.07 seconds” would be true of first paint and materially misleading about the experience. The honest summary is that the service worker eliminates network transfer of the shell entirely and all but eliminates time to first paint, while time to main content remains bounded by client-side rendering and improves by a factor of about three and a half. That warm largest-contentful-paint figure is, to within two milliseconds, the same as the one measured on the earlier build (1,613.8 ms), which is itself informative: reducing the transferred bundle does not move a metric that was never network-bound.

The cold results locate a threshold. Between 1.6 Mbps and 0.4 Mbps first paint rises by 3.95 s, and the arithmetic is checkable: a 139,245-byte payload is 1,113,960 bits, requiring 2.78 s of transfer at 400 Kbps against 0.68 s at 1,638.4 Kbps — 2.1 s of the gap — with the remainder accounted for by the additional round-trip latency of the slower profile (400 ms against 150 ms). CPU throttling was identical in both conditions, confirming a network effect rather than a compute effect. The application therefore performs well from a degraded 3G connection upwards and degrades materially only at throughput characteristic of 2G or EDGE-class service.


### 4.10.3 Movement against the earlier measurement set, one confound, and a discarded pair of measurements

Three qualifications are reported in this section rather than deferred to the limitations, because each changes what the numbers above may be used for.

First, the host machine’s speed varies across runs. Lighthouse records a benchmark index of available compute with every run: it ranged from 425 to 1,654 across the 17 August set and from 1,406 to 1,996 across the 29 August set, so the machine was both faster and more consistent on the later date. First contentful paint, largest contentful paint and speed index are modelled analytically under simulated throttling and are largely insulated from host speed. Total blocking time and the composite performance score are not. **No score difference and no blocking-time difference between the two measurement dates may be attributed to the code, and none is attributed to it here** — which specifically rules out reading the improvement in total blocking time, from a median of 121 ms to 10.5 ms on the cold slow-3G condition, as an effect of the code. The comparisons that survive the confound are the warm-against-cold contrast, measured within a single browser session, and the network-bound metrics and byte counts.

Second, the earlier measurement set is superseded and is reconciled here rather than discarded. It was taken on 17 August 2026 at commit `c16924e`, which precedes the route-level code-splitting present in the baseline; at that point the application shipped as a single JavaScript chunk. The comparison below is restricted to the metrics that are legitimately comparable across dates.


**Table 4.23: Movement between the earlier and the baseline measurement, comparable metrics only**


| Metric | 17 Aug 2026, `c16924e` | 29 Aug 2026, `78a68c2` | Movement |
|---|---|---|---|
| Cold transfer, both conditions | 243,724 B over 7 requests | 139,245 B over 8 requests | −43% bytes, one more request |
| Cold FCP/LCP/SI, slow 3G | 7,674.4 ms | 5,661.2 ms | −2,013 ms (−26%) |
| Cold FCP, slow 4G | 2,317.7 ms | 1,709.9 ms | −608 ms (−26%) |
| Warm FCP, slow 3G | 116.4 ms | 70.6 ms | −46 ms |
| Warm LCP, slow 3G | 1,613.8 ms | 1,612.0 ms | unchanged |
| Warm transfer | 0 B (application shell) | 0 B (application shell), 127 B total | unchanged in substance |
| Composite score, TBT | not comparable | not comparable | host-speed confound |

The direction the earlier draft could only predict is now measured. Route-level code-splitting removed 104,479 bytes from the first load — the entry chunk is now 400.07 KB raw and 130.03 KB gzipped, with the charting code and every non-login route arriving separately and only where used — and the cold first paint fell by about a quarter on both network conditions, which is the expected consequence of transferring 43% fewer bytes over a bandwidth-bound link. What did not move is the warm largest contentful paint, because it was never bounded by transfer. The precache grew from 21 entries at 859.67 KiB to 22 at 866.74 KiB, since splitting produces more, smaller files.

Third, two measurement configurations were executed at the 17 August measurement, found invalid, and discarded. They are reported because in each case the error surfaced through an internal inconsistency in the data rather than through inspection of the configuration, which is the more instructive point. An intermediate network condition specified at 1,600 Kbps was invalid because the default mobile profile already throttles to 1,638.4 Kbps, making the intended reduction negligible, and because the latency parameter used belongs to a different throttling method and was disregarded entirely; it was identified as invalid because the supposedly slower setting returned a marginally faster median first paint, which no genuine bandwidth reduction can produce. A first attempt at the warm condition used repeated command-line invocations on the assumption that a registered service worker would persist between them; it does not, because each invocation launches a fresh browser profile, so every supposedly warm run was in fact cold. This was caught by the transfer field showing a full bundle transfer with no service-worker attribution, and confirmed by inspecting the profile directory, which contained no service worker at all. Had those timings been reported they would have shown the service worker to be ineffective, which is the opposite of the truth. Both errors were fixed in the harness before the 17 August set was kept, and the 29 August re-run inherits the corrected harness unchanged.


### 4.10.4 A defect found during measurement

The application’s manifest icon, `pwa-192x192.png`, is absent from the service-worker precache and is therefore unavailable offline. At the earlier measurement the evidence of record was the precache listing rather than a failed request, because whether a browser attempts to fetch a manifest icon during a navigation varies between runs. The baseline re-run supplies the stronger evidence directly: on the warm navigation every other request in the document transferred zero bytes and this one transferred 127, which is the icon being fetched from the network because the precache does not hold it. The defect is therefore confirmed at the baseline by measurement rather than by listing. The impact is cosmetic — the shell renders correctly without it and an installed application would fall back to a default — and it is recorded as a genuine finding about the build rather than an artefact of the measurement.


## 4.11 Hosting-Cost Analysis

Objective 4 requires an assessment of cost-effectiveness. A production deployment was outside the scope of this study, so operating cost is estimated rather than incurred. The estimate is anchored on the platform’s measured resource consumption rather than on assumption, and is labelled an estimate wherever it appears.


### 4.11.1 Measured footprint


**Table 4.24: Measured container footprint**


| Component | Measured memory | At the baseline | Note |
|---|---|---|---|
| FastAPI backend | 145.5–161.5 MiB | 160.3 MiB | At rest, ≈0.1–0.2% CPU. Includes the Python runtime, the framework, the ORM, numpy, scikit-learn and the fitted model |
| PostgreSQL 15 | 33.4–41.3 MiB | 32.9 MiB | At rest, ≈0.0% CPU, against the seeded dataset |
| Measured subtotal | 178.9–202.8 MiB | 193.2 MiB | The two containers exercised during the original sampling |
| Static file server | Not measured | 83.5 MiB | The `vite preview` container, measured at the baseline. The shipped production frontend is nginx, not this, and was not measured — a static nginx image would be materially smaller |
| Host OS and container runtime | Not measured | Not measured | Conventionally 300–400 MiB |

Ranges rather than single figures are given for the original sampling because memory varied by approximately 11% between two instances of the same image. Startup was sampled by repeated single-shot polling at a mean interval of 2.37 s, and the widest gap of 4.11 s falls across the steepest part of the memory climb, so the 145.5 MiB startup peak is a lower bound on the true maximum rather than the maximum itself.

The third column was taken at the baseline commit, on the running development composition, and is reported because the original sampling predates the baseline. It confirms the earlier figures rather than replacing them: the backend sits inside its earlier range and the database marginally below it, and the previously unmeasured static file server is now measured at 83.5 MiB — above the 50–80 MiB the earlier analysis reasoned for a Node process, and well above the figure a lightweight static server would show. That last number should not be carried into the cost model, because the composition this thesis would actually deploy serves the frontend from nginx, whose footprint was not measured. The host operating system and container runtime remain unmeasured, so the total is still part-measured and part-assumed, and is described as such.


### 4.11.2 A correction to the earlier reasoned estimate

An earlier version of this analysis reasoned the footprint from the known composition of each container and concluded that the machine-learning tier dominated memory, that the train-on-boot step set the sizing constraint, and that a 4 GB instance was required. Measurement does not support that argument. The entire backend process occupies 145 to 162 MiB, and whatever share the machine-learning tier accounts for is far too small to influence the choice of instance. The reasoned estimate was wrong by a factor of approximately three, and wrong in kind rather than merely in degree. A 2 GB instance is sufficient.

What measurement does show is that the train-on-boot step costs time rather than memory: 8.57 s from restart to accepting traffic, of which the memory climb occupies roughly the first eight seconds. On a single-instance deployment with no redundancy that is 8.6 s of unavailability on every restart or redeployment. The architectural case for externalising the model artefact therefore stands, but it rests on availability and the ability to run replicas, not on hosting cost. This correction is reported rather than quietly replaced, because a superseded estimate and the reason it was superseded are part of an honest method.


### 4.11.3 Estimated monthly cost


**Table 4.25: Estimated monthly operating cost**


| Line item | USD / month | NGN / month |
|---|---|---|
| Instance (2 GB RAM, 50 GB SSD) | $12.00 | ₦16,327 |
| Automated snapshot backups (≈20% of instance) | $2.40 | ₦3,265 |
| Domain name (amortised) | $1.00 | ₦1,361 |
| TLS certificate | $0.00 | ₦0 |
| Estimated total | $15.40 | ≈ ₦20,950 |

Conversions use the Central Bank of Nigeria rate of ₦1,360.58 to the US dollar as at 12 August 2026; the parallel-market rate on 13 August 2026 was ₦1,425, so the naira figures are indicative rather than exact. Prices are list prices captured on a single date, exclusive of tax and of any committed-use discount; no provider was contacted and no quotation obtained. [CONFIRM — re-check provider pricing pages and restate the retrieval date before submission.]

Storage and bandwidth are immaterial at any plausible pilot scale. A paired record occupies on the order of 1 KB including index overhead, so a farm logging five activities a day generates roughly 1.8 MB a year, and the 50 GB volume included with an entry-level instance would hold tens of thousands of farm-years. The application bundle crosses the network once per device because it is served from the precache thereafter, and API responses are measured in kilobytes.


### 4.11.4 Cost per farm at scale


**Table 4.26: Reasoned cost per farm served**


| Farms per instance | NGN / farm / month | Assumption |
|---|---|---|
| 50 | ₦419 | Early pilot |
| 100 | ₦210 | Small cooperative |
| 200 | ₦105 | Conservative single-instance capacity |
| 500 | ₦42 | Upper bound before single-instance limits bind |

Because cost is dominated by a fixed monthly instance charge rather than by per-farm consumption, cost per farm falls almost linearly with the number of farms served. That is the structural finding of this strand, and it bears directly on the problem stated in Chapter One: the platform’s cost profile is the opposite of per-seat licensing.

These tenancy figures are reasoned, not measured. They assume the low write rate characteristic of manual data entry, and no concurrent-load, stress or soak testing was performed. The single-instance architecture and the platform’s unresolved query-efficiency issue on the ledger listing would bind well before hardware capacity did. The estimate also excludes staff time, a managed database service, observability, secret management, any data-residency requirement, messaging aggregator fees, and the farmer’s own data cost — the first of which would dominate total cost of ownership in any real deployment.


## 4.12 Usability Evaluation

Section 3.8.4 specifies a usability evaluation combining observed task performance, heuristic inspection against Nielsen’s ten heuristics, and the System Usability Scale, with a panel of three to five evaluators.

The instrument for this strand exists and the results do not. The project holds a complete facilitator run-sheet and a three-part evaluation pack — a task script, a heuristic checklist and the ten-item SUS questionnaire — and the frozen evidence base contains no completed instrument of any kind: no scored SUS forms, no filled heuristic checklists, no session notes, no participant records and no scans or photographs. This section is therefore drafted to receive real data and reports no figure that no retained instrument supports.


**Table 4.27: Usability evaluation — to be completed from retained instruments**


| Measure | Evaluator 1 | Evaluator 2 | Evaluator 3 | Panel |
|---|---|---|---|---|
| Tasks completed | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | — |
| Mean ease rating (1–5) | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | — |
| Session duration | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | — |
| Mean heuristic compliance (1–5) | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | — |
| SUS score (0–100) | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED RESULT HERE] | [INSERT VERIFIED MEAN HERE] |

Author’s note — what must exist before each cell is filled. SUS is scored by the standard procedure: odd-numbered items score (response − 1), even-numbered items score (5 − response), the ten adjusted scores are summed to a total out of 40, and the total is multiplied by 2.5 to give a score from 0 to 100. It is not a percentage. Report the mean with the individual scores beside it and label it indicative rather than statistically representative, since SUS is understood to be unstable below roughly a dozen respondents and the specified panel is three to five. Merge the issue logs, deduplicate, and keep the highest severity any evaluator assigned to each issue. Photograph or scan every completed sheet: these are the raw instruments an examiner may ask to see. State the panel at its true size — a panel smaller than the method specifies is a limitation, and a panel reported larger than it was is misconduct.

Two procedural points are recorded now because they belong to the method rather than to the results. First, browser site data must be cleared between evaluators. This is a validity control rather than a courtesy: the offline queue task deliberately creates queued entries, and the identity partitioning of that queue — verified in Section 4.3.3 — protects against cross-account flushing within the application, but a shared browser profile would still carry one evaluator’s session state into the next. Second, the heuristic checklist and the SUS questionnaire must be completed without the author present, because a self-report instrument administered under the author’s observation is systematically inflated.


**Table 4.28: Usability issue log — to be completed**


| # | Finding | Source | Severity | Disposition |
|---|---|---|---|---|
| 1 | [INSERT VERIFIED RESULT HERE] |  |  |  |

Because this strand is outstanding, Objective 4 is reported as partially met in Section 4.13, and no claim of a usability finding, a task-completion measurement, a SUS score or a comparison against paper-based practice appears anywhere in this thesis.


## 4.13 Results Against the Stated Objectives


**Table 4.29: Evidence and residual gap, by objective**


| Objective | What the evidence shows | Evidence class | Residual gap |
|---|---|---|---|
| 1. Identify and evaluate the socio-technical barriers hindering FMIS adoption in Nigeria | The barriers identified in Chapters One and Two — fragmentation, interoperability, complexity, connectivity and cost — were carried into the non-functional requirements of Section 3.3.2 and answered by specific implemented mechanisms: the paired write against fragmentation, the offline queue against connectivity, the fixed-cost hosting profile against cost | Implemented; numerical (Sections 4.10, 4.11) | The barriers are established from the literature and answered by design. No empirical barrier study with Nigerian farmers was conducted, and none is claimed. The feature-phone entry channel that addresses the rural device gap most directly is not implemented in the frozen build |
| 2. Convert operational and financial records into actionable decision-support metrics | Per-crop margin and ranking, unit cost on two bases, retrospective break-even yield, both break-even prices, sensitivity, operating-expense ratio and partial budget, all computed from a live ledger and each pinned by named tests; the decision-support and enterprise services at 100% coverage; two independent partial-budget implementations agreeing on eight hand-computed cases | Automatically verified; numerical (Sections 4.6, 4.7) | Demonstrated on one seeded farm, not on a season of real farm data. The forecast tier is trained on synthetic data and its reported quality is the recovery of a constructed relationship |
| 3. Design and integrate a secure data-sharing framework to build stakeholder trust | Signed-token authentication with hashed passwords; role-based authorization over a twelve-permission table with permission checked before scope, so a refusal never doubles as an existence oracle; every query farm-scoped with cross-farm reads returning 404, asserted across the enterprise routes and the bioprocess detail route; share tokens revocable, expiring, stored only as a hash, unusable as a bearer credential, and scrubbed from every log that records the request; failed logins throttled on two independent budgets; soft-immutable records with deletion refused and corrections made by linked contra entry | Automatically verified (Section 4.3.3) | The boundary is proven by tests and by live probing of the running stack, not by an independent security assessment, penetration test or threat model. Immutability is application-layer audit-trail discipline, not cryptographic tamper-evidence. There is no session revocation within a token’s lifetime, no refresh mechanism, no password reset and no second factor |
| 4. Evaluate usability, cost-effectiveness and operational viability under Nigerian constraints | Three of four strands executed: functional verification (422 backend cases at 96% statement coverage, 148 frontend tests, negative controls, and a migration chain executed against real PostgreSQL), performance benchmarking across two network conditions with cold and warm cache and driven-browser attribution, and a hosting-cost analysis anchored on a measured footprint. Operational viability is additionally evidenced by a production composition that was built, started, probed and backed up and restored | Numerical; manually inspected (Sections 4.3–4.5, 4.10, 4.11) | Partially met. The usability strand is outstanding (Section 4.12). Performance is simulated throttling against a local server on one machine, re-measured at the baseline but not measured in the field or under real network conditions; tenancy figures are reasoned, not load-tested; hosting cost is estimated, not incurred; and the deployment path has been exercised but never run on a departmental host or against a real domain |


## 4.14 Limitations of the Results

The following bound what the results above may be taken to show. They are stated here so that Chapter Five interprets them rather than rediscovering them.

Application defects. Two are known at the baseline, down from the five reported at the earlier freeze. A mistaken reversal cannot itself be rolled back, only compensated by an unlinked entry, which leaves an audit trail that is truthful but not self-explanatory. And a stale-revalidation window in the service worker is reasoned from the handler’s ordering and has never been reproduced — it is listed as a candidate, not a confirmed defect. Of the three no longer listed, one was never a defect: the per-crop reversal-netting report was incorrect and is withdrawn in Section 4.6.4. The other two were fixed. Monetary and quantity fields are now bounded and finite-checked at the schema edge, so a negative value, a value above a stated ceiling, an infinity and a not-a-number are each rejected with HTTP 422 rather than stored; this was confirmed against the running production stack. Equipment is now correctable through a partial, farm-scoped update route that stamps a correction timestamp only when a value actually changes, so a mistyped depreciation rate is no longer permanent.

Verification gaps. The yield model is not validated, as set out in Section 4.9. There are no component tests for the page and form layer, including the drying-curve chart. The API client and its error paths are approximately half covered. The local-database migration is proven against an in-memory IndexedDB implementation rather than a real browser, so browser-specific storage eviction, quota behaviour and vendor bugs are out of its reach. The concurrency tests run on SQLite; the deterministic cases force the recovery branch to execute on every run and the unstubbed two-thread case covers the genuine interleaving, but PostgreSQL’s behaviour under the same race is inferred from the equivalent constraint rather than measured. There is no end-to-end browser test of the offline-to-online transition, the service-worker lifecycle or the installation path. And there has been no independent security review and no load, stress or soak testing.

Data-state limitations. Every figure derives from one seeded farm. The live database holds eleven unidentified exploratory farms from development, deliberately left in place rather than deleted on an assumption, and two farms share the name “Demo Farm” — only farm 26 carries the seeded data, which is why no figure in this chapter is taken from a farm-list view. Machine hours are populated on three of eight mechanisation logs. The yield model is trained on synthetic data and every forecast inherits that.

Documentation gaps. Two citations remain outstanding in the implementation itself and must be resolved before submission: the cost-behaviour taxonomy needs an agricultural-economics or extension enterprise-budget source, and the safe-storage moisture ceilings need post-harvest handling guidance. Neither is attributed in this chapter, and no source is implied for either.

Validation gaps. There has been no field trial and no real farmer data. There has been no user evaluation, no task-completion measurement and no comparison against the paper-based practice this work is positioned against. The decision-support outputs are verified as arithmetic and are unvalidated as agronomic advice — whether following them improves an outcome is untested and, on synthetic training data, untestable here. And there is no evidence of a deployment serving real users. A production deployment path does exist and was exercised for this chapter: the production composition builds and starts, all services report healthy, the API is reachable through the reverse proxy with its path intact, both application containers run as unprivileged users, the database publishes no host port, and the backup and restore scripts were run end to end against a real PostgreSQL server. What has not been done is to run that configuration on a departmental host, obtain a certificate for a real domain, or serve a real user. Production observability — metrics, tracing and alerting — remains absent, and container logs to standard output are the whole of it.


## 4.15 Summary

The platform’s record-keeping core is verified by 422 backend test cases at 96% statement coverage — 418 passing locally, with the remaining four executing and passing when a PostgreSQL server is supplied — and 148 passing frontend tests across thirteen files, with a clean type check, a clean lint and a successful production build. The paired write, the soft-immutability constraint and the linked contra entry behave as designed; offline queue identity partitioning, logout cleanup and the local-database migration are each asserted by named tests; and same-farm idempotency holds sequentially and under a genuine two-thread race. That coverage is concentrated where it matters — every module that serves a request is fully or almost fully covered — and its distribution, together with a frontend statement coverage of 43.18% reflecting an untested page layer, is reported rather than averaged away. Three sets of negative-control runs establish that these tests are load-bearing.

The deterministic decision-support layer computes per-crop margin and ranking, unit cost on both a harvest and a marketable basis, retrospective break-even yield, both break-even prices, a sensitivity matrix, an operating-expense ratio and a partial budget from a live ledger, and withholds each figure where its inputs are insufficient rather than substituting a plausible default. Two independent implementations of the partial budget agree on eight hand-computed cases. The post-harvest module recovers known thin-layer parameters exactly, keeps water removed distinct from matter lost, and connects a moisture measurement to a price per marketable kilogram in a single computed chain — moving maize from ₦35.00 to ₦41.67 per kilogram, a 19% difference that is post-harvest mass reduction expressed in money.

Under simulated throttling, re-measured at the baseline, the service worker eliminates network transfer of the application shell entirely on a repeat visit and reduces first paint by a factor of eighty, though time to main content improves by a factor of about three and a half, and that is the figure a user experiences. Measured resource consumption places the two exercised containers under 205 MiB, supporting an estimated $15.40 ≈ ₦20,950 per month and a reasoned cost per farm falling to ₦105 at a two-hundred-farm tenancy — a cost structure that scales in the opposite direction to the per-seat licensing identified in Chapter One as excluding this user.

The security and tenancy boundary is exercised as well as asserted: three roles over a twelve-permission table refuse a worker the farm’s financial picture and refuse a manager the power to disclose it, share links expire and revoke to one indistinguishable verdict, the raw token reaches none of the three logs that record its request, failed logins are throttled on two budgets, the migration chain runs and rolls back against real PostgreSQL, and a backup was taken and restored with every row count matching and the paired-write invariant intact.

Against that, the yield forecast is an in-distribution result on synthetic data and is not evidence of field accuracy; the performance figures are simulated throttling against a local server and are not a field measurement; no deployment has served a real user and no certificate has been issued for a real domain; and the usability strand is outstanding, leaving Objective 4 partially met. Chapter Five interprets these results against the problem set out in Chapter One, states the platform’s limitations in full, and sets out what would be required to take it from a verified prototype to a deployed system.


# CHAPTER FIVE


# 5.0  DISCUSSION, CONCLUSION AND RECOMMENDATIONS


## 5.1 Introduction

Chapter Four reported what the AGRI-PROFIT platform does, under a classification that kept implemented functionality, automated test evidence, manually inspected evidence and numerical results apart from one another. This chapter interprets those results. It assesses what was achieved against each of the four objectives set out in Section 1.3, argues what the major findings mean rather than restating them, sets the work against the literature reviewed in Chapter Two, states the limitations that bound every claim made, draws out the implications for the farmer and for the stakeholders the platform is intended to serve, and sets out a prioritised programme of further work.

Two commitments carry over from Chapter Four and govern this chapter as well. Nothing is interpreted that was not first evidenced: where an interpretation rests on a result, the result is the one reported in Chapter Four and not a stronger version of it. And where the evidence does not reach a conclusion the reader might expect — most consequentially on whether the platform would help a real farmer — that is stated as a limit on the work rather than bridged by argument.


## 5.2 Achievement Against the Research Objectives


### 5.2.1 Objective 1 — the socio-technical barriers to FMIS adoption

The first objective was to identify and evaluate the socio-technical barriers — data fragmentation, interoperability constraints and user complexity — that hinder the adoption of farm management information systems in Nigeria.

The barriers were identified from the literature and carried into the design as binding requirements rather than as background. Four in particular became non-functional requirements in Section 3.3.2 and can now be traced to specific implemented mechanisms. Fragmentation between operational and financial records (Poppe, Vrolijk, & Bosloper, 2023) is answered structurally by the paired write: Chapter Four found 109 operational logs and 109 financial transactions in the live database, a one-to-one correspondence that is not a property of the sample but the invariant made visible. Intermittent connectivity (Mhlanga, 2023) is answered by the offline queue, whose identity partitioning, logout cleanup, three-strike retry and schema migration are each asserted by named tests, and by a service worker that was shown by driven browser to serve the whole application shell with the network disconnected. Cost as an exclusion mechanism is answered by an architecture whose cost profile is a fixed monthly instance charge rather than a per-seat licence, giving a reasoned ₦105 per farm per month at a two-hundred-farm tenancy. User complexity is answered by the deliberate reduction of raw ledger data to a small number of ranked, satisficing figures, in the sense of the bounded rationality argument of Section 2.2.2.

The objective is met as identification and design response, and not as empirical evaluation. No study of Nigerian farmers was conducted; the barriers are established from the literature reviewed in Chapter Two, not from primary data gathered in this work. That distinction matters most for the barrier that is quantitatively largest. The rural smartphone gap reported at 68% (Jaiyeola, 2023) is the headline socio-technical constraint in Chapter One, and the mechanism designed to address it — the feature-phone entry channel of Section 3.6.8 — is not present in the frozen build. The platform therefore addresses the barriers facing farmers who already have a smartphone and an intermittent connection, which is the 32% rather than the 68%. That is a real limit on the reach of the contribution and it is stated plainly rather than folded into a claim about inclusion.


### 5.2.2 Objective 2 — converting records into decision-support metrics

The second objective was to formulate and realise an architecture translating static operational and financial records into actionable decision-support metrics.

This is the objective on which the evidence is strongest. The deterministic tier computes, from the farm’s own ledger and with no model and no external data, per-crop gross margin and ranking, unit cost of production on both a harvest and a marketable basis, retrospective break-even yield, cost structure by behaviour with an explicit classification-coverage figure, a derived depreciation overlay and its proportional allocation, two break-even prices, a five-row yield sensitivity matrix, an operating-expense ratio, a partial budget and an Olympic-average yield baseline. The decision-support service and the enterprise-economics service both stand at 100% statement coverage; every behaviour on which the design argument depends is asserted by a named test; and the partial budget — implemented twice, so that it survives offline — was shown to agree with an independent hand-computed fixture in both implementations across eight cases including a sign trap, an exact-zero trap and a transposition trap.

One qualification bounds the achievement, and two that earlier drafts recorded are withdrawn. The qualification that stands is that the figures are demonstrated on one seeded farm, not over a season of real records; the arithmetic is verified, the agronomic relevance is not. Withdrawn are the claims that the per-crop breakdown fails to net reversals — it does net them, as Section 4.6.4 establishes by execution at both the baseline and the earlier freeze — and that the Olympic-average baseline has no interface surface, which ceased to be true when the panel was mounted in the enterprise-economics view. Both were carried in good faith from an earlier audit and neither survives contact with the running system, which is itself a lesson worth stating rather than burying. The reversal-netting entry was not a defect that was later fixed: the capability was introduced nine days before the audit that reported it missing, the audit's own summary table listed it among the verified behaviours, and the two halves of that document contradicted each other. The finding was produced by reading source code and never executing it. A defect established that way is a hypothesis; it becomes a finding when it is reproduced, and this one could not be. The correction is recorded here — rather than the passage simply being deleted — because the erroneous text survives in a dated evidence document that a reader may encounter, and an unexplained disappearance is worse than a stated retraction.


### 5.2.3 Objective 3 — a secure data-sharing framework for stakeholder trust

The third objective was to design and integrate a secure data-sharing framework standardising yield and profit-and-loss reporting, to build operational trust among agricultural banks, investors and policymakers.

The mechanism is built and its boundary properties are verified, by test and by probing the running system. Authentication issues a signed token over hashed credentials; every read and write path is scoped to the authenticated user’s farm, with a cross-farm read returning HTTP 404 rather than an empty result — asserted across the enterprise-economics routes and the bioprocess detail route; and the ledger refuses deletion outright, requiring a category-preserving contra entry linked to its original, with double reversal and cross-farm tampering both rejected.

Two additions since the earlier evaluation bear directly on this objective. The first is that access within a farm is now differentiated rather than uniform. Three roles sit over a twelve-permission table, and endpoints ask for a permission rather than for a role, so a worker may record field activity and read the farm’s own log but is refused its financial picture, a manager has full operational and financial control but cannot disclose the farm to an outsider, and only an owner may mint a link or admit a member. Permission is checked before scope, deliberately, so that a caller who may not perform an operation at all is told so without learning whether the record they named exists — a refusal that would otherwise function as an existence oracle. This matters for Objective 3 because a data-sharing framework whose internal boundary is all-or-nothing is not a framework a farm can actually operate: the person entering records in a field and the person who decides which bank sees the accounts are not the same person.

The second is that the share link is now a bounded capability rather than a permanent one. Every minted link expires, links are revocable, only a hash of the token is stored so a database compromise yields no usable link, and unknown, revoked and expired tokens all resolve to one identical verdict so that the endpoint cannot be used to confirm that a candidate token was ever valid. The token cannot be exchanged for a session and reaches no write path. And because the token is the entire credential and travels in the URL, it is scrubbed from every log that records the request — the proxy writes a redaction, the application and its server write a non-reversible fingerprint that still allows two requests carrying the same link to be correlated. That last property was verified by minting a live link, exercising it, and then searching every container log for the raw value.

That last property is the substantive answer to the question an examiner or a lender would actually ask — how does a bank know the farmer did not simply edit the numbers? The answer is that the numbers cannot be edited, only offset by a further recorded entry that remains visible beside the original. It must be stated with precision, however, that this is audit-trail discipline enforced at the application layer, not cryptographic tamper-evidence. There is no hash chaining, no signing and no append-only log; a party with database access is not constrained by it. Chapter Two reviewed distributed-ledger governance as the mechanism that would provide that stronger guarantee (Huang, 2020), and Chapter One correctly scoped it as a future direction. The present work delivers the weaker but immediately deployable version, and the difference between the two is not rhetorical.

Two residual gaps qualify the objective, and one previously recorded gap is withdrawn. Every property above is implemented and verified — by named tests and by live probing of the running production stack — and none is validated in practice, because no adversary who was not the author has ever tried them. The boundary is proven by tests and by live probing, not by an independent security assessment; no penetration test, review or threat model was conducted, and this is the single most important thing this thesis does not know about its own security posture. Identity management is also incomplete in ways that matter to a real deployment: a leaked token stays valid until it expires, there is no revocation, no refresh, no password reset and no second factor. Withdrawn is the claim that the investor report inherits a per-crop reversal defect. It does not, because there is no such defect; the report was fetched with a live share token after a reversal and returned the netted figures.


### 5.2.4 Objective 4 — usability, cost-effectiveness and operational viability

The fourth objective required empirical evaluation of usability, cost-effectiveness and operational viability under Nigerian infrastructural constraints. It is partially met.

Three of the four specified strands were executed. Functional verification returned 422 backend test cases at 96% statement coverage and 148 passing frontend tests, strengthened by three sets of negative-control runs establishing that those tests fail when the behaviour they guard is broken, and by a migration chain executed against a real PostgreSQL server rather than inferred from the models. Operational viability, which the objective names and which the earlier evaluation could only address by inference, now has direct evidence: the production composition was built and started, every service reported healthy, the API proved reachable through the reverse proxy with its path intact, both application containers were confirmed to run unprivileged with the database unreachable from the host, and the backup and restore scripts were run end to end with every restored row count matching its source and the paired-write invariant intact. Performance benchmarking, re-run at the baseline commit so that it characterises the submitted build, established that the application is bandwidth-bound below roughly 1 Mbps and that a repeat visit transfers none of the application shell, with service-worker attribution proven by driven browser rather than inferred. The hosting-cost analysis, anchored on a measured footprint of 178.9–202.8 MiB across the two exercised containers, produced an estimated $15.40 — approximately ₦20,950 — per month.

The usability strand is outstanding. The instrument exists in full and no completed instrument does, so Chapter Four reports no usability figure. This is the single largest gap in the evaluation, and it is consequential rather than cosmetic: the platform’s central claim is that it reduces cognitive load for a user operating under bounded rationality, and that claim is precisely the one no strand of the completed evaluation touches. A platform that computes correct figures which a user cannot find, or cannot interpret when found, has not met Objective 2 in the sense that matters to a farmer, and nothing in the executed evaluation would detect that condition.

Each executed strand also carries its own limit. The performance figures were re-measured at the baseline, so they now characterise the submitted build; what they remain is simulated throttling against a local server on a single machine, which is a model of a degraded network rather than a measurement of one, and no figure in that strand was obtained on a real device over a real Nigerian connection. The operational evidence establishes that the deployment path works, not that a deployment exists: no departmental host runs this software, and no certificate has been issued for a real domain. The cost figure is an estimate, not an incurred charge; the per-farm tenancy figures are reasoned and no load testing was performed. And functional verification, however extensive, demonstrates only that the behaviours somebody thought to test behave as specified.


## 5.3 Interpretation of the Major Findings


### 5.3.1 The paired write is the structural contribution, and it is visible in the data

The literature identifies the separation of farm financial accounts from operational records as a historical accident with continuing costs: duplicated entry, administrative fatigue, and the impossibility of correlating agronomic inputs with financial outcome (Poppe et al., 2023; Fountas et al., 2015). Most responses to it are integrative — two systems and a synchronisation path between them. AGRI-PROFIT’s response is different in kind: there is only one write, and it posts both records in a single commit, so the two cannot drift because they were never separate.

The finding that makes this more than an assertion is arithmetic. At the baseline the database held exactly as many financial transactions as operational logs. There is no reconciliation step in the platform because there is nothing to reconcile, and the correlation the literature describes as unavailable is not computed but inherent: every cost already carries the activity that incurred it and the crop it was incurred against.

The cost of this design is equally real and is stated in Chapter Three: the ledger is single-entry, so it is an analytical instrument rather than a bookkeeping system in the accounting sense. That is the right trade for the target user, whose alternative is not double-entry software but paper, and it should not be presented as anything else.


### 5.3.2 The drying-to-price chain is the engineering contribution

The result most specific to agricultural and bioresources engineering is the computed chain running from a moisture measurement to a price. A maize harvest weighed in at 100 kg and 25% moisture, dried over ten hours to 13%, weighed out at 84 kg, and the unit cost of production moved from ₦35.00 to ₦41.67 per kilogram. The 19% difference is post-harvest mass reduction expressed in money, and a farmer pricing on the wet-basis figure would under-recover ₦6.67 on every kilogram sold.

Three properties make this a result rather than an illustration. First, the chain is computed end to end without manual intervention: the drying run is an operational log like any other, so it posts its cost through the same paired write, and its computed marketable output becomes the denominator of the unit-cost figure. Second, the denominator is the mass actually weighed out rather than the mass the dry-matter balance predicts — 84 kg against 86.21 kg — which is the conservative choice and charges the pricing decision only with grain that reached the store. Third, the distinction the module is most likely to get wrong is guarded by a test that fails if it is ever collapsed: water removed is a water balance, not a mass difference, and conflating them would make process loss and drying performance the same number.

This is the answer to the question of what makes the platform an agricultural engineering artefact rather than a bookkeeping application. The thin-layer models themselves are long established and are not the contribution; their coupling to the financial record is.


### 5.3.3 Withholding a figure is a design principle, and the null cases are its evidence

A recurring pattern across Chapter Four is that the platform refuses to answer where the inputs do not support an answer. Break-even yield returns null in four distinct cases. Unit cost on a marketable basis is withheld where no drying run exists rather than defaulting to the harvest mass. Mixed harvest units return a null with a stated reason rather than an arithmetically invalid sum. An unrecognised crop returns no safe-storage threshold rather than an unsafe verdict. A zero depreciation rate counts as unrated rather than as a zero charge. An Olympic average over fewer than three seasons is refused, and the season count is reported in every branch so that a null is never read without the count explaining it. The untrained model reports itself as untrained rather than as R² 0.0000.

This is more than defensive coding. Under bounded rationality (Section 2.2.2) the cost of a wrong figure is higher than the cost of a missing one, because a farmer who receives a plausible number has no way to discover it was unfounded, whereas a farmer who receives a stated absence knows exactly what to do about it — record the missing data. The design decision that best illustrates this is the fourth null case on break-even yield: a crop with no attributed cost has an arithmetically valid break-even of zero kilograms, and reporting it would communicate a false completeness to a user whose real situation is that they have not recorded their costs.

The same discipline is what makes the classification-coverage figure worth reporting. At farm level 88.25% of recorded cost carries a cost subtype, and rather than distributing the remaining 11.75% into a plausible bucket the platform reports it as unclassified, so a reader can see how much of the analysis rests on classified data.


### 5.3.4 The service worker is the operative form of the low-bandwidth claim — and a liability

The bundle-size version of the low-bandwidth argument is the weaker one. A 139,245-byte payload takes 2.78 s to transfer at 400 Kbps, which is why cold performance falls from a score of 99 at 1.6 Mbps to 65 at 0.4 Mbps; but Nigerian median mobile throughput is far above that threshold, so on a national average the payload is not the binding constraint. Route-level code-splitting removed 43% of that payload between the two measurement dates and moved cold first paint by about a quarter, which is worth having and does not change the shape of the argument.

The stronger version, and the one the measurements support, is that the application remains usable when the network is intermittent or absent. A returning user reaches first paint in 71 ms and main content in 1.6 s on a link that would otherwise take 5.7 s, and reaches the application at all with no connection whatsoever. That is a different claim from “the bundle is small”, and it maps onto the actual rural condition described by Mhlanga (2023) — unreliable connectivity rather than uniformly slow connectivity.

The finding must be held together with its opposite, which Chapter Four also reported. A caching layer that improves first paint by a factor of eighty is a layer that can make the application misrepresent its own state: a cached shell can make a stopped backend look like a running one, and a cached read can serve pre-reversal figures after a correction. The platform’s response is an explicit purge on every farm-scoped write, and the negative-control run of Section 4.4 is what establishes that the purge does real work — with it neutered, all five tests fail on the value a user would see. A stale-revalidation window nevertheless remains reasoned but unreproduced. Both halves of that sentence belong in an honest evaluation.


### 5.3.5 The cost structure is the finding that scales

The cost analysis produced one result of structural rather than arithmetic interest. Because the platform’s cost is dominated by a fixed monthly instance charge and not by per-farm consumption — storage at roughly 1 KB per paired record and a bundle that crosses the network once per device being immaterial at any pilot scale — cost per farm falls almost linearly with the number of farms served: ₦419 at fifty farms, ₦210 at one hundred, ₦105 at two hundred.

That is the exact structural opposite of the per-seat licensing which Chapter One identifies as excluding smallholders from existing systems. Under per-seat pricing the marginal farmer costs the same as the first; here the marginal farmer is nearly free. The implication is that the natural deployment unit for this platform is a cooperative, an aggregator or an extension service rather than an individual farm — which also happens to be the unit at which the advisory support that conditions adoption (Carrer et al., 2017) is already organised.

The finding is bounded honestly in Chapter Four and the bound should be repeated here: the tenancy figures are reasoned, not measured. No concurrent-load testing was performed, and the single-instance architecture together with an unresolved query-efficiency issue on the ledger listing would bind well before hardware capacity did.


### 5.3.6 The negative controls are the reason the verification figures should be believed

Test counts and coverage percentages are the most commonly quoted and least informative figures in a software evaluation. A suite can be large, green and worthless. The three sets of mutation runs reported in Section 4.4 are what distinguishes this evaluation from one that reports a test count and a coverage percentage and asks to be trusted: with the cache purge neutered, five tests fail — each on a value or on rendered text, none on a call count; with the local-database upgrade hook broken, four of seven fail; and the shared parity fixture cannot go missing, malformed or silently shorter without failing both suites at collection time.

The most instructive detail is the discriminating case in the first experiment. After a reversal, a working purge with correct contra accounting yields ₦2,000, a surviving cache yields ₦5,500, and a lost record yields ₦0. Because the three outcomes are distinguishable, the test can only pass for the right reason. That is what a load-bearing test looks like, and it is the property a coverage percentage cannot express.


## 5.4 Comparison with the Literature

The comparison below is restricted to works already reviewed in Chapter Two. No new source is introduced, and where the platform diverges from what the literature prescribes the divergence is argued rather than concealed.

On fragmentation. Poppe et al. (2023) describe farm financial accounts and farm-management records as having originated in the same note-taking practice and diverged as they computerised. Chapter Four’s finding of one financial transaction per operational log is the platform’s answer to that divergence, and it differs from the integrative approach implied by most FMIS designs (Fountas et al., 2015) in kind rather than in degree: the records are not synchronised because they are not separate.

On interoperability. Tummers, Kassahun, and Tekinerdogan (2019) identify the absence of standardised data-exchange protocols as a primary technical roadblock, and this work does not solve it. AGRI-PROFIT exports a standardised profit-and-loss statement as CSV and exposes a tokenised read-only report, which addresses the sharing problem for a human recipient; it implements no agricultural data-exchange standard and would not interoperate with another FMIS. The contribution here is to the fragmentation problem, not the interoperability one, and conflating the two would overstate it.

On adoption conditioning. Carrer, de Souza Filho, and Batalha (2017) find that FMIS uptake is conditioned by education, advisory access and rural credit. Two of those three are addressed structurally rather than incidentally by findings reported in Chapter Four. The tokenised stakeholder report exists to make a farm’s records legible to a lender, which speaks to the credit channel; and the per-instance cost structure makes cooperative or extension-level deployment economically natural, which speaks to the advisory channel. The third — education — is precisely the channel a usability evaluation would test, and precisely the strand that is outstanding.

On connectivity and the device gap. Mhlanga (2023) argues that rural deployment must assume degraded infrastructure and that edge processing mitigates the latency and bandwidth costs of central cloud computing. AGRI-PROFIT is a partial instance of that argument and should be described as such: the write path and the application shell are genuinely local — a record can be captured, queued and displayed with no connection — while all computation, including the deterministic decision-support tier, executes on the server. The evidence for the local half is the driven-browser probe and the offline queue tests; the server-side half follows from the client–server architecture of Section 3.4.1. Any characterisation of the deterministic tier as running on-device would be incorrect. Jaiyeola (2023) reports 68% of rural Nigerians without smartphones, and as Section 5.2.1 concedes, the channel that would reach them is not built.

On the modelling ladder. van Klompenburg, Kassahun, and Catal (2020) find tree-based ensembles to perform strongly on tabular agricultural data at far lower computational cost than deep networks, and Olisah, Smith, Smith, Lawrence, and Ojukwu (2024) demonstrate that a deliberately inexpensive, mobile-deployable model is viable for smallholder decision support and that pre-processing is decisive for prediction quality in Sub-Saharan contexts. The implemented forecast tier follows the first finding — a 200-estimator Random Forest — and deliberately does not yet exercise the second, because it is trained on clean synthetic data for which the pre-processing pipeline Olisah et al. describe has nothing to do. That is the correct reading of the R² of 0.9762 reported in Chapter Four: it is the recovery of a constructed relationship, and the moment the platform trains on real farm records the pre-processing problem those authors identify becomes the central one. Chapter Two also notes that RMSE is a standard complementary measure and that Olisah et al. propose combining it with MAE; all three are reported in Section 4.9, at R² 0.976204, MAE 0.241393 and RMSE 0.488334 t/ha, and all three are reproducible to six decimal places from the recorded seed.

On trust and the ledger. Huang (2020) presents distributed-ledger technology as the mechanism by which self-reported farm data becomes credible to banks and insurers, and Gebresenbet et al. (2023) frame the underlying problem as the absence of verifiable data. AGRI-PROFIT implements the weaker, immediately deployable mechanism reviewed in Section 2.5 — authenticated, access-controlled, tokenised standardised reporting over an audit-trailed ledger. The comparison should be stated exactly: what the platform provides is a record that cannot be silently edited through the application and a report a farmer can grant and revoke; what it does not provide is cryptographic verifiability against a party with database access. The distributed-ledger layer remains a future extension, as Chapter One scoped it.

On usability method. Nielsen and Molich (1990), Nielsen (1994) and Brooke (1996) supply the instruments specified in Section 3.8.4, and the choice of an expert heuristic panel with a standardised questionnaire remains the appropriate method where a large end-user sample is unavailable. This work reports no result against those instruments, and the comparison cannot be made.

Note for submission: several works cited in Chapter Two, including Poppe et al. (2023), Tummers et al. (2019), Jaiyeola (2023) and Gebresenbet et al. (2023), are cited in text there and above but do not yet carry full entries in the reference list. Those entries must be completed before submission.


## 5.5 Limitations

The limitations below are those that most constrain what this work may claim. They restate, in interpretive form, the results limitations of Section 4.14.

Scope and deployment. The platform has not been deployed to serve real users, and no certificate has been issued for a real departmental domain. What exists, and was exercised for this evaluation, is a production deployment path: a production composition that builds and starts with every service healthy, an nginx-served frontend proxying the API with its path intact, schema migration applied on startup, liveness and readiness probes that answer from the application rather than from the page shell, unprivileged application containers, a database that publishes no host port, environment guards that refuse to start on a default signing key, an optional automatic-TLS edge, and backup and restore scripts that were run end to end against a real PostgreSQL server with every restored row count matching its source. The distinction that matters is between a deployment path that has been demonstrated and a deployment that has been performed; this work has the first and not the second. Production observability — metrics, tracing and alerting — is genuinely absent. The hosting cost is therefore an estimate anchored on a measured footprint, not an incurred charge, and the configuration priced is one in which every restart costs 8.6 s of unavailability. A configuration meeting ordinary production expectations for availability would cost several times the quoted figure, and the distance between the two is part of the honest account of what has been built.

Data. Every figure in Chapter Four derives from a single seeded demonstration farm. There has been no field trial and no real farmer data. The seeded records were constructed to exercise the platform’s analytical paths, so they are not a sample of Nigerian farm practice, and no inference about typical costs, margins or yields should be drawn from them.

The forecast tier. The yield model is trained on synthetic data and is not validated against any real observation. Its reported quality measures the recovery of a constructed relationship. It is, however, reproducible: the pipeline is seed-deterministic and its three metrics were re-derived to six decimal places at the baseline, so what is unproven is the model’s relevance, not the integrity of the procedure that produced it. No claim of field-predictive accuracy is made, and the model should not be relied upon for a planting or input decision in its present state.

The decision-support outputs as advice. The arithmetic of the deterministic tier is verified to an unusual degree. Whether acting on it improves an outcome is untested, and on synthetic training data and one seeded farm it is untestable here. The platform computes what a farm’s records imply; it does not know whether what they imply is good agronomy.

Correctness defects. Two are known and were reported in Section 4.14: a mistaken reversal cannot itself be rolled back, and a stale-revalidation window in the service worker is reasoned but unreproduced. Neither touches the correctness of a figure the platform reports. Three defects carried in earlier drafts are gone: the per-crop reversal-netting report was incorrect and is withdrawn, and unbounded monetary fields and the missing equipment edit path were both fixed. The residual pair is materially less serious than the set this thesis previously carried, and the reason is worth stating plainly — the defects were found by the project’s own audit and closed before submission, rather than being discovered by an examiner.

Verification boundaries. The page and form layer has no component tests, including the drying-curve chart, whose visual correctness rests on inspection alone. The local-database migration is proven against an in-memory IndexedDB implementation rather than a browser. The concurrency behaviour is measured on SQLite and inferred for PostgreSQL. There is no end-to-end browser test, no independent security review, and no load, stress or soak testing.

Evaluation. The usability strand is outstanding, so there is no user evaluation, no task-completion measurement, no SUS score and no comparison against the paper-based practice this work is positioned against. Objective 4 is partially met in consequence, and the claim the platform makes about cognitive load is the claim it has least evidence for.


## 5.6 Implications

For the smallholder and medium-scale farmer. The implication of the drying-to- price chain is specific and actionable: a farmer pricing against harvest mass is pricing against a mass that no longer exists. For the demonstration record the error is ₦6.67 on every kilogram, or 19%, and it is invisible without the moisture and mass figures the platform makes it trivial to record. More generally, the platform’s outputs are of a kind a paper logbook cannot produce at all — not because the arithmetic is difficult, but because it requires operational and financial records to be joined at the point of entry, which paper does not do.

For lenders, investors and cooperatives. A read-only, revocable, standardised report drawn from a ledger that refuses deletion is a materially different artefact from a farmer’s own summary of their year. It is not cryptographically verifiable and should not be presented as such, but it changes the question a lender asks from “do I believe this figure?” to “do I believe this platform’s boundary?” — and the latter is at least assessable. The cost structure compounds this: at ₦105 per farm per month at a two-hundred-farm tenancy, the natural adopter is an organisation serving many farms, which is also the party a lender would rather deal with.

For agricultural and bioresources engineering practice. The work is an instance of a general pattern worth naming: post-harvest process parameters that engineers already measure — moisture content, mass in and out, drying time — become financially decision-relevant the moment they are joined to a cost record. The engineering content of this platform is not the thin-layer models but that junction. The same pattern would extend to any process with a measurable yield loss.

For low-resource FMIS design generally. Three design positions in this work appear to generalise. Pairing the operational and financial write removes a class of reconciliation problem rather than managing it. Withholding a figure whose inputs are insufficient is safer than defaulting it, and costs little to implement. And a service-worker precache converts a bandwidth problem into a first-visit problem, which is a much smaller problem — provided every write path explicitly invalidates the read cache, because the same layer will otherwise make the application lie about its own state.


## 5.7 Recommendations and Future Work

The work below is prioritised in three tiers by what each is needed for.


### 5.7.1 Tier A — required before any deployment or submission

- (a)  Resolve the two outstanding citations in the implementation — an agricultural-economics or extension enterprise-budget source for the cost-behaviour taxonomy, and post-harvest handling guidance for the safe-storage moisture ceilings.
- (b)  Reconcile the wording of “tamper-evident” to “audit-trailed” wherever it appears, and reconcile the front matter and Chapters One to Three to the figures reported in Chapter Four. Chapter Three currently states that the evaluation "actually undertaken" comprises four strands while the abstract correctly states that the usability strand was not conducted; the two must be made to agree.
- (c)  Complete the reference entries for the works cited in Chapter Two without full entries.
- (d)  ~~Re-run the frontend performance audit against the baseline build~~ — **done.** The audit was re-run on 29 August 2026 against commit `78a68c2` and Section 4.10 now reports that set; the 17 August set at `c16924e` is retained, dated and reconciled against it in Section 4.10.3. What remains outstanding is not a re-run but a different measurement: nothing in the strand was obtained on a real device over a real network.

### 5.7.2 Tier B — required to close the evidence gaps

- (a)  Run the usability panel. Three to five evaluators, the existing instrument, the instruments retained as scans. This closes Objective 4 and is the highest-value remaining piece of evidence in the entire project.
- (b)  Add component tests for the page and form layer, beginning with the drying-curve chart and the decision-support panels, which currently carry user-visible figures with no automated assertion.
- (c)  Add an end-to-end browser test of the offline-to-online transition, the service-worker lifecycle and the installation path, and use it to settle the stale-revalidation window that is presently reasoned but unreproduced.
- (d)  Measure the concurrency behaviour on PostgreSQL rather than inferring it from the equivalent constraint.
- (e)  Measure performance on real devices over real Nigerian mobile connections. The simulated-throttling figures now characterise the submitted build, but they remain a model: a Lantern-modelled 0.4 Mbps link is not an observation of one.
- (f)  Commission an independent security review and conduct load testing sufficient to replace the reasoned tenancy figures with measured ones.

### 5.7.3 Tier C — to extend the contribution

- (a)  Retrain the forecast tier on accumulated real records once farms have a season of history, at which point the pre-processing pipeline described by Olisah et al. (2024) — imputation, unit harmonisation, interval reconciliation and outlier handling — becomes the substantive work rather than a design principle.
- (b)  Report the prediction interval prominently in the interface. A confidence band derived from the spread of the forest’s trees is a better answer to “why should a farmer trust a forecast?” than an in-distribution R², because it communicates uncertainty rather than accuracy. The band is already computed and returned; what is missing is its prominence at the point of use.
- (c)  Report a Page fit over a drying series captured through the interface rather than seeded, now that the interface captures one, so that the fitted figures in Section 4.8 come from a user-entered run.
- (e)  Consume the captured equipment identifier and machine hours to produce cost-per-hour and utilisation figures, which the data model already stores and no service currently reads.
- (f)  Implement the feature-phone entry channel against a live carrier gateway, which is the mechanism that would extend the platform’s reach beyond the 32% of rural Nigerians who own a smartphone.
- (g)  Execute the field evaluation designed in Section 3.8.5 — a representative sample of smallholder and medium-scale farmers, using the platform for their own records over a defined period, with task-completion rates, SUS across a larger sample, qualitative feedback, and real device and data-usage measurement.

## 5.8 Conclusion

This study set out to design, develop and evaluate AGRI-PROFIT, an offline-first farm record and decision-support platform for Nigerian smallholder and medium-scale enterprises, in response to a documented separation between operational and financial farm records and to the infrastructural and economic conditions that make existing farm management systems inaccessible to that user.

A working platform was built and evaluated at an identified commit. Its central design decision — that every operational record posts its financial transaction in the same commit, correctable only by a linked contra entry — was verified by 422 backend test cases at 96% statement coverage and 148 passing frontend tests, and is visible in the live database as an exact one-to-one correspondence between operational logs and financial transactions, an invariant that also survived a backup and restore. On that record the platform computes a deterministic decision-support layer that was shown to produce per-crop margin and ranking, unit cost on two bases, retrospective break-even yield, cost structure with an explicit coverage figure, a derived depreciation overlay, two break-even prices, a sensitivity matrix, an operating-expense ratio and a partial budget — and, as consistently, to withhold each figure where its inputs do not support it. A post-harvest drying module recovers known thin-layer parameters exactly, keeps water removed distinct from matter lost, and carries a moisture measurement through to a price per marketable kilogram, moving a maize enterprise from ₦35.00 to ₦41.67 per kilogram. Three sets of negative-control runs establish that the tests behind these claims fail when the behaviour they guard is broken.

Measured against constrained conditions at the baseline commit, the application transfers none of its shell on a repeat visit and renders with no connection at all, reaching first paint eighty times faster warm than cold on a 0.4 Mbps link, though main content improves by a factor of about three and a half and that is the figure a user experiences. Its two exercised containers consume under 205 MiB, supporting an estimated ₦20,950 a month and a reasoned ₦105 per farm per month at a two-hundred-farm tenancy — a cost structure that is the opposite of the per-seat licensing identified in Chapter One as excluding this user.

What the work does not establish is equally definite. There has been no field trial, no real farmer data and no user evaluation; the usability strand of the specified evaluation is outstanding and Objective 4 is therefore partially met. The forecast tier is trained on synthetic data and its reported accuracy is the recovery of a constructed relationship, not a claim about Nigerian yields. The data boundary is proven by tests and by probing a running stack, not by an independent security assessment, and the ledger is audit-trailed rather than cryptographically tamper-evident. The performance figures are modelled throttling against a local server rather than a field measurement. And while the platform now has a production deployment path that has been built, started, probed, backed up and restored, it has never been deployed to serve a real user, on a real domain, on a departmental host — which is a different and smaller claim than the one an earlier draft of this chapter made, and it is the one the evidence supports.

The contribution, stated at its true size, is a verified prototype: an architecture in which the operational and financial record cannot drift apart, a decision-support layer that is arithmetically correct and honest about the limits of its inputs, and a demonstration that post-harvest process measurements can be carried through to a pricing decision automatically. Whether that architecture changes what a Nigerian farmer earns is the question this work makes answerable and does not answer. The route to answering it is set out in Section 5.7, and it begins with putting the platform in front of its users.


---

## Author's note — outstanding blocker outside this chapter's scope

**This note is not thesis prose. It records one unresolved inconsistency that
lives in Chapters One to Three, which were deliberately not edited during the
Chapter 4–5 evidence rebuild, and which must be resolved before submission.**

The usability strand is reported as not conducted throughout Chapters Four and
Five, and no SUS score, task-completion figure or heuristic result appears
anywhere in them. That is correct and consistent with the evidence. Three things
must be checked in the front matter and in Chapters One to Three:

1. **The Abstract carries no SUS score.** It should stay that way. Confirm that
   no revision reintroduces one.
2. **The old 60.0 SUS figure does not appear in the current Chapter 1–3 text.**
   Confirm this holds in the file actually submitted, including any exported
   `.docx` or `.pdf` under `docs/print/`, since those are separate artefacts.
3. **Section 3.8 still needs reconciliation.** If §3.8 states that the
   evaluation undertaken comprised four strands including usability, while the
   Abstract and Chapter Four state that the usability strand was not conducted,
   the two contradict each other. The fix belongs in §3.8 — describe the
   usability strand as *specified* and report in Chapter Four that it was not
   *executed* — and not in Chapter Four, which reports what happened.

This is a Chapter 1–3 correction. It is recorded here so it is not lost, and it
must not be resolved by weakening anything in Chapters Four or Five.
