from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from typing import List

from ...core.roles import Permission, permissions_for
from ...core.security import create_access_token
from ...models.database import get_db
from ...schemas import schemas
from ...services import auth_service
from .. import throttle
from ..deps import get_current_user, require

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Create a farm (tenant) + its first user and return a JWT.

    A duplicate email is a 409 (ConflictError). The password is bcrypt-hashed
    by auth_service — never stored in plaintext.

    Rate-limited per client IP: registration is the cheapest way to fill the
    database, and it needs no credential to attempt.
    """
    throttle.guard_register(request)
    user = auth_service.register(db, payload)
    return schemas.Token(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Exchange credentials for a JWT.

    Rate-limited per account AND per client IP before the password is checked,
    so a guessing loop is bounded whether it targets one address from many hosts
    or many addresses from one. Only FAILURES count against the account budget,
    and a success clears it — otherwise an attacker could lock a farmer out of
    their own account from somewhere else entirely, turning a brute-force
    defence into a denial-of-service tool.
    """
    throttle.guard_login(request, payload.email)
    user = auth_service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    throttle.clear_login(payload.email)
    return schemas.Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    """Return the authenticated user (used by the frontend to confirm a
    persisted token is still valid on reload).

    Carries the caller's permission list so the interface can hide controls the
    server would refuse. The list is derived from the server's own role table,
    so the client never holds a second copy of the policy.

    No permission is required beyond a valid token: this describes the caller to
    themselves and discloses nothing about the farm or anyone else in it.
    """
    return schemas.UserOut(
        id=current_user.id,
        email=current_user.email,
        farm_id=current_user.farm_id,
        role=current_user.role,
        is_active=current_user.is_active,
        permissions=sorted(p.value for p in permissions_for(current_user.role)),
    )


# --- Farm membership (owner-only) ----------------------------------------
# Every route below is farm-scoped through `current_user.farm_id` and gated by
# MEMBER_MANAGE, which only the OWNER role holds. There is no farm_id in any
# request body or path: a caller can only ever manage their own farm's members,
# so the scope is not a parameter and cannot be tampered with.
#
# These exist because a permission model with no way to assign a role is
# decoration. Without them WORKER and MANAGER would be unreachable states and
# the whole table in core/roles.py would be untestable against real traffic.


@router.get("/members", response_model=List[schemas.MemberOut])
def list_members(
    db: Session = Depends(get_db),
    current_user=Depends(require(Permission.MEMBER_MANAGE)),
):
    """Everyone who can sign in to the caller's farm, with role and status."""
    return auth_service.list_members(db, current_user.farm_id)


@router.post("/members", response_model=schemas.MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: schemas.MemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require(Permission.MEMBER_MANAGE)),
):
    """Add a user to the caller's farm with a named role.

    A duplicate email is a 409: the address is the login identifier, so
    uniqueness is global rather than per farm — two accounts sharing one could
    not be told apart at authentication time.
    """
    return auth_service.create_member(db, current_user.farm_id, payload)


@router.patch("/members/{member_id}/role", response_model=schemas.MemberOut)
def set_member_role(
    member_id: int,
    payload: schemas.MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require(Permission.MEMBER_MANAGE)),
):
    """Change a member's role. 404 for a member of another farm.

    Demoting the farm's last active owner is refused (422): only an owner can
    manage members, so the farm would be left with nobody able to restore one or
    to revoke its investor links.
    """
    return auth_service.set_member_role(db, current_user.farm_id, member_id, payload.role)


@router.patch("/members/{member_id}/active", response_model=schemas.MemberOut)
def set_member_active(
    member_id: int,
    payload: schemas.MemberActiveUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require(Permission.MEMBER_MANAGE)),
):
    """Withdraw or restore a member's access.

    Deactivation rather than deletion — the records they entered keep their
    author. It takes effect on the deactivated member's very next request, not
    when their token expires, because `get_current_user` rechecks the flag.
    """
    return auth_service.set_member_active(db, current_user.farm_id, member_id, payload.is_active)
