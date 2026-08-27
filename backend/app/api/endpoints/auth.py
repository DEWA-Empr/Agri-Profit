from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ...core.security import create_access_token
from ...models.database import get_db
from ...schemas import schemas
from ...services import auth_service
from .. import throttle
from ..deps import get_current_user

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
    persisted token is still valid on reload)."""
    return current_user
