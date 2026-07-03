import json
import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...ml import predict, train
from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import dss_service
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
