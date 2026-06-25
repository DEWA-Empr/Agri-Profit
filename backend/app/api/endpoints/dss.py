import json
import os

from fastapi import APIRouter

from ...ml import predict, train
from ...schemas import schemas

router = APIRouter(prefix="/dss", tags=["dss"])


@router.post("/predict", response_model=schemas.DSSPredictResponse)
def get_prediction(payload: schemas.DSSPredictRequest):
    """Predict crop yield (t/ha) from agronomic inputs.

    Inputs are validated against the model's training bounds (422 on failure);
    a 503 is returned if no model has been trained yet.
    """
    return predict.predict_yield(payload.model_dump())


@router.post("/train")
def trigger_training():
    """(Re)train the yield model on the agronomic dataset and refresh the cache."""
    result = train.train_model()
    predict.reset_cache()  # so the next /predict serves the freshly trained model
    return result


@router.get("/model")
def model_info():
    """Return metadata (metrics, feature importances, train time) for the model."""
    if not os.path.exists(train.META_PATH):
        return {"trained": False}
    with open(train.META_PATH) as fh:
        return {"trained": True, **json.load(fh)}
