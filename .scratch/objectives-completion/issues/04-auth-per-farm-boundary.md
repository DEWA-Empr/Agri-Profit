# 04 — Authentication + per-farm data boundary

Status: ready-for-agent

## What to build

Objective 3 (a secure data-sharing framework) has not started: there is no User/tenant table and no auth middleware, yet `python-jose[cryptography]` and `passlib[bcrypt]` already sit unused in `requirements.txt`. Establish identity and a data boundary so records belong to a farm rather than to a shared global pool.

End-to-end behaviour to land:

- A Farm (tenant) and User model with an Alembic migration (schema is Alembic-managed — add a migration, do not use `create_all`).
- Register and login endpoints issuing a JWT; passwords hashed with passlib.
- Every read/write query in the ledger, reports, equipment and DSS paths is scoped to the authenticated user's farm; a user cannot see another farm's data.
- A frontend login screen and token handling (attached to API requests, persisted across reloads, cleared on logout). Existing pages work once authenticated.

## Acceptance criteria

- [ ] Farm + User tables created via a new Alembic migration
- [ ] Register/login endpoints return a JWT; passwords are hashed, never stored plaintext
- [ ] All domain queries are farm-scoped; a cross-farm read is rejected (test proves isolation)
- [ ] Frontend login flow stores the token, authenticates requests, and supports logout
- [ ] CI stays green

## Blocked by

- None - can start immediately (sequence after 03 by priority, not by hard dependency)
