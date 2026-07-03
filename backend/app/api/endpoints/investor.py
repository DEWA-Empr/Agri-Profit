from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...models import models
from ...models.database import get_db
from ...schemas import schemas
from ...services import share_service
from ..deps import get_current_user

router = APIRouter(prefix="/share", tags=["share"])


# --- Owner-side (authenticated, farm-scoped) ---
@router.post("/links", response_model=schemas.ShareLinkMinted, status_code=201)
def mint_link(
    payload: schemas.ShareLinkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mint a read-only share link for the caller's farm. The raw token is
    returned exactly once here — only its hash is stored."""
    link, token = share_service.create_link(db, current_user.farm_id, payload.label)
    return schemas.ShareLinkMinted(
        id=link.id, label=link.label, revoked=link.revoked, created_at=link.created_at, token=token,
    )


@router.get("/links", response_model=List[schemas.ShareLink])
def list_links(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """List the caller's share links (metadata only — the token is never
    re-served; a lost link is re-minted)."""
    return share_service.list_links(db, current_user.farm_id)


@router.post("/links/{link_id}/revoke", response_model=schemas.ShareLink)
def revoke_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Revoke one of the caller's links (404 for a link that isn't theirs)."""
    return share_service.revoke_link(db, current_user.farm_id, link_id)


# --- Public (no auth): token IS the credential ---
@router.get("/report/{token}", response_model=schemas.InvestorReport)
def public_report(token: str, db: Session = Depends(get_db)):
    """Read-only P&L + yield for the farm the token belongs to. No login. The
    farm is derived from the token alone, so this can only ever return the
    token's own farm; an unknown or revoked token is a 404. GET only — there is
    no token-authenticated write path anywhere in the API."""
    return share_service.get_report_by_token(db, token)
