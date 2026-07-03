"""Shared FastAPI dependencies — chiefly resolving a bearer token to the current
user, which every domain endpoint depends on to obtain its farm scope.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.security import decode_token
from ..models import models
from ..models.database import get_db

# tokenUrl is the login endpoint; used by the OpenAPI docs "Authorize" flow. The
# scheme only extracts the Authorization: Bearer header — validation is below.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_credentials_error = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Decode the JWT, load the user, or reject with 401.

    Every domain endpoint takes this dependency; `current_user.farm_id` is the
    scope key threaded into every service call so no farm sees another's data.
    """
    subject = decode_token(token)
    if subject is None:
        raise _credentials_error
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _credentials_error
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise _credentials_error
    return user
