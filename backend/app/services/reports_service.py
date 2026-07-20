import calendar
import csv
import io
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.enums import Category, TransactionType
from ..models import models


def get_pnl_report(db: Session, farm_id: int) -> dict:
    """Assemble a Profit & Loss report from the financial ledger.

    Revenue is the sum of credit transactions, expenses the sum of debits,
    gross margin the difference. The breakdown reports revenue/expenses/net per
    Activity Category so input costs and produce sales can be compared. Scoped
    to a single farm.
    """
    FT = models.FinancialTransaction
    OL = models.OperationalLog
    # A reversal is a category-preserving contra (ticket 10b): same type as the
    # original, flagged by its log's reverses_id. That flag lives on
    # operational_logs (1:1 with its transaction), so we LEFT JOIN to surface it
    # and group by it as a boolean.
    is_reversal = OL.reverses_id.isnot(None)
    rows = (
        db.query(
            FT.category,
            FT.transaction_type,
            is_reversal.label("is_reversal"),
            func.sum(FT.amount),
        )
        .outerjoin(OL, OL.financial_transaction_id == FT.id)
        .filter(FT.farm_id == farm_id)
        .group_by(FT.category, FT.transaction_type, is_reversal)
        .all()
    )

    buckets = {c: {"revenue": 0.0, "expenses": 0.0} for c in Category}
    for category, tx_type, is_rev, total in rows:
        # A contra subtracts from the SAME pile its type feeds, so a reversed
        # expense nets its own Operating Cost to zero and leaves revenue
        # untouched (and vice-versa) — not just Gross Margin.
        amount = -float(total or 0.0) if is_rev else float(total or 0.0)
        if tx_type == TransactionType.CREDIT:
            buckets[category]["revenue"] += amount
        else:
            buckets[category]["expenses"] += amount

    categories = []
    revenue_total = 0.0
    expenses_total = 0.0
    for c in Category:
        revenue = buckets[c]["revenue"]
        expenses = buckets[c]["expenses"]
        revenue_total += revenue
        expenses_total += expenses
        categories.append({
            "category": c.value,
            "revenue": revenue,
            "expenses": expenses,
            "net": revenue - expenses,
        })

    return {
        "revenue": revenue_total,
        "expenses": expenses_total,
        "gross_margin": revenue_total - expenses_total,
        "categories": categories,
    }


def get_monthly_pnl(db: Session, farm_id: int, months: int = 6) -> list[dict]:
    """Revenue and expenses aggregated per month for the last `months` months.

    Aggregated in Python (not SQL) so it works identically on SQLite and
    Postgres without dialect-specific date functions. Months with no activity
    are returned as zeros so the chart always shows a full window. Scoped to a
    single farm.
    """
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month
    window: list[tuple[int, int]] = []
    for _ in range(months):
        window.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    window.reverse()

    buckets = {ym: {"revenue": 0.0, "expenses": 0.0} for ym in window}

    FT = models.FinancialTransaction
    OL = models.OperationalLog
    # LEFT JOIN operational_logs for reverses_id (see get_pnl_report). Bucketing
    # stays in Python on purpose — no dialect-specific SQL date functions.
    rows = (
        db.query(FT.timestamp, FT.transaction_type, FT.amount, OL.reverses_id)
        .outerjoin(OL, OL.financial_transaction_id == FT.id)
        .filter(FT.farm_id == farm_id)
        .all()
    )

    for timestamp, tx_type, amount, reverses_id in rows:
        if timestamp is None:
            continue
        key = (timestamp.year, timestamp.month)
        if key not in buckets:
            continue
        # A reversal subtracts from the same pile its type feeds, in its own
        # month (ticket 10b: category-preserving contra).
        value = -float(amount or 0.0) if reverses_id is not None else float(amount or 0.0)
        if tx_type == TransactionType.CREDIT:
            buckets[key]["revenue"] += value
        else:
            buckets[key]["expenses"] += value

    return [
        {
            "month": calendar.month_abbr[m],
            "revenue": buckets[(y, m)]["revenue"],
            "expenses": buckets[(y, m)]["expenses"],
        }
        for (y, m) in window
    ]


def generate_pnl_csv(db: Session, farm_id: int) -> str:
    """Render the P&L report as CSV text suitable for a file download."""
    report = get_pnl_report(db, farm_id)
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["AgriProfit Profit & Loss Report"])
    writer.writerow(["Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")])
    writer.writerow([])
    writer.writerow(["Category", "Revenue (NGN)", "Expenses (NGN)", "Net (NGN)"])
    for c in report["categories"]:
        writer.writerow([
            c["category"].capitalize(),
            f"{c['revenue']:.2f}",
            f"{c['expenses']:.2f}",
            f"{c['net']:.2f}",
        ])
    writer.writerow([])
    writer.writerow([
        "Total",
        f"{report['revenue']:.2f}",
        f"{report['expenses']:.2f}",
        f"{report['gross_margin']:.2f}",
    ])

    return buffer.getvalue()
