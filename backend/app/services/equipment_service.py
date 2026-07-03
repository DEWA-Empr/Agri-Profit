from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..core.exceptions import NotFoundError

def get_equipment(db: Session, farm_id: int, equipment_id: int) -> models.Equipment:
    # Filter by farm_id as well as id: another farm's equipment id is simply "not
    # found" here, so a cross-farm read is a 404 (no existence leak, no access).
    equipment = (
        db.query(models.Equipment)
        .filter(models.Equipment.id == equipment_id, models.Equipment.farm_id == farm_id)
        .first()
    )
    if equipment is None:
        raise NotFoundError(f"Equipment {equipment_id} not found")
    return equipment

def create_equipment(db: Session, farm_id: int, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(
        farm_id=farm_id,
        name=equipment.name,
        model=equipment.model,
        purchase_date=equipment.purchase_date,
        purchase_price=equipment.purchase_price,
        depreciation_rate=equipment.depreciation_rate
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipment_list(db: Session, farm_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Equipment)
        .filter(models.Equipment.farm_id == farm_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_maintenance_log(db: Session, farm_id: int, log: schemas.MaintenanceLogCreate):
    # Fail clearly (404) instead of a foreign-key 500 when the equipment is gone
    # — and, since get_equipment is farm-scoped, also when it belongs to another
    # farm, so maintenance can't be attached across the boundary.
    get_equipment(db, farm_id, log.equipment_id)

    db_log = models.MaintenanceLog(
        farm_id=farm_id,
        equipment_id=log.equipment_id,
        description=log.description,
        cost=log.cost
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_maintenance_logs(db: Session, farm_id: int, equipment_id: int):
    get_equipment(db, farm_id, equipment_id)
    return db.query(models.MaintenanceLog).filter(models.MaintenanceLog.equipment_id == equipment_id).all()
