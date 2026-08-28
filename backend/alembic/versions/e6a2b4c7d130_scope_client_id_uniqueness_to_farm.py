"""Scope operational_logs.client_id uniqueness to the farm

The global unique index on `client_id` was written in 544b85dc2d20, the initial
schema — before tenancy existed (farm_id arrives two migrations later, in
b2e4d6f81a09). Idempotency, however, has always been resolved per farm:
`ledger_service._find_by_client_id` filters on `farm_id` and its docstring says
so explicitly ("a client_id is only an idempotency match within the same
tenant").

The two disagreed, and the disagreement was reachable. Farm B posting a
client_id that farm A had already used violated the global index; the
IntegrityError handler then looked the key up *within farm B*, found nothing,
and re-raised — landing on the catch-all handler in main.py as an unhandled
HTTP 500. The seed script makes this concrete: it uses fixed, human-readable
client_ids ("seed-bioprocess-yield-0001"), so seeding a second demo farm on the
same database hit it every time.

This migration makes the constraint say what the service already meant:
uniqueness on (farm_id, client_id). The index on client_id alone is kept,
non-unique, because the lookup still filters on it.

Safety: the new composite constraint is strictly weaker than the global one, so
no existing row can violate it and no data is touched. NULL client_ids remain
exempt — NULLs never compare equal in either Postgres or SQLite — which is what
lets every non-offline log leave the column empty.

Revision ID: e6a2b4c7d130
Revises: d5c1f0a9b8e2
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'e6a2b4c7d130'
down_revision: Union[str, None] = 'd5c1f0a9b8e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the pre-tenancy global unique index and put back a plain one: the
    # farm-scoped lookup still reads by client_id, so it still wants the index.
    op.drop_index(op.f('ix_operational_logs_client_id'), table_name='operational_logs')
    op.create_index(
        op.f('ix_operational_logs_client_id'), 'operational_logs', ['client_id'], unique=False
    )
    op.create_unique_constraint(
        'uq_operational_logs_farm_client', 'operational_logs', ['farm_id', 'client_id']
    )


def downgrade() -> None:
    # NOTE: this direction can fail, and that is correct rather than a defect.
    # Once two farms hold the same client_id, restoring a GLOBAL unique index is
    # genuinely impossible without discarding one of their records, and a
    # migration must not choose which farm's ledger row to destroy. Resolve the
    # duplicates deliberately first, then downgrade.
    op.drop_constraint('uq_operational_logs_farm_client', 'operational_logs', type_='unique')
    op.drop_index(op.f('ix_operational_logs_client_id'), table_name='operational_logs')
    op.create_index(
        op.f('ix_operational_logs_client_id'), 'operational_logs', ['client_id'], unique=True
    )
