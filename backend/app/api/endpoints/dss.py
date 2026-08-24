import json
import os

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import Field
from sqlalchemy.orm import Session

from ...ml import predict, train
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import dss_service, enterprise_service
from ..deps import get_current_user

router = APIRouter(prefix="/dss", tags=["dss"])


@router.get("/decision-support", response_model=schemas.DSSDecisionSupport)
def get_decision_support(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Tier 1 deterministic decision support: per-crop unit cost of production
    and gross margin computed directly from the real ledger (no model). Scoped
    to the authenticated user's farm. Returns empty `crops` when the ledger is
    empty — the client shows an empty state rather than fabricated figures."""
    return dss_service.get_decision_support(db, current_user.farm_id)


# The Tier-2 model endpoints operate on the shared, synthetic-data yield model —
# not on any farm's private records — so they require auth but are not
# farm-scoped.
@router.post("/predict", response_model=schemas.DSSPredictResponse)
def get_prediction(payload: schemas.DSSPredictRequest, current_user: models.User = Depends(get_current_user)):
    """Predict crop yield (t/ha) from agronomic inputs.

    Inputs are validated against the model's training bounds (422 on failure);
    a 503 is returned if no model has been trained yet.
    """
    return predict.predict_yield(payload.model_dump())


@router.post("/train")
def trigger_training(current_user: models.User = Depends(get_current_user)):
    """(Re)train the yield model on the agronomic dataset and refresh the cache."""
    result = train.train_model()
    predict.reset_cache()  # so the next /predict serves the freshly trained model
    return result


@router.get("/model")
def model_info(current_user: models.User = Depends(get_current_user)):
    """Return metadata (metrics, feature importances, train time) for the model."""
    if not os.path.exists(train.META_PATH):
        return {"trained": False}
    with open(train.META_PATH) as fh:
        return {"trained": True, **json.load(fh)}


# --- Enterprise economics (Phase 4) ---------------------------------------
# Five routes extending the existing DSS surface rather than adding a parallel
# one. All are farm-scoped through get_current_user, and all read: nothing here
# writes, and the depreciation overlay is computed at report time and never
# posted to the ledger. An unmatched `crop` filter is a 404 — including another
# farm's crop, which is the same verdict and so leaks nothing.


@router.get("/cost-structure", response_model=schemas.CostStructureResponse)
def get_cost_structure(
    crop: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Cost split by behaviour — variable, semi-variable, recorded fixed and
    unclassified — per crop and farm-wide, with classification coverage.

    Coverage is null, never 100 and never 0, where no cost is recorded."""
    return dss_service.get_cost_structure(db, current_user.farm_id, crop)


@router.get("/break-even-price", response_model=schemas.BreakEvenPriceResponse)
def get_break_even_price(
    crop: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Both conditional break-even prices per marketable kilogram, the four cost
    lines behind them, classification coverage, and the count of equipment
    carrying no depreciation rate.

    The two prices use different cost bases on purpose (see
    enterprise_service.break_even_prices): the cash figure is classified
    variable and semi-variable cost only, the total figure is every recorded
    cost plus the allocated fixed overlay. Both are null where the crop has no
    marketable mass."""
    return dss_service.get_break_even_price(db, current_user.farm_id, crop)


@router.get("/sensitivity", response_model=schemas.SensitivityResponse)
def get_sensitivity(
    crop: Optional[str] = None,
    # Bounds are on each ITEM, not on the list: a percentage of 0 would ask for
    # a zero harvest, and a negative one for a negative mass.
    percentages: Optional[List[Annotated[int, Field(gt=0, le=1000)]]] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Both break-even prices recomputed across a range of yield outcomes.

    CONDITIONAL, never predictive: each row answers "if you harvest this much,
    what price covers your costs". It forecasts neither yield nor price, and the
    payload carries `conditional: true` so the interface cannot quietly drop the
    qualifier. Defaults to 75, 90, 100, 110, 125 per cent of the recorded
    marketable mass."""
    return dss_service.get_sensitivity(db, current_user.farm_id, crop, percentages)


@router.post("/partial-budget", response_model=schemas.PartialBudgetResponse)
def post_partial_budget(
    payload: schemas.PartialBudgetRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Appraise one proposed change: (added revenue + reduced cost) − (lost
    revenue + added cost).

    Stateless — it takes no database session at all, so it cannot write even by
    accident. The net change is returned signed and unclamped: a negative result
    says the change is not worth making, which is the answer the farmer needs."""
    return enterprise_service.partial_budget(**payload.model_dump())


@router.get("/yield-baseline", response_model=schemas.YieldBaselineResponse)
def get_yield_baseline(
    crop: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Olympic and grand average yield per crop, or nulls with a stated reason.

    A season is a calendar year of recorded yield — an assumption the model
    forces, since it has no season entity. The Olympic average needs three
    seasons and is null below that; the grand average is still reported, so the
    difference between the two baselines stays visible."""
    return dss_service.get_yield_baseline(db, current_user.farm_id, crop)
