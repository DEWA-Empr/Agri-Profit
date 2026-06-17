from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas

def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(
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

def get_equipment_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Equipment).offset(skip).limit(limit).all()

def create_maintenance_log(db: Session, log: schemas.MaintenanceLogCreate):
    db_log = models.MaintenanceLog(
        equipment_id=log.equipment_id,
        description=log.description,
        cost=log.cost
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_maintenance_logs(db: Session, equipment_id: int):
    return db.query(models.MaintenanceLog).filter(models.MaintenanceLog.equipment_id == equipment_id).all()
