import json
import os

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import Field
from sqlalchemy.orm import Session

from ...ml import predict, train
from ...models import models
from ...core.config import settings
from ...models.database import get_db
from ...schemas import schemas
from ...services import dss_service, enterprise_service
from ...core.roles import Permission
from ..deps import require

router = APIRouter(prefix="/dss", tags=["dss"])


@router.get("/decision-support", response_model=schemas.DSSDecisionSupport)
def get_decision_support(db: Session = Depends(get_db), current_user: models.User = Depends(require(Permission.FINANCE_READ))):
    """Tier 1 deterministic decision support: per-crop unit cost of production
    and gross margin computed directly from the real ledger (no model). Scoped
    to the authenticated user's farm. Returns empty `crops` when the ledger is
    empty — the client shows an empty state rather than fabricated figures."""
    return dss_service.get_decision_support(db, current_user.farm_id)


# The Tier-2 model endpoints operate on the shared, synthetic-data yield model —
# not on any farm's private records — so they require auth but are not
# farm-scoped.
@router.post("/predict", response_model=schemas.DSSPredictResponse)
def get_prediction(payload: schemas.DSSPredictRequest, current_user: models.User = Depends(require(Permission.FORECAST_USE))):
    """Predict crop yield (t/ha) from agronomic inputs.

    Inputs are validated against the model's training bounds (422 on failure);
    a 503 is returned if no model has been trained yet.
    """
    return predict.predict_yield(payload.model_dump())


@router.post("/train")
def trigger_training(current_user: models.User = Depends(require(Permission.MODEL_TRAIN))):
    """(Re)train the yield model on the agronomic dataset and refresh the cache.

    OPERATOR-ONLY, AND OFF BY DEFAULT. There is exactly one model artefact and
    every farm's forecast is served from it, so retraining is a cross-tenant
    side effect: one tenant calling this changes the numbers every other tenant
    sees, and does so on a machine shared with their request traffic. Before
    authorization existed this was reachable by any authenticated user.

    `Permission.MODEL_TRAIN` is granted to no role, so this route is closed
    unless an operator both grants it and sets ALLOW_API_MODEL_TRAINING. The
    supported way to retrain is out-of-band — `python -m backend.app.ml.train`,
    or a container restart, which trains on boot when no artefact is present.
    """
    if not settings.allow_api_model_training:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Model retraining over the API is disabled. Retrain out-of-band "
                "(python -m backend.app.ml.train) — see docs/OPERATIONS.md."
            ),
        )
    result = train.train_model()
    predict.reset_cache()  # so the next /predict serves the freshly trained model
    return result


@router.get("/model")
def model_info(current_user: models.User = Depends(require(Permission.FORECAST_READ))):
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
    current_user: models.User = Depends(require(Permission.FINANCE_READ)),
):
    """Cost split by behaviour — variable, semi-variable, recorded fixed and
    unclassified — per crop and farm-wide, with classification coverage.

    Also carries the operating expense ratio — cash operating cost over revenue,
    per crop and farm-wide. It is here rather than on the break-even route
    because it is a whole-enterprise cash measure, not a figure per marketable
    kilogram, and it is null where there is no revenue to be a proportion of.

    Coverage is null, never 100 and never 0, where no cost is recorded."""
    return dss_service.get_cost_structure(db, current_user.farm_id, crop)


# A century of days. Beyond that the caller is no longer describing a reporting
# period, and an unbounded value would let one request scale the depreciation
# charge arbitrarily far above any cost it is set beside.
MAX_PERIOD_DAYS = 36525.0


@router.get("/break-even-price", response_model=schemas.BreakEvenPriceResponse)
def get_break_even_price(
    crop: Optional[str] = None,
    period_days: Optional[float] = Query(default=None, gt=0, le=MAX_PERIOD_DAYS),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require(Permission.FINANCE_READ)),
):
    """Both conditional break-even prices per marketable kilogram, the four cost
    lines behind them, classification coverage, and the count of equipment
    carrying no depreciation rate.

    The two prices use different cost bases on purpose (see
    enterprise_service.break_even_prices): the cash figure is classified
    variable and semi-variable cost only, the total figure is every recorded
    cost plus the allocated fixed overlay. Both are null where the crop has no
    marketable mass.

    `period_days` pins the depreciation window and is OPTIONAL; omitted, the
    window is derived from the span of the farm's own ledger, and the response
    says which was used in `period_source`. The override exists for
    REPRODUCIBILITY: a derived span widens every time a log is entered, the
    depreciation charge scales with it, and so the break-even price to cover
    total cost silently moves — a figure reported last week cannot be
    re-derived, because the window it was computed over no longer exists."""
    return dss_service.get_break_even_price(
        db, current_user.farm_id, crop, period_days
    )


@router.get("/sensitivity", response_model=schemas.SensitivityResponse)
def get_sensitivity(
    crop: Optional[str] = None,
    # Bounds are on each ITEM, not on the list: a percentage of 0 would ask for
    # a zero harvest, and a negative one for a negative mass.
    percentages: Optional[List[Annotated[int, Field(gt=0, le=1000)]]] = Query(default=None),
    period_days: Optional[float] = Query(default=None, gt=0, le=MAX_PERIOD_DAYS),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require(Permission.FINANCE_READ)),
):
    """Both break-even prices recomputed across a range of yield outcomes.

    CONDITIONAL, never predictive: each row answers "if you harvest this much,
    what price covers your costs". It forecasts neither yield nor price, and the
    payload carries `conditional: true` so the interface cannot quietly drop the
    qualifier. Defaults to 75, 90, 100, 110, 125 per cent of the recorded
    marketable mass.

    `period_days` pins the depreciation window exactly as it does on
    /break-even-price, and for the same reason: every price in this matrix is a
    break-even price and moves with that window."""
    return dss_service.get_sensitivity(
        db, current_user.farm_id, crop, percentages, period_days
    )


@router.post("/partial-budget", response_model=schemas.PartialBudgetResponse)
def post_partial_budget(
    payload: schemas.PartialBudgetRequest,
    current_user: models.User = Depends(require(Permission.FINANCE_READ)),
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
    current_user: models.User = Depends(require(Permission.FINANCE_READ)),
):
    """Olympic and grand average yield per crop, or nulls with a stated reason.

    A season is a calendar year of recorded yield — an assumption the model
    forces, since it has no season entity, recorded as a temporary one in
    ADR-0002. The Olympic average needs three seasons and is null below that;
    the grand average is still reported, so the difference between the two
    baselines stays visible.

    `n_seasons` is reported in every case, including the ones that return no
    average, so a null is never read without the season count that explains
    it."""
    return dss_service.get_yield_baseline(db, current_user.farm_id, crop)
