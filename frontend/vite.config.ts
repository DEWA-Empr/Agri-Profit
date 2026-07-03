import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

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
        runtimeCaching: [
          {
            urlPattern: /\/api\/v1\/(ledger|reports|dss\/decision-support)/,
            handler: 'StaleWhileRevalidate',
            method: 'GET',
            options: {
              cacheName: 'agriprofit-api-reads',
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
