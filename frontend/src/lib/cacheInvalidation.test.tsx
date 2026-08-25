import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, cleanup, fireEvent, waitFor } from '@testing-library/react'
import { AxiosHeaders, type AxiosAdapter, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import api, { dssService } from './apiClient'
import { saveOperationalLog } from './logs'
import { flushPendingLogs } from './sync'
import { API_READ_CACHE } from './apiCacheConfig'
import type { PendingLog } from './db'
import type {
  BreakEvenPriceResponse, CostStructureResponse, DssDecisionSupport, Equipment,
  MaintenanceLog, OperationalLogCreate, SensitivityResponse,
} from '../types/domain'
import { EnterpriseEconomics } from '../features/dss/components/EnterpriseEconomics'
import { MaintenancePanel } from '../features/equipment/components/MaintenancePanel'
import EquipmentPage from '../features/equipment/EquipmentPage'

// Phase 6b: the four farm-scoped write paths must leave no cached derived read
// behind them.
//
// WHY THESE TESTS RUN AGAINST A STAND-IN SERVICE WORKER RATHER THAN A SPY.
// Asserting that purgeApiReadCache() was called proves only that a function
// ran; it would still pass if the purge itself did nothing, which is precisely
// the bug class this phase exists to close. So the harness below reproduces the
// two halves the staleness actually needs — a Cache Storage the real purge
// deletes by name, and a read path that prefers a cached entry over the network
// — and every test seeds a real cache entry, mutates, then reads again. Replace
// purgeApiReadCache with a no-op and all four fail on the value, not the call.
//
// The harness models the SERVE half of StaleWhileRevalidate (a cache hit wins,
// which is the half that goes stale) and deliberately not the background
// revalidation: that race is a separate, out-of-scope concern and provoking it
// here would make these tests about something else.

// --- The device's Cache Storage -------------------------------------------
// One store, two readers: the stubbed `caches` global that the real
// purgeApiReadCache() deletes through, and the adapter below, which stands in
// for the service worker reading the same storage.
const swCache = new Map<string, Map<string, unknown>>()

const readCache = () => {
  let entries = swCache.get(API_READ_CACHE)
  if (!entries) {
    entries = new Map<string, unknown>()
    swCache.set(API_READ_CACHE, entries)
  }
  return entries
}

// --- The server ------------------------------------------------------------
// Mutable state plus derived reads computed from it at read time, the way the
// real /dss endpoints are. Nothing here is a canned response: a write changes
// the state and every read recomputes off it, so a stale figure can only have
// come from the cache.
const server = {
  logs: [] as OperationalLogCreate[],
  equipment: [] as Equipment[],
  maintenance: [] as MaintenanceLog[],
}

const spendOnCrop = (crop: string) =>
  server.logs
    .filter((log) => log.crop === crop && log.financial_data.transaction_type === 'debit')
    .reduce((total, log) => total + log.financial_data.amount, 0)

const maintenanceCost = () =>
  server.maintenance.reduce((total, log) => total + (log.cost ?? 0), 0)

const decisionSupport = (): DssDecisionSupport => {
  const expenses = spendOnCrop('maize') + maintenanceCost()
  return {
    crops: [{ crop: 'maize', revenue: 0, expenses: spendOnCrop('maize'), gross_margin: -spendOnCrop('maize') }],
    overall: { revenue: 0, expenses, gross_margin: -expenses },
  }
}

const costStructure = (): CostStructureResponse => {
  const variable = spendOnCrop('maize')
  const semi = maintenanceCost()
  const line = {
    variable_cost: variable,
    semi_variable_cost: semi,
    fixed_cost_recorded: 0,
    unclassified_cost: 0,
    total_recorded_cost: variable + semi,
    cash_cost: variable + semi,
    classification_coverage_pct: variable + semi === 0 ? null : 100,
    revenue_ngn: 0,
    cash_operating_cost_ngn: variable + semi,
    operating_expense_ratio_pct: null,
  }
  return { crops: [{ crop: 'maize', ...line }], farm: line }
}

const breakEvenPrice = (): BreakEvenPriceResponse => {
  const cash = spendOnCrop('maize') + maintenanceCost()
  return {
    crops: [{
      crop: 'maize',
      break_even_price_cash_ngn_per_kg: cash / 100,
      break_even_price_total_ngn_per_kg: cash / 100,
      variable_and_semi_variable_cost_ngn: cash,
      total_recorded_cost_ngn: cash,
      allocated_fixed_ngn: 0,
      total_cost_ngn: cash,
      marketable_mass_kg: 100,
      classification_coverage_pct: 100,
    }],
    period_days: 90,
    period_source: 'derived',
    period_fixed_cost_ngn: 0,
    equipment_count: server.equipment.length,
    equipment_unrated_count: server.equipment.filter((item) => item.depreciation_rate == null).length,
    total_direct_cost_all_crops: cash,
  }
}

const sensitivity = (): SensitivityResponse => {
  const cash = spendOnCrop('maize') + maintenanceCost()
  return {
    crops: [{
      crop: 'maize',
      conditional: true,
      baseline_marketable_mass_kg: 100,
      cash_cost_ngn: cash,
      total_cost_ngn: cash,
      rows: [{
        percentage: 100,
        marketable_mass_kg: 100,
        break_even_price_cash_ngn_per_kg: cash / 100,
        break_even_price_total_ngn_per_kg: cash / 100,
      }],
    }],
    period_days: 90,
    period_source: 'derived',
  }
}

function route(method: string, url: string, body: unknown): unknown {
  if (method === 'get') {
    if (url.endsWith('/dss/decision-support')) return decisionSupport()
    if (url.endsWith('/dss/cost-structure')) return costStructure()
    if (url.endsWith('/dss/break-even-price')) return breakEvenPrice()
    if (url.endsWith('/dss/sensitivity')) return sensitivity()
    if (url.endsWith('/equipment/')) return server.equipment
    const forEquipment = /\/equipment\/(\d+)\/maintenance$/.exec(url)
    if (forEquipment) return server.maintenance.filter((log) => log.equipment_id === Number(forEquipment[1]))
  }
  if (method === 'post') {
    if (url.endsWith('/ledger/logs')) {
      const payload = body as OperationalLogCreate
      server.logs.push(payload)
      return { id: server.logs.length, activity_type: payload.activity_type, timestamp: new Date().toISOString() }
    }
    if (url.endsWith('/equipment/maintenance')) {
      const payload = body as MaintenanceLog
      const created = { ...payload, id: server.maintenance.length + 1, service_date: new Date().toISOString() }
      server.maintenance.push(created)
      return created
    }
    if (url.endsWith('/equipment/')) {
      const payload = body as Equipment
      const created = { ...payload, id: server.equipment.length + 1 }
      server.equipment.push(created)
      return created
    }
  }
  throw new Error(`No route in the test server for ${method.toUpperCase()} ${url}`)
}

// The URL set the production service worker caches. Copied from the
// runtimeCaching entry in vite.config.ts rather than imported, because
// importing that config would pull the PWA plugin into the test run.
const CACHED_READS = /\/api\/v1\/(ledger|reports|dss\/(decision-support|cost-structure|break-even-price|sensitivity|yield-baseline))/

const respond = (config: InternalAxiosRequestConfig, data: unknown): AxiosResponse => ({
  data, status: 200, statusText: 'OK', headers: new AxiosHeaders(), config,
})

// Stands where the service worker stands: between the app's single axios client
// and the network.
const serviceWorkerAdapter: AxiosAdapter = async (config) => {
  const url = `${config.baseURL ?? ''}${config.url ?? ''}`
  const method = (config.method ?? 'get').toLowerCase()
  const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data

  if (method === 'get' && CACHED_READS.test(url)) {
    const entries = readCache()
    if (entries.has(url)) return respond(config, entries.get(url))
    const fresh = route(method, url, body)
    entries.set(url, fresh)
    return respond(config, fresh)
  }
  return respond(config, route(method, url, body))
}

// --- The offline queue -----------------------------------------------------
// An in-memory stand-in for the Dexie table, implementing only the operations
// logs.ts and sync.ts use (same approach as sync.test.ts).
const { rows, pendingLogs } = vi.hoisted(() => {
  const rows: PendingLog[] = []
  return {
    rows,
    pendingLogs: {
      add: async (row: PendingLog) => { rows.push({ ...row, id: rows.length + 1 }) },
      where: (field: 'status') => ({
        equals: (value: string) => ({ toArray: async () => rows.filter((row) => row[field] === value) }),
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

const seedLog = (amount: number): OperationalLogCreate => ({
  activity_type: 'fertilizer',
  description: `Urea, ${amount}`,
  crop: 'maize',
  financial_data: { amount, transaction_type: 'debit', category: 'fertilizer' },
})

const card = { padding: '12px' }
const bodyText = () => document.body.textContent?.replace(/\s+/g, ' ') ?? ''

const originalAdapter = api.defaults.adapter

beforeEach(() => {
  swCache.clear()
  server.logs.length = 0
  server.equipment.length = 0
  server.maintenance.length = 0
  rows.length = 0
  vi.stubGlobal('caches', { delete: async (name: string) => swCache.delete(name) })
  api.defaults.adapter = serviceWorkerAdapter
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
  api.defaults.adapter = originalAdapter
})

describe('a log write invalidates the cached derived reads', () => {
  it('serves the new record on the next DSS read instead of the pre-write cache', async () => {
    // Seed: a read taken before the write, which is how a stale entry gets into
    // the cache in the first place.
    expect((await dssService.getDecisionSupport()).data.crops[0].expenses).toBe(0)
    expect(readCache().size).toBe(1)

    const result = await saveOperationalLog(seedLog(3500), true)
    expect(result.status).toBe('saved')

    // The freshness claim: this read is served post-purge from the server and
    // carries the 3,500 the cached entry could not know about.
    expect((await dssService.getDecisionSupport()).data.crops[0].expenses).toBe(3500)
  })
})

describe('an offline queue flush invalidates the cached derived reads', () => {
  it('serves every flushed record on the next DSS read', async () => {
    rows.push(
      { id: 1, clientId: 'a', payload: seedLog(3500), status: 'pending', failCount: 0, createdAt: 1 },
      { id: 2, clientId: 'b', payload: seedLog(2000), status: 'pending', failCount: 0, createdAt: 2 },
    )
    expect((await dssService.getDecisionSupport()).data.crops[0].expenses).toBe(0)

    // sync.ts adds no purge of its own: it inherits one per log from
    // ledgerService.createLog, and the last of them lands after the last POST.
    await flushPendingLogs()
    expect(rows).toHaveLength(0)

    // 5,500 is only reachable if BOTH writes are visible — a cache surviving
    // the flush would still read 0, and one surviving the final write, 3,500.
    expect((await dssService.getDecisionSupport()).data.crops[0].expenses).toBe(5500)
  })
})

describe('creating equipment invalidates the cached depreciation qualification', () => {
  it('re-renders the break-even panel with the new unrated-asset counts', async () => {
    server.equipment.push(
      { id: 1, name: 'Tractor', depreciation_rate: 10 },
      { id: 2, name: 'Sprayer', depreciation_rate: null },
    )

    // Seed: the sentence a user reads today, cached along with the response.
    render(<EnterpriseEconomics card={card} />)
    await waitFor(() => expect(bodyText()).toContain('1 of your 2 assets has no depreciation rate recorded'))
    cleanup()

    // Add a third asset with no depreciation rate, through the page's own form.
    const page = render(<EquipmentPage />)
    fireEvent.click(page.getByText('Add Equipment'))
    fireEvent.change(page.container.querySelector('input[required]')!, { target: { value: 'Thresher' } })
    fireEvent.click(page.getByText('Save'))
    await waitFor(() => expect(server.equipment).toHaveLength(3))
    cleanup()

    // The rendered qualification is the thing that goes stale, so it is the
    // thing asserted: without the purge this panel still reads "1 of your 2".
    render(<EnterpriseEconomics card={card} />)
    await waitFor(() => expect(bodyText()).toContain('2 of your 3 assets have no depreciation rate recorded'))
    expect(bodyText()).not.toContain('1 of your 2 assets')
  })
})

describe('logging maintenance invalidates the cached cost structure', () => {
  it('serves the new semi-variable cost on the next cost-structure read', async () => {
    const tractor: Equipment = { id: 1, name: 'Tractor', depreciation_rate: 10 }
    server.equipment.push(tractor)

    expect((await dssService.getCostStructure()).data.crops[0].semi_variable_cost).toBe(0)

    const panel = render(<MaintenancePanel equipment={tractor} onClose={() => {}} />)
    fireEvent.change(panel.getByPlaceholderText('What was serviced?'), { target: { value: 'Gearbox service' } })
    fireEvent.change(panel.getByPlaceholderText('Cost (₦)'), { target: { value: '12000' } })
    fireEvent.click(panel.getByText('Log maintenance'))
    await waitFor(() => expect(server.maintenance).toHaveLength(1))

    // A repair is SEMI_VARIABLE cost, and it moves the cash cost behind the
    // break-even price to cover cash cost with it.
    const structure = (await dssService.getCostStructure()).data.crops[0]
    expect(structure.semi_variable_cost).toBe(12000)
    expect(structure.cash_cost).toBe(12000)
  })
})
