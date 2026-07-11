"""add ledger reversal link + audit columns (ticket 10: soft immutability)

Financial records must never be destroyed. Rather than a hard DELETE, a mistaken
Operational Log is corrected by a *reversing entry* — a new log plus a contra
Financial Transaction that nets its effect to zero while both postings stay
visible. This migration adds:

  - operational_logs.reverses_id: self-referential FK from a reversal to the log
    it offsets.
  - created_at / updated_at audit columns on operational_logs and
    financial_transactions, backfilled from each row's existing `timestamp` so
    historical records carry a real creation time rather than the moment this
    migration happened to run.

Applied automatically on container start (backend/Dockerfile runs
`alembic upgrade head` before uvicorn), against the persistent postgres_data
volume — existing rows are preserved and backfilled, nothing is dropped.

Revision ID: d5c1f0a9b8e2
Revises: c3f7a1e58d24
Create Date: 2026-07-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5c1f0a9b8e2'
down_revision: Union[str, None] = 'c3f7a1e58d24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Ledger tables that gain created_at / updated_at audit columns.
AUDITED_TABLES = ("operational_logs", "financial_transactions")


def upgrade() -> None:
    # 1. Reversal link on operational_logs (self-referential).
    op.add_column("operational_logs", sa.Column("reverses_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_operational_logs_reverses_id",
        "operational_logs", "operational_logs",
        ["reverses_id"], ["id"],
    )
    op.create_index(
        op.f("ix_operational_logs_reverses_id"),
        "operational_logs", ["reverses_id"], unique=False,
    )

    # 2. Audit columns on both ledger tables. server_default=now() so app inserts
    #    are stamped by the database; nullable so the add is non-blocking.
    for table in AUDITED_TABLES:
        op.add_column(table, sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
        op.add_column(table, sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))

    # 3. Backfill audit dates from each row's domain timestamp, so historical
    #    rows reflect when they were actually recorded (adding the column with a
    #    server_default stamped every existing row with now(); overwrite that).
    bind = op.get_bind()
    for table in AUDITED_TABLES:
        # "timestamp" is quoted because it is also a SQL type keyword; quoting
        # forces the parser to read it as the column name on both Postgres and
        # SQLite.
        bind.execute(sa.text(f'UPDATE {table} SET created_at = "timestamp", updated_at = "timestamp"'))


def downgrade() -> None:
    for table in AUDITED_TABLES:
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")
    op.drop_index(op.f("ix_operational_logs_reverses_id"), table_name="operational_logs")
    op.drop_constraint("fk_operational_logs_reverses_id", "operational_logs", type_="foreignkey")
    op.drop_column("operational_logs", "reverses_id")
