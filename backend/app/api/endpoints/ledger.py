from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import ledger_service
from ..deps import get_current_user

router = APIRouter(prefix="/ledger", tags=["ledger"])

@router.post("/logs", response_model=schemas.OperationalLog)
def create_log(log: schemas.OperationalLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return ledger_service.create_operational_log(db=db, farm_id=current_user.farm_id, log=log)

@router.get("/logs", response_model=List[schemas.OperationalLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return ledger_service.get_operational_logs(db=db, farm_id=current_user.farm_id, skip=skip, limit=limit)

@router.get("/transactions", response_model=List[schemas.FinancialTransaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return ledger_service.get_financial_transactions(db=db, farm_id=current_user.farm_id, skip=skip, limit=limit)

@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return ledger_service.calculate_gross_margin(db=db, farm_id=current_user.farm_id)
