from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import equipment_service
from ..deps import get_current_user

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.post("/", response_model=schemas.Equipment)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return equipment_service.create_equipment(db=db, farm_id=current_user.farm_id, equipment=equipment)

@router.get("/", response_model=List[schemas.Equipment])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return equipment_service.get_equipment_list(db=db, farm_id=current_user.farm_id, skip=skip, limit=limit)

@router.post("/maintenance", response_model=schemas.MaintenanceLog)
def create_maintenance(log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return equipment_service.create_maintenance_log(db=db, farm_id=current_user.farm_id, log=log)

@router.get("/{equipment_id}/maintenance", response_model=List[schemas.MaintenanceLog])
def read_maintenance(equipment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return equipment_service.get_maintenance_logs(db=db, farm_id=current_user.farm_id, equipment_id=equipment_id)
