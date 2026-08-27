"""add share_tokens.expires_at

A share token is a bearer credential: whoever holds the URL can read that farm's
financial report, with no account and no second factor. Before this migration
the only way one ever stopped working was the owner remembering to revoke it, so
a link handed to a lender for a single loan assessment stayed live indefinitely.

NULLABLE, AND THAT IS THE WHOLE MIGRATION'S SAFETY ARGUMENT. Every token minted
before this change gets NULL, and NULL is read as "no expiry" by
`share_service.get_report_by_token`. No existing investor link stops working the
moment this deploys — which matters, because a farmer cannot be told that the
link already sitting in a bank's inbox died on upgrade night. New tokens are
given a real expiry by the service layer (default 90 days, see
`Settings.share_link_default_ttl_days`); the column stays nullable only to carry
that history, not as an invitation to mint non-expiring links.

No backfill, deliberately. Stamping an expiry onto existing rows would be
choosing a date on the owner's behalf for links they were told were permanent,
and would revoke access the application had already granted.

Revision ID: f7b3c2d94e15
Revises: e6a2b4c7d130
Create Date: 2026-08-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f7b3c2d94e15'
down_revision: Union[str, None] = 'e6a2b4c7d130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "share_tokens",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Safe in this direction: dropping the column returns every token to
    # "never expires", which is exactly the behaviour that preceded it. Nothing
    # is lost that the application depended on before this revision.
    op.drop_column("share_tokens", "expires_at")
