"""The same-farm client_id race, against a real database and a real constraint.

WHAT IS BEING TESTED. `ledger_service.create_operational_log` resolves
idempotency in two places:

  1. a fast-path lookup before the insert  (`_find_by_client_id`), and
  2. an `IntegrityError` handler after the commit, which repeats that lookup.

(2) exists only because (1) is a time-of-check/time-of-use window: two requests
carrying the same offline `client_id` can both pass the pre-check before either
commits, and the loser's INSERT is then rejected by
`UNIQUE(farm_id, client_id)`. The contract that must hold across the window is
the SAME contract the sequential replay has, and it is not invented here — it is
read off `test_idempotent_log_creation` and the endpoint in
`api/endpoints/ledger.py`:

    * the caller gets the winner's row, not an error;
    * `created` is False, so the endpoint answers 200 Found, not 201 Created;
    * exactly ONE OperationalLog and ONE FinancialTransaction exist afterwards
      — the loser's flushed transaction is rolled back, not double-booked.

The last point is the one that matters financially and the one an id-equality
assertion alone would miss.

Since migration e6a2b4c7d130 the constraint is `UNIQUE(farm_id, client_id)`, so
a same-farm replay is the ONLY collision the handler's recovery lookup can
resolve. The cross-farm case that used to fall through to the bare `raise` (and
out as a 500) is covered separately in test_api.py; nothing here changes that
behaviour, and the bare `raise` is deliberately left reachable for genuinely
unexpected integrity failures.

WHY A SEPARATE MODULE. conftest's `db` fixture yields one in-memory session
shared by every client, which cannot model two connections. These tests build a
file-backed SQLite database so each session has a connection of its own and the
unique constraint is enforced by the database, not by Python.
"""

import sqlite3
import threading
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import models
from backend.app.models.database import Base
from backend.app.schemas import schemas
from backend.app.services import ledger_service

CLIENT_ID = "offline-queue-key-0001"


def _log(client_id: str = CLIENT_ID, amount: float = 5000.0) -> schemas.OperationalLogCreate:
    """The payload an offline queue flushes: a real record carrying a client_id."""
    return schemas.OperationalLogCreate(
        activity_type="seed",
        description="Two bags of maize seed",
        quantity=2.0,
        unit="bags",
        client_id=client_id,
        financial_data=schemas.FinancialTransactionCreate(
            amount=amount,
            transaction_type="debit",
            category="seed",
            description="Seed purchase",
        ),
    )


@pytest.fixture
def engine(tmp_path):
    """A file-backed SQLite database, so two sessions get two real connections.

    `timeout` is the busy timeout: when both connections want the write lock, the
    loser waits for it instead of failing with "database is locked". That makes
    the WRITE serialise, which is what a real server's database does; the race
    being tested is between the two reads, not between the two writes.
    """
    engine = create_engine(
        f"sqlite:///{tmp_path / 'race.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def farm_id(engine):
    Session = sessionmaker(bind=engine)
    with Session() as session:
        farm = models.Farm(name="Farm A")
        session.add(farm)
        session.commit()
        return farm.id


@pytest.fixture
def sessions(engine):
    """Two independent sessions on the same database — two "requests"."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    a, b = Session(), Session()
    try:
        yield a, b
    finally:
        a.close()
        b.close()


def _count(session, farm_id):
    logs = session.query(models.OperationalLog).filter_by(farm_id=farm_id).count()
    transactions = session.query(models.FinancialTransaction).filter_by(farm_id=farm_id).count()
    return logs, transactions


# --- 1. The constraint really is enforced by the database -------------------
# A precondition for everything below: if the unique index were missing, the
# loser's insert would simply succeed and every assertion here would pass while
# proving nothing.


def test_the_farm_scoped_unique_constraint_is_live(engine, farm_id, sessions):
    session_a, _ = sessions
    ledger_service.create_operational_log(session_a, farm_id, _log())

    # A second row with the same (farm_id, client_id), inserted underneath the
    # service so no idempotency logic can intervene.
    session_a.add(
        models.OperationalLog(farm_id=farm_id, activity_type="seed", client_id=CLIENT_ID)
    )
    with pytest.raises(Exception) as raised:
        session_a.commit()
    assert isinstance(raised.value.orig, sqlite3.IntegrityError)
    session_a.rollback()


# --- 2. The recovery path, with the pre-check forced to miss ----------------


def test_losing_the_same_farm_race_returns_the_winners_row(engine, farm_id, sessions):
    """The loser's pre-check ran before the winner committed.

    That interleaving is reproduced by forcing `_find_by_client_id` to miss on
    its FIRST call inside the loser's request and behave normally afterwards —
    which is exactly the state the loser is in when it read a moment too early.
    Everything after the pre-check is real: a real INSERT, rejected by a real
    UNIQUE index, recovered by the real handler.
    """
    session_a, session_b = sessions

    winner, created = ledger_service.create_operational_log(session_a, farm_id, _log())
    assert created is True
    winner_id = winner.id

    real_lookup = ledger_service._find_by_client_id
    calls = {"n": 0}

    def stale_first_read(db, farm, client_id):
        calls["n"] += 1
        if calls["n"] == 1:
            return None  # the pre-check, taken before the winner committed
        return real_lookup(db, farm, client_id)

    with patch.object(ledger_service, "_find_by_client_id", stale_first_read):
        loser, loser_created = ledger_service.create_operational_log(
            session_b, farm_id, _log(amount=9999.0)
        )

    # The pre-check missed and the recovery lookup ran — otherwise the fast path
    # would have returned on call 1 and there would be no race to speak of.
    assert calls["n"] == 2

    # The contract: the winner's row, reported as found rather than created.
    assert loser_created is False
    assert loser.id == winner_id

    # And the money is booked once. The loser flushed a FinancialTransaction
    # before its log insert failed; the rollback must have discarded it.
    logs, transactions = _count(session_b, farm_id)
    assert (logs, transactions) == (1, 1)
    assert session_b.query(models.FinancialTransaction).one().amount == 5000.0


def test_losing_the_race_is_a_200_at_the_api_surface(client):
    """The same race, observed through the endpoint: 200 Found, not a 500.

    This is the assertion the audit asked for. It runs on conftest's ordinary
    authenticated client, because what is being checked here is the status code
    the endpoint derives from `created` — not the connection topology, which
    the service-level test above covers.
    """
    payload = {
        "activity_type": "seed",
        "description": "Two bags of maize seed",
        "quantity": 2.0,
        "unit": "bags",
        "client_id": CLIENT_ID,
        "financial_data": {
            "amount": 5000.0,
            "transaction_type": "debit",
            "category": "seed",
            "description": "Seed purchase",
        },
    }
    assert client.post("/api/v1/ledger/logs", json=payload).status_code == 201

    real_lookup = ledger_service._find_by_client_id
    calls = {"n": 0}

    def stale_first_read(db, farm, client_id):
        calls["n"] += 1
        return None if calls["n"] == 1 else real_lookup(db, farm, client_id)

    with patch.object(ledger_service, "_find_by_client_id", stale_first_read):
        raced = client.post("/api/v1/ledger/logs", json=payload)

    assert calls["n"] == 2
    assert raced.status_code == 200, raced.text
    assert len(client.get("/api/v1/ledger/logs").json()) == 1
    assert len(client.get("/api/v1/ledger/transactions").json()) == 1


def test_an_unrecoverable_integrity_error_still_raises(engine, farm_id, sessions):
    """The handler is a recovery, not a blanket swallow.

    If the lookup after the rollback still finds nothing, the exception is
    re-raised — a 500, correctly, because the failure is then something other
    than a same-farm replay. Pinning this stops a future edit from turning the
    handler into `except IntegrityError: pass`, which would silently drop a
    farmer's record.
    """
    session_a, session_b = sessions
    ledger_service.create_operational_log(session_a, farm_id, _log())

    with patch.object(ledger_service, "_find_by_client_id", lambda *_: None):
        with pytest.raises(Exception) as raised:
            ledger_service.create_operational_log(session_b, farm_id, _log())
    assert isinstance(raised.value.orig, sqlite3.IntegrityError)


# --- 3. Two real threads, unpatched -----------------------------------------


def test_two_threads_posting_one_client_id_book_exactly_one_record(engine, farm_id):
    """The race with nothing stubbed out: two threads, two connections, one key.

    Which thread wins is genuinely nondeterministic, and which code path the
    loser takes depends on how the reads interleave — so the assertions are on
    the invariants that must hold under EVERY interleaving, not on the path
    taken. A run in which the pre-check happens to win is still a valid run; the
    forced-miss test above is what guarantees the IntegrityError branch itself
    is exercised on every run.

    The failure this would catch is the one that matters: an exception escaping
    to the caller (the 500), or two records booked for one offline write.
    """
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    results: list[tuple[int, bool]] = []
    errors: list[BaseException] = []
    start = threading.Barrier(2)

    def post():
        session = Session()
        try:
            start.wait(timeout=10)
            log, created = ledger_service.create_operational_log(session, farm_id, _log())
            results.append((log.id, created))
        except BaseException as exc:  # noqa: BLE001 — the point is to catch everything
            errors.append(exc)
        finally:
            session.close()

    threads = [threading.Thread(target=post) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert errors == [], f"the race raised: {errors!r}"
    assert len(results) == 2

    # Both callers were handed the same row...
    assert results[0][0] == results[1][0]
    # ...and exactly one of them was told it created it.
    assert sorted(created for _, created in results) == [False, True]

    # One log, one transaction. Nothing double-booked.
    with Session() as verifier:
        assert _count(verifier, farm_id) == (1, 1)
