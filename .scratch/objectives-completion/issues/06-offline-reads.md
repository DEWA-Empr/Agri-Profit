# 06 — Offline reads via service-worker runtime caching

Status: ready-for-agent

## What to build

Offline support is currently write-only: the Dexie queue lets a farmer record activity offline, but the VitePWA service worker precaches only the app shell, so opening the dashboard or reports with no connection shows nothing. Make reads survive intermittent connectivity, as the low-bandwidth/intermittent-power objective requires.

End-to-end behaviour to land:

- VitePWA runtime caching (stale-while-revalidate) for the report and ledger GET endpoints, so the dashboard and P&L open from cache when offline and refresh silently when back online.
- The existing offline indicator reflects that cached data is being shown.

If the team decides building this is out of budget for the marked submission, the fallback deliverable is to narrow the "works offline" claim in `CONTEXT.md`/`PRD.md` to "offline data capture only" so the docs stay honest — but the runtime-caching build is the preferred outcome.

## Acceptance criteria

- [ ] VitePWA configured with runtime caching for report/ledger GETs (stale-while-revalidate)
- [ ] With the network disabled, a previously-loaded dashboard + P&L still render from cache
- [ ] Cached views refresh once connectivity returns
- [ ] If descoped instead: the offline claim in docs is narrowed to capture-only

## Blocked by

- None - can start immediately
