import { db } from './db';

const API_BASE = (import.meta as { env: Record<string, string> }).env.VITE_API_URL || 'http://localhost:8000/api/v1';

export async function flushPendingLogs(): Promise<void> {
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
}

export function registerSyncListener(): () => void {
  const handler = () => flushPendingLogs();
  window.addEventListener('online', handler);
  if (navigator.onLine) flushPendingLogs();
  return () => window.removeEventListener('online', handler);
}
