import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Dev-side guard against stale service workers. A previous production build can
// leave a PWA worker registered on this origin (e.g. localhost:5173); in dev it
// would keep serving cached assets and silently shadow the vite dev server. So
// in development we proactively unregister any leftover worker — the production
// PWA registration (registerType 'autoUpdate') is unaffected. Compiled out of
// production builds via the import.meta.env.DEV guard.
if (import.meta.env.DEV && 'serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => registration.unregister())
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
