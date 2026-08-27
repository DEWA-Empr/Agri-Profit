from datetime import datetime, timezone

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

def update_equipment(
    db: Session, farm_id: int, equipment_id: int, changes: schemas.EquipmentUpdate
):
    """Correct an asset in place. Farm-scoped, partial, and stamped.

    WHY THIS IS NOT A BREACH OF THE PLATFORM'S IMMUTABILITY RULE. The ledger is
    append-only because a Financial Transaction records something that happened;
    rewriting one would rewrite history. An Equipment row is not that. It
    describes a thing the farm owns, and `depreciation_rate` in particular is an
    estimate the farmer supplies — a parameter, not an event. The overlay it
    feeds is computed at report time and never posted to the ledger, so
    correcting it changes no recorded transaction. Before this existed a
    mistyped rate was permanent and silently biased the overlay, allocated fixed
    cost and both break-even prices, with no way to put it right.

    `exclude_unset` so an omitted field is left alone. Sending only
    `depreciation_rate` must not blank the purchase price.

    `updated_at` is stamped ONLY when something actually changed. A PATCH whose
    every field matches the current value is not a correction, and recording one
    would tell a reader the asset moved when it did not.
    """
    equipment = get_equipment(db, farm_id, equipment_id)

    updates = changes.model_dump(exclude_unset=True)
    applied = {
        field: value
        for field, value in updates.items()
        if getattr(equipment, field) != value
    }
    if not applied:
        return equipment

    for field, value in applied.items():
        setattr(equipment, field, value)
    equipment.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(equipment)
    return equipment


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
