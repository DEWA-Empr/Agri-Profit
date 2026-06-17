from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...models.database import get_db
from ...schemas import schemas
from ...services import ledger_service

router = APIRouter(prefix="/ledger", tags=["ledger"])

@router.post("/logs", response_model=schemas.OperationalLog)
def create_log(log: schemas.OperationalLogCreate, db: Session = Depends(get_db)):
    return ledger_service.create_operational_log(db=db, log=log)

@router.get("/logs", response_model=List[schemas.OperationalLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ledger_service.get_operational_logs(db=db, skip=skip, limit=limit)

@router.get("/transactions", response_model=List[schemas.FinancialTransaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ledger_service.get_financial_transactions(db=db, skip=skip, limit=limit)

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return ledger_service.calculate_gross_margin(db=db)
