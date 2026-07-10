from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
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
        db.rollback()
        if log.client_id:
            existing = _find_by_client_id(db, farm_id, log.client_id)
            if existing:
                return existing, False
        raise
    db.refresh(db_log)
    return db_log, True

def get_operational_logs(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.OperationalLog)
        .filter(models.OperationalLog.farm_id == farm_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_financial_transactions(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.FinancialTransaction)
        .filter(models.FinancialTransaction.farm_id == farm_id)
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
