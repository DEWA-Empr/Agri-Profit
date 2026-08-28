# Operating AgriProfit

Running it after it is deployed: backups, restores, health, logs, incidents.
Getting it deployed in the first place is `docs/DEPLOYMENT.md`.

---

## 1. Health and what each answer means

| Endpoint | Question | Healthy | Unhealthy |
|---|---|---|---|
| `GET /health` | Is the process up? | `200 {"status":"healthy"}` | no response / connection refused |
| `GET /health/ready` | Can it serve a request? | `200`, `checks.database == "ok"` | `503`, `checks.database == "unreachable"` |

The split is deliberate. A liveness probe that checked the database would
restart a perfectly healthy application every time Postgres hiccupped, turning a
brief outage into a restart loop that makes recovery slower. **Restart on
`/health` failing. Alert, but do not restart, on `/health/ready` failing.**

Neither endpoint requires authentication and neither discloses anything about a
farm. The readiness failure reason is written to the log in full and is
deliberately **not** returned — a connection string in a probe response is a
credential sitting somewhere nobody is watching.

```bash
docker compose -f docker-compose.prod.yml ps        # health of every service
curl -fsS localhost:8080/../health/ready            # from the host
```

## 2. Backups

### Taking one

```bash
sh ops/backup.sh                    # writes ./backups/agriprofit-<UTC stamp>.dump
sh ops/backup.sh /mnt/nas/agri      # or elsewhere
```

The script dumps with `pg_dump -Fc`, refuses to keep a zero-byte file, and
**verifies the archive is readable** by listing its table of contents with
`pg_restore --list`. That catches the two silent failures — a dump truncated by
a full disk, and one taken against an empty database because a container name
was wrong — without restoring anything.

### Scheduling it

`crontab -e` on the host:

```cron
# 02:15 daily. Output goes to a log you can actually read afterwards.
15 2 * * * cd /opt/agriprofit && sh ops/backup.sh >> /var/log/agriprofit-backup.log 2>&1

# First of the month: rehearse a restore. See §3 — this is the part that turns
# a backup into a verified backup, and it runs against a scratch database so it
# needs no maintenance window.
30 3 1 * * cd /opt/agriprofit && sh ops/restore.sh "$(ls -t backups/*.dump | head -1)" >> /var/log/agriprofit-restore-check.log 2>&1
```

### Retention

30 days by default; `RETENTION_DAYS=90 sh ops/backup.sh` to change it. Older
dumps are pruned by the script, so the directory does not grow without bound.

**A backup on the same host as its database is not a backup.** It shares a disk
with the thing it exists to survive. Copy dumps to institutional storage —
whatever your department already backs up — and treat the local copy as a
convenience for fast recovery only.

## 3. Restoring

### Rehearsal (safe, and the one to run regularly)

```bash
sh ops/restore.sh backups/agriprofit-20260827T021500Z.dump
```

Restores into a scratch database beside the live one, prints the row counts, the
`alembic_version` and the count of unpaired operational logs, then drops the
scratch database. The live database is never touched, so this is safe to run on
the production host on a schedule.

Read the output rather than just its exit code:

- **row counts** should be in the range you expect for the farm's activity;
- **`alembic_version`** must be a revision the deployed code knows. A dump
  restored under a codebase expecting a later migration fails on the first
  query;
- **unpaired logs must be 0.** Every operational log posts its financial
  transaction in the same commit; a non-zero count means the restore produced
  data that violates the platform's central integrity invariant, and it is not
  usable even though `pg_restore` "succeeded".

### Real restore

```bash
docker compose -f docker-compose.prod.yml stop backend       # stop writes first
sh ops/restore.sh backups/agriprofit-<stamp>.dump --force    # prompts for the DB name
docker compose -f docker-compose.prod.yml start backend
curl -fsS https://your-host/health/ready
```

Stopping the backend first is not optional. A restore into a database the
application is still writing to produces a mixture of two states.

> **Verification status — rehearsal executed 2026-08-28.** Both scripts have now
> been run end to end against a real PostgreSQL 15 database (the `db` service of
> `docker-compose.prod.yml`), not merely syntax-checked.
>
> What was done: migrations were applied to an empty database with
> `alembic upgrade head`, representative data was seeded (2 farms, 3 users at
> all three roles, 5 operational logs each paired to a financial transaction,
> 1 equipment asset), `ops/backup.sh` produced a 27,800-byte custom-format dump
> and verified it listed 8 tables with data, and `ops/restore.sh` restored that
> dump into the scratch database.
>
> What the rehearsal showed:
>
> | Check | Result |
> |---|---|
> | farms / users / operational_logs / financial_transactions / equipment | 2 / 3 / 5 / 5 / 1 — every count matched the source exactly |
> | `alembic_version` in the restored database | `b9e5f30c74a1` — the chain head |
> | Unpaired operational logs (the paired-write invariant) | 0 |
> | Live `agriprofit` database after the rehearsal | untouched (5 logs, as before) |
> | Scratch database afterwards | dropped |
>
> The backup is therefore verified as restorable, not merely documented. Re-run
> the §3 rehearsal monthly, on the real data, and record the date and counts —
> a restore verified against seeded data proves the mechanism, not this month's
> backup file.

## 4. Logging

Everything goes to stdout, so `docker compose logs` and whatever the institution
already collects will see it. There is no bespoke aggregation stack here on
purpose.

```bash
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs --since 1h backend | grep ' 5[0-9][0-9] '
```

Each request logs method, path, status and duration:

```
INFO:     [agriprofit] GET /api/v1/reports/pnl -> 200 (24.1ms)
INFO:     [agriprofit] GET /api/v1/share/report/[redacted]:a3f9c1e04b7d -> 200 (31.7ms)
```

**What is deliberately kept out of the log.** The investor share token is the
whole credential for a farm's financial report, and it travels in the URL path.
Logging the path verbatim wrote working share links into stdout on every
investor view. `core/logging_safety.py` replaces the secret with a short
non-reversible fingerprint instead of dropping it, so an operator can still tell
one link from another across a log file — two requests carrying the same link
share a fingerprint, and the fingerprint cannot be turned back into a link.

Passwords and session tokens never reach the log at all: they arrive in bodies
and headers, neither of which is logged.

If a new route ever carries a secret in its path, add it to the allow-list in
`core/logging_safety.py` **and** add a test to `test_logging_safety.py` — that
test file is the enforcement, not the module.

## 5. Rate limits, and what to do when someone is locked out

Counters are in-process fixed windows (`backend/app/core/rate_limit.py`).

| Route | Default | Keyed on |
|---|---|---|
| `POST /auth/login` | 10 failures / 15 min | account **and** client IP, independently |
| `POST /auth/register` | 20 / hour | client IP |
| `GET /share/report/{token}` | 60 / 5 min | client IP |

Only **failed** logins count, and a success clears the account's budget — so a
farmer who mistypes their password three times and then gets it right starts
clean. The IP budget is not cleared by a success.

A locked-out user waits out the window; there is no unlock command, deliberately
— one would be a way to bypass the control. To widen a limit, change it in
`.env` and restart the backend. `RATE_LIMIT_ENABLED=false` exists only to
diagnose a lockout and should never be left off.

**Two limits worth knowing before you scale.** The counters do not span
replicas: two backend containers each keep their own, so the effective limit
doubles. And they do not survive a restart. Both are acceptable for one
container serving one institution and both are the trigger to move the counters
into Redis or the proxy. Neither is a reason to add Redis today.

## 6. Share links

Every new link expires — 90 days by default (`SHARE_LINK_DEFAULT_TTL_DAYS`), and
a farmer may request 1–365 when minting. Links minted before expiry existed
carry `NULL` and never lapse; that is deliberate, so an upgrade could not kill a
link already sitting in a bank's inbox.

An expired, revoked or unknown token all answer with an identical 404. That is
not vagueness: distinguishing them would confirm that a token recovered from a
log or a browser history was once real.

To find links that never expire:

```sql
SELECT id, farm_id, label, created_at FROM share_tokens
WHERE expires_at IS NULL AND revoked = false;
```

Ask the owning farm to re-mint and revoke the old one.

## 7. Retraining the yield model

Not over the API. `POST /dss/train` is closed by a permission no role holds
**and** an off-by-default setting, because there is one model artefact and every
farm's forecast is served from it — one tenant calling it would change what
every other tenant sees, on a machine shared with their request traffic.

```bash
docker compose -f docker-compose.prod.yml exec backend python -m app.ml.train
docker compose -f docker-compose.prod.yml restart backend      # clears the cached model
```

A container with no artefact trains one on boot, so a rebuild also retrains. The
model is synthetic-data only; see `docs/REPRODUCIBILITY.md` for what its figures
do and do not claim.

## 8. Common problems

| Symptom | Likely cause | What to do |
|---|---|---|
| Backend restarts in a loop on first deploy | `SECRET_KEY` unset with `ENVIRONMENT=production` | The guard is working. Set it in `.env` |
| `/health/ready` returns 503 | Database down or credentials wrong | `logs db`; check `DATABASE_URL` matches `POSTGRES_PASSWORD` |
| Frontend loads, every API call fails with a CORS error | `CORS_ORIGINS` does not exactly match the browser's origin | Match scheme and host exactly, no trailing slash. Same-origin (`VITE_API_URL=/api/v1`) avoids this entirely |
| App works, but nothing is available offline | Service worker not installed | It will not install over plain HTTP. Check TLS. Then check `/sw.js` is served with `no-cache` |
| A farmer's offline records never sync | Records failed three times and are marked `failed` | They are shown with a Retry control in the app. If they 422, the record is invalid — the values are out of bounds |
| Everyone locked out of login at once | Shared NAT hitting the per-IP limit | Raise `LOGIN_IP_MAX_ATTEMPTS`, restart backend |
| Break-even prices moved and nobody changed anything | The reporting window is derived and widens with every log | Pin it: `?period_days=365`. Check `period_source` in the response |
| A figure changed after someone edited equipment | A correction moves the depreciation overlay | `updated_at` on the asset shows when. See `docs/REPRODUCIBILITY.md` §7 |

## 9. Routine schedule

| When | Task |
|---|---|
| Daily | Backup (cron, §2) |
| Weekly | Skim logs for 5xx; check disk on the backups volume |
| Monthly | **Restore rehearsal** (§3). Record the date and the counts |
| Monthly | Review share links with `expires_at IS NULL` (§6) |
| Per release | Backup before deploying; `alembic current` after |
| Termly | Review farm members and roles; deactivate accounts that have left |
