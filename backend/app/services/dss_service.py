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


def get_decision_support(db: Session) -> dict:
    """Compute per-crop unit cost of production and gross margin from the ledger.

    Reuses reports_service.get_pnl_report for the farm-wide top line so the
    overall figures are the single source of truth shared with the P&L report.
    """
    # Only paired logs carry a crop and a financial consequence, so join on the
    # financial transaction (inner join drops any unpaired log defensively).
    rows = (
        db.query(models.OperationalLog, models.FinancialTransaction)
        .join(
            models.FinancialTransaction,
            models.OperationalLog.financial_transaction_id == models.FinancialTransaction.id,
        )
        .all()
    )

    buckets: dict[str, dict] = {}
    for log, tx in rows:
        crop = log.crop or UNSPECIFIED
        b = buckets.setdefault(
            crop,
            {"revenue": 0.0, "expenses": 0.0, "yield_quantity": 0.0, "yield_unit": None},
        )
        amount = float(tx.amount or 0.0)
        if tx.transaction_type == TransactionType.CREDIT:
            b["revenue"] += amount
        else:
            b["expenses"] += amount
        # Physical output for the unit-cost denominator comes from yield logs.
        if log.activity_type == Category.YIELD and log.quantity:
            b["yield_quantity"] += float(log.quantity)
            if b["yield_unit"] is None and log.unit:
                b["yield_unit"] = log.unit

    crops = []
    for crop in sorted(buckets):
        b = buckets[crop]
        yq = b["yield_quantity"]
        unit_cost = (b["expenses"] / yq) if yq > 0 else None
        crops.append({
            "crop": crop,
            "revenue": b["revenue"],
            "expenses": b["expenses"],
            "gross_margin": b["revenue"] - b["expenses"],
            "yield_quantity": yq,
            "yield_unit": b["yield_unit"],
            "unit_cost_of_production": unit_cost,
        })

    pnl = reports_service.get_pnl_report(db)
    return {
        "crops": crops,
        "overall": {
            "revenue": pnl["revenue"],
            "expenses": pnl["expenses"],
            "gross_margin": pnl["gross_margin"],
        },
    }
