import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// Test-only Vite config. Kept separate from vite.config.ts on purpose: the app
// config carries the PWA plugin, which we do NOT want running during unit tests
// (it would try to generate a service worker). Vitest auto-prefers this file, so
// tests get JSX/TSX support via the react plugin and a DOM via jsdom, nothing
// more. Scope is deliberately narrow — see AuthProvider.test.tsx / apiCache.test.ts.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      // `include` is set deliberately. Without it the v8 provider measures only
      // the files a test happened to import, which reports ~91% — a figure that
      // describes the four tested modules, not the frontend. Chapter Four needs
      // the honest denominator: every source file under src, tested or not.
      include: ['src/**/*.{ts,tsx}'],
      reporter: ['text'],
    },
  },
})
