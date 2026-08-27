"""Investor/lender share links (ticket 05).

A farm owner mints a revocable, read-only capability; an investor opens the link
and sees that farm's P&L + yield with no account. The farm is bound to the token
by the ShareToken row alone — the public report is derived from the token's
farm_id and never accepts a farm from the caller, so a token cannot reach any
farm but its own (a cross-farm read is unrepresentable, not merely blocked).

Only the SHA-256 hash of a token is stored; the raw token is returned once, at
mint time, and never again.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import NotFoundError
from ..core.security import generate_share_token, hash_share_token
from ..models import models
from . import dss_service, reports_service


def create_link(
    db: Session,
    farm_id: int,
    label: str | None,
    expires_in_days: int | None = None,
) -> tuple[models.ShareToken, str]:
    """Mint a share link for a farm. Returns (row, raw_token); the raw token is
    the caller's only chance to see the secret.

    EVERY NEW LINK EXPIRES. `expires_in_days` of None means the configured
    default rather than "no expiry" — there is no code path here that mints a
    non-expiring token, because a bearer credential to a farm's finances should
    not outlive the reason it was shared. The nullable column exists solely to
    carry links minted before expiry was introduced (migration f7b3c2d94e15),
    which keep working untouched.
    """
    days = expires_in_days or settings.share_link_default_ttl_days
    token = generate_share_token()
    link = models.ShareToken(
        farm_id=farm_id,
        token_hash=hash_share_token(token),
        label=label,
        revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=days),
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link, token


def list_links(db: Session, farm_id: int) -> list[models.ShareToken]:
    return (
        db.query(models.ShareToken)
        .filter(models.ShareToken.farm_id == farm_id)
        .order_by(models.ShareToken.created_at.desc(), models.ShareToken.id.desc())
        .all()
    )


def revoke_link(db: Session, farm_id: int, link_id: int) -> models.ShareToken:
    # Scoped by farm_id: another farm's link id is simply "not found", so an
    # owner can only ever revoke their own links.
    link = (
        db.query(models.ShareToken)
        .filter(models.ShareToken.id == link_id, models.ShareToken.farm_id == farm_id)
        .first()
    )
    if link is None:
        raise NotFoundError(f"Share link {link_id} not found")
    link.revoked = True
    db.commit()
    db.refresh(link)
    return link


def get_report_by_token(db: Session, token: str) -> dict:
    """Resolve a raw token to its farm's read-only report.

    The farm is read off the token row — the caller supplies no farm — so the
    report can only ever be the token's own farm. Unknown, revoked and expired
    tokens all resolve to nothing (404), which is how revocation and expiry take
    effect.

    ONE VERDICT FOR ALL THREE, deliberately. Telling a caller that a token was
    valid but has expired distinguishes "this was once a real link" from "this
    was never a link", and that difference is an oracle: it confirms a candidate
    recovered from a leaked log or a browser history was once well-formed, which
    is exactly the signal an attacker probing them wants. The farmer who needs
    to know why a banker's link stopped working reads `expires_at` from their
    own links list, where they are authenticated.
    """
    now = datetime.now(timezone.utc)
    link = (
        db.query(models.ShareToken)
        .filter(
            models.ShareToken.token_hash == hash_share_token(token),
            models.ShareToken.revoked.is_(False),
            # NULL expiry means a link minted before expiry existed, and those
            # never lapse. The OR is load-bearing: `expires_at > now` alone
            # evaluates to NULL for those rows, a NULL predicate is not true,
            # and every legacy investor link would start returning 404.
            or_(
                models.ShareToken.expires_at.is_(None),
                models.ShareToken.expires_at > now,
            ),
        )
        .first()
    )
    if link is None:
        raise NotFoundError("Share link is invalid, has expired, or has been revoked")

    farm = db.query(models.Farm).filter(models.Farm.id == link.farm_id).first()
    farm_name = farm.name if farm else "Farm"

    pnl = reports_service.get_pnl_report(db, link.farm_id)
    crops = dss_service.get_decision_support(db, link.farm_id)["crops"]

    return {
        "farm_name": farm_name,
        "generated_at": datetime.now(timezone.utc),
        "pnl": pnl,
        "crops": crops,
    }
