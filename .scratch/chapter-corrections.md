# Chapter correction redline — Chapters 1–3

Read-only audit output. **No chapter file was edited.** `CURRENT` blocks are
verbatim from `AgriProfit_Chapters_1-3_corrected.docx` so they can be located
with Ctrl+F in Word. Paragraph numbers refer to the extraction order of that
document.

Each item carries a `BUILDABLE` line where the claim could be made true by
writing code instead of weakening the text. A consolidated list of other
already-built-but-unreachable capabilities is at the end.

---

# FIX DOWNWARD — the chapter claims more than the code does

### 1.5 Scope ¶[26]

**CURRENT:**
> The platform primarily targets core FMIS functionalities: digital operational logbooks, financial-accounting integration, mechanisation tracking, and decision support for standard crop and livestock enterprises.

**PROBLEM:** There is no livestock concept anywhere in the system — no entity, no category, no field.

**PROPOSED:**
> The platform primarily targets core FMIS functionalities: digital operational logbooks, financial-accounting integration, mechanisation tracking, and decision support for crop enterprises. Livestock enterprises are outside the scope of the current implementation; the activity-category model would extend to them without structural change, but no livestock-specific entity or metric is implemented.

**EVIDENCE:** `backend/app/core/enums.py:7-14` — `Category` is seed/fertilizer/labour/mechanization/yield/bioprocess/other. `backend/app/services/dss_service.py:80` groups by `crop` only. `grep -rni livestock backend/app frontend/src` returns nothing.

**BUILDABLE:** No. Livestock is a domain model, not a label — it needs herd/head-count entities and per-animal metrics. Weeks, not hours. Correct the text.

---

### 1.5 Limitations ¶[28]

**CURRENT:**
> Finally, the decision-support modules employ deterministic, rule-based modelling complemented by lightweight statistical regression rather than advanced deep-learning algorithms, ensuring the computational requirements remain feasible for accessible mobile processors (van Klompenburg et al., 2020).

**PROBLEM:** The statistical tier is a Random Forest ensemble, not a regression. Section 2.6.3 ¶[72] already states this correctly, so the two sections contradict each other.

**PROPOSED:**
> Finally, the decision-support modules employ deterministic, rule-based modelling complemented by a lightweight tree-based ensemble (Random Forest) rather than advanced deep-learning algorithms, ensuring the computational requirements remain feasible for modest server hosting and accessible mobile clients (van Klompenburg et al., 2020).

**EVIDENCE:** `backend/app/ml/train.py:42` — `RandomForestRegressor(...)`. `backend/app/ml/train.py:23` imports `train_test_split`, not a linear model.

**BUILDABLE:** Technically yes — adding a `LinearRegression` alternative is ~30 minutes — but it would make the sentence true by adding a model nobody uses. Correct the text.

---

### 2.6.1 Data Layer and Feature Definition ¶[64] — feature list

**CURRENT:**
> From these records, candidate predictor variables (features) are defined: agronomic features (crop type, area cultivated, input quantities, season), resource features (machine-hours, labour-hours, fuel), and contextual features (location, rainfall band, soil class where available).

**PROBLEM:** Of the features named, exactly one (crop type) exists. There is no area, season, machine-hours, labour-hours, fuel, location or soil-class field in the data model. The implemented feature set is rainfall, fertiliser, soil pH and crop.

**PROPOSED:**
> From these records, candidate predictor variables (features) are defined. The current implementation uses four: crop type, together with three agronomic conditions entered at the point of forecast — rainfall, fertiliser applied, and soil pH. A wider feature set — cultivated area, season, machine-hours, labour-hours, fuel, location and soil class — is specified here as the intended direction of the data layer; those fields are not yet captured by the operational log and are therefore not available to the model in this release.

**EVIDENCE:** `backend/app/ml/dataset.py:37-38` — `NUMERIC_FEATURES = ["rainfall", "fertilizer_used", "soil_ph"]`, `CATEGORICAL_FEATURES = ["crop"]`. `backend/app/models/models.py:62-99` — `OperationalLog` has no area, season, hours or location column.

**BUILDABLE:** Partly, and worth knowing. `quantity`/`unit` already capture input quantities and `timestamp` yields season. Adding an `area_ha` column to `OperationalLog` is a one-line migration plus a form field (~1 hour) and would make "area cultivated" true, which also unlocks per-hectare metrics. Machine-hours and labour-hours would follow the same pattern. Location and soil class need new capture UI. Recommend: build `area_ha`, correct the rest.

---

### 2.6.1 Data Layer and Feature Definition ¶[64] — prediction targets

**CURRENT:**
> The corresponding prediction targets are crop yield, gross margin or profit/loss, and recommended input allocation.

**PROBLEM:** The only prediction target is crop yield. Gross margin is computed deterministically, not predicted. Nothing recommends an input allocation.

**PROPOSED:**
> The corresponding prediction target in the current implementation is crop yield. Gross margin and profit/loss are not predicted but computed deterministically from recorded transactions by the Tier 1 engine. Recommended input allocation is identified as future work, dependent on the wider feature set described above.

**EVIDENCE:** `backend/app/ml/dataset.py:40` — `TARGET = "yield_t_ha"`, a single target. `backend/app/services/dss_service.py:180-192` computes margin arithmetically. No allocation code exists.

**BUILDABLE:** Not cheaply. Input-allocation optimisation needs a cost/response model per input, which the synthetic dataset does not support. Correct the text.

---

### 2.6.3 A Tiered Modelling Strategy ¶[69] — "runs fully offline"

**CURRENT:**
> This tier runs fully offline, requires no training data, and is explainable—satisfying the bounded-rationality requirement for clear, satisficing recommendations (Section 2.2.2).

**PROBLEM:** Tier 1 is computed server-side and fetched over HTTP. Offline, the client serves a previously cached response — availability, not local computation. Section 2.6.5 ¶[76] states the server-side position correctly, so the chapters contradict each other.

**PROPOSED:**
> This tier requires no training data, runs on modest server hosting, and is explainable—satisfying the bounded-rationality requirement for clear, satisficing recommendations (Section 2.2.2). Its most recent results remain readable without connectivity, because the client caches decision-support responses in the service worker; the computation itself is performed server-side.

**EVIDENCE:** `backend/app/services/dss_service.py:29` — `get_decision_support(db, farm_id)` requires a database session. `backend/app/api/endpoints/dss.py:17` exposes it over HTTP. `frontend/vite.config.ts:34` caches `/api/v1/(ledger|reports|dss/decision-support)` StaleWhileRevalidate.

**BUILDABLE:** Yes, but not small. Tier 1 is pure arithmetic over rows the client could hold in IndexedDB, so genuine offline computation is possible — but it means mirroring the reversal-netting and unit-grouping rules in TypeScript and keeping two implementations in agreement. That duplication is a correctness risk on the figures that matter most. Estimate 1–2 days. Recommend correcting the text and keeping one authoritative implementation.

---

### 2.6.3 A Tiered Modelling Strategy ¶[69] — Tier 1 outputs

**CURRENT:**
> Tier 1 – Deterministic, rule-based engine (baseline). Transparent IF–THEN agronomic and financial rules compute gross margin, break-even points, and input thresholds directly from the records.

**PROBLEM:** Tier 1 computes gross margin and unit cost of production. It computes no break-even point and no input threshold.

**PROPOSED:**
> Tier 1 – Deterministic, rule-based engine (baseline). Transparent financial rules compute per-crop gross margin and unit cost of production directly from the records, together with a per-kilogram cost against marketable mass where post-harvest drying has been recorded.

**EVIDENCE:** `backend/app/services/dss_service.py:196-207` — the emitted keys are `revenue`, `expenses`, `gross_margin`, `yield_quantity`, `yield_by_unit`, `unit_cost_of_production`, `marketable_mass_kg`, `unit_cost_per_kg_marketable`. `grep -rni "break-even|threshold" backend/app/services/dss_service.py` returns nothing.

**BUILDABLE: Yes — this one is genuinely small.** Break-even is already latent in the data: for a crop with revenue R, expenses E and yield Q in a single unit, unit revenue is R/Q and break-even yield is E ÷ (R/Q). That is ~15 lines in `dss_service.py` beside the existing unit-cost calculation, guarded the same way (None when yield is absent or units are mixed), plus one line in `DecisionSupport.tsx`. Estimate 45 minutes including a test. **Recommend building it rather than deleting the claim** — it is the single most decision-useful number the engine could add, and it makes both this sentence and item 7 partly true.

---

### 2.6.5 From Prediction to Decision Support ¶[76]

**CURRENT:**
> Rather than presenting raw numbers, AGRI-PROFIT converts predictions into ranked, actionable options—for example, the input mix that maximises expected gross margin, or an early warning when projected costs approach the break-even threshold.

**PROBLEM:** The decision-support panel presents exactly raw numbers, in an unranked list. There is no ranking, no input-mix option set, and no break-even warning.

**PROPOSED:**
> The decision-support outputs are presented as per-crop figures — gross margin, unit cost of production, and recorded yield — ordered so that the least profitable crops are visible without scrolling. Converting these into a ranked option set (for example, the input mix that maximises expected gross margin) and into threshold-based early warnings is specified here as the intended direction and is not implemented in the current release.

**EVIDENCE:** `frontend/src/features/dashboard/components/DecisionSupport.tsx:77` renders `crops.map(...)` in server order; `backend/app/services/dss_service.py:132` iterates `sorted(buckets)` — alphabetical by crop, not by any metric. No warning logic exists.

**BUILDABLE: Ranking, yes — trivially.** Changing `sorted(buckets)` to sort by gross margin ascending is a one-line change (~10 minutes with a test) and would make "ranked" literally true. The early warning depends on break-even (item 6, 45 min). The input-mix optimiser is the only genuinely out-of-reach part. **Recommend building the ranking and the warning, then narrowing the claim to drop only the input-mix example.**

---

### 3.4.2 Technology Stack ¶[102]

**CURRENT:**
> The backend is implemented in Python using an asynchronous web framework with an object-relational mapper and a migration tool for schema evolution.

**PROBLEM:** FastAPI is async-capable, but every route handler in the application is a synchronous `def`. FastAPI runs those in a threadpool. As written, an examiner asking "show me your async request handling" would find none.

**PROPOSED:**
> The backend is implemented in Python using FastAPI, with SQLAlchemy as the object-relational mapper and Alembic for schema evolution. FastAPI supports asynchronous request handling, but the route handlers in this implementation are written synchronously and are executed in FastAPI's worker threadpool, because the ORM session and database driver in use are synchronous. This keeps the data-access code straightforward at the cost of not exploiting asynchronous I/O; migration to an asynchronous driver is identified as a future optimisation.

**EVIDENCE:** `grep -c "async def" backend/app/api/endpoints/*.py` returns 0 for all eight endpoint modules. `backend/app/models/database.py` constructs a synchronous engine and `sessionmaker`.

**BUILDABLE:** Not small, and not obviously desirable. True async needs `asyncpg` plus `AsyncSession` and a rewrite of every service function and test fixture — 2–3 days, with no measured benefit at this scale (the P&L aggregate already runs in under 1 ms in-database, per `LIMITATIONS.md` §7). Correct the text; it then reads as an honest engineering trade-off rather than a gap.

---

### 3.6.4 Mechanisation and Equipment Tracker ¶[130]

**CURRENT:**
> This module records equipment acquisition cost, maintenance events, and depreciation, and records mechanisation usage and fuel as operational entries tagged with the mechanisation activity category, so that machinery costs are captured within the ledger alongside other activities (addressing the mechanisation-tracking element of the aim).

**PROBLEM:** The module stores a depreciation *rate* and echoes it back. Nothing computes accumulated depreciation, an annual charge, or a book value — and no depreciation figure reaches the P&L.

**PROPOSED:**
> This module records equipment acquisition cost, an annual depreciation rate, and maintenance events, and records mechanisation usage and fuel as operational entries tagged with the mechanisation activity category, so that machinery costs are captured within the ledger alongside other activities (addressing the mechanisation-tracking element of the aim). The depreciation rate is stored against each item as a planning input; computing an accumulated depreciation charge and carrying it into the profit-and-loss statement is identified as a future refinement.

**EVIDENCE:** `backend/app/models/models.py:130-132` — `purchase_date`, `purchase_price`, `depreciation_rate` are stored. `backend/app/services/equipment_service.py` contains no arithmetic. The UI label was corrected to "Dep. rate {n}%/yr" at `frontend/src/features/equipment/EquipmentPage.tsx:97` for exactly this reason.

**BUILDABLE: Yes — small.** Straight-line depreciation is a pure function of three fields already stored: annual charge = price × rate, accumulated = charge × years elapsed, book value = price − accumulated (floored at zero). ~25 lines in `equipment_service.py`, two lines on the equipment card, one test. Estimate 1 hour. **Recommend building it** — it makes the original sentence true as written and answers PRD story 14. Carrying the charge into the P&L is a separate, larger decision (capex vs opex) and should stay future work either way.

---

### 3.6.8 Feature-Phone (USSD/SMS) Data Entry ¶[141]–¶[142]

**CURRENT (the whole section):**
> 3.6.8 Feature-Phone (USSD/SMS) Data Entry
>
> To address the socio-technical barrier at the heart of Objective 1—that a large proportion of rural farmers lack smartphones—the design includes an inbound message channel through which a farm activity can be recorded from a feature phone. An inbound webhook accepts a message consisting of a sender identifier and a short structured text, parses it into an activity and amount, and creates a paired Operational Log and Financial Transaction through the same ledger service used by the application, so that a phone-entered record is indistinguishable from an app-entered one and appears in the same reports. The sender’s number is mapped to a registered farm so that messages are routed to the correct ledger and unregistered senders are rejected. The channel is designed to be gateway-agnostic, so that it can be exercised through simulated inbound-message payloads independently of any carrier; implementation and integration with a live carrier gateway are identified as future work.

**PROBLEM:** The most exposed claim in the three chapters. It describes, in the present tense, a webhook that accepts, parses and creates records. **No such endpoint, service, parser or sender-to-farm mapping exists, and none ever has.** The closing hedge covers only "integration with a live carrier gateway", which reads as though the webhook itself is built and merely unconnected. The placeholder screens that gestured at this channel were removed from the application this week, so nothing in the running system now refers to it at all.

**PROPOSED (replace the whole section):**
> 3.6.8 Feature-Phone (USSD/SMS) Data Entry — Design Specification (Not Implemented)
>
> Objective 1 identifies the absence of smartphones among a large proportion of rural farmers as a socio-technical barrier to adoption. A complete response to that barrier requires an entry path that does not presuppose a smartphone, and this section specifies the design of such a path. It is presented as a specification only: no part of it is implemented in the current release, and the platform as evaluated in Chapter Four requires a smartphone or computer.
>
> The design is an inbound message channel. A webhook would accept a payload carrying a sender identifier and a short structured text, parse it into an activity category and an amount, and create the paired Operational Log and Financial Transaction through the same ledger service the application uses — so that a phone-entered record would be indistinguishable from an app-entered one and would appear in the same reports. The sender's number would be mapped to a registered farm so that messages route to the correct ledger and unregistered senders are rejected. The channel would be gateway-agnostic, exercisable through simulated inbound payloads independently of any carrier.
>
> The consequence for this study should be stated plainly: the feature-phone accessibility requirement in Section 3.3.2 is specified and designed but not delivered, and the evaluation in Chapter Four therefore covers only the smartphone client.

**EVIDENCE:** `grep -rniE "ussd|webhook|twilio|sms" backend/app` returns **no matches**. The complete route table (`backend/app/api/router.py:5-11`, 28 routes across `backend/app/api/endpoints/`) contains no inbound-message path. The former placeholder screens `frontend/src/features/messaging/UssdPage.tsx` and `WhatsappPage.tsx` were deleted this week along with their routes.

**BUILDABLE: Yes, and this is the most valuable build on the list.** The chapter has already written the specification precisely enough to implement: one `POST /messaging/inbound` endpoint taking `{sender, text}`, a parser for a small grammar (e.g. `FERT 25000`, `SELL maize 100kg 25000`), a `phone_number` column on `Farm` (or a `FarmPhone` table) for sender→farm mapping, and a call into the existing `ledger_service.create_operational_log` — which already handles pairing, idempotency and farm scoping, so no ledger logic is duplicated. Estimate **4–6 hours** including tests and a simulated-payload fixture, with no carrier account needed. That would convert the largest false claim in Chapter 3 into a demonstrable feature and restore the Section 3.3.2 accessibility requirement. **Strongly recommend building rather than rewriting.** If built, this section reverts to present tense and only the live-carrier hedge remains.

---

# FIX UPWARD — the chapter undersells what shipped

### 3.6.1 Offline Operational Logbook ¶[124]

**CURRENT:**
> In the current release, offline support is provided for the data-entry (write) path; retrieval of previously stored data assumes connectivity unless runtime caching of read endpoints is enabled, which is identified as a planned enhancement.

**PROBLEM:** Read caching is enabled and shipping, and has been verified offline by driven browser. The chapter describes a delivered capability as planned.

**PROPOSED:**
> In the current release, offline support covers both paths. Records entered without connectivity are queued locally and synchronised on reconnection, and read endpoints for the ledger, reporting and decision support are cached by the service worker, so a farmer who opens the application offline sees their most recently retrieved figures rather than an error. This was verified by a driven-browser probe: with the network disconnected, a full navigation was served by the service worker and rendered the application shell, while control requests to non-cached URLs failed as expected. The cache is purged on every authentication change, so one account's data can never be served to another on a shared device.

**EVIDENCE:** `frontend/vite.config.ts:32-45` — StaleWhileRevalidate over `/api/v1/(ledger|reports|dss/decision-support)`, 64 entries, 7-day expiry. `frontend/src/lib/apiCache.ts` purges on auth change. `docs/perf/offline-probe.mjs` exits PASS; results recorded in `docs/perf/README.md` under "Service-worker attribution".

**BUILDABLE:** Already built. Text only.

---

### 3.3.2 Non-Functional Requirements ¶[93]

**CURRENT:**
> Low-bandwidth, mobile-first operation: the interface must be usable on affordable smartphones over constrained networks.

**PROBLEM:** The requirement is correctly stated but Chapter 3 never evidences it, and until this week it was not met — the navigation rail held a fixed 220px at every viewport, leaving roughly 140px of content on a 360px screen. It is now met and should be claimed.

**PROPOSED (keep the requirement line as written; add beneath it):**
> This requirement is met by a responsive layout with a single breakpoint at 768px: below it the navigation rail collapses to a dismissible drawer, the main content takes the full viewport width, the metric tiles stack into a single column, and wide tables scroll within their own container so that the page itself never scrolls horizontally. The layout was verified at 360 × 640 and 414 × 896 across the dashboard, records, reporting, decision-support and stakeholder-sharing screens, with no horizontal overflow on any of them. Low-bandwidth operation is evidenced separately by the performance benchmarking in Section 3.8.2.

**EVIDENCE:** `frontend/src/index.css:102-166` — responsive layer, `@media (max-width: 768px)`. `frontend/src/hooks/useMediaQuery.ts:39` — `MOBILE_QUERY = '(max-width: 768px)'`. `frontend/src/app/layout/AppShell.tsx:27` and `:60-82` — breakpoint hook and drawer.

**BUILDABLE:** Already built. Text only.

---

# ADDITIONS — facts a correct paragraph must contain

Per instruction these are fact lists with evidence, not drafted prose.

### 13. Table 3.1 omits ShareToken ¶[107]–¶[120]

A corrected table must state:

- A **Share Token** entity exists and is a principal entity of the model — it carries the whole of the Objective 3 stakeholder-sharing mechanism described in 3.6.7, which the current table leaves without a data-model counterpart. — `backend/app/models/models.py:35`
- Its role: a revocable, read-only capability granting an investor or lender access to one farm's P&L and yield report without an account. — `backend/app/models/models.py:35-60`
- Only a **SHA-256 hash** of the token is stored; the raw token is returned once at mint time and never again, so a database compromise cannot yield a usable link. — `backend/app/core/security.py` (`hash_share_token`), `backend/app/services/share_service.py:23-35`
- It is bound to a farm by its own `farm_id`; the public report derives the farm from the token and never accepts a farm from the caller, so a cross-farm read is unrepresentable rather than merely blocked. — `backend/app/services/share_service.py:60-70`
- It carries a `revoked` boolean; revocation takes effect by the token resolving to nothing (404). — `backend/app/models/models.py:53`, `backend/app/services/share_service.py:46-58`
- It was added by a versioned migration, consistent with the managed-schema claim in 3.6.6. — `backend/alembic/versions/c3f7a1e58d24_add_share_tokens.py`

**BUILDABLE:** N/A — the entity exists; the table is simply incomplete.

---

### 14. Chapter 3 contains no description of the reversal mechanism

Chapter 3 describes creation and reporting but never how a mistaken record is corrected. Natural home: 3.5 after the single-entry paragraph ¶[105], or a new 3.6.x beside the ledger engine. Any such subsection must state:

- Ledger records are **immutable**: never edited, never deleted. — `backend/app/api/endpoints/ledger.py:53-62` returns HTTP **405** on `DELETE` with a pointer to reversal; deletion is unsupported for anyone.
- Correction is by **reversal**: a new Operational Log paired with a *contra* Financial Transaction of the **same** type, amount and Activity Category as the original, linked back by `reverses_id`. — `backend/app/services/ledger_service.py:70-130`, `backend/app/models/models.py:88`
- Because the contra preserves category and type, reports subtract it from the same pile its type feeds: a reversed expense returns that category's operating cost to its prior value and leaves revenue untouched — not merely the net margin. — `backend/app/services/reports_service.py:42-50`
- A reversal carries **no crop and no quantity**, so it corrects the finances without distorting yield analytics; a reversed yield's quantity is removed from the unit-cost denominator. — `backend/app/services/dss_service.py:96-103`
- An already-reversed log, and a reversal itself, **cannot be reversed again** (HTTP 409), preventing over-correction. — `backend/app/services/ledger_service.py:98-110`
- Both original and reversal remain visible in the audit trail, and this is now surfaced in the interface: the original is struck through and marked "Reversed", the contra marked "Correction of #N". — `frontend/src/features/farm-records/FarmRecordsPage.tsx:160-200`
- Audit columns (`created_at`, `updated_at`) distinguish record birth from the domain event time the farmer is recording. — `backend/app/models/models.py:92-97`
- Relevance to Objective 3: this is what makes the shared report defensible — figures can be corrected without any record disappearing.

**BUILDABLE:** N/A — fully implemented and now reachable in the UI. The chapter under-reports a delivered mechanism; this is not a gap.

---

### 15. Chapter 3 has no subsection for the bioprocess drying module

The domain vocabulary (`CONTEXT.md`), an ADR, a pure-function service, read endpoints, tests and a seed script all exist, but Chapter 3 never describes the module. Any new subsection must state:

- A **Drying Run** is a post-harvest processing step recorded as an Operational Log with Activity Category Bioprocess, carrying inlet and outlet mass, inlet and outlet moisture content, duration, air temperature and drying method. — `backend/app/schemas/schemas.py:58-78`
- Moisture is entered on a **wet basis**, because that is what field meters report and what buyers price against, and is converted to dry basis internally for kinetics. — `backend/app/services/bioprocess_service.py:46-56`
- The payload is validated at the schema edge for physical consistency: mass cannot increase, and final moisture must be strictly below initial. — `backend/app/schemas/schemas.py:69-78`
- Derived metrics are computed **on read, never stored**: dry matter, expected outlet mass, process loss, water removed, drying rate, specific drying rate, and a Newton thin-layer drying constant per method. — `backend/app/services/bioprocess_service.py:58-125`, `backend/app/api/endpoints/bioprocess.py:30-44`
- **Marketable Mass** — outlet mass after drying — feeds an additive per-kilogram unit cost reported alongside the unchanged harvest-unit figure, coupling the module to the DSS. — `backend/app/services/dss_service.py:120-129`, `:202-207`
- Reversed runs and reversal contras are excluded from every bioprocess aggregate and from marketable mass. — `backend/app/api/endpoints/bioprocess.py:55-75`
- The decision to carry drying parameters in the log's `extra_data` JSON rather than a dedicated table is recorded as an ADR. — `docs/adr/0001-bioprocess-drying-parameters-in-extra-data.md`
- **The honest status, which must be stated:** none of this is reachable by a user. There is no create form for drying parameters, and `GET /bioprocess/summary` and `GET /bioprocess/{log_id}` have no client method and no screen. Drying runs can currently be created only through the API or the seed script. The Bioprocess option was removed from the activity dropdown this week because, without parameter fields, selecting it always failed validation with HTTP 422. — `backend/app/api/endpoints/bioprocess.py:46`, `:128`; `grep -rn bioprocess frontend/src` matches only the `Category` type; `frontend/src/features/farm-records/FarmRecordCreateForm.tsx:7-22`

**BUILDABLE: Yes — the second most valuable build available.** A drying-parameters sub-form revealed when Bioprocess is selected (seven numeric fields plus a method select, validated client-side against the same bounds the schema enforces) would make the entire module reachable, restore the Bioprocess entry path removed this week, and turn `marketable_mass_kg` and `unit_cost_per_kg_marketable` into visible figures. Estimate **2–3 hours** for the form, plus **1–2 hours** for a read screen over `GET /bioprocess/summary`. No backend work — it is all built and tested. Write this subsection in the present tense only if that is done; otherwise it must carry the "specified but not reachable" statement above.

---

# Other built-but-unreachable capabilities

Flagged per instruction: code that already exists where only a client method or a screen is missing. Each is a claim that could be made true cheaply.

| Capability | Backend | Missing | Estimate |
|---|---|---|---|
| **Model quality metrics (R², MAE)** — the example named in the brief | `GET /dss/model` (`api/endpoints/dss.py:47`) serves `r2` and `mae` from `ml/train.py:93-94` | No `apiClient` method, no UI. §3.6.5 ¶[136] and §2.6.4 ¶[74] both claim these are "expressed" | **30 min** — add `dssService.getModel()` and a line on `DSSPredictPage` |
| **Bioprocess read endpoints** | `GET /bioprocess/summary`, `GET /bioprocess/{log_id}` | No client method, no screen | 1–2 h (see item 15) |
| **Marketable-mass unit cost** | `dss_service.py:207` | Not in `types/domain.ts`, not rendered | 20 min once drying runs exist |
| **Retrain trigger** | `POST /dss/train` (`dss.py:39`) | `dssService.train()` exists at `apiClient.ts:120`, called from nowhere | 20 min for an admin control |
| **Transactions list** | `GET /ledger/transactions` (`ledger.py:25`) | `getTransactions()` defined at `apiClient.ts:90`, never called | 1 h for a transactions view |
| **Tax categorisation** | `tax_category` captured and stored (`ledger_service.py:38`) | Read by no report, export or view. PRD story 7 claims it streamlines tax reporting | 40 min — group the CSV export and add a P&L column |

**Recommended build order, maximising true claims per hour:** R²/MAE client method (30 min) → DSS ranking one-liner (10 min) → break-even (45 min) → depreciation (1 h) → tax-category reporting (40 min) → drying sub-form (2–3 h) → USSD webhook (4–6 h).

That sequence retires items 6, 7 and 9 outright, restores the Section 3.3.2 accessibility requirement and item 10, and makes the additions in item 15 writable in the present tense — roughly a day and a half of work in total.
