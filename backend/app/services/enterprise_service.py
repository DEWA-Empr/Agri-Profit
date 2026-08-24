"""Enterprise economics — pure functions (enterprise-economics ticket, Phase 3).

Numbers and plain dicts in, numbers out. This module has NO database access, NO
I/O, and no imports from models or endpoints. Every derived economic figure is
computed here so it can be tested in isolation and reused on read (the endpoints
in Phase 4 aggregate ledger rows and call into this module).

Conventions:

  * Cost behaviour is a THREE-state classification (variable, semi-variable,
    fixed) plus a fourth outcome, unclassified, for rows carrying no cost
    subtype. An unclassified row is never defaulted into a bucket.
  * Every figure derived from cost behaviour travels with a classification
    coverage percentage, so a reader can tell a claim made over fully classified
    cost from one made over partially classified cost.
  * Depreciation is a derived overlay computed at report time. Nothing here is
    ever posted to the ledger.
  * `None` means undefined, never zero. Coverage of nothing, a break-even price
    on nothing marketable and an allocation with no base are all undefined.
"""
from typing import Optional, Sequence

from ..schemas.schemas import CostBehaviour, cost_behaviour_for

# The lookup is imported rather than re-declared: the taxonomy has exactly one
# home (schemas.COST_BEHAVIOUR), and this module reads it. Importing the schema
# constant is not database access and does not make these functions impure.
#
# RELATIVE, like every other import in this package. An absolute
# `backend.app.schemas...` resolves under pytest, which runs from the repo root
# with `backend` importable as a package, and fails under the container, whose
# application root is the `app` directory and which has no `backend` module at
# all. The test suite therefore could not catch it: the only environment that
# reproduces it is the deployed one.


# --- 4.1 Cost structure summary --------------------------------------------

def cost_structure(
    entries: Sequence[tuple[float, str, Optional[str]]],
) -> dict:
    """Summarise a set of (amount, activity_category, cost_subtype) rows.

    Semi-variable cost FOLDS INTO `cash_cost` for computation and is reported on
    its own line as well, so a reader can see the assumption rather than having
    to infer it. Repairs are genuinely semi-variable; merging them silently into
    the variable pool would hide that.

    `classification_coverage_pct` is None when there is no recorded cost — not
    100, and not 0. There is no coverage of nothing.
    """
    variable = semi_variable = fixed = unclassified = 0.0

    for amount, category, subtype in entries:
        behaviour = cost_behaviour_for(category, subtype)
        if behaviour is CostBehaviour.VARIABLE:
            variable += amount
        elif behaviour is CostBehaviour.SEMI_VARIABLE:
            semi_variable += amount
        elif behaviour is CostBehaviour.FIXED:
            fixed += amount
        else:
            unclassified += amount

    total = variable + semi_variable + fixed + unclassified
    coverage = None if total == 0 else 100.0 * (total - unclassified) / total

    return {
        "variable_cost": variable,
        "semi_variable_cost": semi_variable,
        "fixed_cost_recorded": fixed,
        "unclassified_cost": unclassified,
        "total_recorded_cost": total,
        "cash_cost": variable + semi_variable,
        "classification_coverage_pct": coverage,
    }


# --- 4.2 Depreciation overlay ----------------------------------------------

DAYS_PER_YEAR = 365.0


def depreciation_overlay(
    equipment: Sequence[dict],
    period_days: float,
) -> dict:
    """Periodic depreciation charge across a set of equipment records.

        annual_charge_ngn = purchase_value_ngn * depreciation_rate
        period_charge_ngn = annual_charge_ngn * (period_days / 365)

    THREE SIMPLIFICATIONS, stated rather than hidden:
      1. STRAIGHT LINE. The charge is a constant fraction of the purchase value
         each year; it does not decline as the asset ages.
      2. NO SALVAGE VALUE. The whole purchase value is depreciated, so the
         charge is an upper bound on the true one.
      3. NO DECLINING BALANCE and no accumulated-depreciation floor: an asset
         held past its implied life keeps charging, because no acquisition date
         is recorded to measure life against.

    This is a DERIVED OVERLAY computed at report time. Nothing here is written
    to the ledger — posting synthetic depreciation rows would need unpaired
    entries in an immutable paired-write ledger.

    Equipment with a null or zero rate contributes zero and is counted in
    `equipment_unrated_count`, so the reader can see that the overlay is partial
    rather than reading a small charge as a small true cost.
    """
    annual = 0.0
    unrated = 0

    for item in equipment:
        rate = item.get("depreciation_rate")
        value = item.get("purchase_value_ngn")
        if not rate or not value:
            unrated += 1
            continue
        annual += value * rate

    return {
        "annual_charge_ngn": annual,
        "period_charge_ngn": annual * (period_days / DAYS_PER_YEAR),
        "period_days": period_days,
        "equipment_count": len(equipment),
        "equipment_unrated_count": unrated,
    }


# --- 4.3 Proportional fixed-cost allocation --------------------------------

def allocate_fixed_cost(
    period_fixed_cost_ngn: float,
    direct_cost_by_crop: dict[str, float],
) -> dict:
    """Apportion a period's fixed cost across crops by recorded direct cost.

        crop_share      = crop_direct_cost / total_direct_cost_all_crops
        allocated_fixed = period_fixed_cost * crop_share

    There is no field, plot or area entity in the model, so no PHYSICAL
    allocation base exists. Proportional-to-direct-cost is the standard fallback
    and is an ASSUMPTION, not a measurement; ADR-0002 records it as one, in the
    same way N-03 records the whole-harvest-drying assumption.

    Where the total direct cost is zero, every share and every allocation is
    None. An even split would invent an allocation base that does not exist, and
    a zero would claim the fixed cost had disappeared; both are worse answers
    than "undefined".
    """
    total = sum(direct_cost_by_crop.values())

    allocations: dict[str, dict] = {}
    for crop, direct in direct_cost_by_crop.items():
        if total == 0:
            allocations[crop] = {
                "direct_cost_ngn": direct,
                "share": None,
                "allocated_fixed_ngn": None,
            }
            continue
        share = direct / total
        allocations[crop] = {
            "direct_cost_ngn": direct,
            "share": share,
            "allocated_fixed_ngn": period_fixed_cost_ngn * share,
        }

    return {
        "period_fixed_cost_ngn": period_fixed_cost_ngn,
        "total_direct_cost_all_crops": total,
        "allocations": allocations,
    }


# --- 4.4 Dual break-even price ---------------------------------------------

def break_even_prices(
    cash_cost: float,
    total_recorded_cost: float,
    allocated_fixed_ngn: Optional[float],
    marketable_mass_kg: Optional[float],
    classification_coverage_pct: Optional[float] = None,
) -> dict:
    """The two conditional break-even prices, per marketable kilogram.

        break_even_price_cash_ngn_per_kg  = cash_cost / marketable_mass_kg
        break_even_price_total_ngn_per_kg = (total_recorded_cost
                                             + allocated_fixed) / marketable_mass_kg

    The CASH price is the short-run continuation threshold: below it, each extra
    kilogram sold loses money outright. The TOTAL price is the long-run survival
    threshold, covering the machine wearing out as well.

    THE ASYMMETRY IS DELIBERATE. The two figures do NOT share a cost base:

      * `cash_cost` is CLASSIFIED variable and semi-variable cost only.
      * `total_recorded_cost` is EVERY recorded cost — including cost that
        carries no subtype and is therefore unclassified — plus the allocated
        fixed overlay.

    Unclassified cost therefore sits INSIDE the total figure and OUTSIDE the
    cash figure, so it inflates the apparent gap between the two. A wide gap can
    mean a fixed-cost-heavy enterprise, or it can mean poor classification, and
    the two are not distinguishable from the prices alone. This is why
    `classification_coverage_pct` travels with both numbers, and why the four
    cost lines (variable+semi-variable, total recorded, allocated fixed, total)
    are reported separately rather than collapsed into two.

    The two prices are never equal and the cash figure is always strictly the
    lower, because the total base contains the cash base plus recorded fixed
    cost, unclassified cost and the overlay.

    Both prices are None where `marketable_mass_kg` is zero, None or absent —
    the existing contract that a unit cost is undefined rather than fabricated
    as zero. `allocated_fixed_ngn` may be None (no allocation base upstream), in
    which case the total falls back to recorded cost alone.
    """
    allocated = allocated_fixed_ngn or 0.0
    total_cost = total_recorded_cost + allocated

    if not marketable_mass_kg:
        cash_price = None
        total_price = None
    else:
        cash_price = cash_cost / marketable_mass_kg
        total_price = total_cost / marketable_mass_kg

    return {
        "break_even_price_cash_ngn_per_kg": cash_price,
        "break_even_price_total_ngn_per_kg": total_price,
        "variable_and_semi_variable_cost_ngn": cash_cost,
        "total_recorded_cost_ngn": total_recorded_cost,
        "allocated_fixed_ngn": allocated_fixed_ngn,
        "total_cost_ngn": total_cost,
        "marketable_mass_kg": marketable_mass_kg,
        "classification_coverage_pct": classification_coverage_pct,
    }


# --- 4.5 Yield sensitivity matrix ------------------------------------------

DEFAULT_SENSITIVITY_PCT: tuple[int, ...] = (75, 90, 100, 110, 125)


def yield_sensitivity(
    baseline_marketable_mass_kg: Optional[float],
    cash_cost: float,
    total_cost: float,
    percentages: Sequence[int] = DEFAULT_SENSITIVITY_PCT,
) -> dict:
    """Both break-even prices recomputed across a range of yield outcomes.

    Pure arithmetic on §4.4: cost is held constant and the marketable mass is
    scaled, so each row answers *if you harvest this much, what price covers
    your costs*.

    The output is labelled CONDITIONAL and is flagged as such in the payload. It
    forecasts neither yield nor price, and the interface copy must carry that
    explicitly — the existing break-even yield is deliberately retrospective for
    the same reason, and a matrix read as a prediction would break the
    platform's strongest reporting convention.

    An undefined baseline mass yields undefined prices at every row rather than
    an infinite price.
    """
    rows = []
    for pct in percentages:
        mass = None
        if baseline_marketable_mass_kg:
            mass = baseline_marketable_mass_kg * pct / 100.0
        rows.append({
            "percentage": pct,
            "marketable_mass_kg": mass,
            "break_even_price_cash_ngn_per_kg": (cash_cost / mass) if mass else None,
            "break_even_price_total_ngn_per_kg": (total_cost / mass) if mass else None,
        })

    return {
        "conditional": True,
        "baseline_marketable_mass_kg": baseline_marketable_mass_kg,
        "cash_cost_ngn": cash_cost,
        "total_cost_ngn": total_cost,
        "rows": rows,
    }


# --- 4.6 Operating expense ratio -------------------------------------------

def operating_expense_ratio_pct(
    cash_operating_cost_ngn: float,
    revenue_ngn: float,
) -> Optional[float]:
    """100 * cash operating cost / revenue.

    The numerator is CASH operating cost — variable, semi-variable AND
    unclassified recorded cost — and it EXCLUDES the depreciation overlay. The
    ratio is conventionally a cash measure, and a non-cash overlay in the
    numerator would make the figure incomparable to any published benchmark.
    The exclusion is enforced by the signature: allocated fixed cost has no
    parameter here and therefore no route into the numerator.

    Unclassified cost is included because it was in fact spent. Excluding it
    would understate the ratio in exact proportion to how poor the
    classification is, which is the wrong direction for a data-quality problem
    to push a headline figure.

    Returns None at zero revenue — a ratio against no revenue is undefined, not
    infinite and not zero.
    """
    if not revenue_ngn:
        return None
    return 100.0 * cash_operating_cost_ngn / revenue_ngn


# --- 4.7 Partial budget -----------------------------------------------------

def partial_budget(
    added_revenue_ngn: float,
    reduced_cost_ngn: float,
    lost_revenue_ngn: float,
    added_cost_ngn: float,
) -> dict:
    """Appraise one proposed change:

        net_change = (added_revenue + reduced_cost) - (lost_revenue + added_cost)

    A partial budget evaluates ONLY the quantities the change affects, so it
    needs no complete enterprise budget — that is the whole point of the method
    and the reason it is usable on a farm with partial records.

    All four inputs are required and expected non-negative (the sign convention
    lives in which of the four slots a quantity occupies, not in the number).
    Each is echoed back so the interface can show the working rather than a bare
    total.

    The net change is returned SIGNED and UNCLAMPED. A negative result is a
    valid and useful answer — it says the change is not worth making — and
    suppressing it to zero would turn a decision tool into an advertisement.
    """
    benefits = added_revenue_ngn + reduced_cost_ngn
    costs = lost_revenue_ngn + added_cost_ngn
    return {
        "added_revenue_ngn": added_revenue_ngn,
        "reduced_cost_ngn": reduced_cost_ngn,
        "lost_revenue_ngn": lost_revenue_ngn,
        "added_cost_ngn": added_cost_ngn,
        "benefits_ngn": benefits,
        "costs_ngn": costs,
        "net_change_ngn": benefits - costs,
    }


# --- 4.8 Olympic average yield ---------------------------------------------

MIN_SEASONS_FOR_OLYMPIC = 3


def olympic_average_yield(season_yields_kg: Sequence[float]) -> dict:
    """A yield baseline with one high and one low season discarded.

    THE SINGLE-INSTANCE RULE. Exactly ONE maximum observation and exactly ONE
    minimum observation are discarded — not every observation equal to the
    extreme value. Sorting and slicing the ends implements this correctly; a
    value-based filter (`[y for y in ys if y != lowest]`) does not, and silently
    discards every tie. On the verification dataset the minimum 589 occurs
    twice: removing one leaves 9 values averaging 668.2222, removing both leaves
    8 averaging 678.6250, and only the first is the Olympic average.

    Returns None below three seasons — there is nothing left after discarding
    both extremes, and a two-value mean is not an Olympic average under another
    name. The grand average is still reported at any non-zero count, so the
    difference between the two baselines stays visible rather than asserted.
    """
    n = len(season_yields_kg)
    grand = sum(season_yields_kg) / n if n else None

    if n < MIN_SEASONS_FOR_OLYMPIC:
        return {
            "olympic_average_kg": None,
            "grand_average_kg": grand,
            "n_seasons": n,
            "n_used": 0,
            "n_discarded": 0,
        }

    # Sort, then drop the first and last POSITIONS. Positional, so ties survive.
    trimmed = sorted(season_yields_kg)[1:-1]
    return {
        "olympic_average_kg": sum(trimmed) / len(trimmed),
        "grand_average_kg": grand,
        "n_seasons": n,
        "n_used": len(trimmed),
        "n_discarded": 2,
    }
