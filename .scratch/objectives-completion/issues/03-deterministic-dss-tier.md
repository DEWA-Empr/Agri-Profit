# 03 — Deterministic DSS tier from the real ledger (keystone)

Status: ready-for-agent

## What to build

The decision-support story is currently inverted: the heavy ML yield model exists, but the **rule-based baseline tier** the academic scope demands does not, and the dashboard's `DecisionSupport` panel is a hardcoded mock ("the rules engine that would derive these from the ledger and field data isn't built yet"). Build that deterministic tier and feed it real data.

End-to-end behaviour to land:

- A backend service computes deterministic decision metrics directly from the persisted ledger — at minimum **unit cost of production** and **per-crop gross margin** — by reading actual Operational Logs and their paired Financial Transactions (grouped by Activity Category / crop). No synthetic inputs.
- A new endpoint exposes these metrics.
- The dashboard `DecisionSupport` panel renders the live computed metrics, replacing the hardcoded array. When there is no data, it shows the existing empty-state pattern rather than fabricated numbers.
- This is the rule-based first tier; the existing RandomForest forecast remains the optional second tier on top.

## Acceptance criteria

- [ ] A service derives unit cost of production and per-crop gross margin from real Operational Logs + Financial Transactions
- [ ] An endpoint returns these metrics and is covered by a test asserting exact figures from seeded ledger rows
- [ ] `DecisionSupport.tsx` consumes the endpoint; the hardcoded mock array is gone
- [ ] Empty ledger renders the shared empty state, not placeholder numbers

## Blocked by

- 01 — Green the CI + add the missing offline-sync test
