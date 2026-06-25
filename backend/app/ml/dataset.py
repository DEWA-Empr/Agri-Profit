# Predictive DSS Engine - Training dataset
#
# The application does not yet collect agronomic field readings (rainfall, soil
# pH, fertilizer rate), so there is no in-house data to learn from. Until real
# field data accumulates, we train on a SYNTHETIC dataset generated from a
# documented agronomic response surface:
#
#   * Rainfall   - yield rises to an optimum (~1000 mm) then declines as excess
#                  water causes leaching / waterlogging (a Gaussian response).
#   * Fertilizer - diminishing returns (a Mitscherlich-style saturating curve):
#                  each extra kg/ha adds less yield than the last.
#   * Soil pH    - a Gaussian peak near 6.5, the agronomic sweet spot for maize;
#                  yield falls off in acidic or alkaline soils.
#
# Yields are in tonnes/ha for maize. The relationship is non-monotonic on
# purpose, which is exactly why the model is a RandomForest and not a line.
#
# Swapping in a real dataset later means replacing FEATURES/TARGET and the body
# of `generate()` (or just dropping a CSV at DATA_PATH); nothing else changes.

import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_PATH = os.path.join(DATA_DIR, "crop_yield.csv")

# Feature order is the contract shared by training and inference. Keep it stable.
FEATURES = ["rainfall", "fertilizer_used", "soil_ph"]
TARGET = "yield_t_ha"
TARGET_UNIT = "t/ha"

# Plausible sampling ranges for each input (used for the synthetic draw and as
# soft validation bounds on the API).
BOUNDS = {
    "rainfall": (300.0, 2000.0),       # mm / season
    "fertilizer_used": (0.0, 120.0),   # kg N / ha
    "soil_ph": (4.5, 8.5),             # pH units
}

# Agronomic response parameters (documented above).
_POTENTIAL = 7.0          # t/ha ceiling under ideal conditions
_RAIN_OPT, _RAIN_WIDTH = 1000.0, 450.0
_FERT_K = 0.04            # saturation rate; ~0.86 of max reached by 50 kg/ha
_PH_OPT, _PH_WIDTH = 6.5, 1.1
_NOISE_SD = 0.08          # ~8% multiplicative noise


def _response(rainfall, fertilizer, soil_ph):
    """Deterministic yield potential (no noise) for the given inputs."""
    f_rain = np.exp(-(((rainfall - _RAIN_OPT) / _RAIN_WIDTH) ** 2))
    f_fert = 1.0 - np.exp(-_FERT_K * fertilizer)
    f_ph = np.exp(-(((soil_ph - _PH_OPT) / _PH_WIDTH) ** 2))
    return _POTENTIAL * f_rain * f_fert * f_ph


def generate(n: int = 4000, seed: int = 42) -> pd.DataFrame:
    """Draw `n` agronomically-plausible (inputs -> yield) samples."""
    rng = np.random.default_rng(seed)
    rainfall = rng.uniform(*BOUNDS["rainfall"], n)
    fertilizer = rng.uniform(*BOUNDS["fertilizer_used"], n)
    soil_ph = rng.uniform(*BOUNDS["soil_ph"], n)

    base = _response(rainfall, fertilizer, soil_ph)
    noisy = base * (1.0 + rng.normal(0.0, _NOISE_SD, n))
    yield_t_ha = np.clip(noisy, 0.2, None)  # never negative; a thin floor

    return pd.DataFrame(
        {
            "rainfall": rainfall.round(1),
            "fertilizer_used": fertilizer.round(1),
            "soil_ph": soil_ph.round(2),
            "yield_t_ha": yield_t_ha.round(3),
        }
    )


def load() -> pd.DataFrame:
    """Return the training frame, generating + caching the CSV on first use."""
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    df = generate()
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df


if __name__ == "__main__":
    frame = generate()
    os.makedirs(DATA_DIR, exist_ok=True)
    frame.to_csv(DATA_PATH, index=False)
    print(f"Wrote {len(frame)} rows to {DATA_PATH}")
    print(frame.describe().round(2))
