import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.core.rate_limit import limiter
from backend.app.main import app
from backend.app.models.database import Base, get_db


@pytest.fixture(autouse=True)
def _isolate_rate_limits():
    """Every test starts with empty rate-limit counters.

    The limiter is process-global by design, so without this a test that
    registers three farms would leave three hits on the shared client IP and the
    next test would inherit them — tests would pass or fail depending on
    execution order, which is the same reason each test already gets its own
    database.

    This weakens no assertion. The limits themselves are unchanged and are
    exercised deliberately in `test_rate_limit.py`; this only stops one test's
    traffic counting against another's.
    """
    limiter.reset()
    yield
    limiter.reset()

# Each test gets its own in-memory SQLite database. StaticPool keeps the single
# in-memory connection alive for the duration of the test so the schema and data
# persist across requests, and a fresh engine per test keeps tests isolated and
# order-independent (no data bleeds between tests).


@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# --- Auth-aware clients ---------------------------------------------------
# All domain endpoints now require a bearer token scoped to a farm. `make_client`
# is a factory that registers a fresh farm/user against the SHARED test db and
# returns a TestClient with its Authorization header preset. Because every client
# built here is bound to the same `db` fixture instance, two clients model two
# tenants sharing one database — exactly what the isolation tests need.

_email_seq = itertools.count(1)


@pytest.fixture(scope="function")
def make_client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    created: list[TestClient] = []

    def _make(email: str | None = None, password: str = "secret-password", farm_name: str | None = None):
        email = email or f"farmer-{next(_email_seq)}@test.example"
        c = TestClient(app)
        c.__enter__()  # trigger startup events (trains the DSS model) like `with`
        created.append(c)
        resp = c.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "farm_name": farm_name},
        )
        assert resp.status_code == 201, resp.text
        token = resp.json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        return c

    yield _make

    for c in created:
        c.__exit__(None, None, None)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(make_client):
    """The default authenticated client (one farm). Existing domain tests use
    this unchanged — they simply now run as an authenticated farm."""
    return make_client(farm_name="Farm A")


@pytest.fixture(scope="function")
def anon_client(db):
    """An unauthenticated client, for register/login and 401-rejection tests."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
