# 01 — Green the CI + add the missing offline-sync test

Status: ready-for-agent

## What to build

The backend CI job is red: `test_dss_predict_without_model_returns_503` posts `{"features": [1, 2, 3]}` and asserts a 503, but the multi-crop DSS endpoint now validates its request body and returns **422** for that payload. Bring the test in line with the real contract, and add the offline-sync test the suite is currently missing.

End-to-end behaviour to land:

- The DSS-predict test reflects today's contract: an out-of-contract/empty payload is a `422` (validation), and the genuine "no model trained" path is exercised honestly (or removed if it can no longer occur given train-on-boot).
- A new test proves the offline write path round-trips: a log queued client-side and flushed lands exactly once, and replaying the same `client_id` returns the same record id (idempotency), so a farmer who loses connectivity mid-entry never double-books a transaction.
- CI is green on `main`.

## Acceptance criteria

- [ ] `python -m pytest backend/tests/ -v` passes locally with `DATABASE_URL=sqlite:///./test.db`
- [ ] The DSS-predict test asserts the real status code for its payload (no stale 503 expectation)
- [ ] A new test covers offline-queue replay: same `client_id` posted twice yields one record and identical ids
- [ ] The GitHub Actions backend job is green

## Blocked by

- None - can start immediately
