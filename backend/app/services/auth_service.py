"""Registration and authentication (Objective 3: identity + data boundary).

Registering creates a Farm (tenant) and its first User in one step; the user's
farm_id is the scope key every domain query later filters on.
"""
from sqlalchemy.orm import Session

from ..core.exceptions import ConflictError
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
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.email == email.strip().lower()).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
