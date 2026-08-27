"""Domain bounds on money and quantity.

Each of the first three groups replays an input that the running API ACCEPTED
before `schemas.Money` / `schemas.Quantity` existed. They are regression tests
against demonstrated defects, not hypotheticals:

  * a debit of -1,000,000 was accepted, and a farm with 50,000 of revenue
    reported a gross margin of 1,050,000;
  * `Infinity` was accepted and stored, turning that farm's gross margin into
    null permanently — the ledger has no delete, so it could not be repaired
    through the API at all;
  * `NaN` reached the database and surfaced as an unhandled 500.

The last group is the other half of the job and matters just as much: the bounds
must not reject values a farm legitimately records. Zero cost and zero yield are
both real, and both are asserted here, because a validation change that quietly
broke sun drying would be worse than the hole it closed.
"""
import pytest

from backend.app.schemas.schemas import MAX_NAIRA, MAX_QUANTITY


def _log(client, **financial):
    body = {
        "activity_type": financial.pop("activity_type", "seed"),
        "crop": financial.pop("crop", "maize"),
        "financial_data": {
            "amount": financial.pop("amount", 1000.0),
            "transaction_type": financial.pop("transaction_type", "debit"),
            "category": financial.pop("category", "seed"),
        },
        **financial,
    }
    return client.post("/api/v1/ledger/logs", json=body)


def _raw_log(client, amount_literal):
    """Post a body with a raw JSON literal, so Infinity/NaN reach the parser."""
    return client.post(
        "/api/v1/ledger/logs",
        headers={"Content-Type": "application/json"},
        content=(
            '{"activity_type":"seed","financial_data":{"amount":%s,'
            '"transaction_type":"debit","category":"seed"}}' % amount_literal
        ),
    )


# --- 1. the negative-amount hole -----------------------------------------

def test_a_negative_expense_is_rejected(client):
    assert _log(client, amount=-1_000_000.0, transaction_type="debit").status_code == 422


def test_a_negative_revenue_is_rejected(client):
    assert _log(client, amount=-50_000.0, transaction_type="credit").status_code == 422


def test_a_negative_expense_can_no_longer_inflate_the_profit_and_loss(client):
    """The defect in full: sign belongs to `transaction_type`, so a negative
    debit was an expense that ADDED to profit — and no other control on this
    ledger would have shown it, because they all protect an entry's history
    rather than its value."""
    assert _log(client, amount=50_000.0, transaction_type="credit", category="yield",
                activity_type="yield").status_code == 201
    assert _log(client, amount=-1_000_000.0, transaction_type="debit").status_code == 422

    assert client.get("/api/v1/reports/pnl").json()["gross_margin"] == 50_000.0


# --- 2. non-finite values -------------------------------------------------

@pytest.mark.parametrize("literal", ["Infinity", "-Infinity", "NaN"])
def test_a_non_finite_amount_is_rejected_at_the_edge(client, literal):
    """422, and specifically NOT a 500 and NOT a 201. An infinity that reaches
    the ledger cannot be removed, because the ledger does not delete."""
    assert _raw_log(client, literal).status_code == 422


def test_the_profit_and_loss_survives_an_attempted_infinity(client):
    _log(client, amount=25_000.0)
    _raw_log(client, "Infinity")

    margin = client.get("/api/v1/reports/pnl").json()["gross_margin"]
    assert margin == -25_000.0        # a real number, not null


def test_a_non_finite_quantity_is_rejected(client):
    resp = client.post(
        "/api/v1/ledger/logs",
        headers={"Content-Type": "application/json"},
        content=('{"activity_type":"yield","crop":"maize","quantity":Infinity,'
                 '"unit":"kg","financial_data":{"amount":1,"transaction_type":'
                 '"credit","category":"yield"}}'),
    )
    assert resp.status_code == 422


# --- 3. magnitude and payload size ---------------------------------------

def test_an_absurd_amount_is_rejected(client):
    assert _log(client, amount=1e308).status_code == 422


def test_the_ceiling_itself_is_accepted(client):
    """A boundary is only correct if the boundary value passes."""
    assert _log(client, amount=MAX_NAIRA).status_code == 201


def test_just_over_the_ceiling_is_refused(client):
    assert _log(client, amount=MAX_NAIRA * 1.001).status_code == 422


def test_an_oversized_description_is_rejected(client):
    assert _log(client, description="x" * 200_000).status_code == 422


def test_an_oversized_unit_is_rejected(client):
    assert _log(client, activity_type="yield", quantity=10, unit="k" * 500).status_code == 422


def test_an_oversized_client_id_is_rejected(client):
    """It is an index key; unbounded text here is an unbounded index entry."""
    assert _log(client, client_id="c" * 5_000).status_code == 422


# --- 4. quantities --------------------------------------------------------

def test_a_negative_yield_quantity_is_rejected(client):
    """A negative yield makes unit cost of production negative, and unit cost is
    the figure a farmer prices against."""
    resp = _log(client, activity_type="yield", quantity=-50.0, unit="kg",
                transaction_type="credit", category="yield")
    assert resp.status_code == 422


def test_an_absurd_quantity_is_rejected(client):
    resp = _log(client, activity_type="yield", quantity=MAX_QUANTITY * 10,
                unit="kg", transaction_type="credit", category="yield")
    assert resp.status_code == 422


# --- 5. equipment and maintenance ----------------------------------------

def test_a_negative_purchase_price_is_rejected(client):
    """It propagates through the depreciation overlay into allocated fixed cost
    and into the break-even price to cover total cost."""
    resp = client.post("/api/v1/equipment/", json={
        "name": "Tractor", "purchase_price": -5_000_000.0, "depreciation_rate": 10.0,
    })
    assert resp.status_code == 422


def test_an_absurd_purchase_price_is_rejected(client):
    resp = client.post("/api/v1/equipment/", json={
        "name": "Tractor", "purchase_price": 1e15, "depreciation_rate": 10.0,
    })
    assert resp.status_code == 422


def test_an_empty_equipment_name_is_rejected(client):
    resp = client.post("/api/v1/equipment/", json={
        "name": "", "purchase_price": 100_000.0, "depreciation_rate": 10.0,
    })
    assert resp.status_code == 422


def test_a_negative_maintenance_cost_is_rejected(client):
    eq = client.post("/api/v1/equipment/", json={
        "name": "Tractor", "purchase_price": 1_000_000.0, "depreciation_rate": 10.0,
    }).json()
    resp = client.post("/api/v1/equipment/maintenance", json={
        "equipment_id": eq["id"], "description": "service", "cost": -900.0,
    })
    assert resp.status_code == 422


# --- 6. partial budget ----------------------------------------------------

@pytest.mark.parametrize("field", [
    "added_revenue_ngn", "reduced_cost_ngn", "lost_revenue_ngn", "added_cost_ngn",
])
def test_partial_budget_rejects_a_non_finite_input(client, field):
    body = {
        "added_revenue_ngn": 1000.0, "reduced_cost_ngn": 0.0,
        "lost_revenue_ngn": 0.0, "added_cost_ngn": 0.0,
    }
    raw = ", ".join(
        f'"{k}": {"Infinity" if k == field else v}' for k, v in body.items()
    )
    resp = client.post(
        "/api/v1/dss/partial-budget",
        headers={"Content-Type": "application/json"},
        content="{" + raw + "}",
    )
    assert resp.status_code == 422


def test_partial_budget_rejects_an_absurd_input(client):
    resp = client.post("/api/v1/dss/partial-budget", json={
        "added_revenue_ngn": 1e15, "reduced_cost_ngn": 0.0,
        "lost_revenue_ngn": 0.0, "added_cost_ngn": 0.0,
    })
    assert resp.status_code == 422


# --- 7. what must STILL be accepted --------------------------------------
# The other half of the job. A bound that rejects a legitimate agricultural
# value is a worse defect than the one it closed, because it stops a farmer
# recording what actually happened.

def test_a_zero_cost_log_is_still_accepted(client):
    """Sun drying with the farm's own labour costs nothing. The platform relies
    on this and pairs a transaction at 0.00 regardless."""
    assert _log(client, amount=0.0).status_code == 201


def test_a_zero_yield_is_still_accepted(client):
    """A failed harvest is a real, recordable zero — not a missing value."""
    resp = _log(client, activity_type="yield", quantity=0.0, unit="kg",
                amount=0.0, transaction_type="credit", category="yield")
    assert resp.status_code == 201


def test_a_large_but_plausible_transaction_is_accepted(client):
    """A combine harvester. The ceiling must not second-guess a real purchase."""
    assert _log(client, amount=200_000_000.0).status_code == 201


def test_a_fractional_amount_is_accepted(client):
    """Kobo. Money is not integral here."""
    assert _log(client, amount=1234.56).status_code == 201


def test_a_large_but_plausible_harvest_is_accepted(client):
    resp = _log(client, activity_type="yield", quantity=250_000.0, unit="kg",
                amount=1_000_000.0, transaction_type="credit", category="yield")
    assert resp.status_code == 201


def test_a_normal_description_is_accepted(client):
    assert _log(client, description="Urea applied to the north block, 5 bags").status_code == 201


def test_the_seeded_demonstration_figures_still_pass_validation(client):
    """The exact amounts Chapter Four quotes from farm 26 must remain enterable —
    a bound that rejected them would invalidate the reported figures."""
    for amount in (3_500.0, 45_000.0, 25_000.0, 94_400.0, 178_600.0, 624_950.0):
        assert _log(client, amount=amount).status_code == 201, amount
