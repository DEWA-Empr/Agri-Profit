import { db } from './db';

const API_BASE = (import.meta as { env: Record<string, string> }).env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Single-flight guard: connectivity changes can trigger several flush calls at
// once (the 'online' event is handled in two places, plus the initial flush on
// load). Without this guard the same pending log can be POSTed concurrently;
// the server's client_id idempotency would dedupe it, but we avoid the wasted
// round-trips and the double-delete race entirely.
let flushing = false;

export async function flushPendingLogs(): Promise<void> {
  if (flushing) return;
  flushing = true;
  try {
    const pending = await db.pendingLogs.where('status').equals('pending').toArray();
    for (const log of pending) {
      try {
        const res = await fetch(`${API_BASE}/ledger/logs`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(log.payload),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        await db.pendingLogs.delete(log.id!);
      } catch {
        const failCount = log.failCount + 1;
        await db.pendingLogs.update(log.id!, {
          failCount,
          status: failCount >= 3 ? 'failed' : 'pending',
        });
      }
    }
  } finally {
    flushing = false;
  }
}

// Requeue logs that exhausted their retries. Called from the UI's "Retry"
// action so a 'failed' log is never silently stranded in IndexedDB — the user
// can re-attempt once the underlying problem (server down, bad payload) clears.
export async function retryFailedLogs(): Promise<void> {
  const failed = await db.pendingLogs.where('status').equals('failed').toArray();
  for (const log of failed) {
    await db.pendingLogs.update(log.id!, { status: 'pending', failCount: 0 });
  }
  await flushPendingLogs();
}

export function registerSyncListener(): () => void {
  const handler = () => flushPendingLogs();
  window.addEventListener('online', handler);
  if (navigator.onLine) flushPendingLogs();
  return () => window.removeEventListener('online', handler);
}
