# Predictive DSS Engine - Inference logic
#
# Loads the trained RandomForest once and serves yield predictions. Confidence
# is derived honestly from the spread of the forest's individual trees: a tight
# agreement between trees -> high confidence; a wide spread -> low confidence.
# This replaces the previously hardcoded "84.2%" in the UI.

import json
import os

import joblib
import numpy as np

from ..core.exceptions import ServiceUnavailableError
from . import dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "latest_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")

# Module-level cache so the joblib file is read from disk once, not per request.
_model = None
_meta = None


def _load():
    global _model, _meta
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise ServiceUnavailableError(
                "Model not trained yet. POST /dss/train first."
            )
        _model = joblib.load(MODEL_PATH)
        if os.path.exists(META_PATH):
            with open(META_PATH) as fh:
                _meta = json.load(fh)
    return _model, _meta


def reset_cache():
    """Drop the cached model so the next predict reloads (used after retrain)."""
    global _model, _meta
    _model, _meta = None, None


def predict_yield(data: dict) -> dict:
    """Predict yield (t/ha) with a confidence and prediction interval."""
    model, meta = _load()

    # Assemble the feature vector in the exact order the model was trained on.
    try:
        row = [float(data[f]) for f in dataset.FEATURES]
    except (KeyError, TypeError, ValueError) as exc:
        raise ServiceUnavailableError(f"Invalid feature input: {exc}")

    X = np.array([row])

    # Mean prediction, plus the per-tree spread for an honest uncertainty band.
    tree_preds = np.array([tree.predict(X)[0] for tree in model.estimators_])
    mean = float(tree_preds.mean())
    std = float(tree_preds.std())

    # Confidence: how tight the trees agree, relative to the prediction. A
    # coefficient of variation of 0 -> 100%; it falls as the spread widens.
    cv = std / mean if mean > 0 else 1.0
    confidence = round(max(0.0, min(1.0, 1.0 - cv)) * 100, 1)
    lower = round(max(0.0, mean - 1.96 * std), 2)
    upper = round(mean + 1.96 * std, 2)

    unit = (meta or {}).get("target_unit", dataset.TARGET_UNIT)
    return {
        "prediction": round(mean, 2),
        "unit": unit,
        "confidence": confidence,
        "interval": {"lower": lower, "upper": upper},
        "feature_importances": (meta or {}).get("feature_importances", {}),
    }
