import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Make `app` importable regardless of the working directory alembic was invoked
# from. alembic.ini's `prepend_sys_path = .` resolves against the CWD, which is
# only correct when alembic is run from inside backend/ (as the container does).
# The test suite and the CI migrations job run pytest from the repository root,
# where `.` is the repo and `app` is a directory down — so the import below
# failed there and the chain was never actually executed. Anchoring to this
# file's own location makes the invocation directory irrelevant.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Import the models' metadata so autogenerate can detect schema changes.
from app.models.models import Base

config = context.config

# The DATABASE_URL env var is the single source of truth for the connection.
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
