from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from . import reports_service


def _find_by_client_id(db: Session, client_id: str):
    return db.query(models.OperationalLog).filter(
        models.OperationalLog.client_id == client_id
    ).first()


def create_operational_log(db: Session, log: schemas.OperationalLogCreate):
    # Fast path: this client_id was already persisted (a retried offline log).
    if log.client_id:
        existing = _find_by_client_id(db, log.client_id)
        if existing:
            return existing

    financial_tx = models.FinancialTransaction(
        amount=log.financial_data.amount,
        transaction_type=log.financial_data.transaction_type,
        category=log.financial_data.category,
        description=log.financial_data.description,
        tax_category=log.financial_data.tax_category
    )
    db.add(financial_tx)
    db.flush()

    db_log = models.OperationalLog(
        activity_type=log.activity_type,
        description=log.description,
        quantity=log.quantity,
        unit=log.unit,
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
            existing = _find_by_client_id(db, log.client_id)
            if existing:
                return existing
        raise
    db.refresh(db_log)
    return db_log

def get_operational_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.OperationalLog).offset(skip).limit(limit).all()

def get_financial_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FinancialTransaction).offset(skip).limit(limit).all()

def calculate_gross_margin(db: Session):
    # The P&L report is the single source of truth for revenue/expenses/margin;
    # the summary is just its top-line totals (without the category breakdown).
    report = reports_service.get_pnl_report(db)
    return {
        "revenue": report["revenue"],
        "expenses": report["expenses"],
        "gross_margin": report["gross_margin"],
    }
