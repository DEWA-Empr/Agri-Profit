"""add share_tokens

Ticket 05: revocable, read-only investor/lender share links. A brand-new table
(no backfill) storing only the SHA-256 hash of each token, bound to a farm by
farm_id. down_revision chains after the auth/farm-scope migration.

Revision ID: c3f7a1e58d24
Revises: b2e4d6f81a09
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f7a1e58d24'
down_revision: Union[str, None] = 'b2e4d6f81a09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "share_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_share_tokens_id"), "share_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_share_tokens_farm_id"), "share_tokens", ["farm_id"], unique=False)
    op.create_index(op.f("ix_share_tokens_token_hash"), "share_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_share_tokens_token_hash"), table_name="share_tokens")
    op.drop_index(op.f("ix_share_tokens_farm_id"), table_name="share_tokens")
    op.drop_index(op.f("ix_share_tokens_id"), table_name="share_tokens")
    op.drop_table("share_tokens")
