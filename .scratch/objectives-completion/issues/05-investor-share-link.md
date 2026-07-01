# 05 — Read-only tokenised investor/lender share link

Status: ready-for-agent

## What to build

The trust-building half of Objective 3: a farmer can grant a bank or investor a read-only view of their standardised P&L and yield reporting without handing over an account. The `InvestorsPage` is currently a ComingSoon stub.

End-to-end behaviour to land:

- A share-token model + Alembic migration: a farm owner mints a revocable, opaque token granting read-only access to that farm's P&L report and yield figures.
- A tokenised read-only endpoint that returns the P&L + yield report for the farm the token belongs to, requiring no login — only the token. The token cannot be used to write anything or to reach any other farm.
- A minimal public, read-only report view rendered from a shared link (the page an investor opens), and replacement of the `InvestorsPage` stub with the owner-side UI to mint and revoke a link.

## Acceptance criteria

- [ ] Share-token model created via Alembic migration; tokens are revocable
- [ ] A token-only endpoint returns P&L + yield for the owning farm and rejects writes and other farms' data
- [ ] A public read-only report view renders from the shared link with no login
- [ ] `InvestorsPage` lets the owner mint and revoke a link; the ComingSoon stub is gone
- [ ] Test proves a revoked token is denied

## Blocked by

- 04 — Authentication + per-farm data boundary
