# Predictive DSS Engine - Training logic
#
# Trains a RandomForest yield regressor on the agronomic dataset (see
# dataset.py) and persists it alongside a metadata sidecar. A forest is used
# rather than a linear model because the yield response is non-monotonic
# (rainfall and pH each have an optimum); a line cannot represent that.

import json
import os
from datetime import datetime, timezone

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from . import dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "latest_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")


def train_model(n_estimators: int = 200, seed: int = 42) -> dict:
    """Train, evaluate and persist the yield model. Returns a metrics summary."""
    df = dataset.load()
    X = df[dataset.FEATURES]
    y = df[dataset.TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    model = RandomForestRegressor(
        n_estimators=n_estimators, random_state=seed, n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    meta = {
        "features": dataset.FEATURES,
        "target": dataset.TARGET,
        "target_unit": dataset.TARGET_UNIT,
        "bounds": dataset.BOUNDS,
        "model": "RandomForestRegressor",
        "n_estimators": n_estimators,
        "n_samples": int(len(df)),
        "metrics": {
            "r2": round(float(r2_score(y_test, preds)), 4),
            "mae": round(float(mean_absolute_error(y_test, preds)), 4),
        },
        "feature_importances": {
            f: round(float(w), 4)
            for f, w in zip(dataset.FEATURES, model.feature_importances_)
        },
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    with open(META_PATH, "w") as fh:
        json.dump(meta, fh, indent=2)

    return {"status": "trained", **meta}


def ensure_model() -> bool:
    """Train the model if none exists yet. Returns True if it trained one.

    Called on app startup so a freshly-built container can serve predictions
    without a manual /dss/train call (there is no backend volume, so the model
    does not survive a rebuild)."""
    if os.path.exists(MODEL_PATH):
        return False
    train_model()
    return True


if __name__ == "__main__":
    print("Starting model training...")
    result = train_model()
    print(json.dumps(result, indent=2))
