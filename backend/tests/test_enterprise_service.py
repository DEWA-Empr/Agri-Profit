"""Unit tests for the pure enterprise-economics functions (Phase 3).

Numbers-in / numbers-out — no database, no client, no fixtures. The expected
values in Fixtures A-G are hand-calculated and independently verified: if the
implementation disagrees, the implementation is wrong, not the fixture.
Tolerance is pytest.approx(rel=1e-4) throughout.
"""
import pytest

from backend.app.services import enterprise_service as es


# --- Fixture A: classification and coverage --------------------------------

MAIZE_COSTS = [
    (1200.0, "MECHANIZATION", "FUEL"),
    (800.0, "MECHANIZATION", "MACHINERY_HIRE"),
    (500.0, "MECHANIZATION", "REPAIRS"),
    (900.0, "FERTILIZER", None),
    (600.0, "LABOUR", None),
    (400.0, "MECHANIZATION", None),   # legacy row, extra_data = NULL
]


def test_fixture_a_classification_and_coverage():
    s = es.cost_structure(MAIZE_COSTS)
    assert s["variable_cost"] == pytest.approx(3500.0, rel=1e-4)
    assert s["semi_variable_cost"] == pytest.approx(500.0, rel=1e-4)
    assert s["fixed_cost_recorded"] == pytest.approx(0.0, abs=1e-9)
    assert s["unclassified_cost"] == pytest.approx(400.0, rel=1e-4)
    assert s["total_recorded_cost"] == pytest.approx(4400.0, rel=1e-4)
    assert s["cash_cost"] == pytest.approx(4000.0, rel=1e-4)
    assert s["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)


def test_zero_total_cost_has_undefined_coverage():
    """THE TRAP: coverage of nothing is undefined. Not 100 (a vacuous truth
    reads as 'fully classified'), not 0 (reads as 'nothing classified')."""
    s = es.cost_structure([])
    assert s["total_recorded_cost"] == 0.0
    assert s["classification_coverage_pct"] is None
    assert s["classification_coverage_pct"] != 100.0
    assert s["classification_coverage_pct"] != 0.0


def test_fixed_recorded_cost_is_its_own_bucket_and_stays_out_of_cash():
    """A DEPRECIATION row posted to the ledger is recorded fixed cost. It counts
    as classified, but it is not cash — it must not reach `cash_cost`."""
    s = es.cost_structure([
        (1000.0, "MECHANIZATION", "FUEL"),
        (250.0, "MECHANIZATION", "DEPRECIATION"),
    ])
    assert s["fixed_cost_recorded"] == pytest.approx(250.0, rel=1e-4)
    assert s["cash_cost"] == pytest.approx(1000.0, rel=1e-4)
    assert s["total_recorded_cost"] == pytest.approx(1250.0, rel=1e-4)
    assert s["classification_coverage_pct"] == pytest.approx(100.0, rel=1e-4)


def test_unclassified_categories_never_default_into_a_bucket():
    """YIELD and OTHER are outside the taxonomy. They are unclassified, and they
    depress coverage — they do not become variable by default."""
    s = es.cost_structure([
        (300.0, "OTHER", None),
        (700.0, "SEED", None),
    ])
    assert s["variable_cost"] == pytest.approx(700.0, rel=1e-4)
    assert s["unclassified_cost"] == pytest.approx(300.0, rel=1e-4)
    assert s["classification_coverage_pct"] == pytest.approx(70.0, rel=1e-4)


# --- Fixture B: depreciation overlay and allocation ------------------------

def test_fixture_b_depreciation_overlay():
    o = es.depreciation_overlay(
        equipment=[
            {"purchase_value_ngn": 240000.0, "depreciation_rate": 0.10},
            {"purchase_value_ngn": 150000.0, "depreciation_rate": None},
        ],
        period_days=30.0,
    )
    assert o["annual_charge_ngn"] == pytest.approx(24000.0, rel=1e-4)
    assert o["period_charge_ngn"] == pytest.approx(1972.60, rel=1e-4)
    assert o["equipment_unrated_count"] == 1
    assert o["equipment_count"] == 2
    assert o["period_days"] == pytest.approx(30.0, rel=1e-4)


def test_zero_rate_equipment_counts_as_unrated_not_as_a_zero_charge():
    """A zero rate is indistinguishable from an unrecorded one in the data, and
    both make the overlay partial. Neither may pass silently."""
    o = es.depreciation_overlay(
        equipment=[{"purchase_value_ngn": 90000.0, "depreciation_rate": 0.0}],
        period_days=365.0,
    )
    assert o["annual_charge_ngn"] == pytest.approx(0.0, abs=1e-9)
    assert o["period_charge_ngn"] == pytest.approx(0.0, abs=1e-9)
    assert o["equipment_unrated_count"] == 1


def test_equipment_with_no_purchase_value_is_unrated():
    """A rate with nothing to apply it to yields no charge and is reported."""
    o = es.depreciation_overlay(
        equipment=[{"purchase_value_ngn": None, "depreciation_rate": 0.15}],
        period_days=365.0,
    )
    assert o["annual_charge_ngn"] == pytest.approx(0.0, abs=1e-9)
    assert o["equipment_unrated_count"] == 1


def test_overlay_over_no_equipment_is_a_zero_charge_over_zero_records():
    o = es.depreciation_overlay(equipment=[], period_days=30.0)
    assert o["annual_charge_ngn"] == pytest.approx(0.0, abs=1e-9)
    assert o["equipment_count"] == 0
    assert o["equipment_unrated_count"] == 0


def test_fixture_b_proportional_allocation():
    a = es.allocate_fixed_cost(
        period_fixed_cost_ngn=2000.0,
        direct_cost_by_crop={"maize": 4400.0, "cowpea": 1600.0},
    )
    assert a["total_direct_cost_all_crops"] == pytest.approx(6000.0, rel=1e-4)
    assert a["allocations"]["maize"]["share"] == pytest.approx(0.733333, rel=1e-4)
    assert a["allocations"]["maize"]["allocated_fixed_ngn"] == pytest.approx(1466.67, rel=1e-4)
    assert a["allocations"]["cowpea"]["share"] == pytest.approx(0.266667, rel=1e-4)
    assert a["allocations"]["cowpea"]["allocated_fixed_ngn"] == pytest.approx(533.33, rel=1e-4)
    # Maize total cost = recorded direct 4400 + allocated fixed 1466.67.
    maize_total = 4400.0 + a["allocations"]["maize"]["allocated_fixed_ngn"]
    assert maize_total == pytest.approx(5866.67, rel=1e-4)
    # The allocation is exhaustive: shares sum to 1, charges sum to the pool.
    assert sum(v["allocated_fixed_ngn"] for v in a["allocations"].values()) == pytest.approx(
        2000.0, rel=1e-4
    )


def test_allocation_with_no_base_is_undefined_not_an_even_split():
    """With no recorded direct cost there is no allocation base. An even split
    would invent one; a zero would claim the fixed cost vanished."""
    a = es.allocate_fixed_cost(
        period_fixed_cost_ngn=2000.0,
        direct_cost_by_crop={"maize": 0.0, "cowpea": 0.0},
    )
    assert a["total_direct_cost_all_crops"] == pytest.approx(0.0, abs=1e-9)
    assert a["allocations"]["maize"]["share"] is None
    assert a["allocations"]["maize"]["allocated_fixed_ngn"] is None
    assert a["allocations"]["cowpea"]["allocated_fixed_ngn"] is None


# --- Fixture C: dual break-even price --------------------------------------

def test_fixture_c_dual_break_even_price():
    s = es.cost_structure(MAIZE_COSTS)
    b = es.break_even_prices(
        cash_cost=s["cash_cost"],
        total_recorded_cost=s["total_recorded_cost"],
        allocated_fixed_ngn=1466.6667,
        marketable_mass_kg=84.0,
        classification_coverage_pct=s["classification_coverage_pct"],
    )
    assert b["break_even_price_cash_ngn_per_kg"] == pytest.approx(47.6190, rel=1e-4)
    assert b["break_even_price_total_ngn_per_kg"] == pytest.approx(69.8413, rel=1e-4)
    assert b["classification_coverage_pct"] == pytest.approx(90.9091, rel=1e-4)

    # The four cost lines travel with the prices, so a reader can see WHICH cost
    # sits in which figure rather than having to reconstruct it.
    assert b["variable_and_semi_variable_cost_ngn"] == pytest.approx(4000.0, rel=1e-4)
    assert b["total_recorded_cost_ngn"] == pytest.approx(4400.0, rel=1e-4)
    assert b["allocated_fixed_ngn"] == pytest.approx(1466.6667, rel=1e-4)
    assert b["total_cost_ngn"] == pytest.approx(5866.6667, rel=1e-4)

    # THE TRAP: the two prices use DIFFERENT cost bases and must never collapse
    # into one number. Collapsing them is the specific error this module exists
    # to prevent — the gap between them IS the fixed-cost argument.
    assert (
        b["break_even_price_cash_ngn_per_kg"]
        != pytest.approx(b["break_even_price_total_ngn_per_kg"])
    )
    assert b["break_even_price_cash_ngn_per_kg"] < b["break_even_price_total_ngn_per_kg"]


def test_cash_price_is_strictly_lower_even_with_full_coverage_and_no_overlay():
    """Strictly lower is structural, not an artifact of the fixture: with no
    unclassified cost AND no allocated fixed cost, recorded fixed cost alone
    still keeps the two apart."""
    b = es.break_even_prices(
        cash_cost=1000.0,
        total_recorded_cost=1250.0,     # 250 of recorded DEPRECIATION
        allocated_fixed_ngn=0.0,
        marketable_mass_kg=50.0,
        classification_coverage_pct=100.0,
    )
    assert b["break_even_price_cash_ngn_per_kg"] == pytest.approx(20.0, rel=1e-4)
    assert b["break_even_price_total_ngn_per_kg"] == pytest.approx(25.0, rel=1e-4)
    assert b["break_even_price_cash_ngn_per_kg"] < b["break_even_price_total_ngn_per_kg"]


def test_unclassified_cost_sits_inside_total_and_outside_cash():
    """The documented asymmetry, asserted: moving 400 of cost from classified to
    unclassified leaves the TOTAL price untouched and lowers the CASH price."""
    classified = es.break_even_prices(
        cash_cost=4400.0, total_recorded_cost=4400.0,
        allocated_fixed_ngn=0.0, marketable_mass_kg=100.0,
        classification_coverage_pct=100.0,
    )
    partly = es.break_even_prices(
        cash_cost=4000.0, total_recorded_cost=4400.0,
        allocated_fixed_ngn=0.0, marketable_mass_kg=100.0,
        classification_coverage_pct=90.9091,
    )
    assert (
        partly["break_even_price_total_ngn_per_kg"]
        == pytest.approx(classified["break_even_price_total_ngn_per_kg"], rel=1e-4)
    )
    assert (
        partly["break_even_price_cash_ngn_per_kg"]
        < classified["break_even_price_cash_ngn_per_kg"]
    )


@pytest.mark.parametrize("mass", [0.0, None])
def test_break_even_price_is_undefined_without_marketable_mass(mass):
    """Preserves the existing unit-cost contract: undefined, never a
    fabricated zero and never a division by zero."""
    b = es.break_even_prices(
        cash_cost=4000.0, total_recorded_cost=4400.0,
        allocated_fixed_ngn=1466.6667, marketable_mass_kg=mass,
        classification_coverage_pct=90.9091,
    )
    assert b["break_even_price_cash_ngn_per_kg"] is None
    assert b["break_even_price_total_ngn_per_kg"] is None
    # The cost lines are still reported: the costs are known, the price is not.
    assert b["total_cost_ngn"] == pytest.approx(5866.6667, rel=1e-4)


def test_allocated_fixed_cost_may_be_absent():
    """With no allocation base upstream, allocated fixed is None and the total
    price falls back to recorded cost alone rather than failing."""
    b = es.break_even_prices(
        cash_cost=4000.0, total_recorded_cost=4400.0,
        allocated_fixed_ngn=None, marketable_mass_kg=84.0,
        classification_coverage_pct=90.9091,
    )
    assert b["allocated_fixed_ngn"] is None
    assert b["total_cost_ngn"] == pytest.approx(4400.0, rel=1e-4)
    assert b["break_even_price_total_ngn_per_kg"] == pytest.approx(52.3810, rel=1e-4)


# --- Fixture D: yield sensitivity matrix -----------------------------------

def test_fixture_d_yield_sensitivity_matrix():
    m = es.yield_sensitivity(
        baseline_marketable_mass_kg=84.0,
        cash_cost=4000.0,
        total_cost=5866.6667,
    )
    assert m["conditional"] is True
    assert m["baseline_marketable_mass_kg"] == pytest.approx(84.0, rel=1e-4)

    expected = [
        (75, 63.0, 63.4921, 93.1217),
        (90, 75.6, 52.9101, 77.6014),
        (100, 84.0, 47.6190, 69.8413),
        (110, 92.4, 43.2900, 63.4921),
        (125, 105.0, 38.0952, 55.8730),
    ]
    assert len(m["rows"]) == len(expected)
    for row, (pct, kg, cash, total) in zip(m["rows"], expected):
        assert row["percentage"] == pct
        assert row["marketable_mass_kg"] == pytest.approx(kg, rel=1e-4)
        assert row["break_even_price_cash_ngn_per_kg"] == pytest.approx(cash, rel=1e-4)
        assert row["break_even_price_total_ngn_per_kg"] == pytest.approx(total, rel=1e-4)
        # The asymmetry holds at every point on the matrix, not just at 100%.
        assert (
            row["break_even_price_cash_ngn_per_kg"]
            < row["break_even_price_total_ngn_per_kg"]
        )


def test_sensitivity_accepts_caller_supplied_percentages():
    m = es.yield_sensitivity(
        baseline_marketable_mass_kg=100.0,
        cash_cost=1000.0,
        total_cost=2000.0,
        percentages=[50, 200],
    )
    assert [r["percentage"] for r in m["rows"]] == [50, 200]
    assert m["rows"][0]["break_even_price_cash_ngn_per_kg"] == pytest.approx(20.0, rel=1e-4)
    assert m["rows"][1]["break_even_price_total_ngn_per_kg"] == pytest.approx(10.0, rel=1e-4)


def test_sensitivity_over_zero_baseline_yields_undefined_prices():
    """Conditional, not predictive — and undefined stays undefined all the way
    down the matrix rather than becoming an infinite price."""
    m = es.yield_sensitivity(
        baseline_marketable_mass_kg=0.0, cash_cost=4000.0, total_cost=5866.6667,
    )
    assert all(r["break_even_price_cash_ngn_per_kg"] is None for r in m["rows"])
    assert all(r["break_even_price_total_ngn_per_kg"] is None for r in m["rows"])


# --- Fixture E: operating expense ratio ------------------------------------

def test_fixture_e_operating_expense_ratio():
    # Maize: cash operating cost 4400 (variable 3500 + semi-variable 500 +
    # unclassified 400) against revenue 45000.
    assert es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=4400.0, revenue_ngn=45000.0
    ) == pytest.approx(9.7778, rel=1e-4)
    # Farm-wide: 6000 against 45000.
    assert es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=6000.0, revenue_ngn=45000.0
    ) == pytest.approx(13.3333, rel=1e-4)


def test_operating_expense_ratio_excludes_the_depreciation_overlay():
    """THE TRAP: the ratio is conventionally a CASH measure. Adding 2000 of
    allocated fixed cost — a non-cash overlay — must leave it unchanged, or the
    figure is no longer comparable to any published benchmark."""
    without_overlay = es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=4400.0, revenue_ngn=45000.0
    )
    # The caller's cash operating cost is built from the cost structure alone;
    # allocated fixed cost has no route into this numerator.
    s = es.cost_structure(MAIZE_COSTS)
    cash_operating = s["cash_cost"] + s["unclassified_cost"]
    with_overlay_available = es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=cash_operating, revenue_ngn=45000.0
    )
    assert cash_operating == pytest.approx(4400.0, rel=1e-4)
    assert with_overlay_available == pytest.approx(without_overlay, rel=1e-4)
    assert with_overlay_available == pytest.approx(9.7778, rel=1e-4)
    # And explicitly: had the 2000 overlay leaked in, the figure would be this.
    leaked = es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=4400.0 + 2000.0, revenue_ngn=45000.0
    )
    assert leaked == pytest.approx(14.2222, rel=1e-4)
    assert with_overlay_available != pytest.approx(leaked)


def test_operating_expense_ratio_is_undefined_at_zero_revenue():
    assert es.operating_expense_ratio_pct(
        cash_operating_cost_ngn=4400.0, revenue_ngn=0.0
    ) is None


# --- Fixture F: partial budget ---------------------------------------------

def test_fixture_f_partial_budget_solar_dryer_is_worth_it():
    p = es.partial_budget(
        added_revenue_ngn=12000.0,
        reduced_cost_ngn=3000.0,
        lost_revenue_ngn=0.0,
        added_cost_ngn=9500.0,
    )
    assert p["net_change_ngn"] == pytest.approx(5500.0, rel=1e-4)
    # The four inputs are echoed back so the interface can show the working.
    assert p["added_revenue_ngn"] == pytest.approx(12000.0, rel=1e-4)
    assert p["reduced_cost_ngn"] == pytest.approx(3000.0, rel=1e-4)
    assert p["lost_revenue_ngn"] == pytest.approx(0.0, abs=1e-9)
    assert p["added_cost_ngn"] == pytest.approx(9500.0, rel=1e-4)
    assert p["benefits_ngn"] == pytest.approx(15000.0, rel=1e-4)
    assert p["costs_ngn"] == pytest.approx(9500.0, rel=1e-4)


def test_fixture_f_negative_partial_budget_is_returned_signed():
    """A negative result is a valid and useful answer — the change is not worth
    making. Never clamped to zero, never raised as an error."""
    p = es.partial_budget(
        added_revenue_ngn=4000.0,
        reduced_cost_ngn=1000.0,
        lost_revenue_ngn=500.0,
        added_cost_ngn=9500.0,
    )
    assert p["net_change_ngn"] == pytest.approx(-5000.0, rel=1e-4)
    assert p["net_change_ngn"] < 0


# --- Fixture G: Olympic average, and the tie trap --------------------------

VERIFICATION_YIELDS = [589, 632, 646, 644, 610, 748, 809, 783, 589, 696, 666]


def test_fixture_g_olympic_average_discards_one_instance_not_all_ties():
    o = es.olympic_average_yield(VERIFICATION_YIELDS)
    assert o["grand_average_kg"] == pytest.approx(673.8182, rel=1e-4)
    assert o["olympic_average_kg"] == pytest.approx(668.2222, rel=1e-4)
    assert o["n_seasons"] == 11
    assert o["n_discarded"] == 2
    assert o["n_used"] == 9

    # THE TRAP: the minimum, 589, appears TWICE. The rule discards exactly ONE
    # maximum instance and ONE minimum instance. Discarding both 589s leaves 8
    # values averaging 678.6250 — the wrong answer, and the one a naive
    # value-based filter produces.
    assert o["olympic_average_kg"] != pytest.approx(678.6250, rel=1e-4)
    assert o["n_used"] != 8


def test_fixture_g_five_maize_seasons():
    o = es.olympic_average_yield([1800, 2100, 1450, 2400, 1950])
    assert o["grand_average_kg"] == pytest.approx(1940.0, rel=1e-4)
    assert o["olympic_average_kg"] == pytest.approx(1950.0, rel=1e-4)
    assert o["n_discarded"] == 2


def test_fixture_g_two_seasons_is_undefined_never_a_two_value_mean():
    """Below three seasons there is nothing left after discarding the extremes.
    Same shape as the unknown-crop verdict: build the function, let the platform
    grow into the data."""
    o = es.olympic_average_yield([1800, 2100])
    assert o["olympic_average_kg"] is None
    assert o["n_seasons"] == 2
    assert o["n_discarded"] == 0
    # The grand average is still defined — only the Olympic baseline is not.
    assert o["grand_average_kg"] == pytest.approx(1950.0, rel=1e-4)


def test_olympic_average_over_no_seasons_has_no_average_of_any_kind():
    o = es.olympic_average_yield([])
    assert o["olympic_average_kg"] is None
    assert o["grand_average_kg"] is None
    assert o["n_seasons"] == 0


def test_three_identical_seasons_survive_the_single_instance_rule():
    """Every value is both the maximum and the minimum. Discarding one of each
    must leave exactly one observation, not zero and not a division by zero."""
    o = es.olympic_average_yield([700, 700, 700])
    assert o["olympic_average_kg"] == pytest.approx(700.0, rel=1e-4)
    assert o["grand_average_kg"] == pytest.approx(700.0, rel=1e-4)
    assert o["n_used"] == 1
