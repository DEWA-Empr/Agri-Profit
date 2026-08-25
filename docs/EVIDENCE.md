# Evidence — the read-cache invalidation tests actually test the cache

This file records how the Phase 6b/6c cache-invalidation tests were verified to
be **load-bearing**, and how to repeat that verification. It exists because the
strongest claim this work makes — *these tests fail if the purge stops working* —
is not visible in the test output when everything passes, and was until now only
demonstrated in a transcript.

Everything below is a procedure to re-run, not a result to take on trust.

## Provenance

| | |
|---|---|
| **Subject** | `frontend/src/lib/cacheInvalidation.test.tsx` — five tests, one per farm-scoped write path |
| **Under test** | `purgeApiReadCache()` in `frontend/src/lib/apiCache.ts`, and the call sites that invoke it |
| **Runner** | Vitest **4.1.10**, `win32-x64`, `node v24.15.0` |
| **Working directory** | `frontend/` |
| **Commit at time of run** | Phase 6c working tree, on `feat/enterprise-economics` (parent `d82419d`) |
| **Date of run** | 2026-08-25 |

## Why a mutation test and not a spy

`expect(purgeApiReadCache).toHaveBeenCalled()` proves a function ran. It passes
just as happily when the purge deletes nothing, which is the exact bug class
these tests exist to close. So each test instead seeds a **real** cache entry
through a stand-in service worker, performs the write, and re-reads — asserting
on the **value** that comes back.

The verification below confirms that: with the purge neutered, every one of the
five fails on a value or on rendered text, and none fails on a call count.

## The edit

Replace the body of `purgeApiReadCache` in `frontend/src/lib/apiCache.ts` with a
no-op. The signature and the export are unchanged, so every call site still
resolves and still awaits — only the deletion stops happening:

```ts
export async function purgeApiReadCache(): Promise<void> {
  void API_READ_CACHE;
  return;
}
```

For reference, the real body it replaces:

```ts
export async function purgeApiReadCache(): Promise<void> {
  if (typeof caches === 'undefined') return; // no Cache Storage (e.g. dev/SSR)
  try {
    await caches.delete(API_READ_CACHE);
  } catch {
    // Best-effort: a failure here must never block login/logout.
  }
}
```

`void API_READ_CACHE;` is there only to keep the now-unused import from failing
lint during the experiment. **Revert the file afterwards** — the no-op must not
be committed.

## The command

```
cd frontend
npx vitest run src/lib/cacheInvalidation.test.tsx
```

## Expected result: 5 failed, 0 passed

```
 ❯ src/lib/cacheInvalidation.test.tsx (5 tests | 5 failed)
```

Each failure, with the value asserted and where the stale value comes from:

| # | Write path | Failure message | Asserted | Received (stale) | Why the stale value is that |
|---|---|---|---|---|---|
| 1 | Online log save (`saveOperationalLog` → `ledgerService.createLog`) | `AssertionError: expected +0 to be 3500 // Object.is equality` | `3500` | `0` | The DSS read cached before the ₦3,500 fertiliser log was written |
| 2 | Offline queue flush (`flushPendingLogs`) | `AssertionError: expected +0 to be 5500 // Object.is equality` | `5500` | `0` | The DSS read cached before either queued log (₦3,500 + ₦2,000) was flushed |
| 3 | Equipment create (`EquipmentPage`) | `AssertionError: expected ' Enterprise economicsEverything below…' to contain '2 of your 3 assets have no depreciati…'` | rendered text `2 of your 3 assets have no depreciation rate recorded` | the panel still renders `1 of your 2 assets has no depreciation rate recorded` | The break-even read cached before the third, unrated asset was added |
| 4 | Maintenance log (`MaintenancePanel`) | `AssertionError: expected +0 to be 12000 // Object.is equality` | `12000` | `0` | The cost-structure read cached before the ₦12,000 gearbox service |
| 5 | Reversal (`ledgerService.reverseLog`) | `AssertionError: expected 5500 to be 2000 // Object.is equality` | `2000` | `5500` | The DSS read cached before the ₦3,500 log was reversed; ₦2,000 survives it |

Note the shape of #5: unlike #1, #2 and #4 its stale value is **not** zero. The
two logs (₦3,500 and ₦2,000) are both written before the seeding read, so the
cached figure is ₦5,500 and the correct figure is ₦2,000. A cache that survived
the reversal reads ₦5,500; a ledger that lost the second log would read ₦0.
Only a purge plus a correctly-netted contra produces ₦2,000.

Note also the shape of #3: it fails on rendered text rather than on a number,
because the thing that goes stale for a user there is a sentence.

## What this does and does not establish

**Does:** that all five tests depend on `purgeApiReadCache` doing real work, and
that each one's assertion moves when the cache is stale.

**Does not:** anything about the background-revalidation half of
StaleWhileRevalidate. The harness models only the serve half (a cache hit wins).
The revalidation race is written up beside the `runtimeCaching` block in
`frontend/vite.config.ts` — it is reasoned from the handler's ordering, has not
been observed, and is not addressed by these tests.

## Where the purge lives (Phase 6c)

The invariant, for anyone re-running the above and wondering why a component no
longer purges: **mutating `ledgerService` methods purge; components do not.**
`createLog` and `reverseLog` each purge on 2xx and on the status codes that mean
the server's state already moved (409 for both; 404 additionally for
`reverseLog`).

Two declared exceptions, because they do not route through the ledger client and
call `purgeApiReadCache` directly:

| File | Line |
|---|---|
| `frontend/src/features/equipment/EquipmentPage.tsx` | `51` |
| `frontend/src/features/equipment/components/MaintenancePanel.tsx` | `53` |

(Import lines are `4` in both files. Verify with
`grep -n "purgeApiReadCache" frontend/src/features/equipment/EquipmentPage.tsx frontend/src/features/equipment/components/MaintenancePanel.tsx`.)
