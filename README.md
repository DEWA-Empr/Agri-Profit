# AgriProfit

An offline-first farm record-management and decision-support platform for
Nigerian smallholder and medium-scale farms. Every operational record posts its
financial transaction in the same commit, so cost of production per crop is
known at sale rather than reconstructed afterwards.

FastAPI + PostgreSQL + Alembic · React + TypeScript PWA · Docker.

---

## What it does

| | |
|---|---|
| **Operational logbook** | Field activity recorded on a phone, queued in IndexedDB when there is no signal, synced idempotently on reconnect |
| **Financial ledger** | Every log posts a paired transaction in one commit. Append-only: deletes are refused, corrections are made by a linked contra entry |
| **Decision support (Tier 1)** | Per-crop gross margin and ranking, unit cost on a harvest and a marketable basis, retrospective break-even yield — computed from the farm's own ledger, no model |
| **Enterprise economics** | Cost-behaviour classification with explicit coverage, a depreciation overlay, proportional fixed-cost allocation, dual break-even prices, a yield-sensitivity matrix, partial budgets, Olympic-average yield baselines |
| **Post-harvest drying** | Page and Newton thin-layer fitting, wet↔dry basis conversion, water balance, safe-storage lookup — connecting a moisture reading to a price per marketable kilogram |
| **Yield forecast (Tier 2)** | A Random Forest trained on **synthetic** agronomic data, with a confidence band from the spread of the forest's own trees. Not a claim about field accuracy — see `docs/REPRODUCIBILITY.md` |
| **Stakeholder sharing** | A revocable, expiring, read-only link that lets a lender see a farm's report with no account. Tokens are stored hashed |

## Getting started

```bash
git clone <repository> && cd agriprofit
docker compose up -d --build          # app on :5173, API on :8000
```

Tests:

```bash
python -m pytest backend -q                    # 402 backend tests
cd frontend && npm ci && npm run test          # 119 frontend tests
```

The backend suite runs on in-memory SQLite and needs no services. Four migration
tests skip unless `MIGRATION_TEST_DATABASE_URL` names a throwaway PostgreSQL —
the chain uses ALTER-constraint operations SQLite cannot run, so CI verifies
them against a real Postgres.

## Access model

Authentication establishes identity; authorization decides what that identity
may do; farm scoping decides which rows it may touch. All three are enforced
server-side — the interface hides controls the server would refuse anyway, and
hiding is never the control.

| Role | May |
|---|---|
| `OWNER` | Everything, plus minting share links and managing members |
| `MANAGER` | Full operational and financial control; no external sharing, no member management |
| `WORKER` | Field entry and the farm's own log; no aggregate financial view, no reversals, no equipment |

Lenders and investors are **not** roles. They hold a share link — a capability,
not an account.

## Documentation

| File | For |
|---|---|
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Getting it running on a departmental host, and rolling back |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Backups, restores, health, logs, rate limits, troubleshooting |
| [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) | What the model figures claim, and how to re-derive them |
| [`CONTEXT.md`](CONTEXT.md) | Domain language — read this before naming anything |
| [`docs/adr/`](docs/adr/) | Decision records for the choices that were genuinely contested |
| [`docs/HARDENING_CHANGELOG.md`](docs/HARDENING_CHANGELOG.md) | What the production-hardening cycle changed, and which earlier documents it supersedes |

## Honest boundaries

Stated here rather than buried, because they bound what the platform may be
claimed to do:

- **The yield forecast is trained on synthetic data.** Its R² measures how well
  a Random Forest recovers a relationship that was constructed to be
  recoverable. It is evidence the pipeline works, not evidence it predicts
  Nigerian yields.
- **Immutability is application-layer discipline, not cryptography.** Records
  are append-only and audit-trailed; they are not tamper-*proof*.
- **The decision-support output is verified as arithmetic and unvalidated as
  advice.** Whether acting on a break-even price improves an outcome is untested.
- **There has been no field trial and no user evaluation.**
- **The rate limiter counts in-process.** Correct for one container; it does not
  span replicas.
- **No restore has been executed against a real database** in the environment
  this was built in. The procedure is documented and the scripts are written;
  run the rehearsal in `docs/OPERATIONS.md` §3 before trusting it.

## Licence

Not yet chosen. Add one before publishing.
