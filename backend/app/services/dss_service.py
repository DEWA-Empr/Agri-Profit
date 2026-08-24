"""Tier 1 deterministic decision-support service (Chapter 3 §3.6.5).

Transparent rules over the farm's REAL Operational Logs and their paired
Financial Transactions — no model, no training data, no synthetic inputs. This
is the deterministic counterpart to the optional Random Forest yield forecast
(Tier 2, ml/predict.py), which this module deliberately does not touch.

For each crop the metrics are, per §3.6.5 ("unit cost of production and per-crop
gross margin ... grouped by Activity Category and crop"):

    gross margin              = Σ revenue (credit tx) − Σ expenses (debit tx)
    unit cost of production   = Σ expenses (debit tx) ÷ Σ yield quantity

Yield quantity is the physical output recorded on YIELD-category logs (their
`quantity` in the crop's own unit, e.g. bags). Unit cost is None — never 0 or a
fabricated figure — when the crop has no recorded yield, so we never divide by
zero. Logs with no crop tag (pre-existing rows, or app entries without a crop)
fall into an "Unspecified" bucket rather than being dropped.
"""
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from ..core.enums import Category, TransactionType
from ..core.exceptions import NotFoundError
from ..models import models
from . import enterprise_service, reports_service

UNSPECIFIED = "Unspecified"


def get_decision_support(db: Session, farm_id: int) -> dict:
    """Compute per-crop unit cost of production and gross margin from the ledger.

    Reuses reports_service.get_pnl_report for the farm-wide top line so the
    overall figures are the single source of truth shared with the P&L report.
    Scoped to a single farm.

    Reversal-aware (ticket 08 / 10b): a reversal is a category-preserving contra
    carrying no crop of its own, so it is attributed to its ORIGINAL's crop and
    SUBTRACTED within the pile its type feeds — mirroring reports_service, but
    crop-aware. A reversed YIELD log's quantity is excluded from the unit-cost
    denominator (the contra's quantity is None, so otherwise the revenue reverses
    but the quantity lingers). No contra ever lands in the "Unspecified" bucket.

    Bioprocess coupling (ticket 08): where a crop has non-reversed Drying Runs,
    an ADDITIVE per-kg unit cost is reported against Marketable Mass, alongside
    the unchanged harvest-unit unit_cost_of_production.
    """
    OL = models.OperationalLog
    FT = models.FinancialTransaction

    # The crop of every log in the farm, so a contra can be resolved to its
    # original's crop via reverses_id (the contra's own crop is None).
    crop_by_id = {
        lid: crop for lid, crop in db.query(OL.id, OL.crop).filter(OL.farm_id == farm_id)
    }

    # Only paired logs carry a crop and a financial consequence, so join on the
    # financial transaction (inner join drops any unpaired log defensively).
    rows = (
        db.query(OL, FT)
        .join(FT, OL.financial_transaction_id == FT.id)
        .filter(OL.farm_id == farm_id)
        .all()
    )

    # Computed ONCE, up front: the ids that have been reversed (targeted by some
    # contra's reverses_id). Used to exclude reversed yield quantities and
    # reversed drying runs from the denominators.
    reversed_ids = {log.reverses_id for log, _ in rows if log.reverses_id is not None}

    buckets: dict[str, dict] = {}
    marketable: dict[str, float] = {}  # crop -> kg, only for non-reversed drying runs

    for log, tx in rows:
        is_contra = log.reverses_id is not None
        if is_contra:
            # Attribute the contra to its ORIGINAL's crop and subtract.
            crop = crop_by_id.get(log.reverses_id) or UNSPECIFIED
            sign = -1.0
        else:
            crop = log.crop or UNSPECIFIED
            sign = 1.0

        b = buckets.setdefault(
            crop,
            # yield_by_unit maps a NORMALISED unit key -> {"unit": <as first
            # written>, "quantity": <total>}. Quantities are only ever summed
            # within one key, never across keys (see below).
            {"revenue": 0.0, "expenses": 0.0, "yield_by_unit": {}},
        )
        amount = sign * float(tx.amount or 0.0)
        if tx.transaction_type == TransactionType.CREDIT:
            b["revenue"] += amount
        else:
            b["expenses"] += amount

        # Physical output for the unit-cost denominator: non-reversed yield logs
        # only (a reversed yield's quantity must leave the denominator).
        if (
            not is_contra
            and log.activity_type == Category.YIELD
            and log.quantity
            and log.id not in reversed_ids
        ):
            # Group BY unit. Previously this summed every quantity into one
            # running total and labelled it with whichever unit happened to
            # arrive first, so 100 kg + 12 bags reported "112 kg" — a number
            # that was never true, on the figure a lender reads.
            #
            # Units are free text on historical rows, so the key is normalised
            # (trimmed + lower-cased) to collapse "kg"/"Kg"/" KG " into one
            # bucket; the first spelling seen is kept for display. A row with no
            # unit at all keys under None and stays its own bucket — unknown is
            # not the same as compatible.
            key = (log.unit or "").strip().lower() or None
            slot = b["yield_by_unit"].setdefault(
                key, {"unit": (log.unit or "").strip() or None, "quantity": 0.0}
            )
            slot["quantity"] += float(log.quantity)

        # Marketable Mass: outlet mass of non-reversed drying runs, by crop.
        if (
            not is_contra
            and log.activity_type == Category.BIOPROCESS
            and log.id not in reversed_ids
            and log.extra_data
        ):
            mass_out = log.extra_data.get("mass_out_kg")
            if mass_out is not None:
                marketable[crop] = marketable.get(crop, 0.0) + float(mass_out)

    crops = []
    for crop in sorted(buckets):
        b = buckets[crop]

        # Stable, presentable breakdown: unit-less bucket last, others by unit.
        by_unit = sorted(
            (
                {"unit": slot["unit"], "quantity": slot["quantity"]}
                for slot in b["yield_by_unit"].values()
                if slot["quantity"] > 0
            ),
            key=lambda s: (s["unit"] is None, s["unit"] or ""),
        )

        # Drop empty buckets. A crop whose every record has been reversed nets
        # to no money and no yield, and rendering it as a row of zeros implies
        # activity that no longer stands. The commonest case is "Unspecified",
        # which collects untagged records and so empties out completely once
        # they are corrected.
        #
        # The test is deliberately NOT "gross margin is zero": a crop with
        # revenue 25,000 and expenses 25,000 has a genuine zero margin and is a
        # real result that must still be shown. Revenue and expenses are
        # therefore checked SEPARATELY, and any recorded yield keeps the bucket
        # alive on its own.
        #
        # Marketable mass keeps it alive too. Sun drying with the farm's own
        # labour costs nothing, so a drying run is routinely recorded at 0.00
        # (its paired transaction still exists — see
        # test_bioprocess_create_zero_cost_still_pairs_transaction). Without
        # this clause a crop whose only record is such a run would have no
        # money and no harvest quantity, and would vanish along with the
        # processing data it does have.
        #
        # Compared against a tolerance rather than exactly 0.0: reversal
        # subtracts the same values that were added, but summing several
        # amounts and then subtracting them individually can leave float
        # residue (a + b - a - b is not always exactly 0). The tolerance is far
        # below one kobo, so it can never mask a real transaction.
        EMPTY = 1e-9
        if (
            abs(b["revenue"]) < EMPTY
            and abs(b["expenses"]) < EMPTY
            and not by_unit
            and not marketable.get(crop)
        ):
            continue

        # A single total is only meaningful when ONE unit is in play. With two
        # or more, the quantity and the unit cost are reported as unavailable
        # (None) rather than invented — the breakdown carries the real figures.
        if len(by_unit) == 1:
            yq = by_unit[0]["quantity"]
            y_unit = by_unit[0]["unit"]
        elif not by_unit:
            yq = 0.0            # no yield recorded: a genuine zero, not ambiguity
            y_unit = None
        else:
            yq = None           # mixed units: no honest single total exists
            y_unit = None

        # Denominator must be a single unit; ambiguous -> no unit cost.
        unit_cost = (b["expenses"] / yq) if (yq is not None and yq > 0) else None
        mm = marketable.get(crop)  # None when the crop has no non-reversed runs
        # Guard the division: None/0 marketable mass -> None, never 0 or infinity.
        unit_cost_kg = (b["expenses"] / mm) if (mm and mm > 0) else None

        # Break-even yield: the quantity that would have covered this crop's
        # costs at the price the farm ACTUALLY realised.
        #
        #     unit price       = revenue / yield_quantity
        #     break-even yield = expenses / unit price
        #
        # RETROSPECTIVE, and this matters for how it is described: the price is
        # derived from realised revenue, so the metric answers "at the price you
        # actually got, you needed X to cover your costs." It cannot forecast a
        # break-even before a sale exists — with no revenue there is no price to
        # divide by, which is why zero revenue yields None rather than infinity.
        #
        # None (never a number) whenever the denominator chain is undefined:
        #   - yq is None    -> mixed units, no single quantity to price against
        #   - yq == 0       -> nothing harvested, so no unit price exists
        #   - revenue == 0  -> no realised price; break-even is unknowable, not
        #                      infinite
        #   - expenses == 0 -> nothing to recover. The arithmetic gives 0, which
        #                      is true but useless: it reads as "you broke even
        #                      on your first kilogram" when what it actually
        #                      means is that no cost has been tagged to this
        #                      crop. Reporting nothing is more honest than
        #                      reporting a zero the farmer would misread.
        # Consistent with unit_cost_of_production above: undefined rather than
        # fabricated.
        break_even_yield = None
        if yq is not None and yq > 0 and b["revenue"] > 0 and b["expenses"] > 0:
            unit_price = b["revenue"] / yq
            break_even_yield = b["expenses"] / unit_price

        crops.append({
            "crop": crop,
            "revenue": b["revenue"],
            "expenses": b["expenses"],
            "gross_margin": b["revenue"] - b["expenses"],
            "yield_quantity": yq,
            "yield_unit": y_unit,
            "yield_by_unit": by_unit,
            "unit_cost_of_production": unit_cost,
            "marketable_mass_kg": mm,
            "unit_cost_per_kg_marketable": unit_cost_kg,
            # Same shape as the yield figures: a quantity plus the unit it is
            # denominated in, so the two are never read against each other in
            # different units.
            "break_even_yield": break_even_yield,
            "break_even_unit": y_unit if break_even_yield is not None else None,
        })

    # Rank best-performing crop first. The question this panel answers is
    # "which crop is worth my inputs", so the most profitable belongs at the
    # top rather than whichever happens to sort first alphabetically.
    #
    # Ties break on crop name ascending, which makes the order total and
    # therefore deterministic — two crops on identical margins always come back
    # in the same sequence, for tests and for a farmer re-reading the screen.
    crops.sort(key=lambda c: (-c["gross_margin"], c["crop"]))

    pnl = reports_service.get_pnl_report(db, farm_id)
    return {
        "crops": crops,
        "overall": {
            "revenue": pnl["revenue"],
            "expenses": pnl["expenses"],
            "gross_margin": pnl["gross_margin"],
        },
    }


# --- Enterprise economics aggregation (Phase 4) ----------------------------
# The arithmetic lives in enterprise_service (pure, 100% covered). Everything
# below is the DB-aware half: it selects the farm's rows, projects them into the
# plain tuples and dicts that module expects, and shapes the response.
#
# REVERSAL HANDLING, and it differs deliberately from get_decision_support
# above. That function NETS a contra out by subtracting it inside the pile its
# type feeds, which is right for a money total. It is wrong here, because these
# figures have a DENOMINATOR as well as a numerator: a reversal carries no cost
# subtype, so netting it would leave its amount inside total_recorded_cost while
# contributing nothing classified, and classification coverage would fall every
# time a farmer corrected a mistake. Correcting the ledger would look
# indistinguishable from a data-quality problem.
#
# So both sides of a reversal pair are EXCLUDED outright — the contra and the
# log it reverses, from cost, from revenue and from marketable mass alike. For
# money totals exclusion and subtraction agree (reverse_log mirrors the
# original's amount exactly); only exclusion also keeps the denominator right.


class CropNotFound(NotFoundError):
    """A crop filter that matches nothing in this farm — including a crop that
    exists only in another farm. Same verdict either way, so no existence leak."""


def _live_rows(db: Session, farm_id: int):
    """Every (log, transaction) pair in the farm that still stands.

    Excludes reversal contras (`reverses_id is not None`) and the logs they
    reverse. Returns the surviving rows plus the crop each log belongs to.
    """
    OL = models.OperationalLog
    FT = models.FinancialTransaction

    rows = (
        db.query(OL, FT)
        .join(FT, OL.financial_transaction_id == FT.id)
        .filter(OL.farm_id == farm_id)
        .all()
    )
    reversed_ids = {log.reverses_id for log, _ in rows if log.reverses_id is not None}
    return [
        (log, tx)
        for log, tx in rows
        if log.reverses_id is None and log.id not in reversed_ids
    ]


def _cost_subtype(log) -> Optional[str]:
    """The Cost Subtype carried on a log, or None.

    Read ONLY off mechanisation rows. Every other activity type keeps
    `extra_data` as an arbitrary dict, so a seed log that happens to contain a
    `cost_subtype` key is not making a classification claim — and treating it as
    one would look up ("SEED", "FUEL"), miss, and push a correctly classified
    row into the unclassified pile.
    """
    if log.activity_type != Category.MECHANIZATION:
        return None
    if not log.extra_data:
        return None
    return log.extra_data.get("cost_subtype")


def _enterprise_base(rows) -> dict:
    """Project the farm's surviving rows into per-crop economics inputs.

    Returns cost entry tuples, marketable mass and yield observations per crop.
    Costs are DEBIT transactions; credits are revenue and are not cost entries.

    No revenue total is accumulated here: none of the five routes needs one.
    The operating expense ratio (enterprise_service.operating_expense_ratio_pct)
    does, but it has no route in this phase — see the ticket, section 5.
    """
    per_crop: dict[str, dict] = {}

    for log, tx in rows:
        crop = log.crop or UNSPECIFIED
        b = per_crop.setdefault(
            crop,
            {"cost_entries": [], "marketable_mass_kg": None, "yields": []},
        )
        amount = float(tx.amount or 0.0)

        # Costs only. A credit is revenue, and revenue is not a cost entry —
        # letting one through would put a sale into the classification
        # denominator and read as a large unclassified expense.
        if tx.transaction_type != TransactionType.CREDIT:
            b["cost_entries"].append(
                (amount, log.activity_type.value, _cost_subtype(log))
            )

        if log.activity_type == Category.BIOPROCESS and log.extra_data:
            mass_out = log.extra_data.get("mass_out_kg")
            if mass_out is not None:
                b["marketable_mass_kg"] = (b["marketable_mass_kg"] or 0.0) + float(mass_out)

        if log.activity_type == Category.YIELD and log.quantity:
            b["yields"].append((log.timestamp, float(log.quantity), log.unit))

    return per_crop


def _select_crops(per_crop: dict, crop: Optional[str]) -> list[str]:
    """The crop keys to report, honouring an optional filter.

    An unmatched filter raises rather than returning an empty list: asking about
    a crop this farm has no record of is a 404, exactly as another farm's
    equipment id is. A farm with no records at all still returns an empty list
    for the unfiltered call — that is an empty state, not a missing resource.
    """
    if crop is None:
        return sorted(per_crop)
    if crop not in per_crop:
        raise CropNotFound(f"No records for crop '{crop}'")
    return [crop]


def get_cost_structure(db: Session, farm_id: int, crop: Optional[str] = None) -> dict:
    """Section 4.1 per crop and farm-wide, with classification coverage.

    The farm-wide summary is computed over every crop's entries regardless of
    the `crop` filter — it is the farm's cost structure, not the filtered
    subset's, and re-deriving it from a filtered list would silently answer a
    different question.
    """
    per_crop = _enterprise_base(_live_rows(db, farm_id))
    keys = _select_crops(per_crop, crop)

    crops = [
        {"crop": key, **enterprise_service.cost_structure(per_crop[key]["cost_entries"])}
        for key in keys
    ]
    farm_entries = [e for b in per_crop.values() for e in b["cost_entries"]]
    return {"crops": crops, "farm": enterprise_service.cost_structure(farm_entries)}


def _equipment_overlay(db: Session, farm_id: int, rows) -> dict:
    """The farm's depreciation overlay over the span its ledger actually covers.

    The period is derived from the ledger rather than asked for: it runs from
    the first surviving log to the last, inclusive, so the charge lines up with
    the costs it is being compared against. It is reported in the response
    (`period_days`) rather than buried, because a reader who cannot see the
    window cannot judge the charge.
    """
    equipment = (
        db.query(models.Equipment).filter(models.Equipment.farm_id == farm_id).all()
    )
    stamps = [log.timestamp for log, _ in rows if log.timestamp is not None]
    # Inclusive of both endpoints, so a single day of records is one day and not
    # zero — a zero-length period would zero the overlay for a real farm.
    period_days = ((max(stamps) - min(stamps)).days + 1) if stamps else 0.0

    return enterprise_service.depreciation_overlay(
        equipment=[
            {"purchase_value_ngn": e.purchase_price, "depreciation_rate": e.depreciation_rate}
            for e in equipment
        ],
        period_days=period_days,
    )


def get_break_even_price(db: Session, farm_id: int, crop: Optional[str] = None) -> dict:
    """Section 4.4: both conditional break-even prices, the four cost lines,
    coverage, and the count of unrated equipment.

    The allocation base is FARM-WIDE and is computed before any filter is
    applied. A crop's share of fixed cost is its share of the whole farm's
    direct cost; deriving it from the filtered subset would give a single
    filtered crop a share of 1.0 and hand it the entire overlay.
    """
    # ONE pass over the ledger, shared by the projection and the overlay window.
    rows = _live_rows(db, farm_id)
    per_crop = _enterprise_base(rows)
    keys = _select_crops(per_crop, crop)

    overlay = _equipment_overlay(db, farm_id, rows)
    structures = {
        key: enterprise_service.cost_structure(b["cost_entries"])
        for key, b in per_crop.items()
    }
    allocation = enterprise_service.allocate_fixed_cost(
        period_fixed_cost_ngn=overlay["period_charge_ngn"],
        direct_cost_by_crop={
            key: s["total_recorded_cost"] for key, s in structures.items()
        },
    )

    crops = []
    for key in keys:
        s = structures[key]
        crops.append({
            "crop": key,
            **enterprise_service.break_even_prices(
                cash_cost=s["cash_cost"],
                total_recorded_cost=s["total_recorded_cost"],
                allocated_fixed_ngn=allocation["allocations"][key]["allocated_fixed_ngn"],
                marketable_mass_kg=per_crop[key]["marketable_mass_kg"],
                classification_coverage_pct=s["classification_coverage_pct"],
            ),
        })

    return {
        "crops": crops,
        "period_days": overlay["period_days"],
        "period_fixed_cost_ngn": overlay["period_charge_ngn"],
        "equipment_count": overlay["equipment_count"],
        "equipment_unrated_count": overlay["equipment_unrated_count"],
        "total_direct_cost_all_crops": allocation["total_direct_cost_all_crops"],
    }


def get_sensitivity(
    db: Session,
    farm_id: int,
    crop: Optional[str] = None,
    percentages: Optional[Sequence[int]] = None,
) -> dict:
    """Section 4.5: the conditional yield sensitivity matrix, per crop.

    Built on the same cost bases as get_break_even_price, so a row at 100% is
    the same pair of numbers that endpoint reports.
    """
    base = get_break_even_price(db, farm_id, crop)
    pct = percentages or enterprise_service.DEFAULT_SENSITIVITY_PCT

    crops = []
    for c in base["crops"]:
        crops.append({
            "crop": c["crop"],
            **enterprise_service.yield_sensitivity(
                baseline_marketable_mass_kg=c["marketable_mass_kg"],
                cash_cost=c["variable_and_semi_variable_cost_ngn"],
                total_cost=c["total_cost_ngn"],
                percentages=pct,
            ),
        })
    return {"crops": crops}


def get_yield_baseline(db: Session, farm_id: int, crop: Optional[str] = None) -> dict:
    """Section 4.8: Olympic and grand average yield per crop, or nulls with a reason.

    A SEASON IS A CALENDAR YEAR of recorded yield, and that is an assumption,
    not a measurement: the model has no season entity, so the year a yield was
    logged in is the only grouping available. Several yield logs in one year are
    one season, summed.

    Mixed units within a crop return nulls with a reason rather than a total —
    the same verdict get_decision_support gives, for the same cause: quantities
    in different units cannot be summed, and no honest single baseline exists.
    """
    per_crop = _enterprise_base(_live_rows(db, farm_id))
    keys = _select_crops(per_crop, crop)

    crops = []
    for key in keys:
        observations = per_crop[key]["yields"]
        units = {(u or "").strip().lower() or None for _, _, u in observations}

        if not observations:
            crops.append({
                "crop": key, "olympic_average_kg": None, "grand_average_kg": None,
                "n_seasons": 0, "n_used": 0, "n_discarded": 0, "unit": None,
                "reason": "No yield has been recorded for this crop.",
            })
            continue

        if len(units) > 1:
            crops.append({
                "crop": key, "olympic_average_kg": None, "grand_average_kg": None,
                "n_seasons": 0, "n_used": 0, "n_discarded": 0, "unit": None,
                "reason": (
                    "This crop's yields are recorded in more than one unit, so no "
                    "single baseline exists. See the per-unit breakdown instead."
                ),
            })
            continue

        by_season: dict[int, float] = {}
        for stamp, quantity, _ in observations:
            by_season[stamp.year] = by_season.get(stamp.year, 0.0) + quantity
        seasons = [by_season[year] for year in sorted(by_season)]

        result = enterprise_service.olympic_average_yield(seasons)
        reason = None
        if result["olympic_average_kg"] is None:
            reason = (
                f"An Olympic average needs at least "
                f"{enterprise_service.MIN_SEASONS_FOR_OLYMPIC} seasons; this crop has "
                f"{result['n_seasons']}. The grand average is shown instead."
            )
        crops.append({
            "crop": key,
            **result,
            "unit": next(iter(units)),
            "reason": reason,
        })

    return {"crops": crops}
