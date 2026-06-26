# Predictive DSS Engine - Training dataset
#
# The application does not yet collect agronomic field readings (rainfall, soil
# pH, fertilizer rate), so there is no in-house data to learn from. Until real
# field data accumulates, we train on a SYNTHETIC dataset generated from a
# documented agronomic response surface. For each sample we draw a crop and
# three field conditions, then compute a yield from a crop-specific response:
#
#   * Rainfall   - yield rises to a crop-specific optimum then declines as
#                  excess water causes leaching / waterlogging (a Gaussian).
#   * Fertilizer - diminishing returns (a Mitscherlich-style saturating curve):
#                  each extra kg/ha adds less yield than the last.
#   * Soil pH    - a Gaussian peak at the crop's preferred pH; yield falls off
#                  in soils that are too acidic or too alkaline.
#   * Crop       - each crop has its own yield ceiling and its own optima, so
#                  the same field can be excellent for one crop and poor for
#                  another. This is what makes crop a real, learnable feature.
#
# Yields are in tonnes/ha. The relationship is non-monotonic on purpose, which
# is exactly why the model is a RandomForest and not a line.
#
# Swapping in a real dataset later means replacing the FEATURE lists and the
# body of `generate()` (or just dropping a CSV at DATA_PATH); nothing else
# changes.

import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_PATH = os.path.join(DATA_DIR, "crop_yield.csv")

# Feature contract shared by training and inference. Keep these stable and in
# order: numeric features first, then the categorical crop. NUMERIC/CATEGORICAL
# are kept separate because the model one-hot encodes the crop.
NUMERIC_FEATURES = ["rainfall", "fertilizer_used", "soil_ph"]
CATEGORICAL_FEATURES = ["crop"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = "yield_t_ha"
TARGET_UNIT = "t/ha"

# Plausible sampling ranges for each numeric input (used for the synthetic draw
# and as soft validation bounds on the API).
BOUNDS = {
    "rainfall": (300.0, 2000.0),       # mm / season
    "fertilizer_used": (0.0, 120.0),   # kg N / ha
    "soil_ph": (4.5, 8.5),             # pH units
}

# Crop-specific agronomic parameters. Values reflect rough West-African field
# expectations: cassava is a high-tonnage root crop, soybean a low-tonnage
# legume, rice wants the most water, sorghum tolerates dry/alkaline soils.
#   potential - t/ha ceiling under ideal conditions for that crop
#   rain_opt / rain_w - Gaussian rainfall optimum (mm) and width
#   fert_k    - fertilizer saturation rate (higher = saturates sooner)
#   ph_opt / ph_w - Gaussian soil-pH optimum and width
_CROP_PARAMS = {
    "maize":   {"potential": 7.0,  "rain_opt": 1000.0, "rain_w": 450.0, "fert_k": 0.040, "ph_opt": 6.5, "ph_w": 1.1},
    "rice":    {"potential": 8.5,  "rain_opt": 1600.0, "rain_w": 500.0, "fert_k": 0.035, "ph_opt": 6.0, "ph_w": 1.2},
    "sorghum": {"potential": 5.0,  "rain_opt": 700.0,  "rain_w": 400.0, "fert_k": 0.050, "ph_opt": 6.2, "ph_w": 1.4},
    "soybean": {"potential": 3.2,  "rain_opt": 900.0,  "rain_w": 350.0, "fert_k": 0.060, "ph_opt": 6.4, "ph_w": 1.0},
    "cassava": {"potential": 22.0, "rain_opt": 1100.0, "rain_w": 550.0, "fert_k": 0.030, "ph_opt": 5.8, "ph_w": 1.5},
}
CROPS = list(_CROP_PARAMS.keys())

_NOISE_SD = 0.08          # ~8% multiplicative noise


def _response(rainfall, fertilizer, soil_ph, crop):
    """Deterministic yield potential (no noise) for the given crop + inputs.

    Accepts scalars or numpy arrays; `crop` may be a single name or an array of
    names the same length as the numeric arrays."""
    crop_arr = np.asarray(crop)
    # Look up per-sample crop parameters (vectorised over the crop array).
    potential = np.array([_CROP_PARAMS[c]["potential"] for c in np.atleast_1d(crop_arr)])
    rain_opt = np.array([_CROP_PARAMS[c]["rain_opt"] for c in np.atleast_1d(crop_arr)])
    rain_w = np.array([_CROP_PARAMS[c]["rain_w"] for c in np.atleast_1d(crop_arr)])
    fert_k = np.array([_CROP_PARAMS[c]["fert_k"] for c in np.atleast_1d(crop_arr)])
    ph_opt = np.array([_CROP_PARAMS[c]["ph_opt"] for c in np.atleast_1d(crop_arr)])
    ph_w = np.array([_CROP_PARAMS[c]["ph_w"] for c in np.atleast_1d(crop_arr)])

    f_rain = np.exp(-(((rainfall - rain_opt) / rain_w) ** 2))
    f_fert = 1.0 - np.exp(-fert_k * fertilizer)
    f_ph = np.exp(-(((soil_ph - ph_opt) / ph_w) ** 2))
    out = potential * f_rain * f_fert * f_ph
    return out if crop_arr.ndim else float(out[0])


def generate(n: int = 6000, seed: int = 42) -> pd.DataFrame:
    """Draw `n` agronomically-plausible (crop + inputs -> yield) samples."""
    rng = np.random.default_rng(seed)
    rainfall = rng.uniform(*BOUNDS["rainfall"], n)
    fertilizer = rng.uniform(*BOUNDS["fertilizer_used"], n)
    soil_ph = rng.uniform(*BOUNDS["soil_ph"], n)
    crop = rng.choice(CROPS, n)

    base = _response(rainfall, fertilizer, soil_ph, crop)
    noisy = base * (1.0 + rng.normal(0.0, _NOISE_SD, n))
    yield_t_ha = np.clip(noisy, 0.2, None)  # never negative; a thin floor

    return pd.DataFrame(
        {
            "rainfall": rainfall.round(1),
            "fertilizer_used": fertilizer.round(1),
            "soil_ph": soil_ph.round(2),
            "crop": crop,
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
    print(frame.groupby("crop")["yield_t_ha"].describe().round(2))
