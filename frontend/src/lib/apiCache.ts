// Offline-read cache lifecycle (ticket 06).
//
// The service worker caches authenticated, farm-scoped GET responses under this
// cache name (the runtimeCaching config in vite.config.ts writes it; both sides
// import the same constant so they can't drift). Because workbox keys entries by
// URL and ignores the Authorization header, cached data from one farm must never
// be served to another account on a shared browser. So we purge this cache on
// every auth change (login/logout): cached reads then only ever accelerate the
// *same* logged-in farm.
import { API_READ_CACHE } from './apiCacheConfig';

export async function purgeApiReadCache(): Promise<void> {
  if (typeof caches === 'undefined') return; // no Cache Storage (e.g. dev/SSR)
  try {
    await caches.delete(API_READ_CACHE);
  } catch {
    // Best-effort: a failure here must never block login/logout.
  }
}
