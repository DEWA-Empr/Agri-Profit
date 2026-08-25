# TICKET — Enterprise economics: cost classification, dual break-even, sensitivity

**Repo:** `C:\Users\DELL\Desktop\Agri P`
**Branch:** `feat/enterprise-economics` (cut from current `feat/bioprocess-drying` head)
**Label:** `ready-for-agent`
**Status of thesis:** defended 19 August 2026, no corrections outstanding. Bundle size and build hash are therefore free to change; §4.6 already needs re-measurement after the lazy-loading work.

**Why this exists:** the platform computes cost per unit against a single undifferentiated cost pool. It cannot answer the two questions a smallholder actually faces mid-season — *what price must I get to cover what I have already spent in cash?* and *what price must I get to cover everything, including the machine wearing out?* Those are different numbers, they diverge, and the gap between them is the whole of the fixed-cost argument. This ticket makes cost structure a first-class property of the ledger and derives conditional break-even prices, a yield sensitivity matrix and a partial-budget calculator from it.

**Why it is defensible as software engineering, not agricultural economics:** the contribution is that a cost taxonomy is enforced at the schema edge on a JSON payload without a migration, that classification coverage is reported as a first-class data-quality metric rather than silently defaulted, and that a non-transactional derived overlay (depreciation) is computed at report time and joined to an immutable ledger without writing to it. The economics is the domain being modelled. The modelling is the contribution.

---

## 0. Read before writing any code

Read these and report a one-paragraph summary **before** starting Phase 1. Do not assume the shapes below are correct.

```
CONTEXT.md
docs/adr/                                  (all existing ADRs)
backend/app/models/models.py
backend/app/schemas/schemas.py
backend/app/core/enums.py
backend/app/services/ledger_service.py
backend/app/services/dss_service.py
backend/app/services/bioprocess_service.py   (this is the pattern to copy)
backend/app/services/equipment_service.py
backend/app/api/endpoints/dss.py
backend/app/api/deps.py
backend/tests/test_bioprocess_service.py     (fixture style to match)
backend/scripts/seed_bioprocess_demo.py
frontend/src/                                (locate the DSS view and the log-entry form)
```

Specifically establish:

1. The exact conditional-validation mechanism used to apply `DryingParams` only when `activity_type == BIOPROCESS`. Paste it. **This ticket reuses that mechanism; it does not invent a second one.**
2. Every column on the equipment model, in particular the exact name, type and nullability of the depreciation rate field, whether a purchase value or acquisition cost exists, and whether an acquisition date exists.
3. Whether any equipment rows carry a non-zero depreciation rate today, and how many carry zero or null. Report counts.
4. Where per-crop cost aggregation happens in `dss_service.py` after the bioprocess work, and how `unit_cost_per_kg_marketable` is currently assembled.
5. How reversals are excluded from aggregation, and whether the contra-attribution fix from `6992d1c` is in the code path this ticket will extend.
6. Whether `extra_data` is read anywhere in aggregation today, or only on detail reads. This determines whether Phase 2 needs a query change or only a projection change.
7. **Anything in this ticket that will not work as written given what you found.** Most important answer.

---

## 1. Decisions already made — do not relitigate

| Decision | Rationale |
|---|---|
| Cost subtype lives in the existing `extra_data` JSON column, validated by a Pydantic model applied conditionally on `activity_type` | Identical to `DryingParams`/`BIOPROCESS`. No migration. ADR-0001 already establishes the reasoning; this applies it a second time, which converts a one-off decision into a design pattern. |
| Classification is a **three-state** property: `VARIABLE`, `SEMI_VARIABLE`, `FIXED` — plus a fourth outcome, `UNCLASSIFIED`, for rows carrying no subtype | `Repairs` is genuinely semi-variable and pretending otherwise is a worse answer than reporting it. Legacy rows have `extra_data = NULL` and must never be defaulted into a bucket. |
| Every break-even figure is accompanied by a **classification coverage** percentage | The same discipline as null-for-unknown-crop and null-for-mixed-units. A break-even computed over 60% classified cost is a different claim from one computed over 100%, and the reader must be able to see which they have. |
| Depreciation is a **derived overlay computed at report time, never posted to the ledger** | Posting synthetic depreciation transactions would either violate the paired-write invariant or require unpaired rows in an immutable ledger. Consistent with `unit_cost_per_kg_marketable`: computed, not stored. |
| Fixed cost is allocated to crops **proportionally to each crop's recorded direct cost** | There is no field, plot or area entity, so no physical allocation base exists (register P2-14). Proportional allocation is the standard fallback and it is declared as an assumption in an ADR, exactly as N-03 declares the whole-harvest-drying assumption. |
| The secondary-revenue offset in the source framework is **omitted, not zeroed** | No secondary-enterprise revenue category exists in the ledger. A hard-coded zero offset would imply the concept is modelled and measured at nil. Omission with a stated reason is honest; a zero is not. |
| Sensitivity output is labelled **conditional, never predictive** | The existing break-even yield is deliberately retrospective — "was N kg at the price you got" — precisely to avoid implying a price forecast. A matrix over yield at a user-stated price is conditional. The interface copy must carry the conditional explicitly or this feature breaks the platform's strongest reporting convention. |
| Olympic average returns `None` below three seasons | Same shape as the unknown-crop storage verdict. Build the function, let the platform grow into the data. |
| Write ADR-0002 covering the depreciation overlay and the proportional allocation assumption | Repo convention, and it becomes the citable artifact for the write-up. |

---

> **Not on this list:** the realised-unit-price denominator at
> `dss_service.py:225` is an **open decision**, not a settled one. See §12.

## 2. Phase 1 — Domain and documentation

Add to `CONTEXT.md` under a new **Cost structure** heading, in house style (definition, then `_Avoid_:` line):

- **Cost Subtype** — a classification carried on a cost-bearing Operational Log identifying whether the expense scales with production. One of Fuel, Lubricants, Repairs, Machinery Hire, Depreciation for mechanisation activity, with equivalent sets for other categories. Stored as a structured parameter in `extra_data`, not as a ledger column. *Avoid:* cost type, expense class, cost code.
- **Cost Behaviour** — the derived property of a Cost Subtype describing how it responds to output: Variable (scales with production), Semi-variable (a fixed component plus a variable component), or Fixed (constant regardless of output). Rows carrying no subtype are Unclassified and enter no behaviour bucket. *Avoid:* fixed/variable, cost nature, direct/indirect.
- **Classification Coverage** — the proportion of a crop's or farm's recorded cost that carries a Cost Subtype, reported alongside every figure derived from cost behaviour. A break-even price computed over partially classified cost is a weaker claim than one computed over fully classified cost, and the figure states which. *Avoid:* completeness, data quality score, coverage.
- **Break-even Price to Cover Cash Cost** — the price per marketable kilogram at which a crop's classified variable and semi-variable costs would be recovered. The short-run continuation threshold: below it, each additional kilogram sold loses money outright. *Avoid:* break-even, breakeven price, VC breakeven.
- **Break-even Price to Cover Total Cost** — the price per marketable kilogram at which every recorded cost plus allocated fixed cost would be recovered. The long-run survival threshold. *Avoid:* break-even, full cost price, TC breakeven.
- **Allocated Fixed Cost** — a crop's share of the farm's periodic fixed cost, derived at report time from equipment depreciation and apportioned in proportion to the crop's recorded direct cost. Never a ledger entry. *Avoid:* overhead, fixed cost, indirect cost.
- **Partial Budget** — an appraisal of a single proposed change, computed as (additional revenue + reduced cost) − (lost revenue + additional cost). Evaluates only the quantities the change affects, so it requires no complete enterprise budget. *Avoid:* ROI, cost-benefit analysis, business case.
- **Olympic Average Yield** — a yield baseline computed by discarding exactly one highest and one lowest observation from a crop's recorded season yields and averaging the remainder. Requires at least three seasons; returns undefined below that. *Avoid:* trimmed mean, adjusted average, normalised yield.

> **Naming discipline — read this twice.** The platform now has three distinct metrics that a careless reader will call "break-even": the existing retrospective **break-even yield**, and the two new conditional **break-even prices**. Register finding P1-04 records exactly this failure mode, where the same model carried two tier numbers in one document. Use the full distinct names in code identifiers, API field names, interface labels and the write-up. Never the bare word.

Update the existing **Bioprocess** and **Mechanisation** entries to point at Cost Subtype.

---

## 3. Phase 2 — Schema and classification

In `backend/app/schemas/schemas.py`:

```python
class CostBehaviour(str, Enum):
    VARIABLE      = "VARIABLE"
    SEMI_VARIABLE = "SEMI_VARIABLE"
    FIXED         = "FIXED"

class MechanizationParams(BaseModel):
    cost_subtype: Literal["FUEL", "LUBRICANTS", "REPAIRS", "MACHINERY_HIRE", "DEPRECIATION"]
    equipment_id: int | None = None
    hours_used: float | None = None      # > 0, <= 1000
```

Module-level constant, one place, easy to cite and easy to change:

```python
# TODO(cite): cost-behaviour classification follows standard enterprise-budget
# practice (variable = scales with output; fixed = independent of output).
# Cite an agricultural economics text or extension enterprise-budget guide
# before submission. "The taxonomy was supplied" is not a citation.
COST_BEHAVIOUR: dict[tuple[str, str], CostBehaviour] = {
    ("MECHANIZATION", "FUEL"):           CostBehaviour.VARIABLE,
    ("MECHANIZATION", "LUBRICANTS"):     CostBehaviour.VARIABLE,
    ("MECHANIZATION", "REPAIRS"):        CostBehaviour.SEMI_VARIABLE,
    ("MECHANIZATION", "MACHINERY_HIRE"): CostBehaviour.VARIABLE,
    ("MECHANIZATION", "DEPRECIATION"):   CostBehaviour.FIXED,
    ("SEED",      None):                 CostBehaviour.VARIABLE,
    ("FERTILIZER", None):                CostBehaviour.VARIABLE,
    ("LABOUR",    None):                 CostBehaviour.VARIABLE,
    ("BIOPROCESS", None):                CostBehaviour.VARIABLE,
}
```

Structure the constant so `LABOUR` can later split into permanent and casual by the same mechanism. **Do not build that split now** — it needs a subtype model of its own and it is not on the critical path.

Validation requirements, all returning **422** and never 500:

- An unrecognised `cost_subtype` for `MECHANIZATION` → reject.
- `hours_used` non-positive or above 1000 → reject.
- **A non-`MECHANIZATION`, non-`BIOPROCESS` log with an arbitrary `extra_data` dict must still succeed exactly as it does today.** Validate conditionally. Tightening `extra_data` globally breaks unrelated existing tests.
- A `MECHANIZATION` log with `extra_data = None` must still succeed. Legacy rows exist and classification is opt-in; refusing them would be a breaking change to a shipped write path.

Lookup must be a pure function returning `CostBehaviour | None`. `None` means unclassified. **Never default to `VARIABLE`.**

---

## 4. Phase 3 — Enterprise service (use the `tdd` skill; tests first)

New file `backend/app/services/enterprise_service.py`. **Pure functions. No database access, no I/O, no imports from models or endpoints.** Numbers and plain dicts in, numbers out. `numpy` only where genuinely needed; most of this is arithmetic. This is the part that is graded as engineering.

### 4.1 Cost structure summary

Given a list of `(amount, activity_category, cost_subtype)` tuples, return:

```
variable_cost         sum where behaviour == VARIABLE
semi_variable_cost    sum where behaviour == SEMI_VARIABLE
fixed_cost_recorded   sum where behaviour == FIXED
unclassified_cost     sum where behaviour is None
total_recorded_cost   sum of all
cash_cost             variable_cost + semi_variable_cost
classification_coverage_pct   100 * (total_recorded - unclassified) / total_recorded
```

`classification_coverage_pct` returns `None` when `total_recorded_cost == 0` — never 100, and never 0. There is no coverage of nothing.

Semi-variable folds into `cash_cost` for computation and is **reported separately** so a reader can see the assumption. Do not silently merge it.

### 4.2 Depreciation overlay

```
annual_charge_ngn  = purchase_value_ngn * depreciation_rate
period_charge_ngn  = annual_charge_ngn * (period_days / 365)
```

Straight-line, no salvage value, no declining balance — state all three simplifications in the docstring. Equipment with a null or zero rate contributes zero and is **counted and reported** as unrated, so the reader knows the overlay is partial.

### 4.3 Proportional fixed-cost allocation

```
crop_share      = crop_direct_cost / total_direct_cost_all_crops
allocated_fixed = period_fixed_cost * crop_share
```

Where `total_direct_cost_all_crops == 0`, return `None` for every allocation. Do not divide by zero and do not allocate evenly as a fallback — an even split would invent an allocation base that does not exist.

### 4.4 Dual break-even price

```
break_even_price_cash_ngn_per_kg  = cash_cost / marketable_mass_kg
break_even_price_total_ngn_per_kg = (total_recorded_cost + allocated_fixed) / marketable_mass_kg
```

**Note the deliberate asymmetry and document it in the docstring.** The cash figure uses only classified variable and semi-variable cost. The total figure uses every recorded cost plus the overlay. Unclassified cost therefore sits inside the total figure but outside the cash figure, so it inflates the apparent gap between them. This is why `classification_coverage_pct` must travel with both numbers, and why the response reports variable, semi-variable, unclassified and allocated-fixed as four separate lines rather than two.

Both return `None` where `marketable_mass_kg` is zero, null or absent — preserving the existing contract that unit cost is undefined rather than a fabricated zero.

### 4.5 Yield sensitivity matrix

For a baseline marketable mass and a list of percentages (default 75, 90, 100, 110, 125), return per row: percentage, yield in kg, cash break-even price, total break-even price. Pure arithmetic on §4.4.

Label the output `conditional`. It answers *if you harvest this much, what price covers your costs* — it forecasts neither yield nor price.

### 4.6 Operating expense ratio

```
operating_expense_ratio_pct = 100 * cash_operating_cost / revenue
```

Use cash operating cost — variable, semi-variable and unclassified recorded cost — and **exclude the depreciation overlay**, since the ratio is conventionally a cash measure and a non-cash overlay in the numerator would make it incomparable to any published benchmark. State that in the docstring. Returns `None` at zero revenue.

### 4.7 Partial budget

```
net_change_ngn = (added_revenue + reduced_cost) - (lost_revenue + added_cost)
```

Four inputs, all `>= 0`, all required. Return the net change signed and unclamped, plus each of the four inputs echoed back so the interface can show the working. A negative result is a valid and useful answer; never suppress it.

### 4.8 Olympic average yield

Given a list of season yields: discard **exactly one** maximum and **exactly one** minimum instance, then average the remainder. Return `None` for fewer than three observations.

> The single-instance rule is the trap. In the verification dataset the minimum value 589 appears twice; removing both ties gives the wrong answer. Remove one occurrence, not all occurrences of the extreme value. Write the test that catches this.

Also return the grand average and the count discarded, so the difference between the two baselines is visible rather than asserted.

---

## 5. Phase 4 — Endpoints

Extend the existing DSS response rather than adding a parallel surface.

- **`GET /dss/cost-structure?crop=`** — the §4.1 summary per crop and farm-wide, with classification coverage.
- **`GET /dss/break-even-price?crop=`** — both prices, the four cost lines, coverage, and the count of unrated equipment.
- **`GET /dss/sensitivity?crop=&percentages=`** — the §4.5 matrix.
- **`POST /dss/partial-budget`** — four numbers in, net change out. Stateless; writes nothing.
- **`GET /dss/yield-baseline?crop=`** — Olympic and grand average, or nulls with a reason.

All routes through the existing farm-scoping dependency. Cross-farm read → 404, consistent with every other resource; add a test.

**Reversal handling.** Reversed logs and reversal logs are excluded from every cost aggregation. A reversal carries no subtype, so it must not enter a classification bucket and must not depress classification coverage. Add an explicit test for the coverage case — this is the subtle one and it is easy to get wrong.

---

## 6. Phase 5 — Multi-crop seed

Extend `seed_bioprocess_demo.py`, idempotent by `client_id`, **leaving every existing maize record untouched** so the ₦35.00 / ₦41.67 figures in §4.3.2 remain exactly reproducible.

Add:

- **Cowpea** — profitable, with mechanisation costs carrying subtypes, with a drying run recording visible process loss.
  Cowpea's drying run must record an observed outlet mass that visibly diverges
  from the dry-matter prediction — process loss on the order of 2–4%, matching the
  seeded maize in kind. A run entered within 0.01% of theoretical demonstrates
  nothing about the observed-vs-predicted distinction that Chapter Four §4.3.2
  turns on. Do not seed a well-behaved run.
- **Sorghum** — input costs recorded, no sale. The realistic loss case, and the one the farmer most needs to see.
- **One legacy-shaped mechanisation row** with `extra_data = NULL`, so classification coverage is visibly below 100% in the demonstration. Do not seed a tidy 100%.
- **One equipment record** with a non-zero depreciation rate, and **one with a null rate**, so the unrated count is non-zero in the demo.

Retrofit subtypes onto the existing maize mechanisation costs **only if** doing so leaves the §4.3.2 unit-cost figures bit-identical. If it would change them, add new rows instead and say so in the commit message.

---

## 7. Phase 6 — Frontend (only if the backend is green)

Route-level lazy loading is already in place, so a new view does not regress first-load cost. **Add no new dependency.**

- **Cost structure panel** on the DSS view: four stacked lines (variable, semi-variable, unclassified, allocated fixed) with the coverage percentage stated as text, not as a gauge. A gauge implies a target; there is none.
- **Dual break-even price**, both figures side by side with their full distinct labels, and a one-line plain reading: the cash figure is the price below which each kilogram sold loses money now; the total figure is the price that also covers the machine wearing out.
- **Sensitivity table**, five rows, with the conditional stated in the heading — *if you harvest X and sell at Y*. Not a chart. A table cannot be misread as a forecast; a line going up and to the right can.
- **Partial budget form**, four inputs and a signed result. Fully offline-capable: it touches no ledger data.
- **Marketable unit cost line** — if Phase 0 has not already shipped it, ship it here. It has been computed and returned by the API and rendered nowhere for weeks.

---

## 8. Test fixtures — hand-calculated, must pass exactly

`pytest.approx(..., rel=1e-4)`.

### Fixture A — classification and coverage

Maize costs: fuel ₦1,200; machinery hire ₦800; repairs ₦500; fertilizer ₦900; labour ₦600; one legacy mechanisation row ₦400 with `extra_data = NULL`.

| Quantity | Expected |
|---|---|
| variable_cost | ₦3,500.00 |
| semi_variable_cost | ₦500.00 |
| unclassified_cost | ₦400.00 |
| total_recorded_cost | ₦4,400.00 |
| cash_cost | ₦4,000.00 |
| classification_coverage_pct | 90.9091 % |

### Fixture B — depreciation overlay and allocation

Equipment: purchase value ₦240,000, rate 0.10/yr. Period 30 days. Second equipment record with a null rate.

| Quantity | Expected |
|---|---|
| annual_charge | ₦24,000.00 |
| period_charge (30 d) | ₦1,972.60 |
| equipment_unrated_count | 1 |

Then, for allocation, use a 365-day period charge of ₦2,000.00 (i.e. treat the period fixed cost as given) against maize direct ₦4,400 and cowpea direct ₦1,600:

| Quantity | Expected |
|---|---|
| total_direct_all_crops | ₦6,000.00 |
| maize_share | 0.733333 |
| maize_allocated_fixed | ₦1,466.67 |
| cowpea_allocated_fixed | ₦533.33 |
| maize_total_cost | ₦5,866.67 |

### Fixture C — dual break-even price

Maize, marketable mass 84.0 kg (the existing demo figure).

| Quantity | Expected |
|---|---|
| break_even_price_cash | ₦47.6190 / kg |
| break_even_price_total | ₦69.8413 / kg |
| classification_coverage_pct | 90.9091 % |

Assert explicitly that the two prices are **not equal**, and that the cash figure is strictly the lower. A test that fails if they are ever made equal is worth more than one that checks each value, because collapsing the two is the specific error this module exists to prevent — exactly as Fixture A of the bioprocess suite traps water-removed against process-loss.

### Fixture D — sensitivity matrix

Baseline 84.0 kg, cash ₦4,000, total ₦5,866.6667.

| Yield % | Yield kg | Cash ₦/kg | Total ₦/kg |
|---|---|---|---|
| 75 | 63.0 | 63.4921 | 93.1217 |
| 90 | 75.6 | 52.9101 | 77.6014 |
| 100 | 84.0 | 47.6190 | 69.8413 |
| 110 | 92.4 | 43.2900 | 63.4921 |
| 125 | 105.0 | 38.0952 | 55.8730 |

### Fixture E — operating expense ratio

Maize revenue ₦45,000, cash operating cost ₦4,400 (including unclassified, excluding the overlay).

| Quantity | Expected |
|---|---|
| maize opex ratio | 9.7778 % |
| farm-wide (₦6,000 / ₦45,000) | 13.3333 % |

Assert that the overlay is absent from the numerator: adding ₦2,000 of allocated fixed cost must leave this figure unchanged.

### Fixture F — partial budget

Solar dryer appraisal. Added revenue ₦12,000; reduced cost ₦3,000; lost revenue ₦0; added cost ₦9,500 → **net +₦5,500.00**.

Negative case: ₦4,000; ₦1,000; ₦500; ₦9,500 → **net −₦5,000.00**. Must return the negative, not zero and not an error.

### Fixture G — Olympic average, and the tie trap

Verification dataset, arithmetic independently confirmed: `589, 632, 646, 644, 610, 748, 809, 783, 589, 696, 666`

| Quantity | Expected |
|---|---|
| grand average | 673.8182 |
| olympic average | 668.2222 |
| discarded | 2 (one 809, one 589) |

**The trap:** 589 appears twice. Discarding both minima gives 678.6250, which is wrong. Write the assertion that catches it.

Second case, five maize seasons `1800, 2100, 1450, 2400, 1950`: grand 1940.0, olympic 1950.0.

Third case, two seasons → `None`, never a two-value mean.

### Fixture H — rejections and isolation

- Unrecognised `cost_subtype` → 422.
- `hours_used = 0` and `hours_used = 1001` → 422.
- A `SEED` log with an arbitrary `extra_data` dict → still 201.
- A `MECHANIZATION` log with `extra_data = None` → still 201, classified `None`.
- Zero total cost → `classification_coverage_pct` is `None`, not 100 and not 0.
- Zero marketable mass → both break-even prices `None`.
- Cross-farm read of any new endpoint → 404.
- A reversed mechanisation cost is excluded from every bucket **and does not lower classification coverage**.

---

## 9. Definition of done

- [ ] Fixtures A–H all pass.
- [ ] `enterprise_service.py` at 100% coverage — pure functions, no excuse for less.
- [ ] Overall backend coverage not below the current 91%.
- [ ] Full existing suite still green; no previously passing test modified to accommodate this work.
- [ ] `CONTEXT.md` carries the eight new terms.
- [ ] ADR-0002 written: depreciation overlay computed-not-posted, and proportional allocation as a declared assumption.
- [ ] No new Python or JavaScript dependency.
- [ ] No Alembic migration.
- [ ] Multi-crop seed runs idempotently and leaves the maize unit-cost figures bit-identical.
- [ ] Marketable unit cost per kg is visible in the interface.
- [ ] `docs/EVIDENCE.md` updated with the command producing every new figure quoted anywhere.

## 10. Explicitly out of scope

Return on assets; debt-to-equity and debt-service coverage; inventory turnover; current ratio and working capital; any bank, accounting-package or open-banking integration; remote sensing, NDVI/EVI or any satellite index; IoT soil, moisture, flow or nutrient sensors; telematics; multi-modal data fusion; declining-balance or salvage-value depreciation; the labour permanent/casual split; secondary-enterprise revenue; anything touching `backend/app/ml/`.

If you find yourself editing `ml/`, stop — you have gone out of scope.

---

## 11. What this is *not*, and why that matters to the write-up

Two research documents motivated this ticket. Both describe an instrumented farm — sensor arrays, satellite indices, accounting APIs, real-time bank feeds — and both propose dashboards that assume those feeds exist.

This ticket implements none of them, and the omission is the argument rather than a shortfall. The second document's own research gap statement is that precision platforms "excel at biophysical yield forecasting but essentially ignore production costs," leaving biological models operating in a financial vacuum. That gap is what this platform closes, and it closes it under the opposite resource assumption: no sensors, no APIs, intermittent connectivity, a farmer typing numbers into a phone. Every feature admitted to this ticket passes one filter — it is computable from records a smallholder already enters by hand.

Say that explicitly in the write-up. A platform that answers the same question as an instrumented system, from manual records, on a ₦20,950-per-month single instance, is a stronger claim than one that answers it with a sensor network. Do not present the exclusions as limitations. They are the specification.

---

## 12. Open decisions — NOT settled, do not assume either way

### OD-01 — realised unit price divides revenue by harvest quantity

`backend/app/services/dss_service.py:225`:

```python
        break_even_yield = None
        if yq is not None and yq > 0 and b["revenue"] > 0 and b["expenses"] > 0:
            unit_price = b["revenue"] / yq
            break_even_yield = b["expenses"] / unit_price
```

`yq` is the crop's **harvested** quantity, so the demo maize yields
`45,000 / 100 kg = ₦450.00/kg` and `3,500 / 450 = 7.78 kg`.

**Both candidate denominators are inferences, and neither is the transaction.**
Sale quantity is not recorded anywhere in the schema. A YIELD log carries a
harvest `quantity` and a paired credit; nothing records how much was actually
sold, or when, or in how many lots. So:

- dividing by harvest quantity (100 kg) assumes revenue is attributable to the
  mass that came off the field;
- dividing by marketable mass (84 kg) assumes the entire dried output was sold,
  in one lot, at one price.

The second is **not** "truer to the transaction" — it is a different assumption
with the same standing. Recording sale quantity would settle the question with
data instead of a convention, and that is the only change that actually resolves
OD-01 rather than relabelling it.

### The constraint that governs any change here

**Chapter Four §4.3.3 quotes ₦450/kg and a break-even of 7.8 kg on the current
convention.** So does the committed data pack, which reproduces the arithmetic
and the rounding path in full:

- `docs/ch4-data/DATA_PACK.md` §4.1 — "`unit_price = 45000.0 / 100.0 = 450.0`;
  `3500.0 / 450.0 = 7.777…`", and "**This agrees with the chapter's stated
  7.8 kg**"
- `docs/ch4-data/screenshot-runsheet.md` — the maize screenshot is specified as
  showing "**Break-even was 7.8 kg at the price you got**"

**Do not change line 225 without re-stating §4.3.3**, and without reissuing the
data pack and the affected screenshot. The figure is quoted in a defended
chapter; the arithmetic is not free to move on its own.

### Bearing on Phase 3

§4.4's two new break-even **prices** are denominated per marketable kilogram.
That is a deliberate choice for the new metrics and does **not** retroactively
settle OD-01 for the existing retrospective break-even **yield** — the two can
legitimately differ, provided the interface names each denominator, which is now
what the DSS panel and the investor report both do. What must not happen is a
silent third convention appearing in Phase 3 (register P1-04).

### Interface copy

`DecisionSupport.tsx` renders this as "at the price you got". Given that the
price is an inference from an unrecorded sale quantity, that wording overstates
what is known regardless of which denominator wins. Rewording the label is
cheap, touches no arithmetic, and does **not** disturb §4.3.3's figures — it can
be done independently of OD-01 and probably should be.

**Status:** open. Decide before Phase 3. Untouched by `2a282ba` and `502dced`,
which are presentation-only and change no service code.
