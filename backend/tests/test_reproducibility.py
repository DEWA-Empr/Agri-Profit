"""Is the yield model reproducible, and under what conditions.

THE CLAIM THIS FILE MAKES PRECISE. Chapter Four reports R² 0.9762 and MAE
0.2414 for the Tier-2 forecast, and it previously stated that re-running the
training script would produce different figures "because the training data is
synthesised afresh". That is not what the code does: `dataset.generate` draws
from `np.random.default_rng(42)` and `train_model` passes `random_state=42` to
both the split and the forest, so the whole pipeline is seed-deterministic. The
real limitation is narrower — the fitted artefact is not under version control
and the environment was not pinned — and this file is what turns the narrow
version into something checkable.

TWO KINDS OF TEST, and the distinction is the point:

  * DETERMINISM tests are environment-independent. Same inputs, same process,
    same answer — twice. They hold on any machine, any library version, and are
    what actually rules out hidden entropy in the pipeline.

  * BASELINE tests compare against the recorded figures in
    `backend/app/ml/model_baseline.json` and are SKIPPED when the running
    library versions differ from the ones recorded there. Tree construction and
    RNG behaviour can change across a scikit-learn minor, so asserting the exact
    figures under an unknown environment would either fail for the wrong reason
    or force the tolerance so wide it proved nothing.

That is what "reproducible" means here, stated exactly:

    the recorded environment + the recorded seeds + the same generator
      => the recorded metrics, within the recorded tolerance.

Nothing is claimed outside the recorded environment, and no metric in this file
was invented — each was measured by the command in docs/REPRODUCIBILITY.md.
"""
import hashlib
import importlib.metadata as md
import json
import os

import numpy as np
import pytest
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from backend.app.ml import dataset, train

BASELINE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app", "ml", "model_baseline.json",
)


@pytest.fixture(scope="module")
def baseline():
    with open(BASELINE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _current_environment():
    return {
        "scikit-learn": md.version("scikit-learn"),
        "numpy": md.version("numpy"),
        "pandas": md.version("pandas"),
    }


def _environment_matches(baseline) -> tuple[bool, str]:
    recorded = baseline["environment"]
    current = _current_environment()
    differences = [
        f"{pkg}: recorded {recorded[pkg]}, running {current[pkg]}"
        for pkg in current
        if recorded.get(pkg) != current[pkg]
    ]
    return (not differences), "; ".join(differences)


def _fingerprint(df) -> str:
    """A hash of the VALUES, not of pandas' CSV text.

    `to_csv` float formatting can shift between pandas versions, which would
    break this check for a reason that has nothing to do with the data.
    """
    digest = hashlib.sha256()
    for column in ("rainfall", "fertilizer_used", "soil_ph", "yield_t_ha"):
        digest.update(np.ascontiguousarray(df[column].to_numpy(dtype="float64")).tobytes())
    digest.update("".join(df["crop"].astype(str)).encode())
    return digest.hexdigest()


def _fit_and_score():
    frame = dataset.generate()
    X, y = frame[dataset.FEATURES], frame[dataset.TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train._build_estimator(200, 42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return {
        "r2": float(r2_score(y_test, predictions)),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(np.sqrt(((y_test - predictions) ** 2).mean())),
    }


# --- determinism: holds anywhere -----------------------------------------

def test_the_generator_is_deterministic():
    """Two draws, one answer. This is the property the chapter's superseded
    claim denied, and it is environment-independent: `default_rng(42)` has a
    documented stable stream."""
    assert _fingerprint(dataset.generate()) == _fingerprint(dataset.generate())


def test_the_generator_ignores_the_call_order():
    """No hidden global RNG state: drawing something else in between must not
    move the result."""
    first = _fingerprint(dataset.generate())
    np.random.default_rng(7).normal(size=1000)   # unrelated draw
    assert _fingerprint(dataset.generate()) == first


def test_an_explicit_seed_changes_the_data():
    """The converse — otherwise the seed is decorative and 'seed-deterministic'
    would be true for the wrong reason."""
    assert _fingerprint(dataset.generate(seed=42)) != _fingerprint(dataset.generate(seed=43))


def test_the_cached_dataset_matches_a_fresh_draw():
    """`dataset.load` caches a CSV on first use and reads it forever after. If
    the cache and the generator disagreed, every later retrain would silently
    train on stale data."""
    cached = dataset.load()
    assert _fingerprint(cached) == _fingerprint(dataset.generate())


def test_training_is_deterministic():
    """Same data, same seeds, same metrics — twice in one process. Rules out
    entropy inside the estimator itself."""
    first, second = _fit_and_score(), _fit_and_score()
    for metric in ("r2", "mae", "rmse"):
        assert first[metric] == pytest.approx(second[metric], abs=1e-12), metric


def test_prediction_is_deterministic():
    """The served path, not just the training path: two identical requests must
    return the same forecast and the same confidence band."""
    payload = {"rainfall": 900.0, "fertilizer_used": 50.0, "soil_ph": 6.2, "crop": "maize"}
    train.ensure_model()
    from backend.app.ml import predict
    assert predict.predict_yield(dict(payload)) == predict.predict_yield(dict(payload))


# --- the recorded figures: only within the recorded environment ----------

def test_the_recorded_baseline_is_complete(baseline):
    """The baseline is the artefact a reader is asked to trust, so it must name
    its own conditions. A metric with no environment beside it is not a
    reproducible result."""
    assert set(baseline["metrics"]) == {"r2", "mae", "rmse"}
    assert set(baseline["environment"]) >= {"python", "scikit-learn", "numpy", "pandas"}
    assert baseline["dataset"]["seed"] == 42
    assert baseline["training"]["seed"] == 42
    assert baseline["training"]["split_random_state"] == 42
    assert baseline["dataset"]["n_samples"] == 6000


def test_the_seeds_in_the_baseline_are_the_seeds_in_the_code(baseline):
    """Guards the baseline against becoming a fiction: if someone changes the
    default seed, the recorded figures no longer describe what the code does."""
    import inspect
    assert f"seed: int = {baseline['dataset']['seed']}" in inspect.getsource(dataset.generate)
    assert f"seed: int = {baseline['training']['seed']}" in inspect.getsource(train.train_model)


def test_the_dataset_fingerprint_matches_the_baseline(baseline):
    assert _fingerprint(dataset.generate()) == baseline["dataset"]["sha256"]


def test_the_metrics_match_the_baseline(baseline):
    matches, differences = _environment_matches(baseline)
    if not matches:
        pytest.skip(
            "Environment differs from the one the baseline was recorded under "
            f"({differences}). Tree construction and RNG can change across a "
            "scikit-learn minor, so the exact figures are only claimed within "
            "the recorded environment. Determinism is asserted separately and "
            "does hold here. See docs/REPRODUCIBILITY.md."
        )

    measured = _fit_and_score()
    for metric, expected in baseline["metrics"].items():
        tolerance = baseline["tolerance"][metric]
        assert measured[metric] == pytest.approx(expected, abs=tolerance), (
            f"{metric}: measured {measured[metric]:.6f}, baseline {expected}"
        )


def test_the_metrics_are_in_a_sane_range_whatever_the_environment():
    """A weaker claim that holds everywhere, so an environment mismatch does not
    leave the model entirely unchecked. It is not evidence of field accuracy —
    the data is synthetic and the response surface was constructed to be
    recoverable — only that the pipeline is fitting rather than failing."""
    measured = _fit_and_score()
    assert 0.8 < measured["r2"] <= 1.0
    assert 0.0 < measured["mae"] < 1.0
    assert measured["rmse"] >= measured["mae"]   # true of any error distribution


def test_the_bounds_the_api_validates_against_match_the_generator():
    """The API rejects inputs outside the model's training range. If the two
    drifted, the endpoint would either refuse valid inputs or serve
    extrapolations as forecasts."""
    from backend.app.schemas import schemas
    request_fields = schemas.DSSPredictRequest.model_fields
    for feature, (low, high) in dataset.BOUNDS.items():
        constraints = request_fields[feature].metadata
        limits = {type(c).__name__: getattr(c, "ge", getattr(c, "le", None)) for c in constraints}
        assert low in limits.values(), f"{feature} lower bound drifted from the generator"
        assert high in limits.values(), f"{feature} upper bound drifted from the generator"
