import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPendingLogs, retryFailedLogs, registerSyncListener, purgeQueueForCurrentOwner } from './sync'
import { ledgerService } from './apiClient'
import type { PendingLog } from './db'

// Ticket 06: the offline write queue is the one path where a farmer's record
// exists only on the device, so a silent drop here loses data the server never
// saw. Chapter Four Section 4.2.3 records it as untested. Three behaviours carry
// the guarantee: a queued log is POSTed and cleared when the connection returns,
// a log that keeps failing gives up after exactly three attempts instead of
// retrying forever, and a 'failed' log stays recoverable through the UI's Retry
// action rather than being stranded in IndexedDB (see sync.ts).

// An in-memory stand-in for the Dexie table, implementing exactly the four
// operations sync.ts uses and nothing else. Hoisted because the vi.mock factory
// below is itself hoisted above the imports and has to close over it.
const { rows, pendingLogs } = vi.hoisted(() => {
  const rows: PendingLog[] = []
  // Matches the three query shapes sync.ts uses and nothing else:
  //   where('[ownerKey+status]').equals([owner, status]).toArray()
  //   where('ownerKey').equals(owner).delete()
  // plus the by-id delete/update below.
  const select = (index: string, value: string | string[]) =>
    index === '[ownerKey+status]'
      ? rows.filter((row) => row.ownerKey === value[0] && row.status === value[1])
      : rows.filter((row) => row.ownerKey === value)
  return {
    rows,
    pendingLogs: {
      where: (index: string) => ({
        equals: (value: string | string[]) => ({
          toArray: async () => select(index, value),
          count: async () => select(index, value).length,
          delete: async () => {
            const doomed = new Set(select(index, value))
            for (let i = rows.length - 1; i >= 0; i--) if (doomed.has(rows[i])) rows.splice(i, 1)
            return doomed.size
          },
        }),
      }),
      delete: async (id: number) => {
        const index = rows.findIndex((row) => row.id === id)
        if (index !== -1) rows.splice(index, 1)
      },
      update: async (id: number, changes: Partial<PendingLog>) => {
        const row = rows.find((candidate) => candidate.id === id)
        if (row) Object.assign(row, changes)
      },
    },
  }
})

vi.mock('./db', () => ({ db: { pendingLogs } }))

// The signed-in account, swappable per test. sync.ts reads it on every queue
// access, which is the whole point of the owner partition.
const { ownerState } = vi.hoisted(() => ({ ownerState: { key: null as string | null } }))
vi.mock('./queueOwner', () => ({ currentOwnerKey: () => ownerState.key }))

const FARM_A = 'user:1'
const FARM_B = 'user:2'

// The queue posts through the shared axios client, which throws on non-2xx.
// Mocking it is what lets "server down" be expressed as a rejected promise.
vi.mock('./apiClient', () => ({
  ledgerService: { createLog: vi.fn() },
}))

const createLog = vi.mocked(ledgerService.createLog)
// sync.ts ignores the response body; only resolve-vs-reject matters here.
const accepted = {} as Awaited<ReturnType<typeof ledgerService.createLog>>

// Drain the microtask queue for flushes that are fired but not awaited (the
// 'online' handler). A macrotask tick is enough — nothing in sync.ts uses timers.
const settle = () => new Promise((resolve) => setTimeout(resolve, 0))

let nextId = 1

const basePayload: PendingLog['payload'] = {
  activity_type: 'seed',
  description: 'Maize seed, 2 kg',
  financial_data: { amount: 3500, transaction_type: 'debit', category: 'seed' },
}

function queue(overrides: Partial<PendingLog> = {}): PendingLog {
  const row: PendingLog = {
    id: nextId++,
    ownerKey: FARM_A,
    clientId: `client-${nextId}`,
    payload: basePayload,
    status: 'pending',
    failCount: 0,
    createdAt: Date.now(),
    ...overrides,
  }
  rows.push(row)
  return row
}

beforeEach(() => {
  vi.clearAllMocks()
  rows.length = 0
  nextId = 1
  ownerState.key = FARM_A
  createLog.mockResolvedValue(accepted)
})

describe('flushPendingLogs', () => {
  it('posts a queued log and clears it from the queue', async () => {
    const log = queue()

    await flushPendingLogs()

    expect(createLog).toHaveBeenCalledTimes(1)
    expect(createLog).toHaveBeenCalledWith(log.payload)
    expect(rows).toHaveLength(0)
  })

  it('keeps the rest of the queue moving when one log fails', async () => {
    const failing = queue()
    const succeeding = queue()
    createLog.mockRejectedValueOnce(new Error('network down'))

    await flushPendingLogs()

    expect(createLog).toHaveBeenCalledTimes(2)
    expect(rows).toEqual([expect.objectContaining({ id: failing.id, status: 'pending', failCount: 1 })])
    expect(rows).not.toContain(succeeding)
  })

  it('runs one pass at a time when connectivity fires several flushes at once', async () => {
    // The 'online' event is handled in two places and the on-load flush is a
    // third caller, so overlapping flushes are the normal case, not a corner
    // one. Without the single-flight guard both passes read the same undeleted
    // rows and POST them twice.
    let accept = () => {}
    createLog.mockImplementationOnce(() => new Promise((resolve) => { accept = () => resolve(accepted) }))
    queue()
    queue()

    const firstPass = flushPendingLogs()
    const overlapping = flushPendingLogs()  // must return without touching the queue
    await settle()  // let the first pass reach the POST that is holding it open
    accept()
    await Promise.all([firstPass, overlapping])

    expect(createLog).toHaveBeenCalledTimes(2)  // two logs, one pass each
    expect(rows).toHaveLength(0)
  })

  it('gives up after exactly three failed attempts', async () => {
    createLog.mockRejectedValue(new Error('network down'))
    const log = queue()

    await flushPendingLogs()
    expect([log.failCount, log.status]).toEqual([1, 'pending'])

    await flushPendingLogs()
    expect([log.failCount, log.status]).toEqual([2, 'pending'])

    await flushPendingLogs()
    expect([log.failCount, log.status]).toEqual([3, 'failed'])

    // The fourth flush must not touch it. 'failed' is terminal until the user
    // retries; without this the queue would hammer a permanently bad payload.
    await flushPendingLogs()
    expect(createLog).toHaveBeenCalledTimes(3)
    expect([log.failCount, log.status]).toEqual([3, 'failed'])
  })
})

describe('registerSyncListener', () => {
  it('flushes the queue when the browser reports the connection back', async () => {
    const unregister = registerSyncListener()
    // The listener also flushes on load (queue empty, so no call). Let that
    // settle first, or its single-flight guard could swallow the flush below.
    await settle()
    expect(createLog).not.toHaveBeenCalled()

    const log = queue()
    window.dispatchEvent(new Event('online'))

    await vi.waitFor(() => expect(createLog).toHaveBeenCalledWith(log.payload))
    expect(rows).toHaveLength(0)

    // And it stops listening when unregistered, so a torn-down component leaves
    // no handler behind still POSTing.
    unregister()
    queue()
    window.dispatchEvent(new Event('online'))
    await settle()

    expect(createLog).toHaveBeenCalledTimes(1)
  })

  it('does not flush on load when the browser is already offline', async () => {
    const onLine = vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(false)
    queue()

    const unregister = registerSyncListener()
    await settle()

    // Posting here would fail and spend a strike on a log that never had a
    // connection to lose.
    expect(createLog).not.toHaveBeenCalled()

    unregister()
    onLine.mockRestore()
  })
})

describe('retryFailedLogs', () => {
  it('requeues a failed log and flushes it once the server is back', async () => {
    const log = queue({ status: 'failed', failCount: 3 })

    await flushPendingLogs()
    expect(createLog).not.toHaveBeenCalled()  // a failed log is invisible to a flush

    await retryFailedLogs()

    expect(createLog).toHaveBeenCalledTimes(1)
    expect(createLog).toHaveBeenCalledWith(log.payload)
    expect(rows).toHaveLength(0)
  })

  it('restarts the three-strike count instead of failing again immediately', async () => {
    const log = queue({ status: 'failed', failCount: 3 })
    createLog.mockRejectedValue(new Error('still down'))

    await retryFailedLogs()

    // Retrying against a server that is still down must cost one strike, not
    // send the log straight back to 'failed' on a stale count.
    expect(log.failCount).toBe(1)
    expect(log.status).toBe('pending')
  })
})

// --- Owner scoping: the queue is partitioned by the account that filled it ----
//
// The audit (docs/STATE_REPORT_2026-08-25.md §9.13) found the queue carried no
// identity at all: every pending row was flushed under whatever token was
// current, so a record captured offline by one farm was POSTed into the next
// account to sign in. These are the regressions for that.

describe('queue isolation by identity', () => {
  it('never flushes another account\'s queued write', async () => {
    // Distinguishable payloads: the default queue() payload is identical row to
    // row, and toHaveBeenCalledWith compares by value, so two default rows would
    // match each other and the negative assertion below would be vacuous.
    const mine = queue({ ownerKey: FARM_A, payload: { ...basePayload, description: 'farm A seed' } })
    const theirs = queue({ ownerKey: FARM_B, payload: { ...basePayload, description: 'farm B seed' } })

    await flushPendingLogs()

    expect(createLog).toHaveBeenCalledTimes(1)
    expect(createLog).toHaveBeenCalledWith(mine.payload)
    expect(createLog).not.toHaveBeenCalledWith(theirs.payload)
    // Farm B's record is untouched, not sent and not deleted: it is still B's.
    expect(rows).toEqual([expect.objectContaining({ id: theirs.id, ownerKey: FARM_B })])
  })

  it('never retries another account\'s failed write', async () => {
    const theirs = queue({ ownerKey: FARM_B, status: 'failed', failCount: 3 })

    await retryFailedLogs()

    expect(createLog).not.toHaveBeenCalled()
    expect(rows).toEqual([expect.objectContaining({ id: theirs.id, status: 'failed', failCount: 3 })])
  })

  it('leaves the queue alone entirely when nobody is signed in', async () => {
    queue({ ownerKey: FARM_A })
    ownerState.key = null

    await flushPendingLogs()
    await retryFailedLogs()

    // Signed out there is no account to POST as, so the rows wait rather than
    // being drained into a session that does not exist.
    expect(createLog).not.toHaveBeenCalled()
    expect(rows).toHaveLength(1)
  })
})

describe('logout cleanup', () => {
  it('drops the signed-in account\'s queued writes and nobody else\'s', async () => {
    queue({ ownerKey: FARM_A })
    queue({ ownerKey: FARM_A, status: 'failed', failCount: 3 })
    const theirs = queue({ ownerKey: FARM_B })

    await purgeQueueForCurrentOwner()

    // Both of A's rows go — pending and failed alike — and B's stays.
    expect(rows).toEqual([expect.objectContaining({ id: theirs.id, ownerKey: FARM_B })])
  })

  it('does nothing when there is no signed-in account to purge for', async () => {
    queue({ ownerKey: FARM_A })
    ownerState.key = null

    await purgeQueueForCurrentOwner()

    expect(rows).toHaveLength(1)
  })

  it('a write queued before logout is not flushed after a different account logs in', async () => {
    // The exact sequence the defect produced: farm A captures a record with no
    // connection, signs out, farm B signs in on the same browser, connectivity
    // returns. Before the fix this POSTed A's record into B's ledger.
    const captured = queue({ ownerKey: FARM_A })

    await purgeQueueForCurrentOwner()   // A signs out
    ownerState.key = FARM_B             // B signs in
    await flushPendingLogs()            // connection comes back

    expect(createLog).not.toHaveBeenCalled()
    expect(rows).not.toContain(captured)
  })

  it('survives the purge failing: the row is still inert for the next account', async () => {
    // purgeQueueForCurrentOwner is fire-and-forget and best-effort, so the
    // owner scope has to hold on its own if the purge never lands.
    const captured = queue({ ownerKey: FARM_A })

    ownerState.key = FARM_B             // B signs in; A's purge never happened
    await flushPendingLogs()

    expect(createLog).not.toHaveBeenCalled()
    expect(rows).toEqual([expect.objectContaining({ id: captured.id, ownerKey: FARM_A })])
  })
})
