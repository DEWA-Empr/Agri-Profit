# 04 — Authentication + per-farm data boundary

Status: done

## What to build

Objective 3 (a secure data-sharing framework) has not started: there is no User/tenant table and no auth middleware, yet `python-jose[cryptography]` and `passlib[bcrypt]` already sit unused in `requirements.txt`. Establish identity and a data boundary so records belong to a farm rather than to a shared global pool.

End-to-end behaviour to land:

- A Farm (tenant) and User model with an Alembic migration (schema is Alembic-managed — add a migration, do not use `create_all`).
- Register and login endpoints issuing a JWT; passwords hashed with passlib.
- Every read/write query in the ledger, reports, equipment and DSS paths is scoped to the authenticated user's farm; a user cannot see another farm's data.
- A frontend login screen and token handling (attached to API requests, persisted across reloads, cleared on logout). Existing pages work once authenticated.

## Acceptance criteria

- [x] Farm + User tables created via a new Alembic migration
- [x] Register/login endpoints return a JWT; passwords are hashed, never stored plaintext
- [x] All domain queries are farm-scoped; a cross-farm read is rejected (test proves isolation)
- [x] Frontend login flow stores the token, authenticates requests, and supports logout
- [x] CI stays green

## Blocked by

- None - can start immediately (sequence after 03 by priority, not by hard dependency)

## Comments

**2026-07-03 — Shipped.** Commits `f6ea4b0` (feat: authentication and per-farm
data boundary) + `2dbbfff` (chore: build resilience), both on `origin/main`.

- **Schema/migration:** new `Farm` + `User` models; `farm_id` (NOT NULL, FK,
  indexed) on `operational_logs`, `financial_transactions`, `equipment`,
  `maintenance_logs`. Migration `b2e4d6f81a09` creates the tables, backfills
  pre-existing rows into a seeded **"Legacy Farm"** (non-destructive), then
  enforces NOT NULL.
- **Auth:** `/auth/register` (creates farm + first user) and `/auth/login`
  issue a JWT; `get_current_user` resolves the bearer token. Passwords hashed
  with **bcrypt** — swapped from `passlib[bcrypt]` because passlib 1.7.4 cannot
  read the installed bcrypt 5.x (same algorithm, `$2b$` hashes, never plaintext).
- **Scope:** every ledger/reports/DSS/equipment query filters by the caller's
  `farm_id`; the `client_id` idempotency lookup is farm-scoped too. Tier-2 ML
  endpoints require auth but stay unscoped (shared synthetic model).
- **Frontend:** token persisted in `localStorage` (survives reload), axios
  request interceptor attaches it, 401 interceptor clears it → login; Login
  screen (sign in + register), app gate, header Sign out.
- **Tests:** full suite runs authenticated via new fixtures; added
  register/login, password-hashing, 401-rejection and cross-farm isolation
  tests. **22 passed.**
- **Go-live verified on live Postgres:** Alembic at head `b2e4d6f81a09`; all
  existing rows (34 op-logs / 34 fin-tx / 1 equipment / 1 maintenance) preserved
  under Legacy Farm, counts matched the pre-migration backup, zero NULL
  `farm_id`; register/login/isolation confirmed end to end against the running
  API.
