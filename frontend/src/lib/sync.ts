import { db } from './db';
import { ledgerService } from './apiClient';
import { currentOwnerKey } from './queueOwner';

// Single-flight guard: connectivity changes can trigger several flush calls at
// once (the 'online' event is handled in two places, plus the initial flush on
// load). Without this guard the same pending log can be POSTed concurrently;
// the server's client_id idempotency would dedupe it, but we avoid the wasted
// round-trips and the double-delete race entirely.
let flushing = false;

// Every queue read is scoped to the account currently signed in. A row queued by
// one farm must never be POSTed under another farm's token — the flush uses
// whatever bearer token is current, so an unscoped read writes one farm's field
// records into another farm's ledger. Signed out, there is no account to flush
// as, so the queue is left untouched rather than drained.
function ownerScopedRows(status: 'pending' | 'failed') {
  const owner = currentOwnerKey();
  if (!owner) return null;
  return db.pendingLogs.where('[ownerKey+status]').equals([owner, status]);
}

export async function flushPendingLogs(): Promise<void> {
  if (flushing) return;
  flushing = true;
  try {
    const scoped = ownerScopedRows('pending');
    if (!scoped) return;
    const pending = await scoped.toArray();
    for (const log of pending) {
      try {
        // Go through the shared axios client (throws on non-2xx) so the queue
        // uses the same single HTTP layer as the rest of the app.
        await ledgerService.createLog(log.payload);
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
// Scoped to the signed-in account for the same reason the flush is.
export async function retryFailedLogs(): Promise<void> {
  const scoped = ownerScopedRows('failed');
  if (!scoped) return;
  const failed = await scoped.toArray();
  for (const log of failed) {
    await db.pendingLogs.update(log.id!, { status: 'pending', failCount: 0 });
  }
  await flushPendingLogs();
}

// Drop every queued write belonging to one account. Called on logout, before the
// token is cleared, so unsent records do not sit in a shared browser's IndexedDB
// after their owner has left it — the same reason the read cache is purged
// there (see lib/apiCache).
//
// This DOES discard unsent work. That is the deliberate trade: the queue holds
// one farm's ledger records in plain IndexedDB, the device is shared, and the
// alternative is leaving them readable and restorable by whoever uses the
// browser next. Signing out is an explicit act; the pending count is on screen
// in the sidebar while it is non-zero (app/layout/SyncStatus).
export async function purgeQueueForCurrentOwner(): Promise<void> {
  const owner = currentOwnerKey();
  if (!owner) return;
  try {
    await db.pendingLogs.where('ownerKey').equals(owner).delete();
  } catch {
    // Best-effort: a failure here must never block logout.
  }
}

export function registerSyncListener(): () => void {
  const handler = () => flushPendingLogs();
  window.addEventListener('online', handler);
  if (navigator.onLine) flushPendingLogs();
  return () => window.removeEventListener('online', handler);
}
