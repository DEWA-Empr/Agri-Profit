# 2. Derived fixed-cost overlay, and three temporary domain assumptions

Status: Accepted

## Context

The enterprise-economics work derives two conditional break-even prices per
marketable kilogram: one covering cash cost, one covering total cost. The second
needs a fixed cost, apportioned to a crop, over a period. The ledger supplies
none of those three things directly, and each gap was closed by an assumption
rather than a measurement. This ADR states all three in one place so they can be
cited, argued with and — when the model grows the entities they stand in for —
removed together.

What exists today:

- **`equipment`** carries `purchase_price` and `depreciation_rate`, both
  nullable. There is no acquisition date and no accumulated-depreciation column,
  so an asset's remaining life cannot be measured.
- **No field, plot or area entity.** Register item P2-14. There is therefore no
  physical base — hectares, plot count, machine hours per crop — to apportion a
  farm-level cost across crops with.
- **No season entity.** An Operational Log carries a timestamp and a crop, and
  nothing groups a set of logs into one production cycle.
- **An immutable, paired-write ledger.** Every Financial Transaction is paired
  with an Operational Log, and correction is by contra entry, not by mutation.

## Decision

### 1. Depreciation is a derived overlay, computed at report time, never posted

The periodic charge is `purchase_value × depreciation_rate × (period_days ÷
365)`, computed in `enterprise_service.depreciation_overlay` when a report is
read. No depreciation Financial Transaction is ever written by this code path.

Posting synthetic depreciation rows would require either unpaired entries — a
direct violation of the paired-write invariant — or fabricated Operational Logs
describing events that did not happen. Neither is acceptable in a ledger whose
whole claim is that every row records something a farmer did. The overlay is
consistent with `unit_cost_per_kg_marketable` and every other derived figure on
this platform: computed, transparent, recomputable, never stored.

Three simplifications ride along, stated rather than hidden: straight line, no
salvage value, and no accumulated-depreciation floor, so an asset held past its
implied life keeps charging. The charge is therefore an upper bound. Equipment
with a null or zero rate contributes nothing and is counted in
`equipment_unrated_count`, so a partial overlay is visible as partial rather
than being read as a small true fixed cost.

A **recorded** `DEPRECIATION` cost subtype on a real ledger row is a different
thing entirely and stays in its own bucket, `fixed_cost_recorded`. The two are
never added together.

### 2. TEMPORARY: fixed cost is allocated to crops in proportion to direct cost

`allocated_fixed = period_fixed_cost × (crop_direct_cost ÷ total_direct_cost)`.

Proportional-to-direct-cost is the standard fallback where no physical base
exists, and it is an **assumption, not a measurement**. It will over-allocate to
an input-intensive crop and under-allocate to a land-intensive one, because
direct cost is not a proxy for the share of a tractor's life a crop consumed.

Where the total direct cost is zero, every share and every allocation is `None`.
An even split would invent an allocation base that does not exist; a zero would
claim the fixed cost had disappeared. "Undefined" is the better answer, in the
same way a unit cost over no yield is undefined.

The allocation base is computed **farm-wide, before any crop filter is applied**.
Deriving it from a filtered subset would give a single filtered crop a share of
1.0 and hand it the entire overlay — the same figure would change depending on
how it was requested.

### 3. TEMPORARY: a season is a calendar year of recorded yield

`get_yield_baseline` groups a crop's yield observations by
`timestamp.year`, sums within the year, and treats each year as one season for
the Olympic average. Several yield logs in one year are one season, not several.

This is the only grouping the model can express. It is **wrong wherever a crop
does not align with the calendar**: a double-cropped season straddling December
becomes two seasons or one depending on which side of the new year the harvest
was logged, and a single long cycle spanning a year boundary is split in half.
For a single rain-fed cycle harvested mid-year — the case the platform is built
around — it is correct.

`n_seasons` is reported in **every** branch of the response, including the ones
that return no average at all, so a null Olympic average is never read without
the count that explains it. One season and ten seasons are different reasons for
the same null.

### 4. The depreciation window defaults to the ledger span but can be pinned

By default `period_days` runs from the farm's first surviving log to its last,
inclusive, so the charge lines up with the costs it is compared against. An
optional `period_days` query parameter overrides it, and `period_source`
(`"derived"` | `"specified"`) travels in the response.

The override is a **reproducibility** measure, not a convenience. A derived span
widens every time a log is entered; the charge is proportional to the span; the
allocation is drawn from the charge; the break-even price to cover total cost is
drawn from the allocation. So entering an unrelated log silently moves a price
that was already reported, quoted in a document, or written down — and nobody
can re-derive it afterwards, because the window it was computed over no longer
exists. A pinned window makes a figure reproducible; `period_source` makes the
two cases distinguishable, so a reader comparing reports knows whether a moved
price means the farm changed or only the window did.

An explicit period is used as given and is **not** clamped to the ledger span. A
window longer than the records is a legitimate question — what a full season of
machine wear costs against a part-season of logs — and silently shrinking it
would answer a different one. It is bounded above at a century of days, beyond
which the caller is not describing a reporting period.

## Consequences

- Every figure that depends on allocated fixed cost — the break-even price to
  cover total cost, the total-cost column of the sensitivity matrix — inherits
  assumptions 2 and 4. None of them is a measurement, and the write-up must not
  present them as one.
- The operating expense ratio is deliberately **outside** this blast radius. It
  is a cash measure: the allocated overlay has no parameter in
  `operating_expense_ratio_pct` and therefore no route into its numerator, so it
  stays comparable to published benchmarks. It is reported on the cost-structure
  response, not the break-even one, because it is naira over naira rather than
  a figure per marketable kilogram.
- Assumptions 2 and 3 are **removable**, and removing them is the point of
  stating them. A Field/Plot entity replaces proportional allocation with an
  area or machine-hour base; a Season entity replaces calendar-year grouping
  with a real production cycle. Both are additive: the pure functions in
  `enterprise_service` take a base and a set of season yields as arguments, so
  a better source for either changes the caller, not the arithmetic.
- Assumption 1 is **not** expected to be removed. Deriving depreciation on read
  is the correct design for an immutable paired-write ledger, not a stopgap.
- A depreciation rate of exactly zero is rejected rather than stored. The
  overlay's guard treats zero and null identically, so a stored zero would be a
  value claiming to be a measurement while behaving as an absence. Requiring
  such an asset to be entered as genuinely unrated preserves the distinction
  between an unclassified state and a measured one, consistent with the
  treatment of unclassified cost and of the safe-storage verdict for an unknown
  crop.
- No migration, no new table, no new column. Consistent with ADR-0001: the
  contribution is in what is derived on read, not in what is stored.
