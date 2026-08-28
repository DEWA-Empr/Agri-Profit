"""add equipment.updated_at

Equipment becomes correctable in this revision, and a correction is not a
neutral act: `depreciation_rate` and `purchase_price` drive the depreciation
overlay, the overlay drives allocated fixed cost, and that drives the break-even
price to cover total cost. Editing an asset therefore MOVES a figure that may
already have been reported, quoted or written down — the same reproducibility
problem `period_days` was introduced to solve on the reporting side.

Correcting the record is still right: an asset's depreciation rate is a
parameter describing a thing the farm owns, not a transaction recording
something that happened, and the overlay it feeds is computed at report time and
never posted to the ledger. Nothing here rewrites financial history. But a
figure that moved silently is indistinguishable from a figure that was always
that value, so the fact of the correction has to be visible.

NULLABLE, and NULL is meaningful: it reads as "as originally entered, never
corrected". No backfill, because stamping a timestamp on rows that were never
corrected would assert a correction that did not happen.

Revision ID: b9e5f30c74a1
Revises: a8d4e1c60b27
Create Date: 2026-08-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b9e5f30c74a1'
down_revision: Union[str, None] = 'a8d4e1c60b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "equipment",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("equipment", "updated_at")
