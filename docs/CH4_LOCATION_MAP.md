# Chapter Four — repository location map

Locations verified 2026-08-26 against the working tree at `acb97e4`, which is
source-identical to tag `thesis-evidence-freeze-2026-08-25`. **Line references
throughout are to that tagged state.**

> **Baseline note, 2026-08-29.** The thesis baseline is now
> `78a68c292205acdcac1a52f977fbea31b6e8495e` on `main`, and the authoritative
> evidence document is `docs/EVIDENCE_FREEZE_2026-08-29.md`. The production-
> hardening merge added application code — authorization, rate limiting,
> credential scrubbing, share-token expiry, equipment correction, input bounds —
> and nine backend test modules, so **line numbers in this map may have moved and
> the test-identity figures in §D are superseded** (190 collected → 422; 93% →
> 96%; 89 frontend → 148). The file paths and the claim boundaries remain
> serviceable, and each entry below that the merge changed carries its own
> correction inline. Quote figures from the 29 August freeze, never from here.

Purpose: for every system feature Chapter Four describes, the exact file that
implements it, the exact artefact that proves it, and the boundary of the claim.

This file does not restate the freeze report. It records (a) locations the freeze
does not give, and (b) four places where existing planning material is stale or
imprecise and would put a wrong statement into Chapter Four. Those are in §A.

---

## A. Corrections to existing planning material — read first

### A1. The Chapter Four DSS captures are a THREE-crop snapshot. The demo farm now has FIVE crops.

`docs/ch4-data/dss_per_crop.json` and `dss_break_even.json` were captured at
commit `ab7a0da`. Commit `6f926a5` — `feat(seed): add cowpea, sorghum and two
assets to the demo farm`, an ancestor of the freeze tag — added two more crops
and two equipment records to `backend/scripts/seed_bioprocess_demo.py`.

Crop rows now in the seed script (verified by counting `"crop":` keys):
cassava 6, cowpea 11, maize 2, sorghum 4, tomato 5 = **28 logs**, which is
exactly the 28 logs freeze §5 attributes to farm 26.

Consequence:

| Value in the JSON captures | Status |
| --- | --- |
| The `crops` array (3 entries: cassava, maize, tomato) | **STALE — incomplete.** Farm 26 also holds cowpea and sorghum. |
| The `overall` block (revenue ₦223,600 / expenses ₦210,800 / gross margin ₦12,800) | **STALE.** Farm-wide totals now include cowpea and sorghum. Do not quote. |
| Any statement of crop ranking, or "the three seeded crops" | **STALE.** |
| The **maize row** (₦45,000 / ₦3,500 / GM ₦41,500 / 100 kg / 84 kg marketable / ₦35.00 harvested / ₦41.666666666666664 marketable / break-even yield 7.777777777777778 kg) | **VALID.** `6f926a5`'s commit message records these as verified bit-identical before and after, and its diff touches no maize row. |
| The cassava and tomato rows | **VALID as per-crop rows** (untouched by `6f926a5`), but they are no longer the whole table. |

`6f926a5` also records one figure that **did** move: maize
`break_even_price_TOTAL` went from `41.666666666666664` to
`42.36767852721509`, because the farm now owns a depreciating asset and maize
takes ₦58.88 of the farm-wide overlay. `break_even_price_CASH` is unchanged at
`41.666666666666664`. Neither figure is in the JSON captures.

**Action for Chapter Four:** either re-capture `/dss/decision-support` against
farm 26 at the tagged state, or restrict every quotation to the per-crop maize,
cassava and tomato rows and quote no farm-wide total and no ranking.

### A2. `docs/ch4-data/screenshot-runsheet.md` is written against the same stale three-crop state.

Line 12 asserts the endpoint "matches `dss_per_crop.json` exactly (cassava…)";
line 160 says the ledger is "back to the three seeded crops". Both are false at
the tagged state. Shots 4.3 (per-crop ranking) and 4.5 (break-even) will show
five crops, not three. The URLs and the reset procedure in the runsheet are
still correct; only the expected crop set is not.

### A3. Freeze §6.1 defect 1 — "per-crop decision support does not net reversals" — is FALSE. There was no defect to fix.

Same text in `LIMITATIONS.md:138-147`. Its stated cause ("because a reversal log
carries no crop") is not what the code does.

`backend/app/services/dss_service.py:75-84` attributes a contra to its
**original's** crop and subtracts:

```
crop = crop_by_id.get(log.reverses_id) or UNSPECIFIED
sign = -1.0
```

Reversed yield quantities and reversed drying runs are removed from the
denominators via `reversed_ids` (`dss_service.py:70`). The enterprise path uses
`_live_rows` (`dss_service.py:294-314`), which drops both the contra and the log
it reverses. The investor report reuses `get_decision_support` unchanged
(`share_service.py:87`).

The capability was **introduced** by `6992d1c` (reversal netting) and
`fbdadca` (omit empty crop buckets), both ancestors of the freeze tag — so it
was present at the commit the freeze audited, and nothing was fixed afterwards.
Proven by four tests, re-run 2026-08-26, **4 passed**:

- `test_dss_reversed_crop_expense_no_unspecified_bucket` (`test_api.py:1250`) — asserts `"Unspecified" not in after`
- `test_dss_fully_reversed_crop_is_omitted` (`test_api.py:1332`)
- `test_dss_reversed_yield_restores_quantity_and_unit_cost` (`test_api.py:1266`)
- `test_dss_break_even_reflects_reversal` (`test_api.py:1538`)

**Action:** Chapter Four must not carry this as a limitation, and Chapter Five
must not list it as a known defect. This is a documentation defect, not a code
defect — no source change is implied and the tag does not need to move.

**Adjudicated 2026-08-29 — B-01 = NETTED.** This section's reading of the code
was subsequently confirmed by execution rather than inspection
(`docs/EVIDENCE_FREEZE_2026-08-29.md` §2): at the freeze implementation commit
`59a6286`, reversing a ₦25,000 crop expense moved that crop's expenses from
₦35,000 to ₦10,000 and its unit cost from ₦2,916.67 to ₦833.33 with no
`Unspecified` bucket at any point, and the investor report returned the same
netted figures to an unauthenticated token holder. The identical reproduction at
the baseline `78a68c2` returns the same figures. `LIMITATIONS.md` §3 now carries
the corrected entry. `docs/EVIDENCE_FREEZE_2026-08-25.md` is **left immutable**
as the dated historical record, and its §6.1.1 item 1 stands there as a recorded
false positive that its own §3 already contradicted — the thesis must explain
that contradiction rather than pretend the passage never existed.

### A4. Two naming imprecisions that will produce wrong prose.

- `THESIS_REPORTING_STATE.md` §6 lists the endpoint modules as "(auth, ledger,
  reports, dss, bioprocess, equipment, **share**)". There is no `share.py`. The
  module is **`backend/app/api/endpoints/investor.py`**; `share_service.py` is
  the service behind it. Verified against `backend/app/api/router.py`.
- `dss_break_even.json`'s `_source` field says "no separate break-even route
  exists". True of break-even **yield**, which is a field inside
  `/dss/decision-support`. It is **not** true of break-even **price**, which has
  its own route, `GET /api/v1/dss/break-even-price`
  (`backend/app/api/endpoints/dss.py:91`). Chapter Four must keep break-even
  yield (retrospective, kg, deterministic tier) and break-even price (dual
  cash/total, ₦/kg, enterprise tier) distinct.

---

## B. Feature → location → claim boundary

Evidence-type key: **AT** automated test · **LC** live capture · **SC** source
code only · **MI** manual inspection only.

### B1. Offline-first operational logbook (IndexedDB write queue)

| | |
| --- | --- |
| **Location** | `frontend/src/lib/db.ts` (Dexie schema, v1 and v2 at lines 23-40) · `frontend/src/lib/sync.ts` (`flushPendingLogs` :23, `retryFailedLogs` :53, `purgeQueueForCurrentOwner` :73, `registerSyncListener` :83) · `frontend/src/lib/queueOwner.ts` · `frontend/src/hooks/usePendingSync.ts`, `useOnlineStatus.ts` · `frontend/src/app/layout/SyncStatus.tsx` |
| **Evidence** | **AT** — `sync.test.ts` (15), `queueOwner.test.ts` (16 collected), `dbUpgrade.test.ts` (7). `sync.ts`, `queueOwner.ts`, `db.ts` at 100% statements. |
| **May state** | The queue is partitioned by an owner key derived from the JWT `sub`; every read path goes through the `[ownerKey+status]` compound index; a write retries and transitions to `failed` after three attempts (`sync.ts:40`, `failCount >= 3`); logout deletes only the signing-out account's rows, before the token is cleared, and never blocks logout. |
| **Must NOT state** | That any of this was verified in a browser. It is verified against `fake-indexeddb` under Vitest. No end-to-end offline→online browser test exists. The `SyncStatus` indicator itself has no component test. |

### B2. IndexedDB v1 → v2 migration

| | |
| --- | --- |
| **Location** | `frontend/src/lib/db.ts:29-40` (the `.upgrade()` hook) |
| **Evidence** | **AT** — `frontend/src/lib/dbUpgrade.test.ts` (7 tests, 276 lines). Negative control recorded in `docs/EVIDENCE.md`: breaking the hook fails 4 of the 7. |
| **May state** | A genuine v1 database (v1's own schema string, `verno === 1` asserted) opened by the shipped v2 module keeps every row with payload intact, gains an attributed `ownerKey`, is queryable on `ownerKey` and `[ownerKey+status]`, and the migrated rows then flush through the real `sync.ts`. Dexie's version machinery, the upgrade callback, the object stores, transactions and indexes are all real in the test. |
| **Must NOT state** | Browser-verified. Storage eviction, quota behaviour and vendor IDB bugs are out of the test's reach — stated in the test file's own header. |

### B3. `client_id` idempotency and the farm-scoped uniqueness constraint

| | |
| --- | --- |
| **Location** | `backend/app/services/ledger_service.py` — `_find_by_client_id` :9, `create_operational_log` :18 (the `IntegrityError` recovery path) · `backend/app/models/models.py:71` `UniqueConstraint("farm_id", "client_id", name="uq_operational_logs_farm_client")`, rationale comment :68-99 · migration `backend/alembic/versions/e6a2b4c7d130_scope_client_id_uniqueness_to_farm.py` |
| **Evidence** | **AT** — cross-farm and sequential cases in `backend/tests/test_api.py:189-305`; concurrency in `backend/tests/test_concurrency.py` (5 tests, 291 lines, file-backed SQLite, two real connections). `ledger_service.py` at 98%, one missed statement (line 123). |
| **May state** | Two farms may hold the same offline key without collision or 500; a `NULL` `client_id` is exempt from the composite constraint; a sequential replay returns the same row as 200 with exactly one log and one transaction stored; under a genuine race the loser receives the winner's row with `created=False`, its flushed transaction rolled back rather than double-booked, and the endpoint answers **200, not 500**; a non-replay integrity error still raises. The threaded case was run 10× consecutively without a flake. |
| **Must NOT state** | That PostgreSQL's behaviour under the same race was measured. The tests run on SQLite; the deterministic ones force the pre-check to miss. Postgres is inferred from the equivalent constraint. |

### B4. Financial ledger engine and P&L

| | |
| --- | --- |
| **Location** | `backend/app/services/ledger_service.py` — `get_operational_logs` :156, `get_financial_transactions` :165, `calculate_gross_margin` :174 · `backend/app/services/reports_service.py` — `get_pnl_report` :13, `get_monthly_pnl` :75, `generate_pnl_csv` :131 · `backend/app/api/endpoints/reports.py` (`/pnl`, `/pnl/monthly`, `/pnl.csv`) · `frontend/src/features/reports/ReportsPage.tsx`, `downloadPnlCsv.ts` |
| **Evidence** | **AT** — `test_pnl_report_json` :318, `test_pnl_monthly` :337, `test_pnl_report_csv` :346, `test_monthly_pnl_nets_reversal_in_month` :880. `reports_service.py` at 94% (missed 90-91, 109, 112). |
| **May state** | Every operational log is paired with exactly one financial transaction; farm-wide P&L with a monthly breakdown and CSV export; farm-wide P&L nets reversals within the month they fall in. |
| **Must NOT state** | That `reports_service.py` is fully covered — four statements are not. |

### B5. Ledger immutability and auditable reversal

| | |
| --- | --- |
| **Location** | `backend/app/services/ledger_service.py:77-155` (`reverse_log`) · `backend/app/api/endpoints/ledger.py:34` (reverse), `:53` and `:59` (both DELETE routes, which exist only to refuse) · `backend/app/models/models.py:106` (`reverses_id`) · migration `d5c1f0a9b8e2_add_ledger_reversal_and_audit.py` · `frontend/src/features/farm-records/ReverseConfirmDialog.tsx` |
| **Evidence** | **AT** — `test_ledger_delete_is_blocked` :753, `test_reversal_nets_pnl_to_zero` :765, `test_original_and_reversal_both_readable` :791, `test_reversal_rejected_across_farms` :808, `test_double_reversal_rejected` :820, `test_reversal_leaves_revenue_untouched` :837, `test_reversal_of_income_leaves_expenses_untouched` :864. |
| **May state** | Deletes are refused with 405; a correction is a category-preserving contra entry linked by `reverses_id`; both the original and its contra remain readable; double reversal and cross-farm reversal are rejected. Describe this as **audit-trailed**. |
| **Must NOT state** | **"Tamper-evident."** Immutability here is application-layer discipline, not cryptographic — nothing is hashed or signed. Also: a mistaken reversal cannot be rolled back, only compensated by an unlinked entry (freeze §6.1.4 — this one is still true). |

### B6. DSS deterministic tier — per-crop margin, ranking, unit cost, break-even yield

| | |
| --- | --- |
| **Location** | `backend/app/services/dss_service.py:32-289` (`get_decision_support`) — unit cost per harvested unit :196, marketable-mass guard :198-199, break-even yield :226-229 · `backend/app/api/endpoints/dss.py:20` (`GET /dss/decision-support`) · `frontend/src/features/dashboard/components/DecisionSupport.tsx` |
| **Evidence** | **AT** — `test_api.py:1250-1580`, the `test_dss_*` block. `dss_service.py` at 100%. |
| **May state** | Ranked by gross margin descending with alphabetical tie-breaks; two unit-cost bases reported separately and never merged (harvested unit, and per kg marketable where a non-reversed drying run exists); break-even yield is `expenses / unit_price` and is returned **unrounded** (`dss_service.py:229` — no rounding is applied), with four documented null cases (mixed units, zero revenue, zero yield, zero expenses); every figure derives from the farm's own ledger; reversals are netted (§A3). |
| **Must NOT state** | That break-even yield is rounded by the system. `7.8 kg` is a presentation rounding of the returned `7.777777777777778`; if Chapter Four quotes 7.8 it must say so. That the recommendations are agronomically validated — the arithmetic is verified, the advice is not. |

### B7. Enterprise economics

| | |
| --- | --- |
| **Location** | `backend/app/services/enterprise_service.py` — `cost_structure` :39, `depreciation_overlay` :84, `allocate_fixed_cost` :132, `break_even_prices` :178, `yield_sensitivity` :246, `operating_expense_ratio_pct` :290, `partial_budget` :318, `olympic_average_yield` :359 · orchestration in `dss_service.py` — `_enterprise_base` :333, `get_cost_structure` :425, `depreciation_rate_as_fraction` :466, `_equipment_overlay` :485, `get_break_even_price` :542, `get_sensitivity` :608, `get_yield_baseline` :645 · routes `dss.py:67, 91, 120, 146, 160` · UI `frontend/src/features/dss/components/` — `EnterpriseEconomics.tsx`, `CostStructurePanel.tsx`, `BreakEvenPricePanel.tsx`, `SensitivityTable.tsx`, `YieldBaselinePanel.tsx`, `PartialBudgetForm.tsx` |
| **Evidence** | **AT** — `backend/tests/test_enterprise_service.py` (32 functions, **40 collected**) plus the `test_enterprise_*` API block at `test_api.py:1670-2270`. `enterprise_service.py` at 100%; `EnterpriseEconomics.tsx` 94.28%; `YieldBaselinePanel.tsx` 100%. |
| **May state** | Cost-behaviour classification with an explicit coverage percentage; a zero depreciation rate counts as *unrated*, never as a zero charge; proportional allocation is undefined rather than an even split when there is no base; both break-even prices, with the cash price provably strictly lower; a conditional-labelled sensitivity matrix; operating-expense ratio undefined at zero revenue; partial budget signed both ways; Olympic average requires three seasons and discards one high and one low instance, not all ties. The single percentage→fraction conversion lives in `dss_service.depreciation_rate_as_fraction`. |
| **Must NOT state** | Any source or citation for the cost-behaviour taxonomy — `backend/app/schemas/schemas.py` still carries `TODO(cite)`. Present the taxonomy as an implementation decision recorded in `docs/adr/0002`, not as a cited standard. |

### B8. Offline / backend partial-budget parity

| | |
| --- | --- |
| **Location** | `frontend/src/features/dss/partialBudget.ts` (offline) · `backend/app/services/enterprise_service.py:318` (backend) · shared fixture `frontend/src/fixtures/partial_budget_parity.json`, cases PB-1..PB-8 |
| **Evidence** | **AT** — `frontend/src/features/dss/partialBudget.test.ts` (15 collected) and `test_enterprise_service.py:454-545` (`test_parity_fixture_is_internally_consistent`, `test_parity_partial_budget_matches_hand_computed_expectation`, `test_parity_pb1_sign_is_asserted_separately_from_magnitude`, `test_parity_pb3_exact_zero_is_not_negative_zero`). `partialBudget.ts` at 100%. |
| **May state** | Two independent implementations — one TypeScript, one Python — are asserted against **one file read from disk by both**, including that an exact zero is not returned as negative zero. The backend loader deliberately has no `try/except` and no fallback, so a missing fixture fails the suite loudly rather than skipping (documented in the test file header at `test_enterprise_service.py:9-22`). This is the strongest single piece of cross-implementation evidence in the project and is worth naming as such. |
| **Must NOT state** | That parity was observed in a running browser against a running backend. It is a shared-fixture agreement between two unit suites. |

### B9. DSS predictive tier — yield forecast

| | |
| --- | --- |
| **Location** | `backend/app/ml/dataset.py` (`_response` :70, `generate` :91, `load` :114) · `backend/app/ml/train.py` (`_build_estimator` :34, `_aggregated_importances` :48, `train_model` :67, `ensure_model` :108) · `backend/app/ml/predict.py` (`predict_yield` :47) · routes `dss.py:32` (`/predict`), `:42` (`/train`), `:50` (`/model`) · UI `frontend/src/features/dss/DSSPredictPage.tsx` |
| **Evidence** | **LC** for the metrics — `docs/ch4-data/model_info.json`. **AT** for the endpoint contract only — `test_dss_predict_rejects_malformed_payload` :64, `test_dss_predict_returns_forecast` :79, `test_dss_model_requires_authentication` :1583, `test_dss_model_reports_metrics_when_trained` :1589, `test_dss_model_reports_untrained_without_zero_metrics` :1612. |
| **May state** | `Pipeline(OneHotEncoder + RandomForestRegressor)`, 200 estimators, 6,000 synthetic samples, 5 crops (maize, rice, sorghum, soybean, cassava), target `yield_t_ha`; **R² 0.976204, MAE 0.241393 and RMSE 0.488334 t/ha**, all three **in-distribution on synthetic data**; feature importances crop 0.3445, rainfall 0.2845, soil_ph 0.2479, fertilizer_used 0.1231; the confidence band derives from tree spread; input bounds are enforced; an untrained model is reported as untrained and never as zero-valued metrics (a genuinely tested behaviour, and the one 4.2.3 gap that closed). |
| **UPDATED 2026-08-29** | Two things this row denied are now true. **(a) RMSE exists** — 0.488334 t/ha. **(b) The pipeline is reproducible**: seed-deterministic end to end, 18 tests in `test_reproducibility.py`, the metrics re-derived at the baseline agreeing with `model_baseline.json` to six decimal places, a dataset fingerprint taken over float64 bytes (`sha256 a461b884…`) stable across two environments differing in Python minor and pandas patch version. Coverage also moved: `train.py` **47%**, `dataset.py` **82%** — 37 of the 66 missed backend statements. **Retraining over the API is unreachable for every role**, including owner (403), by permission and by config flag. |
| **Must NOT state** | Any accuracy claim about real farms. Nothing asserts the synthetic data's realism or the fitted model's real-world quality. No train/test protocol on real data, no cross-validation, no holdout on real data. Reproducible is **not** accurate — do not let the determinism evidence be read as validation. |

### B10. Bioprocess drying — model and arithmetic

| | |
| --- | --- |
| **Location** | `backend/app/services/bioprocess_service.py` (284 lines) — `wb_to_db` :46 / `db_to_wb` :51, `dry_matter_kg` :58, `expected_outlet_mass_kg` :63, `process_loss` :71, `water_removed_kg` :90, `drying_rate_kg_h` :130, `specific_drying_rate` :135, `moisture_ratio_final` :144, `newton_k` :149, `page_fit` :159, `safe_storage_threshold` :219, `is_safe_to_store` :227, `compute_drying_metrics` :238 · endpoint `backend/app/api/endpoints/bioprocess.py` (`/summary` :46, `/{log_id}` :133) · parameters stored in `extra_data` per `docs/adr/0001` |
| **Evidence** | **AT** — `backend/tests/test_bioprocess_service.py` (11 tests); `bioprocess_service.py` at **100%**. API behaviour in `test_api.py:1154-1249`. **LC** for the seeded figures — `docs/ch4-data/bioprocess_summary.json`. |
| **May state** | Exact Page-model fit against a fixture; Newton `k`; wet↔dry basis round-trip; water balance distinguished from raw mass difference; process loss computed against a dry-matter-conserving prediction; safe-storage lookup; per-crop aggregation excluding reversed runs; drying-aware unit costs feeding the DSS. Seeded maize: 1 run, 100 kg in, 84 kg marketable, 14.08 kg water removed, mean rate 1.408 kg/h, Newton k 0.08023464725249374 (SOLAR_DRYER), safe-storage share 1.0. |
| **Must NOT state** | Any source for the safe-storage moisture ceilings — `TODO(cite)` remains on that table. Present them as implementation constants pending an FAO/NSPRI/IITA citation. |

### B11. Drying input validation

| | |
| --- | --- |
| **Location** | Server: `backend/app/schemas/schemas.py` (the drying validators) · Client: `frontend/src/features/farm-records/dryingParams.ts` |
| **Evidence** | **AT** — 8 API tests at `test_api.py:931-1030` (`mass_out > mass_in`, final moisture not below initial, non-positive mass, moisture out of range, non-increasing readings, band violations) plus `dryingParams.test.ts` (20 collected) mirroring the same rules client-side. `dryingParams.ts` at 94.33%. |
| **May state** | Every malformed run is rejected as **422 at the schema edge, never 500**; the same rule set is enforced twice, once in the browser and once at the API, so an offline write cannot bypass validation. `schemas.py` is at 100%. |
| **UPDATED 2026-08-29** | Validation is no longer drying-specific. **Monetary and quantity fields are bounded at the schema edge** by the `Money` and `Quantity` types (`ge=0`, `le=1e9` / `1e6`, `allow_inf_nan=False`) — 32 collected tests in `test_input_validation.py`, and live confirmation that −1,000,000, 2,000,000,000, `Infinity` and `NaN` each return 422 while a valid amount returns 201 (29 Aug freeze §3.11). The row that used to say these fields were unconstrained floats is void. |
| **Must NOT state** | That client-side validation is the security boundary. It is a usability mirror of the server rule. Nor that a bound catches a *wrong* value — it catches an impossible one; a plausible mistake still needs a reversal. |

### B12. Drying user interface and the curve chart

| | |
| --- | --- |
| **Location** | `frontend/src/features/farm-records/DryingFields.tsx` · `DryingRunResult.tsx` · `DryingCurveChart.tsx` (imported only by `DryingRunResult.tsx` — verified, no test file references it) |
| **Evidence** | **MI only.** `DryingCurveChart.tsx` 0% coverage; `DryingFields.tsx` 0/26; `DryingRunResult.tsx` 0/34. |
| **May state** | The form collects intermediate readings and the result panel draws the drying curve from them, established by manual inspection and screenshot. Say "manually inspected" explicitly. |
| **Must NOT state** | That the chart or either drying component has automated test coverage. Also: `DATA_PACK.md` §7's claim that there is **no readings input on the form** is stale — the form does collect readings. Do not quote it. |

### B13. Mechanization tracker

| | |
| --- | --- |
| **Location** | `backend/app/services/equipment_service.py` (60 lines: `get_equipment` :6, `create_equipment` :18, `get_equipment_list` :32, `create_maintenance_log` :41, `get_maintenance_logs` :58) · `backend/app/api/endpoints/equipment.py` (4 routes, 26 lines) · `backend/app/models/models.py:140` (Equipment), `:157` (MaintenanceLog) · `frontend/src/features/equipment/EquipmentPage.tsx`, `components/MaintenancePanel.tsx` · classification in `dss_service._cost_subtype` :317 |
| **Evidence** | **AT** — `test_api.py:158` lifecycle, `:306-317` 404 paths, `:452-545` depreciation-rate band and isolation, `:1031-1141` the mechanization `extra_data` block. `equipment_service.py` at 100%. Decision recorded in `docs/adr/0003`. |
| **May state** | `cost_subtype` is validated against a closed taxonomy and is the only mechanization field that moves a derived figure; `depreciation_rate` is bounded to a percentage band and converted to a fraction exactly once; `equipment_id` and `hours_used` are validated, persisted, read back unchanged — and read by nothing. The system can answer "what did mechanisation cost, and was it fixed or variable?" |
| **Must NOT state** | **Any machine-hour, utilisation, or cost-per-tractor-hour analysis.** `equipment_id`/`hours_used` are capture-only by decision (ADR-0003), and `hours_used` is populated on only 3 of 8 seeded mechanisation logs. |
| **CORRECTED 2026-08-29** | This row previously read "equipment cannot be corrected … that defect is still live". **That is false at the baseline and must not be propagated into Chapter Five.** `PATCH /equipment/{id}` exists at `78a68c2` (migration `b9e5f30c74a1`; 20 collected tests in `backend/tests/test_equipment_correction.py`; live PATCH, no-op PATCH and out-of-range 422 all observed — 29 August freeze §3.11, §5.1). The claim boundary is now: the update is **partial and farm-scoped**, an out-of-range rate is refused with 422, and `updated_at` is stamped **only when a value actually changes**, so a non-correction is not recorded as one. State it as equipment correction, not as a ledger-style reversal — equipment is not a financial record. |

### B14. Identity and the per-farm data boundary

| | |
| --- | --- |
| **Location** | `backend/app/core/security.py` (`hash_password` :29, `verify_password` :33, `create_access_token` :41, `decode_token` :48) · `backend/app/api/deps.py:23` (`get_current_user`) · `backend/app/api/endpoints/auth.py` · `backend/app/services/auth_service.py` · migration `b2e4d6f81a09_add_auth_and_farm_scope.py` · every model carries `farm_id` (`models.py` :32, :55, :77, :124, :144, :161) · `frontend/src/features/auth/AuthProvider.tsx`, `Login.tsx`, `lib/authToken.ts`, `lib/apiClient.ts` |
| **Evidence** | **AT** — `test_api.py:368-428` (register/login/hashing/unauthenticated), `:429` ledger isolation, `:511` equipment isolation, `:651-752` (secret-key policy, invalid email, tampered JWT, expired JWT), `:2118` enterprise routes cross-farm 404. `security.py` 93%, `deps.py` 85%, `auth_service.py` 100%. |
| **May state** | JWT bearer auth with bcrypt password hashing; passwords stored hashed, never plaintext; a default secret key is refused in production and allowed in dev; tampered and expired tokens are rejected; every query is farm-scoped and a cross-farm read returns **404, not 403** (so existence is not disclosed). |
| **Must NOT state** | That an independent security review, penetration test, or threat model exists. None does. |
| **UPDATED 2026-08-29** | Two additions at the baseline that this row predates, and that Chapter Four may state. **(a) Role-based access control**: 3 roles / 12 permissions (`backend/app/core/roles.py`, at 100%), 74 collected tests in `test_authorization.py`, endpoints asking for a permission rather than a role, **permission checked before scope** so a 403 is not an existence oracle, and a 403 body naming only the missing permission. **(b)** The boundary is no longer proven *by tests only* — it was probed live against the running production stack (29 Aug freeze §3.10): worker 403 on P&L, DSS, summary and equipment but 200 on the farm's own log; manager 403 on minting a share link; owner 403 on `POST /dss/train`. That is verification, not validation: no independent party has tried to break it. |

### B15. Investor / stakeholder sharing

| | |
| --- | --- |
| **Location** | `backend/app/services/share_service.py` (`create_link` :22, `list_links` :38, `revoke_link` :47, `get_report_by_token` :63) · `backend/app/api/endpoints/investor.py` (**not** `share.py`) · `backend/app/core/security.py:58` `generate_share_token`, `:68` `hash_share_token` · migration `c3f7a1e58d24_add_share_tokens.py` · `frontend/src/features/investors/InvestorsPage.tsx`, `PublicInvestorReport.tsx` · public route matched in `frontend/src/App.tsx:39` (`/investor/:token`, bypasses the auth gate before it is reached) |
| **Evidence** | **AT** — `test_api.py:546-650` (6 tests). `share_service.py` at 100%. |
| **May state** | A tokenised read-only link; tokens are SHA-256 hashed at rest and the raw token is returned exactly once at mint; revocation takes effect by making the token unresolvable (404); a share token cannot write and cannot reach any other route; links are farm-scoped and revocation is owner-scoped. |
| **CORRECTED 2026-08-29** | This row previously read "**Must NOT state** that the link is rate-limited, expiring, or otherwise time-bounded — nothing in `share_service.py` implements expiry". **False at the baseline.** Every minted link now carries `expires_at` (migration `f7b3c2d94e15`), verified live at exactly 90 days to the second; unknown, revoked and expired tokens resolve to one identical 404 so the endpoint is no oracle; the token cannot be exchanged for a session (401 as a bearer credential) and reaches no write path; the public report route is separately rate-capped; and the raw token is scrubbed from all three logs that record the request — nginx writes `[redacted]`, the application middleware and uvicorn's access log write a stable 12-hex non-reversible fingerprint. 16 collected tests in `test_share_lifecycle.py`, 20 in `test_logging_safety.py`, plus live verification (29 Aug freeze §3.8). |
| **Must NOT state** | That a link can be revoked *before* its 90 days by anything other than explicit revocation, or that the fingerprint in the logs is reversible. It is not, and it exists to correlate requests, not to identify a link. |

### B16. Read-cache invalidation on write

| | |
| --- | --- |
| **Location** | `frontend/src/lib/apiCache.ts`, `apiCacheConfig.ts` |
| **Evidence** | **AT** — `frontend/src/lib/cacheInvalidation.test.tsx` (5 collected, 429 lines). Negative control in `docs/EVIDENCE.md`: breaking the purge → 5 failed / 0 passed. |
| **May state** | Log writes, queue flushes, equipment creation, maintenance logging and reversals each invalidate the cached derived reads. |
| **Must NOT state** | That the service-worker stale-revalidation window was reproduced. Freeze §6.1.5 is explicit that it is **reasoned from handler ordering, never observed** — a candidate, not a confirmed defect. |

### B17. PWA, build and frontend performance

| | |
| --- | --- |
| **Location** | `frontend/vite.config.ts:12-21` (`VitePWA`, `registerType: 'autoUpdate'`, Workbox `globPatterns`) · `frontend/src/main.tsx` · route code-splitting in `frontend/src/app/router.tsx` |
| **Evidence** | **LC** — `docs/perf/` (26 raw Lighthouse artefacts) + `docs/perf/README.md`; write-up in `performancebenchmarking.md`. Build figures in freeze §2. |
| **May state (17 Aug set — SUPERSEDED, see the UPDATED row below)** | Lighthouse 13.4.1, headless Chrome, mobile emulation 412×823 @ DPR 1.75, `simulate` (Lantern) throttling, 2026-08-17, commit `c16924e`, against `http://localhost:4173/` (`vite preview` on the production build, so the service worker is live). Medians: cold slow-3G FCP/LCP/SI 7674.4 ms, TBT 121.0, performance **57**; cold slow-4G 2317.7 ms, TBT 107.0, performance **95**; warm flow navigation FCP ≈ 105–122 ms; CLS 0 throughout. Single JS chunk 243,724 bytes transferred, 7 requests on a cold load. Precache 21 entries / 859.67 KiB; `dist/` 959 KB; build 6.86 s. Service-worker attribution settled by `offline-probe.mjs`. **Every figure in this row is superseded except the method and the attribution probe.** |
| **Must NOT state** | That these are production or real-network figures — one developer machine, localhost, emulated network and CPU. And **do not attribute any improvement between measurement dates to code changes** unless the metric is network-bound: `benchmarkIndex` varied 425–1654 on 17 Aug and 1406–1996 on 29 Aug, so TBT and the composite score move with host speed. Only network-bound metrics and byte counts compare across sets. |
| **UPDATED 2026-08-29 — quote this row** | A **third** set now exists and is the one to report: re-run at the baseline `78a68c2` on 29 Aug 2026, same method and machine; raw artefacts in `docs/perf/2026-08-29/`. Build re-measured at the baseline: **13.45 s, precache 22 entries / 866.74 KiB, `dist/` 967 KB**, tsc and eslint clean. Medians — cold slow-3G FCP/LCP/SI 5,661.2 ms, TBT 10.5, perf 65; cold slow-4G FCP 1,709.9 ms, LCP 1,859.9, perf 99; warm FCP 70.6 ms, LCP 1,612.0 ms, perf 100. Cold transfer 139,245 B over 8 requests; warm 127 B over 7, the 127 B being `pwa-192x192.png`, which the precache omits. The 17 Aug figures at `c16924e` are **superseded** and must carry their date and commit wherever quoted. |

### B18. Deployment

| | |
| --- | --- |
| **Location** | `docker-compose.yml` — dev services `agrip-backend-1`, `agrip-db-1`, `frontend-prod` · **`docker-compose.prod.yml`** — nginx-served frontend, `edge` profile for automatic-TLS Caddy · `ops/backup.sh`, `ops/restore.sh` · `backend/alembic/` (migrations run on startup) · `backend/app/main.py`, `backend/app/core/config.py` |
| **Evidence** | **LC** — running containers; the production stack built, started and probed live (29 Aug freeze §3.7, §3.13); backup and restore rehearsed end to end against real PostgreSQL (§3.12); `hostingcostanalysis.md` for the cost model. |
| **May state** | The production composition builds and starts with all three services healthy; nginx proxies the API with its path intact and an unknown path reaches the SPA; migrations are applied on startup (not `create_all`); readiness answers from the backend, not the page shell; both app containers run unprivileged (backend uid 1000, frontend uid 101) and the database publishes no host port; the signing-key guard refuses the default `SECRET_KEY` outside dev/test, no `SECRET_KEY` literal is committed and no `.env` is tracked; the Caddy edge config renders under its profile; `ops/backup.sh` and `ops/restore.sh` were run end to end with every restored row count matching and 0 unpaired logs. Measured container footprint subtotal 178.9–202.8 MiB; **estimated** hosting cost $15.40/month ≈ ₦20,950. |
| **Must NOT state** | **That a production deployment exists.** The row above is a deployment *path* that has been exercised, not a deployment. No instance serves real users, no departmental host runs it, no certificate has ever been issued for a real domain, and there is **no production observability** — no metrics, tracing or alerting. The backup rehearsal used seeded data in a scratch database; it is not a restore of a production backup. The cost is **estimated, not incurred**. No load, stress or soak testing. |

### B19. Demonstration data and its provenance

| | |
| --- | --- |
| **Location** | `backend/scripts/seed_bioprocess_demo.py` (505 lines). Idempotency: every log carries a fixed `client_id` (28 of them) and is posted through the real `POST /ledger/logs`, so the demo is created exactly as a farmer's would be. Equipment has no `client_id`, so `ensure_equipment` matches on name before posting. |
| **Evidence** | **LC** — `docs/EVIDENCE.md` seed-idempotency block; `docs/DATA_CLEANUP_2026-08-25.md` for the live DB state. |
| **May state** | The seed is idempotent — figures bit-identical across a re-run (md5 `1850df22069facec23e86032275c659f` on both captures); three consecutive runs leave 28 logs, 28 transactions and 2 equipment with no 201 after the first. Farm 26 is the seeded demonstration farm and every Chapter Four figure is read from it. Live DB at the freeze: 14 farms, 13 users, 109 operational logs, 109 financial transactions, 3 equipment, 1 maintenance log, 10 share tokens. |
| **Must NOT state** | That the data is real or field-collected. Every figure derives from seeded demo records on one farm. Do **not** use a farm-list screenshot to identify the farm — two farms are named `Demo Farm` (17 and 26) and eleven unattributed exploratory farms remain and are to be left alone. |

---

## C. Locations that do NOT exist — state the absence, do not invent the location

| Chapter Four might want | Reality |
| --- | --- |
| A drafted `AgriProfit_Chapter4.md` | **Does not exist in this repository.** `AGENT_PROMPT_chapter4_gaps.md` references it; the file is not tracked and not in the working tree. The Chapter Four planning material that does exist is `docs/ch4-data/` (DATA_PACK + 4 JSON + runsheet) and `docs/THESIS_REPORTING_STATE.md`. |
| `docs/THESIS_MASTER_INSTRUCTION.md` | **Exists but is 0 bytes.** Cite nothing from it. |
| An equipment edit/correct endpoint | **Exists at the baseline** — `PATCH /equipment/{id}`, 20 collected tests (§B13, corrected row). It did not exist at the freeze tag; this row previously said so flatly and would now mislead. |
| A component test for any page or form | None exist. `FarmRecordCreateForm.tsx` 0/61, `FarmRecordsPage.tsx` 0/60, `DryingFields.tsx` 0/26, `DryingRunResult.tsx` 0/34, `DryingCurveChart.tsx` 0, `Login.tsx` 0/28, `DSSPredictPage.tsx` 0/40, the investor pages, the app shell, `useCropOptions.ts` 0/16. |
| Usability / SUS / task-completion results | **None exist anywhere in the repository.** `usabilitysessionrunsheet.md` is a facilitator *script*. Chapter Four stands at one evaluator honestly reported, per the decision rule in its own 4.8.1. |
| An end-to-end browser test | None. |
| An offline-queue flush test with a mocked client (4.2.3 gap b) | The gap is closed by different means: `sync.test.ts` covers `flushPendingLogs`, the three-strike transition (`sync.ts:40`) and `retryFailedLogs`. Cite `sync.test.ts`, not a nonexistent dedicated module. |

---

## D. Test identity, verified independently 2026-08-26 — SUPERSEDED

> **Superseded at the baseline.** `78a68c2` collects **422** backend cases
> (418 passed, 4 skipped locally, 0 failed) at **96%** statement coverage over
> 1,594 statements, across 13 files, with **148** frontend tests in 13 files at
> 43.18%. The per-file split below is correct **for the four modules that
> existed at the freeze** — and those four still collect exactly the same 190
> cases at the baseline, which is what establishes that nothing was weakened.
> The **totals** are superseded; take them, and the nine additional modules,
> from `docs/EVIDENCE_FREEZE_2026-08-29.md` §3.2. The counting convention below
> still holds and matters more than ever: six backend modules parameterise.

`python -m pytest backend/tests --collect-only -q` → **190 tests collected**
at the freeze, matching freeze §2. Per-file split (not in the freeze):

| File | Collected | `def test_` | Lines |
| --- | ---: | ---: | ---: |
| `backend/tests/test_api.py` | 134 | 120 | 2,259 |
| `backend/tests/test_enterprise_service.py` | 40 | 32 | 547 |
| `backend/tests/test_bioprocess_service.py` | 11 | 11 | 229 |
| `backend/tests/test_concurrency.py` | 5 | 5 | 291 |
| **Total** | **190** | **168** | **3,326** |

**Collected ≠ function count** — parametrisation accounts for the 22-test
difference, concentrated in `test_enterprise_service.py`. If Chapter Four states
a count, state it as **collected tests**, never as "test functions". At the
baseline the figure to state is **422 collected** (355 `def test_` across 13
files); on the frontend, **148** across 13 files.
