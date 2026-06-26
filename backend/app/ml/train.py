# Predictive DSS Engine - Training logic
#
# Trains a RandomForest yield regressor on the agronomic dataset (see
# dataset.py) and persists it alongside a metadata sidecar. A forest is used
# rather than a linear model because the yield response is non-monotonic
# (rainfall and pH each have an optimum) and crop-dependent.
#
# The estimator is a Pipeline: a ColumnTransformer one-hot encodes the crop and
# passes the numeric features through, then a RandomForestRegressor predicts
# yield. Wrapping the encoder in the pipeline means inference can hand the model
# a raw {rainfall, fertilizer, soil_ph, crop} row and the encoding is applied
# consistently.

import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from . import dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "latest_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")


def _build_estimator(n_estimators: int, seed: int) -> Pipeline:
    """Crop one-hot encoder + numeric passthrough, feeding a RandomForest."""
    prep = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), dataset.CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",  # numeric features pass straight through
    )
    forest = RandomForestRegressor(
        n_estimators=n_estimators, random_state=seed, n_jobs=-1
    )
    return Pipeline([("prep", prep), ("rf", forest)])


def _aggregated_importances(model: Pipeline) -> dict:
    """Roll the forest's per-column importances up to original feature names.

    One-hot encoding explodes `crop` into one column per crop; we sum those back
    into a single `crop` importance so the UI can show one bar per real input."""
    prep: ColumnTransformer = model.named_steps["prep"]
    forest: RandomForestRegressor = model.named_steps["rf"]
    encoded_names = prep.get_feature_names_out()  # e.g. cat__crop_maize, remainder__rainfall

    totals: dict[str, float] = {}
    for name, weight in zip(encoded_names, forest.feature_importances_):
        if name.startswith("cat__crop_"):
            key = "crop"
        else:
            key = name.split("__", 1)[-1]  # strip the transformer prefix
        totals[key] = totals.get(key, 0.0) + float(weight)
    return {k: round(v, 4) for k, v in totals.items()}


def train_model(n_estimators: int = 200, seed: int = 42) -> dict:
    """Train, evaluate and persist the yield model. Returns a metrics summary."""
    df = dataset.load()
    X = df[dataset.FEATURES]
    y = df[dataset.TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed
    )

    model = _build_estimator(n_estimators, seed)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    meta = {
        "features": dataset.FEATURES,
        "numeric_features": dataset.NUMERIC_FEATURES,
        "categorical_features": dataset.CATEGORICAL_FEATURES,
        "crops": dataset.CROPS,
        "target": dataset.TARGET,
        "target_unit": dataset.TARGET_UNIT,
        "bounds": dataset.BOUNDS,
        "model": "Pipeline(OneHotEncoder + RandomForestRegressor)",
        "n_estimators": n_estimators,
        "n_samples": int(len(df)),
        "metrics": {
            "r2": round(float(r2_score(y_test, preds)), 4),
            "mae": round(float(mean_absolute_error(y_test, preds)), 4),
        },
        "feature_importances": _aggregated_importances(model),
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
