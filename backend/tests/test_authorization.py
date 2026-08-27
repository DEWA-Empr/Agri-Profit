"""Role boundaries, proven by crossing them.

EVERY TEST HERE CALLS THE API DIRECTLY. None of them goes near the interface,
because hiding a button is not a security control and a test that only proved a
button was hidden would prove nothing about the boundary. What is asserted is
the status code the server returns to a caller holding a real token for a real
account with a real role.

Four verdicts are kept distinct throughout, and the difference between them is
the substance of the model:

    401  no valid identity            (missing, malformed or withdrawn token)
    403  identity, but the role does not permit the operation
    404  permitted, but the resource is not in the caller's farm
    2xx  permitted and in scope

403-before-404 is deliberate and is asserted directly in
`test_permission_is_checked_before_scope`: a caller who may not reverse entries
at all is told so whether or not the id they named exists, because answering 404
first would tell them which ids belong to their farm.
"""
import pytest

from backend.app.core.roles import (
    DEFAULT_ROLE,
    Permission,
    ROLE_PERMISSIONS,
    Role,
    has_permission,
    permissions_for,
)


# --- helpers --------------------------------------------------------------

def _add_member(owner_client, email, role, password="member-password"):
    resp = owner_client.post(
        "/api/v1/auth/members",
        json={"email": email, "password": password, "role": role},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture
def farm(client, make_client, anon_client):
    """One farm: its owner's client, plus a factory for members with a given role.

    The member factory logs in as the new member and returns a client carrying
    THAT member's token — so every role test below is a real end-to-end request
    from a real account, not a hand-built token or a patched dependency.
    """
    def member(role, email=None):
        email = email or f"{role}-{id(object())}@test.example"
        _add_member(client, email, role)
        token = anon_client.post(
            "/api/v1/auth/login", json={"email": email, "password": "member-password"}
        ).json()["access_token"]
        # A fresh client sharing the same app + db, carrying the member's token.
        c = make_client(email=f"unused-{email}", farm_name="throwaway")
        c.headers.update({"Authorization": f"Bearer {token}"})
        return c

    return {"owner": client, "member": member}


# --- the permission table itself -----------------------------------------

def test_owner_holds_every_permission_a_manager_does():
    assert ROLE_PERMISSIONS[Role.MANAGER] <= ROLE_PERMISSIONS[Role.OWNER]


def test_manager_holds_every_permission_a_worker_does():
    assert ROLE_PERMISSIONS[Role.WORKER] <= ROLE_PERMISSIONS[Role.MANAGER]


def test_only_the_owner_may_share_or_manage_members():
    for permission in (Permission.SHARE_MANAGE, Permission.MEMBER_MANAGE):
        assert has_permission(Role.OWNER, permission)
        assert not has_permission(Role.MANAGER, permission)
        assert not has_permission(Role.WORKER, permission)


def test_a_worker_cannot_read_the_farms_finances():
    assert not has_permission(Role.WORKER, Permission.FINANCE_READ)
    assert not has_permission(Role.WORKER, Permission.LOG_REVERSE)
    assert not has_permission(Role.WORKER, Permission.EQUIPMENT_MANAGE)


def test_model_training_is_granted_to_nobody():
    """Retraining rewrites the one artefact every farm's forecast is served
    from. No tenant role may do that, whatever else it holds."""
    for role in Role:
        assert not has_permission(role, Permission.MODEL_TRAIN)


def test_an_unknown_role_gets_nothing():
    """Fail closed: a row carrying a role this build does not know — a downgrade,
    or a hand-edited database — must lose access, not gain it."""
    assert permissions_for("superuser") == frozenset()
    assert permissions_for("") == frozenset()
    assert not has_permission("superuser", Permission.FINANCE_READ)


def test_registration_still_creates_an_owner(client):
    assert client.get("/api/v1/auth/me").json()["role"] == DEFAULT_ROLE.value


# --- unauthenticated ------------------------------------------------------

@pytest.mark.parametrize("method,path", [
    ("get", "/api/v1/ledger/logs"),
    ("get", "/api/v1/ledger/transactions"),
    ("get", "/api/v1/ledger/summary"),
    ("get", "/api/v1/reports/pnl"),
    ("get", "/api/v1/reports/pnl.csv"),
    ("get", "/api/v1/dss/decision-support"),
    ("get", "/api/v1/dss/cost-structure"),
    ("get", "/api/v1/dss/break-even-price"),
    ("get", "/api/v1/dss/sensitivity"),
    ("get", "/api/v1/dss/yield-baseline"),
    ("get", "/api/v1/dss/model"),
    ("get", "/api/v1/equipment/"),
    ("get", "/api/v1/share/links"),
    ("get", "/api/v1/auth/members"),
    ("get", "/api/v1/auth/me"),
    ("get", "/api/v1/bioprocess/summary"),
])
def test_every_protected_read_rejects_an_anonymous_caller(anon_client, method, path):
    assert getattr(anon_client, method)(path).status_code == 401


@pytest.mark.parametrize("path,body", [
    ("/api/v1/ledger/logs", {"activity_type": "seed", "financial_data": {"amount": 1, "transaction_type": "debit", "category": "seed"}}),
    ("/api/v1/share/links", {"label": "x"}),
    ("/api/v1/auth/members", {"email": "x@test.example", "password": "password1", "role": "worker"}),
    ("/api/v1/dss/predict", {"rainfall": 900, "fertilizer_used": 50, "soil_ph": 6.2, "crop": "maize"}),
    ("/api/v1/dss/train", {}),
])
def test_every_protected_write_rejects_an_anonymous_caller(anon_client, path, body):
    assert anon_client.post(path, json=body).status_code == 401


def test_a_garbage_token_is_rejected(anon_client):
    anon_client.headers.update({"Authorization": "Bearer not-a-real-jwt"})
    assert anon_client.get("/api/v1/ledger/logs").status_code == 401


# --- worker: what it may and may not do ----------------------------------

def test_a_worker_may_log_field_activity(farm):
    worker = farm["member"](Role.WORKER.value)
    resp = worker.post("/api/v1/ledger/logs", json={
        "activity_type": "fertilizer", "description": "urea", "crop": "maize",
        "quantity": 5, "unit": "bags",
        "financial_data": {"amount": 25000, "transaction_type": "debit", "category": "fertilizer"},
    })
    assert resp.status_code == 201


def test_a_worker_may_read_the_farms_operational_log(farm):
    worker = farm["member"](Role.WORKER.value)
    assert worker.get("/api/v1/ledger/logs").status_code == 200


def test_a_worker_may_read_the_model_metadata_the_entry_form_needs(farm):
    """The crop selector is built from this. A worker who cannot read it cannot
    file a record at all, which would make the role useless."""
    worker = farm["member"](Role.WORKER.value)
    assert worker.get("/api/v1/dss/model").status_code == 200


@pytest.mark.parametrize("path", [
    "/api/v1/ledger/transactions",
    "/api/v1/ledger/summary",
    "/api/v1/reports/pnl",
    "/api/v1/reports/pnl/monthly",
    "/api/v1/reports/pnl.csv",
    "/api/v1/dss/decision-support",
    "/api/v1/dss/cost-structure",
    "/api/v1/dss/break-even-price",
    "/api/v1/dss/sensitivity",
    "/api/v1/dss/yield-baseline",
    "/api/v1/equipment/",
])
def test_a_worker_is_refused_the_farms_financial_picture(farm, path):
    worker = farm["member"](Role.WORKER.value)
    resp = worker.get(path)
    assert resp.status_code == 403, f"{path} -> {resp.status_code}"


def test_a_worker_cannot_reverse_an_entry(farm):
    owner = farm["owner"]
    log = owner.post("/api/v1/ledger/logs", json={
        "activity_type": "seed", "crop": "maize",
        "financial_data": {"amount": 1000, "transaction_type": "debit", "category": "seed"},
    }).json()

    worker = farm["member"](Role.WORKER.value)
    assert worker.post(f"/api/v1/ledger/logs/{log['id']}/reverse").status_code == 403


def test_a_worker_cannot_mint_a_share_link(farm):
    worker = farm["member"](Role.WORKER.value)
    assert worker.post("/api/v1/share/links", json={"label": "sneaky"}).status_code == 403


def test_a_worker_cannot_add_members_or_promote_itself(farm):
    worker = farm["member"](Role.WORKER.value)
    assert worker.get("/api/v1/auth/members").status_code == 403
    assert worker.post("/api/v1/auth/members", json={
        "email": "accomplice@test.example", "password": "password1", "role": "owner",
    }).status_code == 403


def test_a_worker_cannot_create_equipment(farm):
    worker = farm["member"](Role.WORKER.value)
    assert worker.post("/api/v1/equipment/", json={
        "name": "Tractor", "purchase_price": 1_000_000, "depreciation_rate": 10,
    }).status_code == 403


# --- manager: the middle boundary ----------------------------------------

@pytest.mark.parametrize("path", [
    "/api/v1/reports/pnl",
    "/api/v1/dss/decision-support",
    "/api/v1/dss/cost-structure",
    "/api/v1/equipment/",
])
def test_a_manager_may_read_the_financial_picture(farm, path):
    manager = farm["member"](Role.MANAGER.value)
    assert manager.get(path).status_code == 200


def test_a_manager_may_reverse_an_entry(farm):
    owner = farm["owner"]
    log = owner.post("/api/v1/ledger/logs", json={
        "activity_type": "seed", "crop": "maize",
        "financial_data": {"amount": 1000, "transaction_type": "debit", "category": "seed"},
    }).json()

    manager = farm["member"](Role.MANAGER.value)
    assert manager.post(f"/api/v1/ledger/logs/{log['id']}/reverse").status_code == 201


def test_a_manager_may_manage_equipment(farm):
    manager = farm["member"](Role.MANAGER.value)
    assert manager.post("/api/v1/equipment/", json={
        "name": "Thresher", "purchase_price": 500_000, "depreciation_rate": 12,
    }).status_code == 201


def test_a_manager_cannot_disclose_the_farm_to_an_outsider(farm):
    """The boundary that defines the manager role: full internal control, no
    authority to hand the farm's finances to somebody outside it."""
    manager = farm["member"](Role.MANAGER.value)
    assert manager.post("/api/v1/share/links", json={"label": "bank"}).status_code == 403
    assert manager.get("/api/v1/share/links").status_code == 403


def test_a_manager_cannot_manage_members(farm):
    manager = farm["member"](Role.MANAGER.value)
    assert manager.get("/api/v1/auth/members").status_code == 403


# --- owner: privileged access --------------------------------------------

def test_an_owner_may_do_everything_the_others_may(farm):
    owner = farm["owner"]
    assert owner.get("/api/v1/reports/pnl").status_code == 200
    assert owner.get("/api/v1/share/links").status_code == 200
    assert owner.get("/api/v1/auth/members").status_code == 200
    assert owner.post("/api/v1/equipment/", json={
        "name": "Sprayer", "purchase_price": 200_000, "depreciation_rate": 15,
    }).status_code == 201


def test_the_owner_sees_every_member_of_the_farm(farm):
    farm["member"](Role.WORKER.value, email="w1@test.example")
    farm["member"](Role.MANAGER.value, email="m1@test.example")

    members = farm["owner"].get("/api/v1/auth/members").json()
    by_email = {m["email"]: m["role"] for m in members}
    assert by_email["w1@test.example"] == "worker"
    assert by_email["m1@test.example"] == "manager"


def test_an_owner_can_promote_and_demote(farm):
    member = _add_member(farm["owner"], "promote@test.example", "worker")
    promoted = farm["owner"].patch(
        f"/api/v1/auth/members/{member['id']}/role", json={"role": "manager"}
    )
    assert promoted.status_code == 200
    assert promoted.json()["role"] == "manager"


def test_an_unknown_role_is_refused_at_the_schema_edge(farm):
    resp = farm["owner"].post("/api/v1/auth/members", json={
        "email": "hacker@test.example", "password": "password1", "role": "superuser",
    })
    assert resp.status_code == 422


def test_the_last_active_owner_cannot_be_demoted(client):
    """Otherwise the farm is permanently unmanageable: only an owner can restore
    an owner, and only an owner can revoke the farm's investor links."""
    me = client.get("/api/v1/auth/me").json()
    resp = client.patch(f"/api/v1/auth/members/{me['id']}/role", json={"role": "worker"})
    assert resp.status_code == 422
    assert "only active owner" in resp.json()["detail"]


def test_the_last_active_owner_cannot_be_deactivated(client):
    me = client.get("/api/v1/auth/me").json()
    resp = client.patch(f"/api/v1/auth/members/{me['id']}/active", json={"is_active": False})
    assert resp.status_code == 422


def test_an_owner_can_step_down_once_another_owner_exists(client):
    _add_member(client, "second-owner@test.example", "owner")
    me = client.get("/api/v1/auth/me").json()
    resp = client.patch(f"/api/v1/auth/members/{me['id']}/role", json={"role": "manager"})
    assert resp.status_code == 200


# --- deactivation takes effect immediately -------------------------------

def test_a_deactivated_member_loses_access_on_their_next_request(farm, anon_client):
    """Not when their token expires. Tokens live 24 hours; "remove this person"
    cannot mean "tomorrow"."""
    _add_member(farm["owner"], "gone@test.example", "manager")
    token = anon_client.post("/api/v1/auth/login", json={
        "email": "gone@test.example", "password": "member-password",
    }).json()["access_token"]

    anon_client.headers.update({"Authorization": f"Bearer {token}"})
    assert anon_client.get("/api/v1/reports/pnl").status_code == 200

    member_id = next(
        m["id"] for m in farm["owner"].get("/api/v1/auth/members").json()
        if m["email"] == "gone@test.example"
    )
    farm["owner"].patch(f"/api/v1/auth/members/{member_id}/active", json={"is_active": False})

    # Same token, same client — now refused.
    assert anon_client.get("/api/v1/reports/pnl").status_code == 401


def test_a_deactivated_member_cannot_log_in_again(farm, anon_client):
    _add_member(farm["owner"], "locked@test.example", "worker")
    member_id = next(
        m["id"] for m in farm["owner"].get("/api/v1/auth/members").json()
        if m["email"] == "locked@test.example"
    )
    farm["owner"].patch(f"/api/v1/auth/members/{member_id}/active", json={"is_active": False})

    resp = anon_client.post("/api/v1/auth/login", json={
        "email": "locked@test.example", "password": "member-password",
    })
    assert resp.status_code == 401


# --- cross-farm isolation still holds ------------------------------------

def test_one_farms_owner_cannot_see_another_farms_members(make_client):
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    _add_member(a, "a-worker@test.example", "worker")

    b_emails = {m["email"] for m in b.get("/api/v1/auth/members").json()}
    assert "a-worker@test.example" not in b_emails


def test_one_farms_owner_cannot_change_another_farms_member(make_client):
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    victim = _add_member(a, "a-victim@test.example", "worker")

    resp = b.patch(f"/api/v1/auth/members/{victim['id']}/role", json={"role": "owner"})
    assert resp.status_code == 404      # not 403: existence is not confirmed


def test_one_farms_owner_cannot_deactivate_another_farms_member(make_client):
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    victim = _add_member(a, "a-target@test.example", "manager")

    assert b.patch(
        f"/api/v1/auth/members/{victim['id']}/active", json={"is_active": False}
    ).status_code == 404


def test_a_member_added_to_one_farm_cannot_read_another(make_client, anon_client):
    a = make_client(farm_name="Farm A")
    b = make_client(farm_name="Farm B")
    b.post("/api/v1/ledger/logs", json={
        "activity_type": "seed", "crop": "secret-crop",
        "financial_data": {"amount": 999, "transaction_type": "debit", "category": "seed"},
    })

    _add_member(a, "a-manager@test.example", "manager")
    token = anon_client.post("/api/v1/auth/login", json={
        "email": "a-manager@test.example", "password": "member-password",
    }).json()["access_token"]
    anon_client.headers.update({"Authorization": f"Bearer {token}"})

    crops = {c["crop"] for c in anon_client.get("/api/v1/dss/decision-support").json()["crops"]}
    assert "secret-crop" not in crops


# --- ordering of the two rejections --------------------------------------

def test_permission_is_checked_before_scope(farm, make_client):
    """A worker naming a log id from ANOTHER farm gets 403, not 404.

    Answering 404 first would confirm that the id is not theirs — a scope oracle
    offered to a caller with no authority to ask the question in the first place.
    """
    other = make_client(farm_name="Other Farm")
    foreign = other.post("/api/v1/ledger/logs", json={
        "activity_type": "seed",
        "financial_data": {"amount": 10, "transaction_type": "debit", "category": "seed"},
    }).json()

    worker = farm["member"](Role.WORKER.value)
    assert worker.post(f"/api/v1/ledger/logs/{foreign['id']}/reverse").status_code == 403


def test_a_permitted_role_naming_a_foreign_resource_gets_404(farm, make_client):
    """The other side of the same rule: authority, but no scope."""
    other = make_client(farm_name="Other Farm")
    foreign = other.post("/api/v1/ledger/logs", json={
        "activity_type": "seed",
        "financial_data": {"amount": 10, "transaction_type": "debit", "category": "seed"},
    }).json()

    manager = farm["member"](Role.MANAGER.value)
    assert manager.post(f"/api/v1/ledger/logs/{foreign['id']}/reverse").status_code == 404


# --- investor / shared access remains a capability, not a role -----------

def test_the_public_report_needs_no_account_and_grants_nothing_else(client, anon_client):
    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()["token"]

    assert anon_client.get(f"/api/v1/share/report/{token}").status_code == 200
    # The token is read-only and reaches nothing but its own report.
    assert anon_client.get("/api/v1/ledger/logs").status_code == 401
    assert anon_client.get("/api/v1/reports/pnl").status_code == 401


def test_a_share_token_cannot_be_used_as_a_bearer_credential(client, anon_client):
    """A capability for one report must not be interchangeable with an identity."""
    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()["token"]
    anon_client.headers.update({"Authorization": f"Bearer {token}"})
    assert anon_client.get("/api/v1/ledger/logs").status_code == 401


def test_there_is_no_token_authenticated_write_path(client, anon_client):
    token = client.post("/api/v1/share/links", json={"label": "Bank"}).json()["token"]
    assert anon_client.post(f"/api/v1/share/report/{token}").status_code in (404, 405)


# --- model training is closed -------------------------------------------

def test_model_training_over_the_api_is_refused_even_for_an_owner(client):
    assert client.post("/api/v1/dss/train").status_code == 403
