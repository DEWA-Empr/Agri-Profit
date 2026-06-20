import calendar
import csv
import io
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.enums import Category, TransactionType
from ..models import models


def get_pnl_report(db: Session) -> dict:
    """Assemble a Profit & Loss report from the financial ledger.

    Revenue is the sum of credit transactions, expenses the sum of debits,
    gross margin the difference. The breakdown reports revenue/expenses/net per
    Activity Category so input costs and produce sales can be compared.
    """
    rows = (
        db.query(
            models.FinancialTransaction.category,
            models.FinancialTransaction.transaction_type,
            func.sum(models.FinancialTransaction.amount),
        )
        .group_by(
            models.FinancialTransaction.category,
            models.FinancialTransaction.transaction_type,
        )
        .all()
    )

    buckets = {c: {"revenue": 0.0, "expenses": 0.0} for c in Category}
    for category, tx_type, total in rows:
        amount = float(total or 0.0)
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


def get_monthly_pnl(db: Session, months: int = 6) -> list[dict]:
    """Revenue and expenses aggregated per month for the last `months` months.

    Aggregated in Python (not SQL) so it works identically on SQLite and
    Postgres without dialect-specific date functions. Months with no activity
    are returned as zeros so the chart always shows a full window.
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

    rows = db.query(
        models.FinancialTransaction.timestamp,
        models.FinancialTransaction.transaction_type,
        models.FinancialTransaction.amount,
    ).all()

    for timestamp, tx_type, amount in rows:
        if timestamp is None:
            continue
        key = (timestamp.year, timestamp.month)
        if key not in buckets:
            continue
        if tx_type == TransactionType.CREDIT:
            buckets[key]["revenue"] += float(amount or 0.0)
        else:
            buckets[key]["expenses"] += float(amount or 0.0)

    return [
        {
            "month": calendar.month_abbr[m],
            "revenue": buckets[(y, m)]["revenue"],
            "expenses": buckets[(y, m)]["expenses"],
        }
        for (y, m) in window
    ]


def generate_pnl_csv(db: Session) -> str:
    """Render the P&L report as CSV text suitable for a file download."""
    report = get_pnl_report(db)
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
