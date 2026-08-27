"""The migration chain: that it is coherent, that it runs, and that it lands on
the schema the application expects.

WHY THIS FILE EXISTS. Every other test in this suite builds its schema with
`Base.metadata.create_all` (see conftest.py), which is fast and isolated and
completely blind to Alembic. Before this file, no test executed a single
migration: the six-revision chain — including one that drops a global unique
index and adds a composite constraint on live data — had no automated
verification at all, and a broken migration would have left CI green while
making the next deployment fail on startup.

TWO TIERS, AND THE SPLIT IS DELIBERATE.

  * The chain-integrity tests need no database and run everywhere, every time.
    They catch the failure that is both most likely and cheapest to make: two
    branches each adding a revision, producing two heads, so `upgrade head`
    fails on a machine that has never seen either.

  * The execution tests need PostgreSQL and are skipped without it. They are not
    optional in CI — the workflow runs them against a Postgres service — but
    they cannot run on SQLite, and that is a property of the migrations rather
    than a gap in them: `e6a2b4c7d130` uses ALTER-constraint operations that
    SQLite does not support. Rewriting production migrations into batch mode so
    a test could run on a different database than production uses would be
    changing the thing under test to suit the test.

Set MIGRATION_TEST_DATABASE_URL to a THROWAWAY database to run the second tier
locally. It is dropped and recreated; never point it at anything you value.
"""
import os

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATION_DB_URL = os.getenv("MIGRATION_TEST_DATABASE_URL")

requires_postgres = pytest.mark.skipif(
    not MIGRATION_DB_URL,
    reason=(
        "MIGRATION_TEST_DATABASE_URL is not set. The chain uses ALTER-constraint "
        "operations that SQLite cannot run, so execution is verified against "
        "PostgreSQL (the CI workflow provides one)."
    ),
)


def _alembic_config(url: str | None = None) -> Config:
    cfg = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "alembic"))
    if url:
        cfg.set_main_option("sqlalchemy.url", url)
    return cfg


@pytest.fixture(scope="module")
def script() -> ScriptDirectory:
    return ScriptDirectory.from_config(_alembic_config())


# --- Tier 1: chain integrity (no database) --------------------------------

def test_the_chain_has_exactly_one_head(script):
    """Two heads mean `alembic upgrade head` fails outright. It is the classic
    result of two branches each adding a revision, and it is invisible until
    somebody deploys."""
    heads = script.get_heads()
    assert len(heads) == 1, f"expected one head, found {heads}"


def test_every_revision_is_reachable_from_the_head(script):
    """No orphans: a revision nothing points at will never run, so the column it
    adds will never exist while the model that needs it ships."""
    head = script.get_current_head()
    walked = {rev.revision for rev in script.walk_revisions("base", head)}
    declared = {rev.revision for rev in script.get_revisions("heads")}
    all_revisions = {rev.revision for rev in script.walk_revisions()}
    assert declared <= walked
    assert all_revisions == walked, f"unreachable revisions: {all_revisions - walked}"


def test_every_down_revision_resolves(script):
    known = {rev.revision for rev in script.walk_revisions()}
    for rev in script.walk_revisions():
        if rev.down_revision is None:
            continue
        parents = rev.down_revision if isinstance(rev.down_revision, tuple) else (rev.down_revision,)
        for parent in parents:
            assert parent in known, f"{rev.revision} points at unknown parent {parent}"


def test_there_is_exactly_one_base(script):
    bases = [rev.revision for rev in script.walk_revisions() if rev.down_revision is None]
    assert len(bases) == 1, f"expected one base revision, found {bases}"


def test_revision_identifiers_are_unique(script):
    revisions = [rev.revision for rev in script.walk_revisions()]
    assert len(revisions) == len(set(revisions))


def test_every_migration_defines_both_directions(script):
    """A migration with no downgrade cannot be rolled back, and rollback is the
    recovery plan when a deployment goes wrong at 2am."""
    for rev in script.walk_revisions():
        module = rev.module
        assert hasattr(module, "upgrade"), f"{rev.revision} has no upgrade()"
        assert hasattr(module, "downgrade"), f"{rev.revision} has no downgrade()"


def test_the_head_matches_the_newest_migration_on_disk(script):
    """Guards against a revision file added without being chained in — it would
    sit in the directory looking applied and never run."""
    head = script.get_current_head()
    assert head is not None
    files = [
        f for f in os.listdir(os.path.join(BACKEND_DIR, "alembic", "versions"))
        if f.endswith(".py")
    ]
    assert any(head in f for f in files), f"head {head} has no file in versions/"


# --- Tier 2: the chain actually runs (PostgreSQL) -------------------------

@pytest.fixture
def clean_database():
    """A schema-less database, and the same one dropped again afterwards."""
    from sqlalchemy import create_engine, text

    engine = create_engine(MIGRATION_DB_URL, poolclass=None)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    yield engine
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    engine.dispose()


@requires_postgres
def test_migrations_run_from_an_empty_database_to_head(clean_database):
    """The deployment path itself: a fresh database reaches the current schema."""
    from alembic import command
    from sqlalchemy import inspect

    command.upgrade(_alembic_config(MIGRATION_DB_URL), "head")

    tables = set(inspect(clean_database).get_table_names())
    expected = {
        "farms", "users", "share_tokens", "operational_logs",
        "financial_transactions", "equipment", "maintenance_logs",
        "alembic_version",
    }
    assert expected <= tables, f"missing after upgrade: {expected - tables}"


@requires_postgres
def test_the_migrated_schema_matches_the_models(clean_database):
    """THE DRIFT CHECK, and the reason this file is worth its length.

    A model column added without a migration works perfectly in every other test
    — `create_all` builds it from the same models — and fails only in
    production, on the first query against a column the database does not have.
    Comparing the migrated schema against Base.metadata is what closes that gap.

    Autogenerate is asked what it would still change after `upgrade head`. The
    answer must be nothing.
    """
    from alembic import command
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    from backend.app.models.models import Base

    command.upgrade(_alembic_config(MIGRATION_DB_URL), "head")

    with clean_database.connect() as conn:
        context = MigrationContext.configure(conn)
        diff = compare_metadata(context, Base.metadata)

    # Index and constraint reflection is noisy across backends; the differences
    # that matter — and the ones that actually break production — are missing or
    # extra tables and columns, and column type changes.
    significant = [
        d for d in diff
        if isinstance(d, tuple) and d[0] in {
            "add_table", "remove_table", "add_column", "remove_column", "modify_type",
        }
    ]
    assert not significant, f"schema drift between migrations and models: {significant}"


@requires_postgres
def test_the_newest_migration_can_be_rolled_back_and_reapplied(clean_database):
    """A rehearsal of the rollback step in the deployment runbook.

    Only one revision back: `e6a2b4c7d130` documents that a full downgrade can
    legitimately fail once two farms share a client_id, because restoring a
    global unique index would mean discarding one farm's ledger row and a
    migration must not choose which. Asserting a full downgrade to base would be
    asserting something the chain deliberately does not promise.
    """
    from alembic import command
    from alembic.script import ScriptDirectory

    cfg = _alembic_config(MIGRATION_DB_URL)
    command.upgrade(cfg, "head")

    head = ScriptDirectory.from_config(cfg).get_current_head()
    command.downgrade(cfg, "-1")
    command.upgrade(cfg, "head")

    from sqlalchemy import text
    with clean_database.connect() as conn:
        current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert current == head


@requires_postgres
def test_the_application_can_read_and_write_the_migrated_schema(clean_database):
    """End of the chain: the schema Alembic produced is one the app can use.

    A migration can succeed and still be wrong — a column with the right name
    and the wrong nullability, or a default the model does not expect. This
    exercises the real paired write against the real migrated tables.
    """
    from alembic import command
    from sqlalchemy.orm import sessionmaker

    from backend.app.core.roles import Role
    from backend.app.models import models

    command.upgrade(_alembic_config(MIGRATION_DB_URL), "head")

    session = sessionmaker(bind=clean_database)()
    try:
        farm = models.Farm(name="Migrated Farm")
        session.add(farm)
        session.flush()

        user = models.User(
            email="migrated@test.example", hashed_password="x", farm_id=farm.id,
        )
        session.add(user)
        session.flush()
        # Columns added by a8d4e1c60b27 must carry their server defaults.
        session.refresh(user)
        assert user.role == Role.OWNER.value
        assert user.is_active is True

        tx = models.FinancialTransaction(
            farm_id=farm.id, amount=1000.0,
            transaction_type="DEBIT", category="SEED",
        )
        session.add(tx)
        session.flush()
        log = models.OperationalLog(
            farm_id=farm.id, activity_type="SEED", crop="maize",
            financial_transaction_id=tx.id,
        )
        session.add(log)
        session.commit()

        assert session.query(models.OperationalLog).count() == 1
        # f7b3c2d94e15 and b9e5f30c74a1: both nullable, both meaningful as NULL.
        token = models.ShareToken(farm_id=farm.id, token_hash="deadbeef", revoked=False)
        session.add(token)
        session.commit()
        assert token.expires_at is None
    finally:
        session.close()
