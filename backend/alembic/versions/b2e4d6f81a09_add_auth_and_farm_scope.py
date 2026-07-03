"""add farms + users and farm scope to domain tables

Objective 3 (secure data-sharing framework): introduce tenants (farms) and users
and scope every domain row to a farm. Pre-existing rows predate the boundary, so
they are backfilled into a seeded "Legacy Farm" — non-destructive (the verified
historical ledger is preserved) yet isolated (no newly-registered user is
attached to that farm, so nobody sees the legacy data by default). After the
backfill, farm_id is made NOT NULL: "every record belongs to a farm" becomes a
real database invariant.

Revision ID: b2e4d6f81a09
Revises: a1f3c9e42b71
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2e4d6f81a09'
down_revision: Union[str, None] = 'a1f3c9e42b71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tables that gain a farm_id scope column.
SCOPED_TABLES = ("operational_logs", "financial_transactions", "equipment", "maintenance_logs")


def upgrade() -> None:
    # 1. Tenants + users.
    op.create_table(
        "farms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_farms_id"), "farms", ["id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("farm_id", sa.Integer(), sa.ForeignKey("farms.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 2. Add farm_id (nullable for now) + FK + index to each domain table.
    for table in SCOPED_TABLES:
        op.add_column(table, sa.Column("farm_id", sa.Integer(), nullable=True))
        op.create_foreign_key(f"fk_{table}_farm_id", table, "farms", ["farm_id"], ["id"])
        op.create_index(op.f(f"ix_{table}_farm_id"), table, ["farm_id"], unique=False)

    # 3. Backfill existing rows into a seeded "Legacy Farm".
    bind = op.get_bind()
    legacy_id = bind.execute(
        sa.text("INSERT INTO farms (name) VALUES ('Legacy Farm') RETURNING id")
    ).scalar()
    for table in SCOPED_TABLES:
        bind.execute(
            sa.text(f"UPDATE {table} SET farm_id = :fid WHERE farm_id IS NULL"),
            {"fid": legacy_id},
        )

    # 4. Now that no NULLs remain, enforce the invariant.
    for table in SCOPED_TABLES:
        op.alter_column(table, "farm_id", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    for table in SCOPED_TABLES:
        op.drop_index(op.f(f"ix_{table}_farm_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_farm_id", table, type_="foreignkey")
        op.drop_column(table, "farm_id")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_farms_id"), table_name="farms")
    op.drop_table("farms")
