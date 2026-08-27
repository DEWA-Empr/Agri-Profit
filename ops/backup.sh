#!/usr/bin/env sh
# Take a compressed, verified logical backup of the AgriProfit database.
#
# WHY pg_dump -Fc RATHER THAN A PLAIN SQL FILE. The custom format is compressed,
# and pg_restore can read a table list out of it — which is what makes the
# verification step below possible without restoring anything. A plain .sql dump
# can only be checked by running it.
#
# WHY THE VERIFY STEP IS NOT OPTIONAL. A backup that has never been read is a
# hope, not a backup. This does not prove the data restores correctly — only a
# real restore does that, and ops/restore.sh exists for exactly that rehearsal —
# but it does prove the file is a readable archive containing the tables it
# should, which catches the common failures: a dump truncated by a full disk, or
# one taken against an empty database because the container name was wrong.
#
# Usage (from the repository root, with the prod stack up):
#   sh ops/backup.sh
#   sh ops/backup.sh /mnt/nas/agriprofit      # alternative destination
#
# Restore with ops/restore.sh. Read docs/OPERATIONS.md before you need to.

set -eu

DEST="${1:-./backups}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
DB_SERVICE="${DB_SERVICE:-db}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Read credentials from .env rather than taking them on the command line, where
# they would land in the shell history and in `ps` output.
if [ -f .env ]; then
    # shellcheck disable=SC1091
    . ./.env
fi
: "${POSTGRES_USER:?POSTGRES_USER is not set (is .env present?)}"
: "${POSTGRES_DB:?POSTGRES_DB is not set (is .env present?)}"

mkdir -p "$DEST"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
FILE="$DEST/agriprofit-$STAMP.dump"

echo "==> Dumping $POSTGRES_DB to $FILE"
docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner \
    > "$FILE"

if [ ! -s "$FILE" ]; then
    echo "!! Dump is empty. Refusing to keep a zero-byte file that would look like a backup." >&2
    rm -f "$FILE"
    exit 1
fi

echo "==> Verifying the archive is readable"
# Lists the archive's table of contents without touching any database. A
# corrupt or truncated dump fails here rather than at 3am during a restore.
TABLES="$(docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
    pg_restore --list < "$FILE" | grep -c 'TABLE DATA' || true)"

if [ "$TABLES" -lt 5 ]; then
    echo "!! Archive lists only $TABLES tables with data; expected at least 5." >&2
    echo "   Keeping $FILE for inspection, but do NOT treat it as a good backup." >&2
    exit 1
fi

SIZE="$(wc -c < "$FILE" | tr -d ' ')"
echo "==> OK: $FILE ($SIZE bytes, $TABLES tables with data)"

echo "==> Pruning backups older than $RETENTION_DAYS days in $DEST"
find "$DEST" -name 'agriprofit-*.dump' -type f -mtime "+$RETENTION_DAYS" -print -delete || true

cat <<NOTE

Reminder: this file is on the same host as the database it came from. A backup
that shares a disk with its source does not survive the failure it exists for.
Copy it off — to institutional storage, or wherever your department already
keeps recoverable data.
NOTE
