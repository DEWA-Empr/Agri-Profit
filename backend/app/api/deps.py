"""Shared FastAPI dependencies — chiefly resolving a bearer token to the current
user, and deciding whether that user may attempt the operation behind the route.

THE FLOW, AND WHY IT IS IN THIS ORDER:

    identity        get_current_user   — a valid token names a live account
       |
    account state   get_current_user   — a deactivated account is not an identity
       |
    permission      require(...)       — the role's table says yes (403 if not)
       |
    scope           service layer      — farm_id filters every query (404 if not)
       |
    operation

Permission is checked BEFORE scope on purpose. A caller who may not reverse
entries at all should be told so whether or not the log they named exists, and
answering 404 first would leak whether a given id belongs to their farm to a
caller with no business asking.

Scope is NOT weakened by any of this. Every service still takes `farm_id` from
the authenticated user, so a permission is only ever the right to do something
*to your own farm*. There is no permission in the table that reaches across
tenants, and none can be added by editing this file alone.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.roles import Permission, has_permission
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

    A DEACTIVATED ACCOUNT IS REJECTED HERE, not at the permission layer, and it
    answers 401 rather than 403. Tokens are self-contained and live for 24
    hours, so without this check withdrawing someone's access would not take
    effect until their token expired — which is not what "remove this person"
    means to whoever asked for it. 401 rather than 403 because the correct
    client response is to sign out, not to see a "forbidden" screen while
    holding a token the server no longer honours.
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
    if not user.is_active:
        raise _credentials_error
    return user


def require(permission: Permission):
    """Build a dependency that admits only callers whose role grants `permission`.

    Returns the user, so a route can write

        current_user: models.User = Depends(require(Permission.FINANCE_READ))

    in place of its existing `Depends(get_current_user)` and keep using
    `current_user.farm_id` exactly as before. That substitution is what makes
    applying authorization to the existing route layer a one-line change per
    route rather than a restructure.

    The 403 names the missing permission. That is safe to disclose — it tells
    the caller about their OWN role, not about anyone else's data — and without
    it a legitimate user hitting a boundary has no way to know what to ask their
    farm owner for.
    """
    def _dependency(
        current_user: models.User = Depends(get_current_user),
    ) -> models.User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your role ({current_user.role}) does not permit {permission.value}.",
            )
        return current_user
    return _dependency
