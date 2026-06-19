# AgriProfit — Project Structure & Conventions

> Status: **PROPOSED** (awaiting approval). This document defines the target
> architecture for AgriProfit before the remaining modules are built. It is the
> single source of truth for *where things go* and *what they are named*. When
> code and this document disagree, update one of them deliberately — never let
> them silently drift.
>
> Domain vocabulary is owned by [`CONTEXT.md`](./CONTEXT.md). This document
> never redefines a domain term; it only says where that term's code lives.

---

## 1. Guiding principles

1. **No rewrite.** Everything currently working (dashboard, backend API, DB
   models, offline sync, Docker, tests) stays working. This is reorganization,
   not reinvention.
2. **One way to do each thing.** One app shell, one API client, one styling
   system, one place for shared types. Today several of these have two.
3. **Backend = layer-first. Frontend = feature-first.** The backend is a small
   set of well-understood layers; the frontend is a growing set of independent
   modules. Each is organized the way that scales for *it*.
4. **Domain language wins.** File, folder, route, and component names use the
   canonical terms from `CONTEXT.md` (Operational Log, Financial Transaction,
   Gross Margin, Equipment, Predictive DSS…). Avoid-listed synonyms are not
   used in code identifiers.
5. **New modules are scaffolded, not improvised.** Section 7 is a checklist so
   every module (Farm Records, P&L, Equipment, DSS, Investors, USSD/SMS,
   WhatsApp) looks like every other one.

---

## 2. Backend structure

The backend layering is already sound and largely stays. Target layout:

```
backend/
  alembic/                      # migrations (managed; see schema-managed-by-alembic memory)
  alembic.ini
  Dockerfile
  requirements.txt
  app/
    main.py                     # FastAPI app factory + middleware wiring ONLY
    api/
      router.py                 # aggregates every module router under /api/v1
      endpoints/                # one file per module — thin HTTP layer
        ledger.py               # Operational Logs + Financial Transactions
        equipment.py            # Equipment + Maintenance Logs
        dss.py                  # Predictive DSS
        reports.py              # (NEW) P&L report / export
        investors.py            # (NEW)
        messaging.py            # (NEW) USSD/SMS + WhatsApp webhooks
    services/                   # business logic — one file per module
      ledger_service.py
      equipment_service.py
      reports_service.py        # (NEW)
      ...
    models/
      database.py               # engine, SessionLocal, Base, get_db
      models.py                 # SQLAlchemy ORM models (split later if it bloats)
    schemas/
      schemas.py                # Pydantic models (split per-module when adding)
    core/
      config.py                 # (NEW) Settings (DATABASE_URL, CORS, etc.)
      enums.py                  # Category, TransactionType (shared)
    ml/                         # DSS implementation detail of the dss module
      predict.py
      train.py
  tests/
    conftest.py                 # SQLite + create_all fixtures
    test_*.py                   # one test file per module
```

### Backend layer rules (the contract)

- **`endpoints/*.py` are thin.** They parse the request, call exactly one
  service function, and return the result. No business logic, no direct DB
  queries beyond `Depends(get_db)`. Router prefix + tags match the module name.
- **`services/*.py` hold all business logic and DB access.** They take a
  `Session` and typed arguments, return ORM objects or plain values. Services
  never import `fastapi` (no `HTTPException` in services — raise domain errors
  or return sentinels; the endpoint maps them to HTTP).
- **`models/models.py`** is the only place ORM tables are defined.
- **`schemas/`** is the only place request/response shapes are defined.
- **`core/`** holds cross-cutting config and shared enums — things every layer
  may import but that belong to no single module.
- **`ml/`** is owned by the DSS module; nothing outside `dss.py` /
  `dss_service.py` imports it.

### New: `core/config.py`

Centralize environment config that is currently scattered:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    cors_origins: list[str] = ["http://localhost:5173"]
    class Config:
        env_file = ".env"

settings = Settings()
```

`database.py` reads `settings.database_url`; `main.py` reads
`settings.cors_origins` instead of hardcoded `["*"]`.

---

## 3. Frontend structure (feature-first)

**Decision: organize by feature/domain, not by type.** A type-first layout
(`/components`, `/pages`, `/hooks` holding everything) does not scale past ~3
screens — you end up hunting across four folders to touch one module. With 7
modules incoming, feature-first keeps each module's UI, data access, and types
co-located and independently buildable.

```
frontend/src/
  main.tsx                      # ReactDOM entry — unchanged
  app/                          # the application shell (one, and only one)
    App.tsx                     # providers + <Router> + routes table ONLY
    router.tsx                  # route → feature page mapping
    layout/
      AppShell.tsx              # sidebar + header + <Outlet/> frame
      Sidebar.tsx               # nav definition (single source of nav truth)
      Header.tsx                # top bar (title, Export, Log Activity actions)
      SyncStatus.tsx            # offline/pending badges (lifted out of App.tsx)
  features/
    dashboard/
      DashboardPage.tsx
      components/               # MetricCard, PnlChart, RecentActivities…
      api.ts                    # dashboard-specific calls (or reuse ledger api)
    farm-records/               # = Operational Logs (canonical domain term)
      FarmRecordsPage.tsx
      QuickLogForm.tsx
      api.ts
    reports/                    # = P&L Report
    equipment/
    dss/                        # = Predictive DSS
    investors/
    messaging/                  # = USSD/SMS + WhatsApp
  components/                   # SHARED dumb UI only (Button, Card, Badge…)
  hooks/                        # SHARED hooks (useOnlineStatus, usePendingSync)
  lib/                          # framework-agnostic infra
    db.ts                       # Dexie (offline queue) — unchanged
    sync.ts                     # flush/registerSyncListener — unchanged
    apiClient.ts                # the ONE axios instance (was services/api.ts)
  types/
    domain.ts                   # shared shapes mirroring backend schemas
  styles/
    theme.ts                    # shared colors, spacing, radii, font sizes
```

### Frontend rules (the contract)

- **One shell.** `app/layout/AppShell.tsx` is the only sidebar/header. The
  current inline shell in `App.tsx` moves here; `components/Layout.tsx` (dead)
  is deleted.
- **One API client.** `lib/apiClient.ts` is the only axios instance, with the
  env-based `baseURL`. No component constructs raw `axios` calls or hardcodes
  `http://localhost:8000`. Per-feature `api.ts` files import this client.
- **Pages are thin, like backend endpoints.** A `*Page.tsx` composes
  components and calls feature `api.ts`; data-shaping lives in hooks or the api
  module, not inline in JSX.
- **Shared vs feature components.** If two features use it → `components/`. If
  one feature owns it → that feature's `components/`. Default to feature-local;
  promote to shared only on the second consumer.
- **Styling: inline styles are the standard, backed by a shared theme.**
  Tailwind is **deliberately not used** — earlier attempts hit persistent
  Tailwind v3/v4 compilation conflicts that cost real time, and we will not
  reintroduce that risk near the deadline. The current inline-`style={{…}}`
  approach in `App.tsx` is the accepted pattern and stays. What changes is
  *organization*: the repeated magic values — the green palette (`#639922`,
  `#3B6D11`, `#97C459`…), spacing, border-radii, font sizes — move into a
  single `styles/theme.ts` constants object that components import, instead of
  being re-typed as raw hex/px across files. Components reference
  `theme.colors.primary` etc.; no new hardcoded hex or duplicated spacing.
  Example shape:

  ```ts
  // styles/theme.ts
  export const theme = {
    colors: {
      primary: '#639922', primaryDark: '#3B6D11', primaryLight: '#97C459',
      sidebarBg: '#0f1f09', accentBlue: '#185FA5', warn: '#BA7517',
      text: '#111', textMuted: '#888', border: '#e8ede4',
    },
    radius: { sm: '7px', md: '8px', lg: '12px' },
    space: { xs: '5px', sm: '8px', md: '12px', lg: '22px' },
    font: { xs: '10px', sm: '12px', md: '14px', lg: '17px' },
  } as const;
  ```
- **Routes live in one table** (`app/router.tsx`), and the `Sidebar` nav reads
  from the same route definitions so a link can never point at a missing route.

---

## 4. Naming conventions

| Thing | Convention | Example |
|-------|-----------|---------|
| Python module / file | `snake_case.py` | `ledger_service.py` |
| Python function / variable | `snake_case` | `create_operational_log` |
| Python class (ORM, schema, enum) | `PascalCase` | `OperationalLog`, `TransactionType` |
| Enum members | `UPPER_SNAKE` (value = lowercase str) | `Category.FERTILIZER = "fertilizer"` |
| DB table | `snake_case`, **plural** | `operational_logs` |
| DB column | `snake_case` | `financial_transaction_id`, `client_id` |
| API route segment | `kebab` or single word, plural noun | `/ledger/logs`, `/equipment` |
| React component file & component | `PascalCase.tsx` | `MetricCard.tsx` → `MetricCard` |
| React hook | `useCamelCase.ts` | `useOnlineStatus.ts` |
| Non-component TS file | `camelCase.ts` | `apiClient.ts`, `sync.ts` |
| Feature folder | `kebab-case` | `farm-records/` |
| TS type / interface | `PascalCase`, no `I` prefix | `OperationalLog`, `Summary` |

**Domain-name rule:** identifiers use the canonical term from `CONTEXT.md`.
"Farm Records" is acceptable as a *nav label* (user-facing) but the code,
types, and routes underneath use **Operational Log** (`operationalLogs`,
`/ledger/logs`). One user-facing label, one canonical code name — documented
together in the feature's folder.

---

## 5. Shared types & frontend/backend sync

Backend Pydantic schemas in `app/schemas/` are the source of truth for every
wire shape. The frontend must not redefine them ad-hoc (today `App.tsx` hand-
rolls `Summary` and `Log`).

**Now (zero new tooling):** a single `frontend/src/types/domain.ts` mirrors the
backend schemas by hand, names matching exactly (`OperationalLog`,
`FinancialTransaction`, `Equipment`, `Summary`). Every feature imports from
here; no inline shape definitions.

**Later (recommended upgrade, ~30 min):** generate types from the live API so
they can never drift:

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

FastAPI already serves `/openapi.json`, so this is a one-command, repeatable
generation (wire it into an npm script). Treat `domain.ts` as the bridge until
then. This is explicitly optional and not on the critical path for the capstone.

---

## 6. Offline sync (already built — where it belongs)

The existing offline-first machinery keeps its home and contracts:

- `lib/db.ts` — Dexie `pendingLogs` queue (IndexedDB).
- `lib/sync.ts` — `flushPendingLogs()` + `registerSyncListener()`.
- `client_id` (UUID) is the idempotency key end-to-end: generated in the
  submit handler, stored on the queued record, sent in the payload, enforced
  unique by `operational_logs.client_id` and short-circuited in
  `ledger_service.create_operational_log`.
- The online/offline + pending-count state and the `SyncStatus` badge move out
  of `App.tsx` into `hooks/useOnlineStatus.ts` + `app/layout/SyncStatus.tsx`,
  but the behavior is unchanged.

Any new write-capable module that must work offline reuses `lib/db.ts` +
`lib/sync.ts` with its own `client_id` — it does not invent a second queue.

---

## 7. How to scaffold a new module (the checklist)

Every module — existing or new — has the same shape on both ends. To add one
(e.g. **Investors**):

**Backend**
1. `core/enums.py` — add any shared enum members (if needed).
2. `models/models.py` — add ORM model(s) (`snake_case` plural tables).
3. Generate an Alembic migration (autogenerate in-container, `docker cp` out —
   see the `schema-managed-by-alembic` memory). **Never** `create_all`, never
   `down -v`.
4. `schemas/` — add request/response Pydantic models.
5. `services/<module>_service.py` — business logic + DB access.
6. `api/endpoints/<module>.py` — thin router (`prefix="/investors"`, matching
   `tags`).
7. `api/router.py` — `include_router` the new router.
8. `tests/test_<module>.py` — at least the happy path per endpoint.

**Frontend**
9. `features/<module>/` — `KebabPage.tsx` + `api.ts` (importing
   `lib/apiClient`) + feature `components/`.
10. `types/domain.ts` — add the shapes (mirroring step 4).
11. `app/router.tsx` — register the route.
12. `app/layout/Sidebar.tsx` — add the nav item (route pulled from the router
    table, so no dead links).

A module is "done" when: its endpoint returns real data, its page renders that
data through the shared client and shared types, `npm run build` passes, and
`pytest` covers the endpoint.

---

## 8. Module roadmap (target homes)

| Module (nav label) | Canonical domain | Backend | Frontend feature | Status |
|--------------------|------------------|---------|------------------|--------|
| Dashboard | (aggregate view) | `ledger.py` `/summary` | `features/dashboard` | live (in `App.tsx`) |
| Farm Records | Operational Log | `ledger.py` `/logs` | `features/farm-records` | API live, UI stub |
| P&L Report | Gross Margin report | `reports.py` (new) | `features/reports` | not built (queued: CSV export) |
| Equipment | Equipment + Maintenance | `equipment.py` | `features/equipment` | API live, UI orphaned |
| DSS Predict | Predictive DSS | `dss.py` + `ml/` | `features/dss` | API mock, UI orphaned |
| Investors | (new) | `investors.py` (new) | `features/investors` | not built |
| USSD/SMS | (new) | `messaging.py` (new) | `features/messaging` | not built |
| WhatsApp | (new) | `messaging.py` (new) | `features/messaging` | not built |
