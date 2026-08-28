"""add users.role and users.is_active

Before this revision the platform had authentication and farm isolation but no
authorization: every authenticated user could do everything their farm's data
allowed, including minting a share link that discloses the farm's whole
financial position to an outsider.

THE BACKFILL IS THE COMPATIBILITY GUARANTEE. Registration creates a farm and its
first user in one step, so every account that exists when this runs is the sole
account on its own farm — there is no existing user for whom "owner" is a
promotion. Adding the column with a server default backfills every existing row
to 'owner' in the same statement, so no current behaviour changes: every user
keeps exactly the access they had the moment before the migration ran.

A plain VARCHAR, not a Postgres ENUM type. Roles are the column most likely to
gain a value later, and extending a native enum needs its own migration and a
type rewrite; a string plus validation at the schema edge (core/roles.py) is the
cheaper shape to live with. NOT NULL, because a role of NULL has no defined
answer to "may this caller do X" and `permissions_for` would have to guess.

is_active exists because the platform does not delete records. Removing a
worker's access is a state change on their account, in the same spirit as
revoking a share link rather than deleting it, and it leaves the audit trail of
what they entered intact.

Revision ID: a8d4e1c60b27
Revises: f7b3c2d94e15
Create Date: 2026-08-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a8d4e1c60b27'
down_revision: Union[str, None] = 'f7b3c2d94e15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills every existing row in the same statement, which
    # is the whole point: 'owner' is what each of them effectively already was.
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=False, server_default="owner"),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    # Safe: dropping the columns returns every account to "authenticated means
    # permitted", which is exactly the behaviour that preceded this revision.
    # Role assignments are lost, and that is inherent — there is nowhere to put
    # them in the older schema.
    op.drop_column("users", "is_active")
    op.drop_column("users", "role")
