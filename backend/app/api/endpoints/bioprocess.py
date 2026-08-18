"""Bioprocess (post-harvest drying) read + aggregate endpoints (ticket 08).

There is NO create route here: a drying run is created through the single
existing write path (POST /ledger/logs -> create_operational_log), which
already validates the DryingParams payload at the schema edge and writes the
paired financial transaction. These routes only read that data back and compute
derived engineering metrics on the fly (bioprocess_service, pure functions).

Reversal handling (ticket 10/10b): a reversal contra carries no crop, quantity
or drying payload, and a reversed run must not enter a mass balance — so both
reversal logs and reversed logs are excluded from all bioprocess analytics.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.enums import Category
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import bioprocess_service
from ..deps import get_current_user

router = APIRouter(prefix="/bioprocess", tags=["bioprocess"])

UNSPECIFIED = "Unspecified"


def _params_and_metrics(log: models.OperationalLog):
    """Deserialise a log's stored drying payload and compute every metric."""
    params = schemas.DryingParams.model_validate(log.extra_data)
    readings = [(r.time_hours, r.moisture_wb) for r in params.readings]
    metrics = bioprocess_service.compute_drying_metrics(
        mass_in_kg=params.mass_in_kg,
        mass_out_kg=params.mass_out_kg,
        moisture_initial_wb=params.moisture_initial_wb,
        moisture_final_wb=params.moisture_final_wb,
        drying_time_hours=params.drying_time_hours,
        crop=log.crop,
        readings=readings or None,
    )
    return params, metrics


@router.get("/summary", response_model=schemas.BioprocessSummary)
def get_bioprocess_summary(
    crop: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Per-crop drying aggregates for the authenticated farm. Excludes reversal
    logs and reversed logs. Optional `crop` filter."""
    OL = models.OperationalLog

    # ids of runs that have been reversed (targeted by some reverses_id).
    reversed_ids = {
        r[0]
        for r in db.query(OL.reverses_id)
        .filter(OL.farm_id == current_user.farm_id, OL.reverses_id.isnot(None))
        .all()
    }

    q = db.query(OL).filter(
        OL.farm_id == current_user.farm_id,
        OL.activity_type == Category.BIOPROCESS,
        OL.reverses_id.is_(None),  # not a reversal contra
    )
    if crop is not None:
        q = q.filter(OL.crop == crop)

    buckets: dict[str, dict] = {}
    for log in q.all():
        if log.id in reversed_ids or not log.extra_data:
            continue
        params = schemas.DryingParams.model_validate(log.extra_data)
        key = log.crop or UNSPECIFIED
        b = buckets.setdefault(
            key,
            {
                "runs": 0,
                "mass_in": 0.0,
                "marketable": 0.0,
                "water": 0.0,
                "rates": [],
                "k_by_method": {},
                "threshold": bioprocess_service.safe_storage_threshold(log.crop),
                "safe_met": 0,
            },
        )
        water = bioprocess_service.water_removed_kg(
            params.mass_in_kg,
            params.mass_out_kg,
            params.moisture_initial_wb,
            params.moisture_final_wb,
        )
        rate = bioprocess_service.drying_rate_kg_h(water, params.drying_time_hours)
        k = bioprocess_service.newton_k(
            params.moisture_initial_wb, params.moisture_final_wb, params.drying_time_hours
        )

        b["runs"] += 1
        b["mass_in"] += params.mass_in_kg
        b["marketable"] += params.mass_out_kg
        b["water"] += water
        b["rates"].append(rate)
        b["k_by_method"].setdefault(params.method, []).append(k)
        if b["threshold"] is not None and params.moisture_final_wb <= b["threshold"]:
            b["safe_met"] += 1

    crops = []
    for key in sorted(buckets):
        b = buckets[key]
        share = (b["safe_met"] / b["runs"]) if b["threshold"] is not None else None
        crops.append(
            {
                "crop": key,
                "drying_runs": b["runs"],
                "total_mass_in_kg": b["mass_in"],
                "total_marketable_mass_kg": b["marketable"],
                "total_water_removed_kg": b["water"],
                "mean_drying_rate_kg_h": sum(b["rates"]) / len(b["rates"]),
                "mean_newton_k_by_method": {
                    m: sum(ks) / len(ks) for m, ks in b["k_by_method"].items()
                },
                "safe_storage_share": share,
            }
        )

    return {"crops": crops}


@router.get("/{log_id}", response_model=schemas.BioprocessDetail)
def get_drying_run(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return one drying run's stored parameters plus every derived metric.

    Farm-scoped: another farm's log — or a non-bioprocess log, or a reversal
    contra with no payload — is simply "not found" (404, no existence leak)."""
    log = (
        db.query(models.OperationalLog)
        .filter(
            models.OperationalLog.farm_id == current_user.farm_id,
            models.OperationalLog.id == log_id,
        )
        .first()
    )
    if (
        log is None
        or log.activity_type != Category.BIOPROCESS
        or log.reverses_id is not None
        or not log.extra_data
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drying run not found")

    params, metrics = _params_and_metrics(log)
    return {"id": log.id, "crop": log.crop, "params": params, "metrics": metrics}
