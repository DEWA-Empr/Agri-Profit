"""add crop to operational_logs

Adds a nullable `crop` column to operational_logs so records can be grouped by
crop for the Tier-1 deterministic decision-support report (Chapter 3 §3.6.5:
"unit cost of production and per-crop gross margin ... grouped by Activity
Category and crop"). Purely additive — no data loss; existing rows get NULL and
are reported under an "Unspecified" bucket.

Revision ID: a1f3c9e42b71
Revises: 544b85dc2d20
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f3c9e42b71'
down_revision: Union[str, None] = '544b85dc2d20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('operational_logs', sa.Column('crop', sa.String(), nullable=True))
    op.create_index(op.f('ix_operational_logs_crop'), 'operational_logs', ['crop'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_operational_logs_crop'), table_name='operational_logs')
    op.drop_column('operational_logs', 'crop')
