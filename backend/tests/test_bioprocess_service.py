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
    # Water BALANCE: water in 25.00 - water out 10.92. Was 16.0 while this was
    # computed as mass_in - mass_out; the 1.92 kg difference is dry matter
    # that physically left, not water (see water_removed_kg).
    assert m["water_removed_kg"] == pytest.approx(14.08, rel=1e-4)
    assert m["drying_rate_kg_h"] == pytest.approx(1.408, rel=1e-4)
    assert m["moisture_initial_db"] == pytest.approx(33.3333, rel=1e-4)
    assert m["moisture_final_db"] == pytest.approx(14.9425, rel=1e-4)
    assert m["moisture_ratio_final"] == pytest.approx(0.448276, rel=1e-4)
    assert m["newton_k"] == pytest.approx(0.080235, rel=1e-4)
    assert m["specific_drying_rate"] == pytest.approx(14.08 / (75.0 * 10.0), rel=1e-4)
    assert m["safe_storage"] is True  # maize threshold 13.0, final 13.0 -> at threshold
    assert m["safe_storage_threshold_wb"] == pytest.approx(13.0)
    assert m["process_loss_warning"] is False
    assert m["page"] is None  # no intermediate readings supplied

    # THE TRAP: water_removed (water balance, 14.08) and process_loss (actual
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


# --- Fixture F: water balance vs mass difference ----------------------------
# THE DISCRIMINATING FIXTURE. Neither A nor B can tell the two definitions
# apart: B conserves dry matter exactly, so mass difference and water balance
# agree to four decimals, and A's trap assertion compares water_removed against
# process_loss (16.0 vs 2.2069), which differ under BOTH definitions.
#
# This fixture has large, deliberate process loss and asserts the water balance
# directly, so the two definitions cannot both pass:
#
#   mass in  200 kg @ 30 %wb -> water in  60 kg, dry matter 140 kg
#   mass out 150 kg @ 12 %wb -> water out 18 kg, dry matter 132 kg
#
#   TRUE water removed (water balance) = 60 - 18 = 42.0 kg
#   mass difference                    = 200 - 150 = 50.0 kg
#   dry matter physically lost         = 140 - 132 = 8.0 kg
#   and 42.0 + 8.0 = 50.0 — the mass difference is water PLUS lost solids.
#
# This asserted the correct physics against an implementation that did not
# yet do it, and was xfail(strict=True) until water_removed_kg was corrected
# to a water balance. It now passes, and stands as the regression guard: if
# anyone reverts to a mass difference this is the test that catches it.
def test_fixture_f_water_removed_is_a_water_balance_not_a_mass_difference():
    mass_in, mass_out = 200.0, 150.0
    m_i, m_f, hours = 30.0, 12.0, 12.0

    m = bs.compute_drying_metrics(
        mass_in_kg=mass_in,
        mass_out_kg=mass_out,
        moisture_initial_wb=m_i,
        moisture_final_wb=m_f,
        drying_time_hours=hours,
        crop=None,
    )

    water_in = mass_in * m_i / 100.0        # 60.0
    water_out = mass_out * m_f / 100.0      # 18.0
    true_water_removed = water_in - water_out   # 42.0
    mass_difference = mass_in - mass_out        # 50.0

    # The premise of the fixture: the two definitions genuinely disagree here.
    assert true_water_removed != pytest.approx(mass_difference)
    # And the gap is exactly the dry matter that left the system.
    assert mass_difference - true_water_removed == pytest.approx(
        m["dry_matter_kg"] - mass_out * (1.0 - m_f / 100.0)
    )

    # The assertion under test: water removed must be the WATER balance.
    assert m["water_removed_kg"] == pytest.approx(42.0, rel=1e-9)

    # And both derived rates must follow from it, not from the mass difference.
    assert m["drying_rate_kg_h"] == pytest.approx(42.0 / 12.0, rel=1e-9)          # 3.5
    assert m["specific_drying_rate"] == pytest.approx(42.0 / (140.0 * 12.0), rel=1e-9)  # 0.025

