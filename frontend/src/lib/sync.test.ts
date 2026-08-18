import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPendingLogs, retryFailedLogs, registerSyncListener } from './sync'
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
  return {
    rows,
    pendingLogs: {
      where: (field: 'status') => ({
        equals: (value: string) => ({
          toArray: async () => rows.filter((row) => row[field] === value),
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

function queue(overrides: Partial<PendingLog> = {}): PendingLog {
  const row: PendingLog = {
    id: nextId++,
    clientId: `client-${nextId}`,
    payload: {
      activity_type: 'seed',
      description: 'Maize seed, 2 kg',
      financial_data: { amount: 3500, transaction_type: 'debit', category: 'seed' },
    },
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
