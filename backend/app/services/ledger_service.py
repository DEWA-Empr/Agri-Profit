from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..core.exceptions import ConflictError, NotFoundError
from ..models import models
from ..schemas import schemas
from . import reports_service


def _find_by_client_id(db: Session, farm_id: int, client_id: str):
    # Scoped by farm: a client_id is only an idempotency match within the same
    # tenant, so one farm's offline key can never surface another farm's row.
    return db.query(models.OperationalLog).filter(
        models.OperationalLog.farm_id == farm_id,
        models.OperationalLog.client_id == client_id,
    ).first()


def create_operational_log(db: Session, farm_id: int, log: schemas.OperationalLogCreate):
    """Create a log + its paired transaction.

    Returns ``(log, created)`` where ``created`` is False when an existing row is
    returned for an idempotent replay (same client_id). The endpoint maps that to
    200 (found) vs 201 (created) so a retried offline log isn't reported as a new
    creation.
    """
    # Fast path: this client_id was already persisted (a retried offline log).
    if log.client_id:
        existing = _find_by_client_id(db, farm_id, log.client_id)
        if existing:
            return existing, False

    financial_tx = models.FinancialTransaction(
        farm_id=farm_id,
        amount=log.financial_data.amount,
        transaction_type=log.financial_data.transaction_type,
        category=log.financial_data.category,
        description=log.financial_data.description,
        tax_category=log.financial_data.tax_category
    )
    db.add(financial_tx)
    db.flush()

    db_log = models.OperationalLog(
        farm_id=farm_id,
        activity_type=log.activity_type,
        description=log.description,
        quantity=log.quantity,
        unit=log.unit,
        crop=log.crop,
        extra_data=log.extra_data,
        client_id=log.client_id,
        financial_transaction_id=financial_tx.id
    )
    db.add(db_log)
    try:
        db.commit()
    except IntegrityError:
        # A concurrent request with the same client_id won the race and the
        # unique index rejected this insert. Treat it as the same idempotent
        # outcome and return the row the winner created (200, not 500).
        #
        # Since e6a2b4c7d130 the constraint is UNIQUE(farm_id, client_id), so
        # the only insert this can reject is a same-farm replay — which is
        # exactly what the lookup below recovers. It used to be a GLOBAL unique
        # index, and a cross-farm collision then fell past the lookup to the
        # bare `raise` and out as a 500. Anything still reaching that `raise` is
        # a genuinely unexpected integrity failure and should stay a 500.
        db.rollback()
        if log.client_id:
            existing = _find_by_client_id(db, farm_id, log.client_id)
            if existing:
                return existing, False
        raise
    db.refresh(db_log)
    return db_log, True

def reverse_log(db: Session, farm_id: int, log_id: int):
    """Reverse an operational log with an offsetting ("contra") entry.

    Ledger records are immutable: rather than deleting a mistaken log, we post a
    new log + contra Financial Transaction (ticket 10b: the SAME transaction_type,
    amount and category as the original) so the pair nets within its own pile.
    The aggregates (reports_service) subtract a reversal from the same category
    bucket its type feeds, so a reversed expense's Operating Cost returns to what
    it was and Gross Revenue is left untouched — not just Gross Margin. The
    reversal log carries no crop/quantity, so it corrects the finances without
    distorting operational (yield) analytics.

    Farm-scoped: reversing a log that isn't this farm's raises NotFoundError
    (404), so a reversal can never reach across tenants. An already-reversed log,
    or a reversal entry itself, cannot be reversed (ConflictError, 409) — either
    would over-correct the ledger.
    """
    original = (
        db.query(models.OperationalLog)
        .filter(
            models.OperationalLog.farm_id == farm_id,
            models.OperationalLog.id == log_id,
        )
        .first()
    )
    if original is None:
        raise NotFoundError(f"Operational log {log_id} not found")

    if original.reverses_id is not None:
        raise ConflictError("A reversal entry cannot itself be reversed")

    already_reversed = (
        db.query(models.OperationalLog)
        .filter(
            models.OperationalLog.farm_id == farm_id,
            models.OperationalLog.reverses_id == original.id,
        )
        .first()
    )
    if already_reversed is not None:
        raise ConflictError(f"Operational log {log_id} has already been reversed")

    source_tx = original.financial_transaction
    if source_tx is None:
        # Every app-created log is paired with a transaction; one without a
        # transaction has no financial effect to offset.
        raise ConflictError(f"Operational log {log_id} has no financial transaction to reverse")

    contra_tx = models.FinancialTransaction(
        farm_id=farm_id,
        amount=source_tx.amount,
        # Category-preserving contra (ticket 10b): SAME type as the original.
        # The reversal is identified as a contra by its log's reverses_id, and
        # the aggregates subtract it from the pile its type feeds.
        transaction_type=source_tx.transaction_type,
        category=source_tx.category,
        description=f"Reversal of transaction #{source_tx.id}",
        tax_category=source_tx.tax_category,
    )
    db.add(contra_tx)
    db.flush()

    reversal_log = models.OperationalLog(
        farm_id=farm_id,
        activity_type=original.activity_type,
        description=f"Reversal of log #{original.id}",
        quantity=None,
        unit=None,
        crop=None,
        extra_data=None,
        reverses_id=original.id,
        financial_transaction_id=contra_tx.id,
    )
    db.add(reversal_log)
    db.commit()
    db.refresh(reversal_log)
    return reversal_log


# Newest first, and TOTALLY ordered. A paged read without an ORDER BY returns
# rows in an implementation-defined order, so the records list had no defined
# sort at all: the Date column read as unsorted and a just-saved record could
# appear anywhere in the table.
#
# The `id` tiebreak is not decoration. `timestamp` is a server_default of now(),
# so rows written in one transaction or one clock tick share a value; ordering on
# timestamp alone would leave those in an undefined relative order and reproduce
# the same defect in miniature. `id` is monotonic and unique, which makes the
# pair a total order.
#
# This changes no derived figure. Neither function feeds a report: the P&L, the
# decision support and the enterprise economics each build their own unbounded
# query (reports_service, dss_service) and never call these.
def get_operational_logs(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.OperationalLog)
        .filter(models.OperationalLog.farm_id == farm_id)
        .order_by(models.OperationalLog.timestamp.desc(), models.OperationalLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_financial_transactions(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.FinancialTransaction)
        .filter(models.FinancialTransaction.farm_id == farm_id)
        .order_by(models.FinancialTransaction.timestamp.desc(), models.FinancialTransaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def calculate_gross_margin(db: Session, farm_id: int):
    # The P&L report is the single source of truth for revenue/expenses/margin;
    # the summary is just its top-line totals (without the category breakdown).
    report = reports_service.get_pnl_report(db, farm_id)
    return {
        "revenue": report["revenue"],
        "expenses": report["expenses"],
        "gross_margin": report["gross_margin"],
    }
