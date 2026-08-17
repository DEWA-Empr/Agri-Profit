# AGRI-PROFIT — Progress Summary

**Project:** A secure, offline-first farm record-management and decision-support
Progressive Web App (PWA) for Nigerian smallholder and medium-scale farmers,
unifying operational field records with financial accounting.

**Stack:** FastAPI + SQLAlchemy + PostgreSQL (backend) · React + TypeScript PWA
(frontend) · Alembic-managed schema · Dockerised.

## 1. What the system does today

The platform is a working end-to-end application, not a mockup. A farmer can
register, log field activities (offline if needed), have those automatically
become financial ledger entries, view a profit-and-loss statement, get
decision-support metrics computed from their own records, and share a read-only
report with an investor via a secure link.

## 2. Capabilities delivered (mapped to project objectives)

**Operational logbook + offline-first entry.** Field activities are logged on
the device and stored locally in IndexedDB when there is no connection, then
synced automatically on reconnect. Sync is idempotent (a `client_id` guard
prevents duplicate entries on a flaky network) — the single hardest requirement
for rural deployment, and it is tested.

**Financial ledger engine.** Operational inputs map automatically into a
single-entry ledger, eliminating double data-entry. Revenue and expense are
tracked per crop, and the system produces a P&L report with monthly breakdown
and CSV export for loan/grant applications.

**Ledger integrity.** Records are soft-immutable: deletes are blocked (405);
corrections happen through an auditable reversal that posts a category-preserving
contra entry, with a `reverses_id` audit trail. Double-reversal and cross-farm
tampering are rejected. This makes the financial history tamper-evident at the
application layer.

**Two-tier Decision Support System (DSS).**

- *Deterministic tier* — computes unit cost of production and per-crop gross
  margin directly from the farm's real ledger and operational records.
- *Predictive tier* — a RandomForest yield forecast (rainfall, fertilizer, soil
  pH, crop → t/ha) that returns an honest confidence band derived from the
  forest's own tree spread (replacing an earlier hardcoded confidence number).
  It is transparently trained on representative synthetic agronomic data, not
  the user's records — documented as such, pending accumulation of real field
  history.

**Identity and per-farm data boundary.** JWT authentication with bcrypt-hashed
passwords; every ledger, report, DSS and equipment query is scoped to the
authenticated user's farm. A cross-farm read returns 404 (no data leak), and
this isolation is proven by tests.

**Investor/stakeholder sharing.** A tokenised, read-only share link lets a bank
or investor view a farm's report without an account; tokens are SHA-256 hashed
at rest.

**Mechanization tracker.** Equipment and maintenance logging with depreciation
fields.

## 3. Engineering quality

- Test suite covering offline-sync idempotency, financial mapping, cross-farm
  isolation, JWT verification, and ledger-reversal rules; CI is green.
- Security hardening: secret-key boot guard, validated inputs, structured error
  handling and request logging.
- Alembic-managed migrations (non-destructive — existing rows were preserved and
  backfilled when auth/multitenancy was introduced).
- Deployable: production Docker build serving the offline-capable PWA.

## 4. Honest scope boundaries (deliberate, documented)

- The yield model is trained on synthetic data; its accuracy score is
  in-distribution and not a claim about real-farm performance.
- Immutability is soft (application-enforced), not cryptographic.
- External integrations (weather APIs, IoT sensors, live commodity prices,
  blockchain traceability) are future work, explicitly out of current scope.

These are captured in a draft Limitations & Future Work chapter.

## 5. Current status

Core functionality is complete and the codebase is in a pre-defense hardening
freeze. A read-only pre-defense audit was completed: no critical (P1) defects; a
small number of P2/P3 improvements (e.g., per-crop reversal netting in the DSS,
input-bound tightening) are documented as candidate future work, not blockers.
