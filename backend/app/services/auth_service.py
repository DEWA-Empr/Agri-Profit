"""Registration, authentication, and who else may sign in to a farm.

Registering creates a Farm (tenant) and its first User in one step; the user's
farm_id is the scope key every domain query later filters on, and that user owns
the farm they just created.

MEMBERSHIP IS ALWAYS SCOPED TO THE CALLER'S OWN FARM. Every function below takes
`farm_id` from the authenticated caller and never from the request body, so
there is no representable way to add a user to, or read the members of, a farm
other than your own — the same construction the share-token endpoint uses. A
member id that belongs to another farm is simply not found.
"""
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.roles import DEFAULT_ROLE, Role
from ..core.security import hash_password, verify_password
from ..models import models
from ..schemas import schemas


def register(db: Session, payload: schemas.RegisterRequest) -> models.User:
    email = payload.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise ConflictError("Email already registered")

    farm = models.Farm(name=payload.farm_name or f"{email}'s Farm")
    db.add(farm)
    db.flush()  # assign farm.id before linking the user

    user = models.User(
        email=email,
        hashed_password=hash_password(payload.password),
        farm_id=farm.id,
        # Registration creates the farm, so the registrant owns it. This is also
        # the role every pre-authorization account was backfilled to
        # (migration a8d4e1c60b27), which is what makes the change invisible to
        # existing users.
        role=DEFAULT_ROLE.value,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- Farm membership -----------------------------------------------------

def list_members(db: Session, farm_id: int) -> list[models.User]:
    return (
        db.query(models.User)
        .filter(models.User.farm_id == farm_id)
        .order_by(models.User.id)
        .all()
    )


def _member_or_404(db: Session, farm_id: int, member_id: int) -> models.User:
    """A member of THIS farm, or 404.

    Farm-scoped in the query, so another farm's user id is "not found" rather
    than "forbidden" — the same verdict a foreign equipment id gets, and for the
    same reason: distinguishing them would confirm that the id exists somewhere.
    """
    member = (
        db.query(models.User)
        .filter(models.User.id == member_id, models.User.farm_id == farm_id)
        .first()
    )
    if member is None:
        raise NotFoundError(f"Member {member_id} not found")
    return member


def create_member(db: Session, farm_id: int, payload: schemas.MemberCreate) -> models.User:
    """Add a user to `farm_id`. The caller's own farm, always.

    Email uniqueness is global, not per farm, because it is the login
    identifier: two accounts sharing an address could not be told apart at
    authentication time.
    """
    email = payload.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise ConflictError("Email already registered")

    member = models.User(
        email=email,
        hashed_password=hash_password(payload.password),
        farm_id=farm_id,
        role=Role(payload.role).value,
        is_active=True,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def _assert_not_last_active_owner(db: Session, farm_id: int, member: models.User) -> None:
    """Refuse a change that would leave a farm with no active owner.

    A farm whose last owner is demoted or deactivated is unrecoverable through
    the API: only an owner may manage members, so there would be nobody left who
    could restore one, and the farm's investor links could never be revoked
    again. The check costs one count and turns a permanent lockout into a 422
    that explains itself.
    """
    if member.role != Role.OWNER.value or not member.is_active:
        return
    remaining = (
        db.query(models.User)
        .filter(
            models.User.farm_id == farm_id,
            models.User.role == Role.OWNER.value,
            models.User.is_active.is_(True),
            models.User.id != member.id,
        )
        .count()
    )
    if remaining == 0:
        raise ValidationError(
            "This is the farm's only active owner. Promote another member to "
            "owner first, or the farm would be left with nobody who can manage "
            "members or revoke its share links."
        )


def set_member_role(db: Session, farm_id: int, member_id: int, role: Role) -> models.User:
    member = _member_or_404(db, farm_id, member_id)
    if Role(role) != Role.OWNER:
        _assert_not_last_active_owner(db, farm_id, member)
    member.role = Role(role).value
    db.commit()
    db.refresh(member)
    return member


def set_member_active(db: Session, farm_id: int, member_id: int, is_active: bool) -> models.User:
    """Withdraw or restore a member's access.

    Deactivation, never deletion: the records the member entered keep their
    author and the ledger's audit trail stays intact, in the same spirit as
    revoking a share link rather than removing the row.
    """
    member = _member_or_404(db, farm_id, member_id)
    if not is_active:
        _assert_not_last_active_owner(db, farm_id, member)
    member.is_active = is_active
    db.commit()
    db.refresh(member)
    return member


def authenticate(db: Session, email: str, password: str) -> models.User | None:
    """Verify credentials. None on any failure, with no distinction between
    causes — an unknown address and a wrong password must be indistinguishable
    to the caller, or the login form becomes an account-enumeration oracle.

    A deactivated account fails here too, so a withdrawn member cannot obtain a
    fresh token. `api/deps.get_current_user` independently rejects an already
    issued one, which is what makes deactivation take effect immediately rather
    than whenever the existing token happens to expire.
    """
    user = db.query(models.User).filter(models.User.email == email.strip().lower()).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
