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
