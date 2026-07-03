# 05 — Read-only tokenised investor/lender share link

Status: done

## What to build

The trust-building half of Objective 3: a farmer can grant a bank or investor a read-only view of their standardised P&L and yield reporting without handing over an account. The `InvestorsPage` is currently a ComingSoon stub.

End-to-end behaviour to land:

- A share-token model + Alembic migration: a farm owner mints a revocable, opaque token granting read-only access to that farm's P&L report and yield figures.
- A tokenised read-only endpoint that returns the P&L + yield report for the farm the token belongs to, requiring no login — only the token. The token cannot be used to write anything or to reach any other farm.
- A minimal public, read-only report view rendered from a shared link (the page an investor opens), and replacement of the `InvestorsPage` stub with the owner-side UI to mint and revoke a link.

## Acceptance criteria

- [x] Share-token model created via Alembic migration; tokens are revocable
- [x] A token-only endpoint returns P&L + yield for the owning farm and rejects writes and other farms' data
- [x] A public read-only report view renders from the shared link with no login
- [x] `InvestorsPage` lets the owner mint and revoke a link; the ComingSoon stub is gone
- [x] Test proves a revoked token is denied

## Blocked by

- 04 — Authentication + per-farm data boundary

## Comments

**2026-07-03 — Shipped.** Commits `589ffd3` (feat) + `274d908` (scroll fix),
both verified live. Migration `c3f7a1e58d24` applied to Postgres (Alembic head,
`share_tokens` present and empty; existing data untouched).

- **Model/migration:** `ShareToken` (`farm_id`, `token_hash`, `label`,
  `revoked`, `created_at`). Only a **SHA-256 hash** of the token is stored; the
  raw token (`secrets.token_urlsafe(32)`, 256-bit opaque) is shown once at mint.
  A DB compromise cannot reveal a usable link.
- **Endpoints:** owner-side (authed, farm-scoped) `POST /share/links`,
  `GET /share/links` (metadata only — never re-serves the token),
  `POST /share/links/{id}/revoke`; public `GET /share/report/{token}` (no login).
- **Cross-farm is unrepresentable:** the report derives `farm_id` from the token
  row and accepts no farm from the caller. Revocation flips `revoked`; the public
  lookup filters it out immediately.
- **Frontend:** `InvestorsPage` mints (one-time copy banner) / lists / revokes;
  `PublicInvestorReport` renders the shared P&L + yield read-only; `App.tsx`
  `useMatch('/investor/:token')` bypasses the auth gate without disturbing the
  route tree. Follow-up `274d908` made that page its own scroll container
  (`body { overflow: hidden }` had clipped it outside the AppShell).
- **Tests (28 passed):** mint/list/revoke, public report figures, **revoked
  token → 404**, cross-farm isolation, unauthenticated mint → 401, and a share
  token cannot write or authenticate any domain route (401 / 405).
