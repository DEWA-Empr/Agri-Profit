# Verification-artifact cleanup — 2026-08-25

The 2026-08-25 verification run created records in the live Postgres database
(`agrip-db-1`, database `agriprofit`) purely to exercise two code paths. They are
not seeded demo data and not a farmer's records, and they would appear in thesis
screenshots. This file records exactly what was removed, on what evidence, and
what was confirmed unchanged afterwards.

Nothing was reseeded. No migration was run. No pre-existing record was touched.

## 1. What was identified as an artifact, and why

| Table | ID | Value | Why it is an artifact |
| --- | --- | --- | --- |
| `farms` | 28 | `Verify Farm A` | Created `2026-08-25 11:40:56.331078+00`, inside the verification run. Named for the test, not the domain. |
| `farms` | 29 | `Verify Farm B` | Created `2026-08-25 11:40:56.824472+00`, 0.5 s later — the second tenant of a two-tenant probe. |
| `users` | 27 | `verify-a-518@test.example` | Only user of farm 28; `@test.example` is the reserved test domain. |
| `users` | 28 | `verify-b-518@test.example` | Only user of farm 29. |
| `operational_logs` | 1076 | farm 28, `cross-farm collision probe`, `client_id=collide-0001` | The cross-farm `client_id` probe for migration `e6a2b4c7d130`. |
| `operational_logs` | 1077 | farm 29, `cross-farm collision probe`, `client_id=collide-0001` | Its counterpart: the same key in the second farm. |
| `operational_logs` | 1078 | farm 28, `readings round-trip probe`, `client_id=verify-drying-0001` | The drying-readings round-trip probe. |
| `financial_transactions` | 1076, 1077, 1078 | the paired transactions of the three logs above | Paired-write invariant: each log carries exactly one transaction, and deleting the log without it would orphan the money. |

Every `farm_id`-bearing table was enumerated for farms 28 and 29 before deciding
the set was complete:

```
SELECT table_name, column_name FROM information_schema.columns
WHERE column_name = 'farm_id' AND table_schema = 'public';
-- equipment, financial_transactions, maintenance_logs,
-- operational_logs, share_tokens, users
```

The two verification farms held rows in exactly two of those six tables
(`operational_logs`, `financial_transactions`) plus one `users` row each. They
held no equipment, no maintenance log and no share token.

## 2. Safety checks run before deletion

Both returned zero rows, so nothing outside the artifact set referenced it:

```
SELECT id, farm_id, reverses_id FROM operational_logs
WHERE reverses_id IN (1076,1077,1078);                       -- 0 rows

SELECT id, farm_id, financial_transaction_id FROM operational_logs
WHERE financial_transaction_id IN (1076,1077,1078)
  AND farm_id NOT IN (28,29);                                -- 0 rows
```

No log elsewhere reverses one of these, and no other farm's log is paired to one
of these transactions. The three logs are also the three highest ids in the
table, so nothing was written after them that could depend on them.

## 3. The deletion

One transaction, in foreign-key order (logs reference transactions; users and
logs reference farms):

```sql
BEGIN;
DELETE FROM operational_logs       WHERE id IN (1076,1077,1078);   -- DELETE 3
DELETE FROM financial_transactions WHERE id IN (1076,1077,1078);   -- DELETE 3
DELETE FROM users                  WHERE id IN (27,28);            -- DELETE 2
DELETE FROM farms                  WHERE id IN (28,29);            -- DELETE 2
COMMIT;
```

Ten rows, all of them named in §1. Every statement targets an explicit id list;
none deletes by predicate.

## 4. Verified after the deletion

**The artifacts are gone.**

- `SELECT id, name FROM farms ORDER BY id` returns 14 rows, ids 1–27, with no
  `Verify Farm A` or `Verify Farm B`.
- `SELECT id FROM operational_logs WHERE id IN (1076,1077,1078)` — 0 rows.
- `SELECT id FROM financial_transactions WHERE id IN (1076,1077,1078)` — 0 rows.
- `SELECT max(id) FROM operational_logs` is now **1075** (the last seeded row,
  farm 26's sorghum diesel log), was 1078.

**Everything else is unchanged.** Row counts before → after:

| Table | Before | After | Delta | Expected |
| --- | --- | --- | --- | --- |
| `farms` | 16 | 14 | −2 | −2 |
| `users` | 15 | 13 | −2 | −2 |
| `operational_logs` | 112 | 109 | −3 | −3 |
| `financial_transactions` | 112 | 109 | −3 | −3 |
| `equipment` | 3 | 3 | 0 | 0 |
| `maintenance_logs` | 1 | 1 | 0 | 0 |
| `share_tokens` | 10 | 10 | 0 | 0 |

Per-farm log counts, before and after, for every farm that survives — identical
in each case:

| farm_id | 1 | 3 | 4 | 17 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| before | 34 | 4 | 9 | 2 | 7 | 3 | 5 | 4 | 3 | 5 | 5 | 28 |
| after | 34 | 4 | 9 | 2 | 7 | 3 | 5 | 4 | 3 | 5 | 5 | 28 |

Farm 26 (`Demo Farm`, the bioprocess/enterprise-economics demo that Chapter Four
figures are read from) still holds all 28 of its logs, and farm 1 (`Legacy Farm`,
the pre-auth backfill) still holds all 34.

## 5. Note on id gaps

Farm ids 2, 6–16 and 18 were already absent before this cleanup, and 28–29 are
now absent too. Postgres sequences do not reuse ids, so a gap is normal and is
not evidence of a further deletion. The only ids removed by this operation are
the ten listed in §1.
