import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
// Shared with the runtime purge helper (src/lib/apiCache.ts) so the SW writes and
// the app purges the exact same cache name — one source of truth.
import { API_READ_CACHE } from './src/lib/apiCacheConfig'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      // Guard against stale workers in production: an updated worker deletes the
      // precache from previous builds rather than leaving it to serve old
      // assets. (registerType 'autoUpdate' already applies skipWaiting +
      // clientsClaim, so a new worker takes control immediately instead of
      // waiting behind the old one.) devOptions is intentionally left disabled:
      // we do NOT want a service worker in dev, since a dev worker can itself
      // cache and shadow HMR. The dev-side orphan guard lives in src/main.tsx.
      workbox: {
        cleanupOutdatedCaches: true,
        // Offline reads (ticket 06): cache the GET endpoints the dashboard and
        // P&L read from. StaleWhileRevalidate serves the last-seen response
        // instantly (so views open with no connection) and revalidates in the
        // background when online. These responses are authenticated and
        // farm-scoped, so the cache is purged on login/logout (see
        // lib/apiCache + AuthProvider) — cached data never crosses accounts on a
        // shared device. NOTE: runtimeCaching lives only in the generated
        // production service worker; the vite dev server runs no worker, so this
        // takes effect in a built/installed PWA, not `npm run dev`.
        //
        // UNVERIFIED, REASONED FROM THE ORDERING — NOT AN OBSERVED FAILURE.
        // StaleWhileRevalidate serves the cached body and starts a revalidation
        // fetch in the background. Nothing sequences that fetch against
        // purgeApiReadCache(): a revalidation begun BEFORE a purge can still be
        // in flight when the purge deletes the cache, and Workbox will then
        // write its response — a body the server produced before the mutation —
        // into the store the next read recreates. The cache would be repopulated
        // stale, by a fetch that predates the write.
        //
        // This is deduced from the handler's ordering alone. It has NOT been
        // reproduced, provoked in a test, or seen in the wild, and no attempt is
        // made here to close it; the window is narrow and a fix needs the worker
        // and the app to agree on an epoch, which is out of scope for Phase 6.
        // Treat it as a hypothesis to be tested before it is treated as a bug —
        // and note that the Phase 6b tests (src/lib/cacheInvalidation.test.tsx)
        // deliberately model only the SERVE half of this handler, so they do not
        // and cannot speak to it either way.
        runtimeCaching: [
          {
            // The enterprise-economics reads are listed one by one rather than
            // matched with a bare `dss/` prefix, so /dss/model and /dss/predict
            // stay out: model metadata is not farm data and has no business in
            // a cache that is purged on an auth change for tenant reasons.
            urlPattern: /\/api\/v1\/(ledger|reports|dss\/(decision-support|cost-structure|break-even-price|sensitivity|yield-baseline))/,
            handler: 'StaleWhileRevalidate',
            method: 'GET',
            options: {
              cacheName: API_READ_CACHE,
              cacheableResponse: { statuses: [200] },
              expiration: {
                maxEntries: 64,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 days
              },
            },
          },
        ],
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'AgriProfit',
        short_name: 'AgriProfit',
        description: 'Integrated farm record management and decision-support platform',
        theme_color: '#2e7d32',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
})
