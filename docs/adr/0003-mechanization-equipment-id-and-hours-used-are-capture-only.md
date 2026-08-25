# 3. `equipment_id` and `hours_used` are capture-only metadata

Status: Accepted

Date: 2026-08-25

## Context

A `MECHANIZATION` operational log may carry a validated `extra_data` object,
`MechanizationParams` (`backend/app/schemas/schemas.py`), with three fields:

| Field | Type | Validation |
| --- | --- | --- |
| `cost_subtype` | `Literal["FUEL", "LUBRICANTS", "REPAIRS", "MACHINERY_HIRE", "DEPRECIATION"]` | required; outside the taxonomy → 422 |
| `equipment_id` | `int \| None` | optional, unconstrained |
| `hours_used` | `float \| None` | optional, `0 < h ≤ 1000` |

The 2026-08-25 audit (`docs/STATE_REPORT_2026-08-25.md` §10.3) established, by
search across the whole backend, that only the first of these three is read by
anything. `cost_subtype` is the key `cost_behaviour_for` looks up, so it decides
which bucket a row's money lands in and therefore every cost-structure,
break-even and sensitivity figure downstream. `equipment_id` and `hours_used` are
written to the database and never read out of it by any service.

That absence was flagged as a defect-shaped observation: a validated field with
no consumer either wants a consumer or wants deleting. This ADR records that
neither is correct here, and why, so the state is a decision rather than an
oversight — and so a reviewer who repeats the audit finds the answer instead of
re-opening the question.

## Decision

**`equipment_id` and `hours_used` are classified as capture-only metadata.**
They are validated at the schema edge, persisted verbatim in
`operational_logs.extra_data`, and consumed by nothing. That is the whole of
their contract, and it is deliberate.

They are **not** load-bearing domain inputs. No derived figure anywhere in the
platform changes if either is present, absent, or changed.

## Rationale

### Why not give them a consumer

The obvious consumer would be a machine-hour cost rate — cost per hour, machine
utilisation, an hours-based apportionment of fixed cost to a crop. Writing one
would mean inventing agricultural-economics arithmetic that **no specification in
this repository defines**:

- `CONTEXT.md`'s glossary has no machine-hour, utilisation or machine-rate term.
- ADR-0001 (drying parameters) and ADR-0002 (fixed-cost overlay) define no such
  metric. ADR-0002 in fact records the opposite: it apportions fixed cost by
  **revenue share**, and explicitly names the absence of "hectares, plot count,
  machine hours per crop" as the reason a physical base was unavailable.
- The enterprise-economics ticket (`.scratch/TICKET_enterprise_economics.md`)
  specifies `hours_used` only as a bounded, nullable capture field — bounds and
  their rejection cases are named requirements; no consumer is.

The thesis defends the numbers this platform produces. A machine-hour rate
introduced now would be arithmetic with no cited source, feeding cost-structure
and break-even figures that are quoted in a defended chapter. Inventing it to
close an audit item would make the evidence worse, not better.

An hours-based apportionment is also **not** merely undefined but currently
under-determined: `hours_used` is populated on three of the seed's rows and is
optional on every write, so any total built from it would be a total over an
unknown fraction of actual machine use. A figure like that is worse than no
figure, because it reads as measured.

### Why not delete them

Deleting them would drop behaviour the specification does require:

- The bounds on `hours_used` (`0 < h ≤ 1000`) are a **named test case** in the
  ticket's acceptance criteria, and
  `test_mechanization_hours_used_out_of_range_rejected` asserts both ends.
- The seed script (`backend/scripts/seed_bioprocess_demo.py`) writes eight
  mechanisation logs, six of which carry at least one of the two fields:
  `equipment_id` on five, `hours_used` on three, both together on two. Those are
  live rows in the demo database thesis evidence is drawn from. Removing the
  fields would either invalidate the rows or silently discard their content.
- They are the only record of *which asset* a fuel or repair cost belongs to.
  Once captured, a future ticket that does define a consumer — with a citation —
  starts from real recorded data rather than from nothing. Deleting them today
  guarantees that ticket starts from zero history.

### Why the classification is safe to freeze

Capture-only is a claim that can be falsified, so it is tested rather than
asserted. `test_mechanization_params_are_captured_and_round_trip_intact`
(`backend/tests/test_api.py`) pins both halves:

1. the two fields survive a write and a **read-back** unchanged, not merely a
   create response; and
2. the derived cost-structure response contains neither field's name and is
   driven by `cost_subtype` alone.

Two companion tests fix the edges: omitting both fields is accepted
(`test_mechanization_omitting_the_capture_only_fields_is_accepted`) — a farmer
classifying a cost must not be forced to invent an asset id or an hour count —
and out-of-range hours are rejected at the edge as a 422.

## Consequences

- Chapter Four may describe mechanisation cost classification as driven by
  `cost_subtype`. It must **not** claim any machine-hour, utilisation or
  cost-per-hour analysis; none exists.
- `LIMITATIONS.md` carries this as a scope boundary, not a defect.
- Any future ticket introducing a consumer must supply a cited costing method
  first, and must reckon with `hours_used` being optional — a rate computed over
  partially populated hours is not a measurement.
- Re-running the §10.3 audit will keep finding "no consumer". That finding is
  now expected output, and this ADR is its answer.
