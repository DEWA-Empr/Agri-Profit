# Deploying AgriProfit

For a departmental deployment: one host, Docker Compose, TLS in front. Not a
hyperscale architecture, and deliberately not — there is no Kubernetes, no
service mesh and no multi-region story here, because nothing about this
workload calls for one.

Operating it afterwards — backups, restores, incidents — is `docs/OPERATIONS.md`.

---

## 1. What gets deployed

There are **two supported patterns**, and they differ only in what terminates
TLS. In both, the frontend container is the single HTTP entry point into the
stack and routes `/api` to the backend itself.

**Pattern A — behind your institution's TLS (the common case).**

```
  browser ──HTTPS──▶ institutional reverse proxy ──HTTP──▶ 127.0.0.1:8080
                                                                │
                                                    ┌───────────┴───────────┐
                                                    │ frontend (nginx)      │
                                                    │ · /api/*  ─▶ backend  │
                                                    │ · /health* ─▶ backend │
                                                    │ · /*       ─▶ SPA     │
                                                    └───────────┬───────────┘
```

**Pattern B — with the bundled Caddy edge (`--profile edge`).**

```
  browser ──HTTPS──▶ caddy :443
                       · /api/*   ─▶ backend:8000
                       · /health* ─▶ backend:8000
                       · /*       ─▶ frontend:8080
```

Below either entry point:

```
          ┌───────────────────┐         ┌────────────────────────┐
          │ frontend          │  /api   │ backend                │
          │ nginx + static    │ ──────▶ │ uvicorn + FastAPI      │
          │ PWA build         │         │ migrations run on boot │
          └───────────────────┘         └───────────┬────────────┘
                                                    ▼  (no published port)
                                        ┌────────────────────────┐
                                        │ db — PostgreSQL 15     │
                                        │ named volume, no port  │
                                        └────────────────────────┘
```

**The `/api` prefix is preserved end to end.** The backend mounts every route
under `/api/v1`, so neither proxy strips it — Caddy uses `handle`, not
`handle_path`, and nginx proxies `$request_uri` unchanged. Stripping it is how
both patterns were once broken at the same time: the API answered 404 through
Caddy and 200 text/html through nginx.

The backend publishes **no host port** in either pattern, so an upstream proxy
cannot reach it directly. Point your institutional proxy at `127.0.0.1:8080`
and let the frontend route `/api` — that is the supported topology.

| Component | Image | Notes |
|---|---|---|
| Backend | built from `backend/Dockerfile` | Python 3.11, uvicorn. Applies Alembic migrations before serving. Trains the yield model on first boot if no artefact is baked in |
| Frontend | built from `frontend/Dockerfile.serve` | Multi-stage: Node builds, nginx serves. ~50 MB rather than ~1 GB |
| Database | `postgres:15` | Named volume `postgres_data_prod`. No published port |
| Edge | `caddy:2-alpine` (profile `edge`) | Optional. Skip if your institution already terminates TLS |

**On `Dockerfile.prod` vs `Dockerfile.serve`.** Both build the frontend.
`Dockerfile.prod` serves it with `vite preview`, which Vite documents as a local
preview of a production build, not a production server. It is kept unchanged
because it is the container the Chapter 4 performance figures were measured
against. **Deploy `Dockerfile.serve`.**

## 2. Requirements

- A Linux host with Docker Engine 24+ and the Compose plugin
- 2 GB RAM minimum (measured footprint of the two exercised containers is under
  205 MiB, but the first boot trains the model and wants headroom)
- 10 GB disk, plus room for backups
- A DNS name pointing at the host, if you are using the bundled TLS edge

## 3. First deployment

```bash
git clone <repository> agriprofit && cd agriprofit
git checkout <release tag>

cp .env.example .env
```

Fill in `.env`. Three values have no safe default and the stack will refuse to
start without them:

```bash
# A fresh key per deployment. Never reuse one from another environment.
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

| Variable | Notes |
|---|---|
| `SECRET_KEY` | Signs every session token. The app refuses to boot on the public development key when `ENVIRONMENT` is not dev/test |
| `POSTGRES_PASSWORD` | Generate it the same way. Must match the password inside `DATABASE_URL` |
| `DATABASE_URL` | `postgresql://agriprofit:<password>@db:5432/agriprofit` |
| `CORS_ORIGINS` | JSON array. Exact scheme and host — a trailing slash or an http/https mismatch is the usual cause of "works locally, CORS error in production" |
| `TRUST_PROXY_HEADERS` | `true` **only** because a proxy in front overwrites `X-Forwarded-For`. With nothing in front, leave it false or every per-IP rate limit can be bypassed by sending the header yourself |

Then:

```bash
# Pattern A — your institution terminates TLS and proxies to 127.0.0.1:8080.
# The frontend routes /api to the backend itself; nothing else to configure.
docker compose -f docker-compose.prod.yml up -d --build

# Pattern B — use the bundled Caddy edge (set CADDY_DOMAIN in .env first).
docker compose -f docker-compose.prod.yml --profile edge up -d --build
```

`TRUST_PROXY_HEADERS` is worth a moment here. `.env.example` ships it as
`true`, which is correct for both patterns above: nginx and Caddy each
overwrite `X-Forwarded-For` with the real peer before the backend sees it, so
per-IP rate limiting counts the actual caller. The compose file defaults it to
`false` when the variable is absent, because believing that header with nothing
in front to overwrite it lets any caller pick their own rate-limit bucket. Set
it to `false` if you put something else in front that does not overwrite the
header — accepting that all callers then share one per-IP budget.

## 4. Verifying the deployment

```bash
docker compose -f docker-compose.prod.yml ps     # all services healthy

# Liveness — is the process up? Touches nothing else.
curl -fsS https://your-host/health
# -> {"status":"healthy"}

# Readiness — can it serve? Reports the database too.
curl -fsS https://your-host/health/ready
# -> {"status":"ready","checks":{"database":"ok"}}
```

**Check what comes back, not just the exit code.** Both paths are proxied to
the backend; if either proxy is misconfigured they fall through to the SPA and
return `200 text/html`, so `curl -fsS` exits 0 while proving nothing. That is
exactly how a broken deployment once looked healthy. A one-line assertion that
cannot be fooled:

```bash
curl -fsS https://your-host/health/ready | grep -q '"database":"ok"'   && echo OK || echo 'NOT READY — the check did not reach the backend'
```

The same applies to the API itself. This must print `application/json`, never
`text/html`:

```bash
curl -s -o /dev/null -w '%{content_type}
' https://your-host/api/v1/ledger/logs
```

Then check by hand, because these are the things a green health check does not
cover:

1. **The schema is current.**
   `docker compose -f docker-compose.prod.yml exec backend alembic current`
   should print the head revision. Migrations run automatically on boot; this
   confirms they finished.
2. **Registration works**, and the first account is an owner.
3. **A protected route rejects an anonymous caller** —
   `curl -o /dev/null -w '%{http_code}' https://your-host/api/v1/ledger/logs`
   must be `401`.
4. **The service worker installed.** Load the app, then DevTools → Application →
   Service Workers. It will not install over plain HTTP; if it is missing,
   check TLS before anything else.
5. **Take a backup and rehearse restoring it** before the system carries real
   data. See `docs/OPERATIONS.md` §2 — a backup you have never restored is not
   a backup.

## 5. Updating

```bash
cd agriprofit
sh ops/backup.sh                                        # first, always
git fetch --tags && git checkout <new tag>
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic current
```

The backend applies migrations on start, so a deploy brings the schema forward
on its own. Take the backup **before** the new image starts, because that is the
only artefact that predates the migration.

## 6. Rolling back

The two halves roll back differently, and conflating them is how a rollback
makes things worse.

**Code only** — the new build is bad, the schema is unchanged:

```bash
git checkout <previous tag>
docker compose -f docker-compose.prod.yml up -d --build
```

**Code and schema** — the release included a migration. Roll the schema back
*first*, while the old image is still what will start:

```bash
docker compose -f docker-compose.prod.yml stop backend
docker compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1
git checkout <previous tag>
docker compose -f docker-compose.prod.yml up -d --build backend
```

Every migration in this repository defines a `downgrade()`, and CI rehearses one
step of it on every run. Two caveats, both documented in the migrations
themselves:

- `e6a2b4c7d130`'s downgrade **can legitimately fail** once two farms share a
  `client_id`. Restoring a global unique index would mean discarding one farm's
  ledger row, and a migration must not choose which. Resolve the duplicates
  deliberately, then downgrade.
- Downgrading past `a8d4e1c60b27` discards role assignments. There is nowhere to
  keep them in the older schema.

If a downgrade cannot run, restore from the backup you took in §5. That is what
it is for.

## 7. What is deliberately not here

| Not included | Why |
|---|---|
| Kubernetes, service mesh, multi-region | One departmental host serving one institution. None of these solves a problem this workload has |
| Automated production deployment from CI | Deployment is a deliberate act, not something that happens because a branch moved. CI validates; a human deploys |
| Horizontal scaling of the backend | The rate limiter counts in-process, so two replicas would double the effective limits. Moving those counters to Redis is the prerequisite — see `backend/app/core/rate_limit.py` |
| Centralised log aggregation | Container logs to stdout, which whatever the institution already runs can collect. A bespoke stack here would be one more thing to maintain |
| Blue/green or canary releases | The rollback in §6 is proportionate to a single-host deployment with a maintenance window |
