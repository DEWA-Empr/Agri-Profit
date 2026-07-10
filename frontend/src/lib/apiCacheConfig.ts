// Single source of truth for the offline-read cache name (ticket 06/08).
//
// Imported by BOTH the service-worker config (vite.config.ts, which writes to
// this cache via Workbox runtimeCaching) and the runtime purge helper
// (apiCache.ts, which deletes it on auth change). Keeping one constant means the
// writer and the purger can never drift apart to different cache names.
export const API_READ_CACHE = 'agriprofit-api-reads';
