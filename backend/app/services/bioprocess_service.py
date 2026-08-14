"""Post-harvest drying engineering — pure functions (ticket 08, Phase 3).

Numbers in, numbers out. This module has NO database access, NO I/O, and no
imports from models, schemas or endpoints. Every derived drying metric is
computed here so it can be tested in isolation and reused on read (the endpoints
in Phase 4 deserialise a stored payload and call `compute_drying_metrics`).

Conventions (see docs/adr/0001):

  * Moisture is *entered* on a wet basis (mass of water / total mass), because
    that is what a field meter reads. Drying kinetics are conventionally fitted
    on a *dry* basis (mass of water / mass of dry matter). We convert internally.
  * Equilibrium moisture content (M_e) is neglected: the moisture ratio is
    MR(t) = M_db(t) / M_db(0). This simplification is stated explicitly here.

numpy only — no scipy, no new dependency.
"""
from typing import Optional, Sequence

import numpy as np

# Indicative safe-storage moisture ceilings (% wet basis) for tropical storage.
# The parenthetical qualifiers (paddy, shelled, chips) describe the form the
# figure applies to; the dict key is the crop name as entered on a log.
# TODO(cite): FAO / NSPRI / IITA post-harvest handling guidance — replace this
# comment with the actual citation before the thesis; an examiner will ask.
SAFE_STORAGE_MOISTURE_WB: dict[str, float] = {
    "maize": 13.0,
    "rice": 14.0,       # paddy
    "sorghum": 12.5,
    "millet": 12.0,
    "cowpea": 12.0,
    "groundnut": 7.0,   # shelled
    "soybean": 12.0,
    "cassava": 12.0,    # chips
    "yam": 12.0,        # chips
}

# A |process loss| beyond this fraction is flagged as a data-quality signal, not
# rejected — measurement error and genuine handling loss both live here.
PROCESS_LOSS_WARN_PCT = 5.0


# --- 4.1 Basis conversion --------------------------------------------------

def wb_to_db(moisture_wb: float) -> float:
    """Wet-basis moisture (%) -> dry-basis moisture (%). M_db = 100·M_wb/(100−M_wb)."""
    return 100.0 * moisture_wb / (100.0 - moisture_wb)


def db_to_wb(moisture_db: float) -> float:
    """Dry-basis moisture (%) -> wet-basis moisture (%). M_wb = 100·M_db/(100+M_db)."""
    return 100.0 * moisture_db / (100.0 + moisture_db)


# --- 4.2 Dry-matter balance ------------------------------------------------

def dry_matter_kg(mass_in_kg: float, moisture_initial_wb: float) -> float:
    """Dry matter is conserved through drying: mass_in·(1 − M_i_wb/100)."""
    return mass_in_kg * (1.0 - moisture_initial_wb / 100.0)


def expected_outlet_mass_kg(
    mass_in_kg: float, moisture_initial_wb: float, moisture_final_wb: float
) -> float:
    """Outlet mass predicted by dry-matter conservation:
    mass_in·(100 − M_i_wb)/(100 − M_f_wb)."""
    return mass_in_kg * (100.0 - moisture_initial_wb) / (100.0 - moisture_final_wb)


def process_loss(
    mass_in_kg: float,
    moisture_initial_wb: float,
    moisture_final_wb: float,
    mass_out_actual_kg: float,
) -> tuple[float, float]:
    """Return (process_loss_kg, process_loss_pct), signed and NOT clamped.

    Compares the recorded outlet mass against the dry-matter-predicted outlet
    mass. May be slightly negative from measurement error — returned as-is.
    """
    expected = expected_outlet_mass_kg(mass_in_kg, moisture_initial_wb, moisture_final_wb)
    loss_kg = expected - mass_out_actual_kg
    loss_pct = 100.0 * loss_kg / expected
    return loss_kg, loss_pct


# --- 4.3 Water removed and drying rate -------------------------------------

def water_removed_kg(mass_in_kg: float, mass_out_actual_kg: float) -> float:
    """Water removed uses the ACTUAL recorded outlet mass, not the predicted one.
    (Deliberately distinct from process_loss, which uses the predicted outlet.)"""
    return mass_in_kg - mass_out_actual_kg


def drying_rate_kg_h(water_removed: float, drying_time_hours: float) -> float:
    """Average water-removal rate (kg water / h)."""
    return water_removed / drying_time_hours


def specific_drying_rate(
    water_removed: float, dry_matter: float, drying_time_hours: float
) -> float:
    """Water removed per unit dry matter per hour (kg water / kg dry matter / h)."""
    return water_removed / (dry_matter * drying_time_hours)


# --- 4.4 Thin-layer drying kinetics ----------------------------------------

def moisture_ratio_final(moisture_initial_wb: float, moisture_final_wb: float) -> float:
    """MR_final = M_db(final) / M_db(0), with equilibrium moisture neglected."""
    return wb_to_db(moisture_final_wb) / wb_to_db(moisture_initial_wb)


def newton_k(
    moisture_initial_wb: float, moisture_final_wb: float, drying_time_hours: float
) -> float:
    """Newton / Lewis rate constant from the two endpoints alone.

    MR = exp(−k·t)  =>  k = −ln(MR_final) / t. Always computable (no readings)."""
    mr_final = moisture_ratio_final(moisture_initial_wb, moisture_final_wb)
    return float(-np.log(mr_final) / drying_time_hours)


def page_fit(
    moisture_initial_wb: float,
    readings: Sequence[tuple[float, float]],
    min_readings: int = 3,
) -> Optional[dict]:
    """Fit the Page model MR = exp(−k·t^n) by linearisation, or return None.

    THREE POINTS THAT MUST NOT BE "CORRECTED":
      1. Every reading is converted to DRY basis before the moisture ratio is
         formed — the fit is on dry basis, matching newton_k.
      2. The normaliser M_db(0) comes from `moisture_initial_wb`, NEVER from the
         first reading. (Normalising by the first reading, or fitting on wet
         basis, silently yields the wrong n and k.)
      3. `moisture_initial_wb` is the normaliser and is never itself a fit point:
         it would give MR = 1, and ln(−ln(1)) = ln(0) = −inf.

    Linearisation: ln(−ln(MR)) = ln(k) + n·ln(t), so a straight-line fit of
    y = ln(−ln(MR)) against x = ln(t) gives slope n and intercept ln(k).

    Readings with MR outside (0, 1) cannot take the double logarithm; they are
    dropped and counted (`n_dropped`). Fewer than `min_readings` usable points
    returns None — never a fabricated fit. The reported R² is that of the
    LINEARISED fit, labelled as such (it is not the R² in moisture space).
    """
    mdb0 = wb_to_db(moisture_initial_wb)

    xs: list[float] = []
    ys: list[float] = []
    dropped = 0
    for t, moisture_wb in readings:
        mr = wb_to_db(moisture_wb) / mdb0
        if 0.0 < mr < 1.0:
            xs.append(np.log(t))
            ys.append(np.log(-np.log(mr)))
        else:
            dropped += 1

    if len(xs) < min_readings:
        return None

    x = np.array(xs)
    y = np.array(ys)
    slope, intercept = np.polyfit(x, y, 1)

    y_hat = np.polyval([slope, intercept], x)
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot

    return {
        "n": float(slope),
        "k": float(np.exp(intercept)),
        "r2_linear": r2,
        "n_used": len(xs),
        "n_dropped": dropped,
    }


# --- 4.5 Safe-storage rule -------------------------------------------------

def safe_storage_threshold(crop: Optional[str]) -> Optional[float]:
    """The safe-storage moisture ceiling (% wet basis) for a crop, or None if the
    crop is not in the table (unknown -> None, never a default)."""
    if crop is None:
        return None
    return SAFE_STORAGE_MOISTURE_WB.get(crop.lower())


def is_safe_to_store(crop: Optional[str], moisture_final_wb: float) -> Optional[bool]:
    """True/False whether the dried lot is at or below its safe-storage moisture.
    Returns None for an unknown crop — never False by default."""
    threshold = safe_storage_threshold(crop)
    if threshold is None:
        return None
    return moisture_final_wb <= threshold


# --- Composition: every derived metric for one drying run ------------------

def compute_drying_metrics(
    mass_in_kg: float,
    mass_out_kg: float,
    moisture_initial_wb: float,
    moisture_final_wb: float,
    drying_time_hours: float,
    crop: Optional[str] = None,
    readings: Optional[Sequence[tuple[float, float]]] = None,
) -> dict:
    """Compose all Phase-3 metrics for a single drying run.

    Pure: it assembles the functions above and returns a plain dict. The Page fit
    is included only when three or more usable readings are supplied; otherwise
    `page` is None. Inputs are assumed already validated by DryingParams (the
    schema guarantees mass > 0, 0 < M < 100, final < initial, time > 0).
    """
    dm = dry_matter_kg(mass_in_kg, moisture_initial_wb)
    loss_kg, loss_pct = process_loss(
        mass_in_kg, moisture_initial_wb, moisture_final_wb, mass_out_kg
    )
    removed = water_removed_kg(mass_in_kg, mass_out_kg)

    page = None
    if readings:
        page = page_fit(moisture_initial_wb, readings)

    return {
        "dry_matter_kg": dm,
        "mass_out_expected_kg": expected_outlet_mass_kg(
            mass_in_kg, moisture_initial_wb, moisture_final_wb
        ),
        "process_loss_kg": loss_kg,
        "process_loss_pct": loss_pct,
        "process_loss_warning": abs(loss_pct) > PROCESS_LOSS_WARN_PCT,
        "water_removed_kg": removed,
        "drying_rate_kg_h": drying_rate_kg_h(removed, drying_time_hours),
        "specific_drying_rate": specific_drying_rate(removed, dm, drying_time_hours),
        "moisture_initial_db": wb_to_db(moisture_initial_wb),
        "moisture_final_db": wb_to_db(moisture_final_wb),
        "moisture_ratio_final": moisture_ratio_final(moisture_initial_wb, moisture_final_wb),
        "newton_k": newton_k(moisture_initial_wb, moisture_final_wb, drying_time_hours),
        "page": page,
        "safe_storage": is_safe_to_store(crop, moisture_final_wb),
        "safe_storage_threshold_wb": safe_storage_threshold(crop),
    }
