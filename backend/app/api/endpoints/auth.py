from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.security import create_access_token
from ...models.database import get_db
from ...schemas import schemas
from ...services import auth_service
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Create a farm (tenant) + its first user and return a JWT.

    A duplicate email is a 409 (ConflictError). The password is bcrypt-hashed
    by auth_service — never stored in plaintext.
    """
    user = auth_service.register(db, payload)
    return schemas.Token(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    """Return the authenticated user (used by the frontend to confirm a
    persisted token is still valid on reload)."""
    return current_user
