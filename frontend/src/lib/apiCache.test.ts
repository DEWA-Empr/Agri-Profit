import { describe, it, expect, vi, afterEach } from 'vitest'
import { purgeApiReadCache } from './apiCache'
import { API_READ_CACHE } from './apiCacheConfig'

// Ticket 09: prove the purge helper deletes *exactly* the shared offline-read
// cache. If this drifted (e.g. a wrong or stale cache name), login/logout would
// silently leave one farm's cached reads available to the next account on a
// shared device — the whole point of purging (see apiCache.ts).
describe('purgeApiReadCache', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('deletes exactly the shared offline-read cache', async () => {
    const del = vi.fn().mockResolvedValue(true)
    vi.stubGlobal('caches', { delete: del })

    await purgeApiReadCache()

    expect(del).toHaveBeenCalledWith(API_READ_CACHE)
  })
})
