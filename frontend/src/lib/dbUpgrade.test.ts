// The v1 -> v2 IndexedDB upgrade, exercised against a real IndexedDB.
//
// WHY THIS FILE EXISTS SEPARATELY FROM sync.test.ts. sync.test.ts replaces the
// Dexie table with an in-memory stand-in, which is right for testing the flush
// logic and useless for testing a schema migration: a stand-in has no schema, no
// version and no upgrade hook, so it cannot show that a database written by the
// shipped v1 build survives being opened by the shipped v2 build. That is the
// only question this file asks, and it asks it of a real IndexedDB.
//
// `fake-indexeddb/auto` installs a spec-conformant IndexedDB implementation on
// globalThis (jsdom ships none). It is the whole of the new test infrastructure;
// Dexie itself is the real dependency, unmocked, running its real upgrade path.
//
// LIMITATION, STATED PLAINLY. fake-indexeddb implements the IDB spec, not
// Chrome. It exercises Dexie's version/upgrade machinery and the upgrade
// callback in lib/db.ts against real object stores, transactions and indexes,
// which is where the defect lived. It does not speak to browser-specific
// storage eviction, quota, or a vendor's own IDB bugs; a device that has evicted
// its database presents an empty v1, not a corrupt one, and the upgrade of an
// empty v1 is covered below.
import 'fake-indexeddb/auto'
import Dexie from 'dexie'
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { setToken, clearToken } from './authToken'
import type { PendingLog } from './db'

// The queue POSTs through the shared axios client. Mocked so the "can the
// upgraded database still participate in sync" assertion needs no network — the
// db and queueOwner modules are deliberately NOT mocked.
vi.mock('./apiClient', () => ({ ledgerService: { createLog: vi.fn(async () => ({})) } }))

const DB_NAME = 'agriprofit'

// A token whose `sub` is 7, so the real queueOwner derives 'user:7'.
const jwt = (sub: string) => {
  const b64url = (value: string) =>
    btoa(value).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return b64url('{"alg":"HS256","typ":"JWT"}') + '.' + b64url(JSON.stringify({ sub })) + '.sig'
}
const OWNER = 'user:7'

// A v1 row, exactly as the shipped v1 build wrote it: no ownerKey, because the
// field did not exist. Typed as the pre-v2 shape so the omission is deliberate
// rather than a slip.
type V1Row = Omit<PendingLog, 'ownerKey'>

const v1Rows: V1Row[] = [
  {
    id: 1,
    clientId: 'offline-0001',
    payload: {
      activity_type: 'fertilizer',
      description: 'Applied 5 bags of NPK',
      quantity: 5,
      unit: 'bags',
      financial_data: {
        amount: 25000,
        transaction_type: 'debit',
        category: 'fertilizer',
        description: 'Purchase of 5 NPK bags',
      },
    } as PendingLog['payload'],
    status: 'pending',
    failCount: 0,
    createdAt: 1_750_000_000_000,
  },
  {
    id: 2,
    clientId: 'offline-0002',
    payload: {
      activity_type: 'yield',
      description: 'Maize harvest',
      quantity: 7.8,
      unit: 'kg',
      crop: 'maize',
      financial_data: {
        amount: 3510,
        transaction_type: 'credit',
        category: 'yield',
        description: 'Maize sale',
      },
    } as PendingLog['payload'],
    status: 'pending',
    failCount: 1,
    createdAt: 1_750_000_100_000,
  },
  {
    // A row that exhausted its retries under v1. It must still be 'failed'
    // afterwards — an upgrade that quietly re-queued it would re-POST a write
    // the server may already have rejected three times.
    id: 3,
    clientId: 'offline-0003',
    payload: {
      activity_type: 'mechanization',
      description: 'diesel for the ridger',
      quantity: 1,
      unit: 'unit',
      financial_data: {
        amount: 3000,
        transaction_type: 'debit',
        category: 'mechanization',
        description: 'diesel',
      },
    } as PendingLog['payload'],
    status: 'failed',
    failCount: 3,
    createdAt: 1_750_000_200_000,
  },
]

/** Write a genuine v1 database: v1's schema string, v1's rows, then close. */
async function seedV1Database(rows: V1Row[] = v1Rows): Promise<void> {
  const legacy = new Dexie(DB_NAME)
  // The exact v1 declaration from lib/db.ts before the owner partition landed.
  legacy.version(1).stores({ pendingLogs: '++id, clientId, status, createdAt' })
  await legacy.open()
  expect(legacy.verno).toBe(1)
  if (rows.length) await legacy.table('pendingLogs').bulkAdd(rows)
  legacy.close()
}

/** Load a fresh copy of the v2 module graph, so each test opens the db once. */
async function openV2() {
  vi.resetModules()
  const dbModule = await import('./db')
  const syncModule = await import('./sync')
  await dbModule.db.open()
  return { db: dbModule.db, sync: syncModule }
}

beforeEach(async () => {
  await Dexie.delete(DB_NAME)
  localStorage.clear()
})

afterEach(async () => {
  await Dexie.delete(DB_NAME)
  clearToken()
})

describe('IndexedDB v1 -> v2 upgrade, signed in', () => {
  it('opens the v1 database, keeps every row, and attributes them to the signed-in account', async () => {
    await seedV1Database()
    setToken(jwt('7'))

    const { db } = await openV2()

    expect(db.verno).toBe(2)

    const upgraded = await db.pendingLogs.orderBy('id').toArray()
    // Nothing was lost: three rows in, three rows out, same ids.
    expect(upgraded).toHaveLength(3)
    expect(upgraded.map((row) => row.id)).toEqual([1, 2, 3])

    // Every pre-existing field survives intact. The payload matters most — it is
    // the farmer's record, and the server has never seen it.
    upgraded.forEach((row, index) => {
      const original = v1Rows[index]
      expect(row.clientId).toBe(original.clientId)
      expect(row.status).toBe(original.status)
      expect(row.failCount).toBe(original.failCount)
      expect(row.createdAt).toBe(original.createdAt)
      expect(row.payload).toEqual(original.payload)
    })

    // And the new field is populated on all of them, including the failed one.
    expect(upgraded.map((row) => row.ownerKey)).toEqual([OWNER, OWNER, OWNER])
  })

  it('establishes the ownerKey and [ownerKey+status] indexes on the upgraded store', async () => {
    await seedV1Database()
    setToken(jwt('7'))

    const { db } = await openV2()

    // Declared on the schema...
    const indexes = db.pendingLogs.schema.indexes.map((index) => index.name)
    expect(indexes).toContain('ownerKey')
    expect(indexes).toContain('[ownerKey+status]')

    // ...and actually usable as indexes, which a schema string alone does not
    // prove. These are the two query shapes sync.ts issues.
    const pending = await db.pendingLogs.where('[ownerKey+status]').equals([OWNER, 'pending']).toArray()
    expect(pending.map((row) => row.clientId)).toEqual(['offline-0001', 'offline-0002'])

    const failed = await db.pendingLogs.where('[ownerKey+status]').equals([OWNER, 'failed']).toArray()
    expect(failed.map((row) => row.clientId)).toEqual(['offline-0003'])

    expect(await db.pendingLogs.where('ownerKey').equals(OWNER).count()).toBe(3)

    // A different account sees none of them. The upgrade did not create a row
    // some other tenant can flush.
    expect(await db.pendingLogs.where('ownerKey').equals('user:8').count()).toBe(0)
  })

  it('leaves the upgraded rows able to participate in the current sync logic', async () => {
    await seedV1Database()
    setToken(jwt('7'))

    const { db, sync } = await openV2()
    const { ledgerService } = await import('./apiClient')
    const createLog = vi.mocked(ledgerService.createLog)
    createLog.mockClear()

    await sync.flushPendingLogs()

    // The two pending rows were POSTed — the migrated payloads, unchanged — and
    // cleared. This is the end-to-end claim: a record captured offline under v1
    // still reaches the server after the upgrade.
    expect(createLog).toHaveBeenCalledTimes(2)
    expect(createLog.mock.calls.map((call) => call[0])).toEqual([v1Rows[0].payload, v1Rows[1].payload])

    const remaining = await db.pendingLogs.toArray()
    expect(remaining.map((row) => row.clientId)).toEqual(['offline-0003'])

    // The failed row is still recoverable through the UI's Retry action.
    await sync.retryFailedLogs()
    expect(createLog).toHaveBeenCalledTimes(3)
    expect(await db.pendingLogs.count()).toBe(0)
  })

  it('purges the migrated rows on logout, by owner', async () => {
    await seedV1Database()
    setToken(jwt('7'))

    const { db, sync } = await openV2()
    await sync.purgeQueueForCurrentOwner()

    // Rows that arrived with no owner at all are reachable by the logout purge
    // once attributed — the upgrade did not strand them outside it.
    expect(await db.pendingLogs.count()).toBe(0)
  })
})

describe('IndexedDB v1 -> v2 upgrade, signed out', () => {
  it('drops unattributable rows rather than leaving them for the next account', async () => {
    await seedV1Database()
    // No token: these rows cannot be attributed to anybody, and lib/db.ts
    // deliberately clears them rather than leaving a loaded gun for whoever
    // signs in next. That is documented data loss, so it is pinned as one.
    expect(localStorage.getItem('agriprofit_token')).toBeNull()

    const { db } = await openV2()

    expect(db.verno).toBe(2)
    expect(await db.pendingLogs.count()).toBe(0)

    // The schema still upgraded correctly — the clear is not a failure path.
    const indexes = db.pendingLogs.schema.indexes.map((index) => index.name)
    expect(indexes).toContain('[ownerKey+status]')
  })

  it('upgrades an empty v1 database without error', async () => {
    await seedV1Database([])

    const { db } = await openV2()

    expect(db.verno).toBe(2)
    expect(await db.pendingLogs.count()).toBe(0)
  })
})

describe('a fresh install', () => {
  it('opens straight at v2 with the owner indexes, never running the upgrade', async () => {
    // No v1 database was ever written. This is the case the in-memory stand-in
    // already covers; it is here so the upgrade tests above cannot be passing
    // by silently exercising it instead.
    setToken(jwt('7'))

    const { db } = await openV2()

    expect(db.verno).toBe(2)
    expect(await db.pendingLogs.count()).toBe(0)
    expect(db.pendingLogs.schema.indexes.map((index) => index.name)).toContain('[ownerKey+status]')
  })
})
