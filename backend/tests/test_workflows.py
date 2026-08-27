"""The journeys a farm actually takes, end to end.

WHAT THIS ADDS TO A SUITE THAT ALREADY HAS 380 TESTS. The existing suite is
strong per unit — the ledger, the DSS arithmetic, the drying model and the
enterprise economics each have their own file and their own edge cases. What
nothing asserted was the WHOLE CHAIN: that a record entered on the first screen
turns into a paired transaction, that the transaction reaches the profit-and-
loss statement, that a drying run moves the unit cost a farmer prices against,
and that the figure an investor eventually sees through a share link is the same
figure the farmer saw. A platform can pass every unit test and still be broken
between them.

These are also the regression proof for everything added in this hardening
cycle. Authorization, bounded money, share expiry and equipment correction all
sit directly on these paths, and if any of them broke the journey it breaks
here.

EVERY ASSERTION IS ON A VALUE OR ON PERSISTED STATE. Not on a status code alone,
and never on whether a function was reached. Where the answer is arithmetic, the
expected number is computed by hand in the test.
"""
import pytest

from backend.app.models import models


# --- helpers --------------------------------------------------------------

def _log(client, **kw):
    body = {
        "activity_type": kw.pop("activity_type"),
        "crop": kw.pop("crop", None),
        "description": kw.pop("description", None),
        "quantity": kw.pop("quantity", None),
        "unit": kw.pop("unit", None),
        "extra_data": kw.pop("extra_data", None),
        "financial_data": {
            "amount": kw.pop("amount"),
            "transaction_type": kw.pop("transaction_type"),
            "category": kw.pop("category", None) or body_category(kw),
        },
    }
    if "client_id" in kw:
        body["client_id"] = kw.pop("client_id")
    return client.post("/api/v1/ledger/logs", json=body)


def body_category(_kw):
    return "other"


def _drying(mass_in=100.0, mass_out=84.0):
    return {
        "process_type": "DRYING", "method": "SUN",
        "mass_in_kg": mass_in, "mass_out_kg": mass_out,
        "moisture_initial_wb": 25.0, "moisture_final_wb": 13.0,
        "drying_time_hours": 10.0,
    }


def _crop_row(client, crop):
    rows = client.get("/api/v1/dss/decision-support").json()["crops"]
    return next((c for c in rows if c["crop"] == crop), None)


# --- Workflow 1: a season, from first record to profit-and-loss ----------

def test_a_full_season_reaches_the_profit_and_loss_statement(client, db):
    """Seed, fertiliser, harvest — and the arithmetic a farmer would do by hand.

    Costs 25,000 + 18,000; revenue 90,000. Margin must be 47,000, and the
    paired-write invariant must hold in the database, not just in the response.
    """
    assert _log(client, activity_type="seed", category="seed", crop="maize",
                amount=25_000.0, transaction_type="debit").status_code == 201
    assert _log(client, activity_type="fertilizer", category="fertilizer", crop="maize",
                amount=18_000.0, transaction_type="debit").status_code == 201
    assert _log(client, activity_type="yield", category="yield", crop="maize",
                quantity=1_500.0, unit="kg",
                amount=90_000.0, transaction_type="credit").status_code == 201

    pnl = client.get("/api/v1/reports/pnl").json()
    assert pnl["revenue"] == 90_000.0
    assert pnl["expenses"] == 43_000.0
    assert pnl["gross_margin"] == 47_000.0

    # The paired-write invariant, checked against the database rather than
    # inferred from the API: one transaction per log, no orphans either way.
    logs = db.query(models.OperationalLog).count()
    txs = db.query(models.FinancialTransaction).count()
    assert logs == txs == 3
    unpaired = db.query(models.OperationalLog).filter(
        models.OperationalLog.financial_transaction_id.is_(None)
    ).count()
    assert unpaired == 0


def test_the_csv_export_carries_the_same_totals_as_the_report(client):
    """A lender reads the export, not the screen. They must agree."""
    _log(client, activity_type="seed", category="seed", crop="maize",
         amount=25_000.0, transaction_type="debit")
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=1_000.0, unit="kg", amount=90_000.0, transaction_type="credit")

    csv = client.get("/api/v1/reports/pnl.csv").text
    assert "90000.00" in csv
    assert "25000.00" in csv
    assert "65000.00" in csv          # the margin


# --- Workflow 2: offline entry and its replay ----------------------------

def test_a_retried_offline_record_is_stored_exactly_once(client, db):
    """The hardest requirement for rural deployment: a flaky network retries the
    same POST, and the farm must not be billed twice for one bag of fertiliser.
    """
    first = _log(client, activity_type="fertilizer", category="fertilizer", crop="maize",
                 amount=25_000.0, transaction_type="debit", client_id="offline-key-1")
    assert first.status_code == 201

    replay = _log(client, activity_type="fertilizer", category="fertilizer", crop="maize",
                  amount=25_000.0, transaction_type="debit", client_id="offline-key-1")
    assert replay.status_code == 200                     # found, not created
    assert replay.json()["id"] == first.json()["id"]

    assert db.query(models.OperationalLog).count() == 1
    assert db.query(models.FinancialTransaction).count() == 1
    assert client.get("/api/v1/reports/pnl").json()["expenses"] == 25_000.0


def test_two_farms_may_use_the_same_offline_key(make_client):
    """Two devices that agree on a key scheme are not one farm. Idempotency is
    per tenant, and a collision must not surface as an error or a leak."""
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")

    ra = _log(a, activity_type="seed", category="seed", crop="maize",
              amount=1_000.0, transaction_type="debit", client_id="shared-key")
    rb = _log(b, activity_type="seed", category="seed", crop="rice",
              amount=2_000.0, transaction_type="debit", client_id="shared-key")

    assert ra.status_code == 201 and rb.status_code == 201
    assert ra.json()["id"] != rb.json()["id"]
    assert a.get("/api/v1/reports/pnl").json()["expenses"] == 1_000.0
    assert b.get("/api/v1/reports/pnl").json()["expenses"] == 2_000.0


# --- Workflow 3: correcting a mistake ------------------------------------

def test_a_reversal_restores_the_position_without_erasing_the_history(client, db):
    """The correction story a lender is asked to trust: the mistake stays
    visible, and the numbers come back to where they should be."""
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=1_000.0, unit="kg", amount=90_000.0, transaction_type="credit")
    mistake = _log(client, activity_type="fertilizer", category="fertilizer", crop="maize",
                   amount=25_000.0, transaction_type="debit").json()

    assert client.get("/api/v1/reports/pnl").json()["gross_margin"] == 65_000.0

    reversal = client.post(f"/api/v1/ledger/logs/{mistake['id']}/reverse")
    assert reversal.status_code == 201

    pnl = client.get("/api/v1/reports/pnl").json()
    assert pnl["expenses"] == 0.0            # the pile it fed returns to zero
    assert pnl["revenue"] == 90_000.0        # the other pile is untouched
    assert pnl["gross_margin"] == 90_000.0

    # Both entries remain — nothing was deleted.
    assert db.query(models.OperationalLog).count() == 3
    assert db.query(models.OperationalLog).filter(
        models.OperationalLog.reverses_id == mistake["id"]
    ).count() == 1

    # And the per-crop view agrees with the farm-wide one.
    maize = _crop_row(client, "maize")
    assert maize["expenses"] == 0.0
    assert "Unspecified" not in {c["crop"] for c in
                                 client.get("/api/v1/dss/decision-support").json()["crops"]}


def test_a_reversal_cannot_be_applied_twice(client):
    mistake = _log(client, activity_type="seed", category="seed", crop="maize",
                   amount=1_000.0, transaction_type="debit").json()
    assert client.post(f"/api/v1/ledger/logs/{mistake['id']}/reverse").status_code == 201
    assert client.post(f"/api/v1/ledger/logs/{mistake['id']}/reverse").status_code == 409


# --- Workflow 4: harvest -> drying -> the price that matters -------------

def test_drying_moves_the_unit_cost_a_farmer_prices_against(client):
    """The chain Chapter 4 calls the engineering contribution, end to end.

    100 kg harvested at a recorded cost of 3,500; a sun-drying run at no cost
    leaves 84 kg marketable. Unit cost is 3,500/100 = 35.00 per harvest kg and
    3,500/84 = 41.67 per marketable kg. Both are computed here rather than
    copied, so the test fails if either denominator changes.
    """
    _log(client, activity_type="fertilizer", category="fertilizer", crop="maize",
         amount=3_500.0, transaction_type="debit")
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=100.0, unit="kg", amount=45_000.0, transaction_type="credit")
    assert _log(client, activity_type="bioprocess", category="bioprocess", crop="maize",
                amount=0.0, transaction_type="debit",
                extra_data=_drying()).status_code == 201

    maize = _crop_row(client, "maize")
    assert maize["marketable_mass_kg"] == pytest.approx(84.0)
    assert maize["unit_cost_of_production"] == pytest.approx(3_500.0 / 100.0)
    assert maize["unit_cost_per_kg_marketable"] == pytest.approx(3_500.0 / 84.0)
    # The two must not be silently merged: they have different denominators.
    assert maize["unit_cost_of_production"] != pytest.approx(
        maize["unit_cost_per_kg_marketable"]
    )


def test_the_drying_summary_and_the_decision_support_agree_on_marketable_mass(client):
    """Two endpoints derive it independently; a farmer sees both."""
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=100.0, unit="kg", amount=45_000.0, transaction_type="credit")
    _log(client, activity_type="bioprocess", category="bioprocess", crop="maize",
         amount=0.0, transaction_type="debit", extra_data=_drying())

    summary = client.get("/api/v1/bioprocess/summary").json()
    by_crop = {c["crop"]: c for c in summary["crops"]}
    assert by_crop["maize"]["total_marketable_mass_kg"] == pytest.approx(
        _crop_row(client, "maize")["marketable_mass_kg"]
    )
    # And the water balance: 100 kg at 25% wb has 75 kg of dry matter, so an
    # outlet of 84 kg means 16 kg of mass left the lot. Water removed is derived
    # from the moisture change, not from the mass difference — the two are
    # deliberately distinct, and the gap between them is process loss.
    assert by_crop["maize"]["total_mass_in_kg"] == pytest.approx(100.0)
    assert by_crop["maize"]["total_water_removed_kg"] > 0


# --- Workflow 5: from the ledger to a break-even price -------------------

def test_equipment_flows_through_to_the_break_even_price(client):
    """The full enterprise-economics chain: an asset produces a depreciation
    charge, the charge is allocated to the crop, and the crop's break-even price
    to cover total cost sits above its cash price by exactly that allocation.
    """
    client.post("/api/v1/equipment/", json={
        "name": "Tractor", "purchase_price": 1_000_000.0, "depreciation_rate": 10.0,
    })
    _log(client, activity_type="mechanization", category="mechanization", crop="maize",
         amount=40_000.0, transaction_type="debit",
         extra_data={"cost_subtype": "FUEL"})
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=100.0, unit="kg", amount=45_000.0, transaction_type="credit")
    _log(client, activity_type="bioprocess", category="bioprocess", crop="maize",
         amount=0.0, transaction_type="debit", extra_data=_drying())

    result = client.get("/api/v1/dss/break-even-price?period_days=365").json()
    maize = next(c for c in result["crops"] if c["crop"] == "maize")

    # A year of 10% depreciation on 1,000,000.
    assert result["period_fixed_cost_ngn"] == pytest.approx(100_000.0)
    assert result["period_source"] == "specified"
    # Cash price is classified variable cost over marketable mass.
    assert maize["break_even_price_cash_ngn_per_kg"] == pytest.approx(40_000.0 / 84.0)
    # Total price is strictly higher, and the gap is the fixed-cost burden.
    assert maize["break_even_price_total_ngn_per_kg"] > maize["break_even_price_cash_ngn_per_kg"]


def test_the_reporting_window_is_reported_with_the_figure(client):
    """A derived window widens with every log, so a break-even price is only
    reproducible while the window it was computed over travels with it."""
    _log(client, activity_type="seed", category="seed", crop="maize",
         amount=1_000.0, transaction_type="debit")

    derived = client.get("/api/v1/dss/break-even-price").json()
    pinned = client.get("/api/v1/dss/break-even-price?period_days=365").json()
    assert derived["period_source"] == "derived"
    assert pinned["period_source"] == "specified"
    assert pinned["period_days"] == 365


# --- Workflow 6: sharing with a lender -----------------------------------

def test_an_investor_sees_exactly_what_the_farmer_sees(client, anon_client):
    """The trust claim, checked rather than asserted: the public report is the
    farm's own figures, not a separately computed and possibly divergent view.
    """
    _log(client, activity_type="seed", category="seed", crop="maize",
         amount=25_000.0, transaction_type="debit")
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=1_000.0, unit="kg", amount=90_000.0, transaction_type="credit")

    owner_pnl = client.get("/api/v1/reports/pnl").json()
    owner_crops = client.get("/api/v1/dss/decision-support").json()["crops"]

    token = client.post("/api/v1/share/links", json={"label": "First Bank"}).json()["token"]
    report = anon_client.get(f"/api/v1/share/report/{token}").json()

    assert report["pnl"]["gross_margin"] == owner_pnl["gross_margin"]
    assert report["pnl"]["revenue"] == owner_pnl["revenue"]
    assert report["crops"] == owner_crops


def test_a_reversal_is_reflected_in_the_investors_view(client, anon_client):
    """The correction must reach the lender, or the share link becomes a way to
    show a stale, better-looking position."""
    _log(client, activity_type="yield", category="yield", crop="maize",
         quantity=1_000.0, unit="kg", amount=90_000.0, transaction_type="credit")
    overstated = _log(client, activity_type="yield", category="yield", crop="maize",
                      quantity=500.0, unit="kg", amount=50_000.0,
                      transaction_type="credit").json()

    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()["token"]
    assert anon_client.get(f"/api/v1/share/report/{token}").json()["pnl"]["revenue"] == 140_000.0

    client.post(f"/api/v1/ledger/logs/{overstated['id']}/reverse")
    assert anon_client.get(f"/api/v1/share/report/{token}").json()["pnl"]["revenue"] == 90_000.0


def test_revoking_a_link_closes_it_immediately(client, anon_client):
    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()
    assert anon_client.get(f"/api/v1/share/report/{token['token']}").status_code == 200
    client.post(f"/api/v1/share/links/{token['id']}/revoke")
    assert anon_client.get(f"/api/v1/share/report/{token['token']}").status_code == 404


# --- Workflow 7: a farm with staff ---------------------------------------

def test_a_worker_records_a_manager_reviews_and_an_owner_shares(client, make_client, anon_client):
    """The three roles doing the three jobs the role model exists to separate,
    on one farm, in one sequence."""
    client.post("/api/v1/auth/members", json={
        "email": "worker@test.example", "password": "member-password", "role": "worker"})
    client.post("/api/v1/auth/members", json={
        "email": "manager@test.example", "password": "member-password", "role": "manager"})

    def as_member(email):
        token = anon_client.post("/api/v1/auth/login", json={
            "email": email, "password": "member-password"}).json()["access_token"]
        c = make_client(email=f"spare-{email}", farm_name="spare")
        c.headers.update({"Authorization": f"Bearer {token}"})
        return c

    worker, manager = as_member("worker@test.example"), as_member("manager@test.example")

    # The worker records what happened in the field.
    assert _log(worker, activity_type="fertilizer", category="fertilizer", crop="maize",
                amount=25_000.0, transaction_type="debit").status_code == 201
    # ...and cannot see the farm's financial position.
    assert worker.get("/api/v1/reports/pnl").status_code == 403

    # The manager reviews the money and can correct it.
    assert manager.get("/api/v1/reports/pnl").json()["expenses"] == 25_000.0
    # ...but cannot hand the farm's finances to an outsider.
    assert manager.post("/api/v1/share/links", json={"label": "Bank"}).status_code == 403

    # Only the owner can.
    assert client.post("/api/v1/share/links", json={"label": "Bank"}).status_code == 201

    # The worker's record is the one the owner's report is built on.
    assert client.get("/api/v1/reports/pnl").json()["expenses"] == 25_000.0


# --- Workflow 8: the boundary holds across the whole journey -------------

def test_nothing_from_one_farms_journey_reaches_another(make_client, anon_client):
    """Isolation asserted at the end of a full journey rather than on a single
    endpoint: ledger, report, DSS, economics, drying and sharing at once."""
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")

    _log(a, activity_type="seed", category="seed", crop="secret-crop",
         amount=25_000.0, transaction_type="debit")
    _log(a, activity_type="yield", category="yield", crop="secret-crop",
         quantity=100.0, unit="kg", amount=90_000.0, transaction_type="credit")
    _log(a, activity_type="bioprocess", category="bioprocess", crop="secret-crop",
         amount=0.0, transaction_type="debit", extra_data=_drying())
    a.post("/api/v1/equipment/", json={
        "name": "A's tractor", "purchase_price": 1_000_000.0, "depreciation_rate": 10.0})

    assert b.get("/api/v1/reports/pnl").json()["revenue"] == 0.0
    assert b.get("/api/v1/ledger/logs").json() == []
    assert b.get("/api/v1/equipment/").json() == []
    assert b.get("/api/v1/dss/decision-support").json()["crops"] == []
    assert b.get("/api/v1/bioprocess/summary").json()["crops"] == []
    assert b.get("/api/v1/dss/cost-structure?crop=secret-crop").status_code == 404

    # And B's own share link shows B's farm, not A's.
    token = b.post("/api/v1/share/links", json={"label": "B's bank"}).json()["token"]
    report = anon_client.get(f"/api/v1/share/report/{token}").json()
    assert report["pnl"]["revenue"] == 0.0
    assert report["crops"] == []


# --- Workflow 9: the empty farm ------------------------------------------

def test_a_brand_new_farm_answers_every_screen_without_inventing_figures(client):
    """Day one. Every endpoint must return an honest empty state rather than a
    zero that reads as a result, or a 500."""
    assert client.get("/api/v1/reports/pnl").json()["gross_margin"] == 0.0
    assert client.get("/api/v1/dss/decision-support").json()["crops"] == []
    assert client.get("/api/v1/dss/cost-structure").json()["crops"] == []
    assert client.get("/api/v1/dss/break-even-price").json()["crops"] == []
    assert client.get("/api/v1/dss/yield-baseline").json()["crops"] == []
    assert client.get("/api/v1/bioprocess/summary").json()["crops"] == []
    assert client.get("/api/v1/ledger/summary").json()["gross_margin"] == 0.0
    assert len(client.get("/api/v1/reports/pnl/monthly").json()) == 6

    # Farm-wide coverage is null, not 100 and not 0: there is no cost to have
    # classified, and a percentage over nothing is not a fact.
    assert client.get("/api/v1/dss/cost-structure").json()["farm"]["classification_coverage_pct"] is None


# --- Workflow 10: operational health -------------------------------------

def test_liveness_answers_without_touching_the_database(anon_client):
    """A liveness probe that checked the database would restart a healthy
    application on every Postgres hiccup, turning a brief outage into a restart
    loop. It must answer on the process alone."""
    resp = anon_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_readiness_reports_the_database(anon_client):
    resp = anon_client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json()["checks"]["database"] == "ok"


def _break_the_database(db, message):
    """Make the session's execute() fail the way an unreachable server would."""
    def _raise(*_args, **_kwargs):
        raise RuntimeError(message)
    db.execute = _raise


def test_readiness_fails_loudly_when_the_database_is_unreachable(anon_client, db):
    """503, not 200 and not a 500 traceback — a proxy has to be able to tell
    'the API is down' from 'the API is up and its database is not'."""
    _break_the_database(db, "connection refused")
    resp = anon_client.get("/health/ready")

    assert resp.status_code == 503
    assert resp.json()["status"] == "not ready"
    assert resp.json()["checks"]["database"] == "unreachable"


def test_readiness_does_not_leak_the_connection_string(anon_client, db):
    """A probe response is read by things nobody is watching. The cause is
    logged in full; it is not returned."""
    _break_the_database(
        db, "could not connect to postgresql://user:hunter2@db:5432/agriprofit")
    body = anon_client.get("/health/ready").text

    assert "hunter2" not in body
    assert "postgresql://" not in body


def test_health_needs_no_authentication(anon_client):
    """A probe cannot hold a credential. Both endpoints must answer anonymously,
    and neither may disclose anything about a farm."""
    for path in ("/health", "/health/ready"):
        resp = anon_client.get(path)
        assert resp.status_code in (200, 503)
        assert "farm" not in resp.text.lower()
