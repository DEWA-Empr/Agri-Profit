# Deploying AgriProfit

For a departmental deployment: one host, Docker Compose, TLS in front. Not a
hyperscale architecture, and deliberately not — there is no Kubernetes, no
service mesh and no multi-region story here, because nothing about this
workload calls for one.

Operating it afterwards — backups, restores, incidents — is `docs/OPERATIONS.md`.

---

## 1. What gets deployed

```
                    ┌─────────────────────────────────────────┐
  browser ──HTTPS──▶│  edge (Caddy, optional)                 │
                    │  · terminates TLS, renews automatically │
                    │  · /api/*  ──▶ backend:8000             │
                    │  · /*      ──▶ frontend:8080            │
                    └───────────────┬─────────────────────────┘
                                    │  (compose network, no published ports)
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
          ┌───────────────────┐         ┌────────────────────────┐
          │ frontend          │         │ backend                │
          │ nginx + static    │         │ uvicorn + FastAPI      │
          │ PWA build         │         │ migrations run on boot │
          └───────────────────┘         └───────────┬────────────┘
                                                    ▼
                                        ┌────────────────────────┐
                                        │ db — PostgreSQL 15     │
                                        │ named volume, no port  │
                                        └────────────────────────┘
```

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
# Without the bundled TLS edge (your institution proxies to 127.0.0.1:8080):
docker compose -f docker-compose.prod.yml up -d --build

# With it:
docker compose -f docker-compose.prod.yml --profile edge up -d --build
```

## 4. Verifying the deployment

```bash
docker compose -f docker-compose.prod.yml ps          # all services healthy
curl -fsS https://your-host/api/v1/../health          # liveness  -> {"status":"healthy"}
curl -fsS https://your-host/health/ready              # readiness -> database ok
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
