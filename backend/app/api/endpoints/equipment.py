from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import equipment_service
from ...core.roles import Permission
from ..deps import require

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.post("/", response_model=schemas.Equipment, status_code=status.HTTP_201_CREATED)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.EQUIPMENT_MANAGE))):
    return equipment_service.create_equipment(db=db, farm_id=current_user.farm_id, equipment=equipment)

@router.patch("/{equipment_id}", response_model=schemas.Equipment)
def update_equipment(equipment_id: int, changes: schemas.EquipmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.EQUIPMENT_MANAGE))):
    """Correct an asset. Partial: omitted fields are left unchanged.

    404 for an asset belonging to another farm — the same verdict, and the same
    non-disclosure, as reading one.

    This is the one correctable record on the platform, and deliberately so: an
    Equipment row describes a thing the farm owns rather than something that
    happened, and the depreciation overlay it feeds is computed at report time
    and never posted to the ledger. Financial records remain append-only and are
    still corrected only by contra entry."""
    return equipment_service.update_equipment(db, current_user.farm_id, equipment_id, changes)


@router.get("/", response_model=List[schemas.Equipment])
def read_equipment(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.EQUIPMENT_READ))):
    return equipment_service.get_equipment_list(db=db, farm_id=current_user.farm_id, skip=skip, limit=limit)

@router.post("/maintenance", response_model=schemas.MaintenanceLog, status_code=status.HTTP_201_CREATED)
def create_maintenance(log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.EQUIPMENT_MANAGE))):
    return equipment_service.create_maintenance_log(db=db, farm_id=current_user.farm_id, log=log)

@router.get("/{equipment_id}/maintenance", response_model=List[schemas.MaintenanceLog])
def read_maintenance(equipment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.EQUIPMENT_READ))):
    return equipment_service.get_maintenance_logs(db=db, farm_id=current_user.farm_id, equipment_id=equipment_id)
