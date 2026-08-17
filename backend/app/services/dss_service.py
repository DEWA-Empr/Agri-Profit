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
from sqlalchemy.orm import Session

from ..core.enums import Category, TransactionType
from ..models import models
from . import reports_service

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
        })

    pnl = reports_service.get_pnl_report(db, farm_id)
    return {
        "crops": crops,
        "overall": {
            "revenue": pnl["revenue"],
            "expenses": pnl["expenses"],
            "gross_margin": pnl["gross_margin"],
        },
    }
