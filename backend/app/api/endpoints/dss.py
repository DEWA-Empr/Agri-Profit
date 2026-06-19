from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...models.database import get_db
from ...ml import predict, train

router = APIRouter(prefix="/dss", tags=["dss"])

@router.post("/predict")
def get_prediction(data: dict):
    """
    Endpoint for the Predictive DSS Engine.
    Data should contain features for yield prediction.
    """
    prediction = predict.predict_yield(data)
    return prediction

@router.post("/train")
def trigger_training(db: Session = Depends(get_db)):
    """
    Trigger model training using historical data from the database.
    """
    # In a real scenario, we'd fetch actual data here
    # logs = db.query(models.OperationalLog).all()
    # Mock training for now
    result = train.train_model(None, None)
    return result
