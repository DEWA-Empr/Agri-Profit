#!/usr/bin/env sh
# Restore an AgriProfit backup, or rehearse restoring one.
#
# READ THIS FIRST. Restoring into the live database DESTROYS whatever is
# currently there. That is what a restore is, but it means the command has to be
# hard to run by accident: the script refuses to touch the production database
# unless you pass --force, and its default mode restores into a scratch database
# instead.
#
# THE DEFAULT MODE IS THE ONE TO USE REGULARLY. A backup that has never been
# restored is not a verified backup, and the only way to verify one is to
# restore it and look. This restores into a throwaway database beside the live
# one, counts what arrived, and drops it again — so the rehearsal is safe to run
# on the production host, on a schedule, without a maintenance window.
#
# Usage:
#   sh ops/restore.sh backups/agriprofit-20260827T101500Z.dump          # rehearse
#   sh ops/restore.sh backups/agriprofit-...dump --force                # REAL restore
#
# See docs/OPERATIONS.md for the full procedure, including stopping the backend
# first so it cannot write during a real restore.

set -eu

FILE="${1:?usage: restore.sh <dumpfile> [--force]}"
MODE="${2:-rehearse}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
DB_SERVICE="${DB_SERVICE:-db}"

if [ -f .env ]; then
    # shellcheck disable=SC1091
    . ./.env
fi
: "${POSTGRES_USER:?POSTGRES_USER is not set (is .env present?)}"
: "${POSTGRES_DB:?POSTGRES_DB is not set (is .env present?)}"

[ -s "$FILE" ] || { echo "!! $FILE is missing or empty." >&2; exit 1; }

psql_run() {
    docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
        psql -U "$POSTGRES_USER" -d "$1" -tAc "$2"
}

if [ "$MODE" = "--force" ]; then
    TARGET="$POSTGRES_DB"
    cat <<WARN
!! REAL RESTORE into '$TARGET'. Everything currently in it will be replaced.
!! Stop the backend first:  docker compose -f $COMPOSE_FILE stop backend
WARN
    printf 'Type the database name to continue: '
    read -r CONFIRM
    [ "$CONFIRM" = "$TARGET" ] || { echo "Aborted."; exit 1; }
else
    TARGET="${POSTGRES_DB}_restore_check"
    echo "==> Rehearsal. Restoring into scratch database '$TARGET'; '$POSTGRES_DB' is untouched."
    docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
        psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $TARGET"
    docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
        psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $TARGET"
fi

echo "==> Restoring $FILE into $TARGET"
docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    pg_restore -U "$POSTGRES_USER" -d "$TARGET" --no-owner --clean --if-exists \
    < "$FILE"

echo "==> What arrived:"
for TABLE in farms users operational_logs financial_transactions equipment share_tokens; do
    COUNT="$(psql_run "$TARGET" "SELECT count(*) FROM $TABLE" 2>/dev/null || echo "MISSING")"
    printf '    %-24s %s\n' "$TABLE" "$COUNT"
done

# The schema version matters as much as the rows: a dump restored into a
# codebase expecting a later migration will fail at the first query, and it is
# better to find that out here.
VERSION="$(psql_run "$TARGET" "SELECT version_num FROM alembic_version" 2>/dev/null || echo "MISSING")"
echo "    alembic_version          $VERSION"

# The paired-write invariant is the platform's central integrity claim. If a
# restore breaks it, the data is not usable even though the restore "succeeded".
LOGS="$(psql_run "$TARGET" "SELECT count(*) FROM operational_logs WHERE financial_transaction_id IS NULL" 2>/dev/null || echo "?")"
echo "    unpaired logs            $LOGS  (must be 0)"

if [ "$MODE" != "--force" ]; then
    echo "==> Dropping the scratch database"
    docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
        psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $TARGET"
    echo "==> Rehearsal complete. Record the date and the counts above."
else
    echo "==> Restore complete. Start the backend:"
    echo "    docker compose -f $COMPOSE_FILE start backend"
fi
