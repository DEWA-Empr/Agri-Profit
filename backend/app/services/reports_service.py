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
