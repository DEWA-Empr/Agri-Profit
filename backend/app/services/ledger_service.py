from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas

def create_operational_log(db: Session, log: schemas.OperationalLogCreate):
    if log.client_id:
        existing = db.query(models.OperationalLog).filter(
            models.OperationalLog.client_id == log.client_id
        ).first()
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
    db.commit()
    db.refresh(db_log)
    return db_log

def get_operational_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.OperationalLog).offset(skip).limit(limit).all()

def get_financial_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FinancialTransaction).offset(skip).limit(limit).all()

def calculate_gross_margin(db: Session):
    # Simplified calculation: Total revenue (credit) - Total expenses (debit)
    revenue = db.query(models.FinancialTransaction).filter(
        models.FinancialTransaction.transaction_type == models.TransactionType.CREDIT
    ).with_entities(models.func.sum(models.FinancialTransaction.amount)).scalar() or 0.0
    
    expenses = db.query(models.FinancialTransaction).filter(
        models.FinancialTransaction.transaction_type == models.TransactionType.DEBIT
    ).with_entities(models.func.sum(models.FinancialTransaction.amount)).scalar() or 0.0
    
    return {"revenue": revenue, "expenses": expenses, "gross_margin": revenue - expenses}
