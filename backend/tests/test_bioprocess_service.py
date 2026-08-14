"""Unit tests for the pure drying-engineering functions (ticket 08, Phase 3).

These are numbers-in / numbers-out tests — no database, no client, no fixtures.
The expected values in Fixtures A, B and C are hand-calculated and independently
verified: if the implementation disagrees, the implementation is wrong, not the
fixture. Tolerance is pytest.approx(rel=1e-4) throughout.
"""
import pytest

from backend.app.services import bioprocess_service as bs


# --- Fixture A: maize, with process loss -----------------------------------

def test_fixture_a_maize_with_process_loss():
    m = bs.compute_drying_metrics(
        mass_in_kg=100.0,
        mass_out_kg=84.0,
        moisture_initial_wb=25.0,
        moisture_final_wb=13.0,
        drying_time_hours=10.0,
        crop="maize",
    )
    assert m["dry_matter_kg"] == pytest.approx(75.0, rel=1e-4)
    assert m["mass_out_expected_kg"] == pytest.approx(86.2069, rel=1e-4)
    assert m["process_loss_kg"] == pytest.approx(2.2069, rel=1e-4)
    assert m["process_loss_pct"] == pytest.approx(2.560, rel=1e-4)
    assert m["water_removed_kg"] == pytest.approx(16.0, rel=1e-4)
    assert m["moisture_initial_db"] == pytest.approx(33.3333, rel=1e-4)
    assert m["moisture_final_db"] == pytest.approx(14.9425, rel=1e-4)
    assert m["moisture_ratio_final"] == pytest.approx(0.448276, rel=1e-4)
    assert m["newton_k"] == pytest.approx(0.080235, rel=1e-4)
    assert m["specific_drying_rate"] == pytest.approx(16.0 / (75.0 * 10.0), rel=1e-4)
    assert m["safe_storage"] is True  # maize threshold 13.0, final 13.0 -> at threshold
    assert m["safe_storage_threshold_wb"] == pytest.approx(13.0)
    assert m["process_loss_warning"] is False
    assert m["page"] is None  # no intermediate readings supplied

    # THE TRAP: water_removed (from actual outlet, 16.0) and process_loss (actual
    # vs dry-matter-predicted outlet, 2.2069) are different numbers. If they ever
    # come out equal, the two have been conflated.
    assert m["water_removed_kg"] != pytest.approx(m["process_loss_kg"])


# --- Fixture B: rice paddy, clean balance ----------------------------------

def test_fixture_b_rice_clean_balance():
    m = bs.compute_drying_metrics(
        mass_in_kg=500.0,
        mass_out_kg=450.8671,
        moisture_initial_wb=22.0,
        moisture_final_wb=13.5,
        drying_time_hours=18.0,
        crop="rice",
    )
    assert m["dry_matter_kg"] == pytest.approx(390.0, rel=1e-4)
    assert m["mass_out_expected_kg"] == pytest.approx(450.8671, rel=1e-4)
    assert m["process_loss_kg"] == pytest.approx(0.0, abs=1e-3)  # ~0; rel is undefined at 0
    assert m["water_removed_kg"] == pytest.approx(49.1329, rel=1e-4)
    assert m["drying_rate_kg_h"] == pytest.approx(2.7296, rel=1e-4)
    assert m["moisture_ratio_final"] == pytest.approx(0.553337, rel=1e-4)
    assert m["newton_k"] == pytest.approx(0.032877, rel=1e-4)
    assert m["safe_storage"] is True  # rice threshold 14.0, final 13.5


# --- Fixture C: Page model, exact recovery ---------------------------------

def test_fixture_c_page_fit_exact_recovery():
    # Constructed from a known Page curve: M_0 = 30.0 %wb, k = 0.30, n = 0.75.
    # NORMALISER NOTE: M_db(0) is taken from moisture_initial_wb (30.0 %wb),
    # NEVER from the first reading (t=1). Normalising by the first reading, or
    # fitting on wet basis, gives n~0.805, k~0.218 — wrong. Do not "correct" it.
    readings = [
        (1, 24.098299),
        (2, 20.557042),
        (4, 15.501120),
        (6, 11.947665),
        (8, 9.326998),
    ]
    fit = bs.page_fit(moisture_initial_wb=30.0, readings=readings)
    assert fit is not None
    assert fit["n"] == pytest.approx(0.750000, rel=1e-4)
    assert fit["k"] == pytest.approx(0.300000, rel=1e-4)
    assert fit["r2_linear"] == pytest.approx(1.000000, rel=1e-4)
    assert fit["n_used"] == 5
    assert fit["n_dropped"] == 0


def test_page_fit_insufficient_readings_returns_none():
    # Fewer than three usable readings -> None. Never fabricate a fit.
    assert bs.page_fit(30.0, [(1, 24.098299), (2, 20.557042)]) is None
    assert bs.page_fit(30.0, []) is None


def test_page_fit_drops_out_of_range_readings():
    # A reading whose moisture >= the initial gives MR >= 1, which the double-log
    # cannot take; it must be dropped and counted, and the remaining five still
    # recover the known curve.
    readings = [
        (0.5, 30.0),  # MR = 1 exactly -> dropped
        (1, 24.098299),
        (2, 20.557042),
        (4, 15.501120),
        (6, 11.947665),
        (8, 9.326998),
    ]
    fit = bs.page_fit(30.0, readings)
    assert fit is not None
    assert fit["n_dropped"] == 1
    assert fit["n_used"] == 5
    assert fit["n"] == pytest.approx(0.75, rel=1e-4)


# --- Basis conversion ------------------------------------------------------

def test_basis_conversion_roundtrip():
    assert bs.wb_to_db(25.0) == pytest.approx(33.3333, rel=1e-4)
    assert bs.wb_to_db(13.0) == pytest.approx(14.9425, rel=1e-4)
    assert bs.db_to_wb(33.33333) == pytest.approx(25.0, rel=1e-4)
    assert bs.db_to_wb(bs.wb_to_db(41.7)) == pytest.approx(41.7, rel=1e-4)


# --- Safe-storage verdict --------------------------------------------------

def test_safe_storage_known_crops():
    assert bs.is_safe_to_store("maize", 13.0) is True   # at threshold
    assert bs.is_safe_to_store("maize", 13.1) is False  # above threshold
    assert bs.is_safe_to_store("groundnut", 6.5) is True
    assert bs.is_safe_to_store("groundnut", 8.0) is False
    assert bs.safe_storage_threshold("rice") == 14.0


def test_safe_storage_unknown_crop_is_none_never_false():
    # An unknown crop returns None (unknown), never a default False.
    assert bs.is_safe_to_store("tomato", 10.0) is None
    assert bs.is_safe_to_store(None, 10.0) is None
    assert bs.safe_storage_threshold("tomato") is None


# --- Warning flag and composed page/unknown-crop path ----------------------

def test_process_loss_warning_flag():
    # A large discrepancy between recorded and predicted outlet mass raises the
    # data-quality warning (|loss| > 5%) without being an error.
    m = bs.compute_drying_metrics(100.0, 70.0, 25.0, 13.0, 10.0, crop="maize")
    assert m["process_loss_pct"] > 5.0
    assert m["process_loss_warning"] is True


def test_compute_metrics_with_readings_and_unknown_crop():
    readings = [
        (1, 24.098299),
        (2, 20.557042),
        (4, 15.501120),
        (6, 11.947665),
        (8, 9.326998),
    ]
    m = bs.compute_drying_metrics(
        mass_in_kg=100.0,
        mass_out_kg=84.0,
        moisture_initial_wb=30.0,
        moisture_final_wb=9.0,
        drying_time_hours=10.0,
        crop=None,
        readings=readings,
    )
    assert m["page"] is not None
    assert m["page"]["n"] == pytest.approx(0.75, rel=1e-4)
    assert m["safe_storage"] is None                 # crop None -> unknown -> None
    assert m["safe_storage_threshold_wb"] is None
